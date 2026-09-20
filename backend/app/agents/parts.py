"""Parts agent: deterministic electrical-spec parsing plus Qwen 4B enrichment."""

import re
import uuid
from typing import Any, Dict, List, Optional

from app.core.logging import logger
from app.schemas.parts_analysis import PartEvidence, PartInput, PartSpecification
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway

_SYSTEM_PROMPT = """Extract only specifications explicitly supported by the supplied part text. Return numeric values in SI units. Do not infer absent values. Preserve the supplied part_id and do not invent manufacturer or part numbers."""
_INTERFACES = ("I2C", "SPI", "UART", "CAN", "USB", "PWM", "GPIO", "RS-485")


def _number(value: str) -> float:
    return float(value.replace(",", ""))


def _scaled(value: str, unit: str, scale: Dict[str, float]) -> float:
    return _number(value) * scale[unit.lower().replace("μ", "u")]


class PartsAgent:
    """Extracts explicit component specifications without asking an LLM to do arithmetic."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()

    @staticmethod
    def extract_deterministic(part: PartInput) -> PartSpecification:
        """Parse common datasheet notation and normalize numeric units to SI."""
        text = part.source_text
        spec = PartSpecification(
            part_id=part.part_id, manufacturer=part.manufacturer,
            part_number=part.part_number, power_role=part.power_role,
        )

        def add(field: str, value: Any) -> None:
            setattr(spec, field, value)
            spec.evidence.append(PartEvidence(field=field, value=str(value), method="deterministic"))

        manufacturer = re.search(r"\bmanufacturer\s*[:#-]\s*([^\n,;]+)", text, re.I)
        part_number = re.search(r"\b(?:part\s*(?:number|no\.?|#)|p/?n)\s*[:#-]\s*([^\n,;]+)", text, re.I)
        if manufacturer and not spec.manufacturer:
            add("manufacturer", manufacturer.group(1).strip())
        if part_number and not spec.part_number:
            add("part_number", part_number.group(1).strip())

        def range_or_value(pattern: str, minimum: str, maximum: str, scale: float = 1.0) -> None:
            match = re.search(pattern, text, re.I)
            if not match:
                return
            low = _number(match.group(1)) * scale
            high = _number(match.group(2) or match.group(1)) * scale
            add(minimum, low)
            add(maximum, high)

        range_or_value(r"(?:operating\s+)?voltage\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?\s*V\b", "voltage_min", "voltage_max")
        current = re.search(r"(?:current|supply\s+current)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mA|uA|μA|A)\b", text, re.I)
        if current:
            value = _scaled(current.group(1), current.group(2), {"a": 1, "ma": 1e-3, "ua": 1e-6})
            add("current_min", value)
            add("current_max", value)
        resistance = re.search(r"\b(\d+(?:\.\d+)?)\s*(ohm|Ω|kohm|kΩ|mohm|mΩ)\b", text, re.I)
        if resistance:
            unit = resistance.group(2).lower()
            factor = 1e3 if unit in ("kohm", "kω") else 1e6 if unit in ("mohm", "mω") else 1
            add("resistance_ohms", _number(resistance.group(1)) * factor)
        capacitance = re.search(r"\b(\d+(?:\.\d+)?)\s*(pF|nF|uF|μF|mF|F)\b", text, re.I)
        if capacitance:
            value = _scaled(capacitance.group(1), capacitance.group(2), {"pf": 1e-12, "nf": 1e-9, "uf": 1e-6, "mf": 1e-3, "f": 1})
            add("capacitance_farads", value)
        power = re.search(r"(?:power|rating)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mW|W)\b", text, re.I)
        if power:
            add("power_watts", _scaled(power.group(1), power.group(2), {"mw": 1e-3, "w": 1}))
        tolerance = re.search(r"(?:±|\+/-)\s*(\d+(?:\.\d+)?)\s*%", text)
        if tolerance:
            add("tolerance_percent", _number(tolerance.group(1)))
        frequency = re.search(r"\b(\d+(?:\.\d+)?)\s*(Hz|kHz|MHz|GHz)\b", text, re.I)
        if frequency:
            add("frequency_hz", _scaled(frequency.group(1), frequency.group(2), {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}))
        temperature = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:°?C)\s*(?:-|to)\s*(-?\d+(?:\.\d+)?)\s*°?C", text, re.I)
        if temperature:
            add("temperature_min_c", _number(temperature.group(1)))
            add("temperature_max_c", _number(temperature.group(2)))
        dimensions = re.search(r"\b(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)(?:\s*[x×]\s*(\d+(?:\.\d+)?))?\s*mm\b", text, re.I)
        if dimensions:
            add("dimensions_mm", [_number(item) for item in dimensions.groups() if item])
        package = re.search(r"\b(DIP-?\d+|SOIC-?\d+|QFN-?\d+|QFP-?\d+|SOT-?\d+|TO-?\d+|0?\d{3,4})\b", text, re.I)
        if package:
            add("package", package.group(1).upper())
        connectors = re.search(r"\b(?:connector|header)\s*[:=]\s*([^\n,;]+)", text, re.I)
        if connectors:
            add("connector", connectors.group(1).strip())
        found_interfaces = [item for item in _INTERFACES if re.search(rf"\b{re.escape(item)}\b", text, re.I)]
        if found_interfaces:
            add("interfaces", found_interfaces)
            add("protocols", found_interfaces)
        address = re.search(r"\b(?:i2c\s+)?address\s*[:=]?\s*0x([0-9a-f]+)\b", text, re.I)
        if address:
            add("i2c_address", int(address.group(1), 16))
        return spec

    async def analyze_part(self, part: PartInput, request_id: Optional[str] = None) -> PartSpecification:
        """Use Qwen 4B only to fill non-numeric fields that deterministic parsing missed."""
        request_id = request_id or str(uuid.uuid4())
        deterministic = self.extract_deterministic(part)
        try:
            response = await self._gateway.generate_structured(
                prompt=f"Part ID: {part.part_id}\nSource text:\n{part.source_text}",
                schema=PartSpecification, system_prompt=_SYSTEM_PROMPT,
                temperature=0.1, request_id=request_id,
            )
            model = response.content
            for field in ("manufacturer", "part_number", "connector", "package"):
                if getattr(deterministic, field) is None and getattr(model, field) is not None:
                    setattr(deterministic, field, getattr(model, field))
                    deterministic.evidence.append(PartEvidence(field=field, value=str(getattr(model, field)), method="model"))
            for field in ("interfaces", "protocols"):
                if not getattr(deterministic, field) and getattr(model, field):
                    setattr(deterministic, field, getattr(model, field))
                    deterministic.evidence.append(PartEvidence(field=field, value=str(getattr(model, field)), method="model"))
        except Exception as exc:
            logger.error("Parts analysis failed", extra={"request_id": request_id, "error": str(exc)})
        return deterministic


async def parts_node(state: Dict[str, Any], model_gateway: Optional[ModelGateway] = None) -> Dict[str, Any]:
    parts = [PartInput.model_validate(item) for item in state.get("parts", [])]
    agent = PartsAgent(model_gateway)
    results = [await agent.analyze_part(part, state.get("request_id")) for part in parts]
    return {"parts_results": [result.model_dump() for result in results]}
