"""Rule-first electronics compatibility agent."""

import uuid
from typing import Any, Dict, List, Optional, Sequence, Set

from app.core.exceptions import ModelUnavailableError
from app.schemas.parts_analysis import CompatibilityEvidence, CompatibilityResult, PartSpecification
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway


class CompatibilityAgent:
    """Evaluates known electrical facts before using the reasoning-model gateway."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()

    @staticmethod
    def _evidence(check: str, status: str, reasoning: str, first: PartSpecification, second: PartSpecification) -> CompatibilityEvidence:
        return CompatibilityEvidence(check=check, status=status, reasoning=reasoning, part_ids=[first.part_id, second.part_id])

    @staticmethod
    def _overlap(low_a: float, high_a: float, low_b: float, high_b: float) -> bool:
        return max(low_a, low_b) <= min(high_a, high_b)

    async def check_compatibility(
        self,
        first: PartSpecification,
        second: PartSpecification,
        request_id: Optional[str] = None,
        use_deep_reasoning: bool = True,
    ) -> CompatibilityResult:
        """Return deterministic status/evidence; Qwen 8B only elaborates unresolved cases."""
        evidence: List[CompatibilityEvidence] = []
        unresolved = False

        if None not in (first.voltage_min, first.voltage_max, second.voltage_min, second.voltage_max):
            if not self._overlap(first.voltage_min, first.voltage_max, second.voltage_min, second.voltage_max):
                evidence.append(self._evidence("voltage", "incompatible", "Operating voltage ranges do not overlap.", first, second))
            else:
                evidence.append(self._evidence("voltage", "compatible", "Operating voltage ranges overlap.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("voltage", "unknown", "One or both operating-voltage ranges are unavailable.", first, second))

        first_interfaces, second_interfaces = set(first.interfaces), set(second.interfaces)
        if first_interfaces and second_interfaces:
            if first_interfaces.isdisjoint(second_interfaces):
                evidence.append(self._evidence("interface", "incompatible", "Parts expose no common interface.", first, second))
            else:
                evidence.append(self._evidence("interface", "possibly_compatible", "Parts share at least one interface; electrical checks still apply.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("interface", "unknown", "Interface data is incomplete.", first, second))

        first_protocols, second_protocols = set(first.protocols), set(second.protocols)
        if first_protocols and second_protocols:
            if first_protocols.isdisjoint(second_protocols):
                evidence.append(self._evidence("protocol", "incompatible", "Parts expose no common protocol.", first, second))
            else:
                evidence.append(self._evidence("protocol", "possibly_compatible", "Parts share a protocol; address and power checks may remain.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("protocol", "unknown", "Protocol data is incomplete.", first, second))

        if first.i2c_address is not None and second.i2c_address is not None and "I2C" in first_interfaces & second_interfaces:
            status = "incompatible" if first.i2c_address == second.i2c_address else "compatible"
            evidence.append(self._evidence("i2c_address", status, "I2C addresses collide." if status == "incompatible" else "I2C addresses differ.", first, second))

        if first.connector and second.connector:
            status = "compatible" if first.connector.lower() == second.connector.lower() else "incompatible"
            evidence.append(self._evidence("connector", status, "Connectors match." if status == "compatible" else "Connector identifiers differ.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("connector", "unknown", "Connector data is incomplete.", first, second))

        if first.package and second.package:
            status = "compatible" if first.package.lower() == second.package.lower() else "possibly_compatible"
            evidence.append(self._evidence("form_factor", status, "Package identifiers match." if status == "compatible" else "Different packages may require an adapter or different footprint.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("form_factor", "unknown", "Package/form-factor data is incomplete.", first, second))

        supply, load = (first, second) if first.power_role == "supply" and second.power_role == "load" else (second, first) if second.power_role == "supply" and first.power_role == "load" else (None, None)
        if supply and load and supply.current_max is not None and load.current_min is not None:
            status = "compatible" if supply.current_max >= load.current_min else "incompatible"
            evidence.append(self._evidence("current", status, "Supply current meets the declared load minimum." if status == "compatible" else "Supply current is below the declared load minimum.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("current", "unknown", "Source/load current roles or limits are incomplete.", first, second))

        if supply and load and supply.power_watts is not None and load.power_watts is not None:
            status = "compatible" if supply.power_watts >= load.power_watts else "incompatible"
            evidence.append(self._evidence("power", status, "Supply power meets load requirement." if status == "compatible" else "Supply power is below load requirement.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("power", "unknown", "Source/load power data is incomplete.", first, second))

        if None not in (first.temperature_min_c, first.temperature_max_c, second.temperature_min_c, second.temperature_max_c):
            status = "compatible" if self._overlap(first.temperature_min_c, first.temperature_max_c, second.temperature_min_c, second.temperature_max_c) else "incompatible"
            evidence.append(self._evidence("operating_conditions", status, "Operating-temperature ranges overlap." if status == "compatible" else "Operating-temperature ranges do not overlap.", first, second))
        else:
            unresolved = True
            evidence.append(self._evidence("operating_conditions", "unknown", "Operating-temperature data is incomplete.", first, second))

        known_evidence = any(item.status != "unknown" for item in evidence)
        if any(item.status == "incompatible" for item in evidence):
            status, summary = "incompatible", "At least one deterministic requirement is contradicted."
        elif not known_evidence:
            status, summary = "unknown", "No compatibility data was available."
        elif unresolved:
            status, summary = "possibly_compatible", "No deterministic conflict found, but required compatibility data is incomplete."
        elif evidence:
            status, summary = "compatible", "All available deterministic checks passed."

        result = CompatibilityResult(status=status, part_ids=[first.part_id, second.part_id], evidence=evidence, reasoning=summary, requires_further_validation=status != "compatible")
        if use_deep_reasoning and status in ("possibly_compatible", "unknown"):
            try:
                await self._add_reasoning_evidence(result, first, second, request_id or str(uuid.uuid4()))
            except ModelUnavailableError as exc:
                result.evidence.append(CompatibilityEvidence(
                    check="reasoning", status=result.status,
                    reasoning=f"Deep technical reasoning is unavailable: {exc}",
                    part_ids=result.part_ids, deterministic=False,
                ))
        return result

    async def _add_reasoning_evidence(self, result: CompatibilityResult, first: PartSpecification, second: PartSpecification, request_id: str) -> None:
        """Qwen 8B may explain missing-context risks but cannot alter deterministic status."""
        response = await self._gateway.generate_reasoning(
            prompt=f"Assess unresolved technical risks for these normalized specifications: {first.model_dump()} and {second.model_dump()}. Do not recalculate known numeric checks or override deterministic results.",
            system_prompt="Explain only ambiguity, missing datasheet facts, and required validation steps.",
            temperature=0.1,
            request_id=request_id,
        )
        result.evidence.append(CompatibilityEvidence(
            check="reasoning", status=result.status, reasoning=response.content,
            part_ids=result.part_ids, deterministic=False,
        ))
        result.reasoning = result.reasoning + " Qwen reasoning: " + response.content


async def compatibility_node(state: Dict[str, Any], model_gateway: Optional[ModelGateway] = None) -> Dict[str, Any]:
    parts = [PartSpecification.model_validate(item) for item in state.get("parts_results", [])]
    if len(parts) < 2:
        return {"compatibility_results": []}
    result = await CompatibilityAgent(model_gateway).check_compatibility(parts[0], parts[1], state.get("request_id"), bool(state.get("use_deep_compatibility_reasoning", True)))
    return {"compatibility_results": [result.model_dump()]}
