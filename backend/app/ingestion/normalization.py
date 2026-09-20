"""Normalization service for standardizing engineering units, interfaces, and specifications."""

import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.ingestion import (
    ExtractedEntity,
    ExtractedSpecification,
    NormalizedEntity,
    NormalizedSpecification,
)
from app.ingestion.cleaning import CleaningService


class NormalizationService:
    """Normalizes technical specifications, engineering units, and electrical interfaces."""

    # Unit conversion regexes
    VOLTAGE_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(mV|V|kV)?", re.IGNORECASE)
    CURRENT_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(uA|µA|mA|A)", re.IGNORECASE)
    FREQUENCY_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(kHz|MHz|GHz|Hz)", re.IGNORECASE)
    STORAGE_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(MB|GB|TB|KB)", re.IGNORECASE)

    INTERFACE_CANONICAL = {
        "i2c": "I2C",
        "iic": "I2C",
        "twi": "I2C",
        "spi": "SPI",
        "uart": "UART",
        "serial": "UART",
        "usb-c": "USB-C",
        "usb type-c": "USB-C",
        "type-c": "USB-C",
        "pcie 4.0": "PCIe 4.0",
        "pci express 4.0": "PCIe 4.0",
        "pcie 3.0": "PCIe 3.0",
        "bluetooth 5.0": "Bluetooth 5.0",
        "bluetooth": "Bluetooth",
        "ble": "Bluetooth",
        "wi-fi": "Wi-Fi",
        "wifi": "Wi-Fi",
        "gpio": "GPIO",
        "can": "CAN",
    }

    def normalize(self, extracted: ExtractedEntity) -> NormalizedEntity:
        """Standardize all specifications, units, text, and metadata."""
        cleaned_title = CleaningService.clean_text(extracted.title)
        cleaned_desc = CleaningService.clean_text(extracted.description or "")
        cleaned_text = CleaningService.clean_text(extracted.raw_text or "")

        normalized_specs: List[NormalizedSpecification] = []
        electrical_params: Dict[str, Any] = {}

        for spec in extracted.specifications:
            norm_spec = self._normalize_specification(spec)
            normalized_specs.append(norm_spec)

            # Extract into top-level electrical params
            key_lower = norm_spec.key.lower()
            if "voltage" in key_lower and "voltage" not in electrical_params:
                if norm_spec.normalized_value is not None:
                    electrical_params["voltage"] = norm_spec.normalized_value
                    electrical_params["voltage_display"] = norm_spec.display_value
            elif "current" in key_lower and "current" not in electrical_params:
                if norm_spec.normalized_value is not None:
                    electrical_params["current"] = norm_spec.normalized_value
                    electrical_params["current_display"] = norm_spec.display_value
            elif ("ram" in key_lower or "memory" in key_lower) and "ram_gb" not in electrical_params:
                if norm_spec.normalized_value is not None:
                    electrical_params["ram_gb"] = norm_spec.normalized_value
            elif "gpu" in key_lower and "gpu" not in electrical_params:
                electrical_params["gpu"] = norm_spec.display_value
            elif "interface" in key_lower and "interface" not in electrical_params:
                interfaces = self._normalize_interfaces(norm_spec.display_value)
                electrical_params["interface"] = interfaces
            elif "package" in key_lower and "package" not in electrical_params:
                electrical_params["package"] = norm_spec.display_value.upper()

        # Compute deterministic content hash based on normalized data
        canonical_str = (
            f"{cleaned_title}|{extracted.brand or ''}|{extracted.model_number or ''}|"
            f"{extracted.sku or ''}|{extracted.price or ''}|{cleaned_desc}"
        )
        content_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        # Update metadata content hash
        metadata = extracted.source_metadata
        if metadata:
            metadata.content_hash = content_hash

        return NormalizedEntity(
            entity_type=extracted.entity_type,
            title=cleaned_title,
            brand=extracted.brand,
            model_number=extracted.model_number,
            sku=extracted.sku,
            category_name=extracted.category_name or "Electronic Components",
            description=cleaned_desc,
            specifications=normalized_specs,
            electrical_parameters=electrical_params,
            price=extracted.price,
            currency=extracted.currency,
            availability=extracted.availability or "in_stock",
            cleaned_text=cleaned_text,
            content_hash=content_hash,
            source_metadata=metadata,
        )

    def _normalize_specification(self, spec: ExtractedSpecification) -> NormalizedSpecification:
        """Normalize an individual specification key and its unit value."""
        key = spec.key.strip()
        val = spec.raw_value.strip()

        # Handle voltage: e.g. "3.3V", "3V3", "3300 mV", "3.0V to 3.6V"
        if "voltage" in key.lower() or val.lower().endswith("v"):
            # Handle notation like 3V3 -> 3.3V
            val_fixed = re.sub(r"(\d+)V(\d+)", r"\1.\2V", val, flags=re.IGNORECASE)
            match = self.VOLTAGE_RE.search(val_fixed)
            if match:
                num = float(match.group(1))
                unit = (match.group(2) or "V").upper()
                # Convert to base Volts
                if unit == "MV":
                    num_volts = round(num / 1000.0, 3)
                elif unit == "KV":
                    num_volts = round(num * 1000.0, 3)
                else:
                    num_volts = round(num, 3)
                return NormalizedSpecification(
                    group=spec.group,
                    key=key,
                    display_value=f"{num_volts}V",
                    normalized_value=num_volts,
                    unit="V",
                )

        # Handle current: e.g. "500mA", "2A"
        if "current" in key.lower() or val.lower().endswith("a"):
            match = self.CURRENT_RE.search(val)
            if match:
                num = float(match.group(1))
                unit = match.group(2).lower()
                if unit in ("ua", "µa"):
                    num_amps = round(num / 1000000.0, 6)
                elif unit == "ma":
                    num_amps = round(num / 1000.0, 4)
                else:
                    num_amps = round(num, 4)
                return NormalizedSpecification(
                    group=spec.group,
                    key=key,
                    display_value=val,
                    normalized_value=num_amps,
                    unit="A",
                )

        # Handle RAM / Memory: e.g. "16GB RAM", "16384 MB"
        if "ram" in key.lower() or "memory" in key.lower() or "storage" in key.lower():
            match = self.STORAGE_RE.search(val)
            if match:
                num = float(match.group(1))
                unit = match.group(2).upper()
                if unit == "MB":
                    num_gb = round(num / 1024.0, 2)
                elif unit == "TB":
                    num_gb = round(num * 1024.0, 2)
                elif unit == "KB":
                    num_gb = round(num / (1024.0 * 1024.0), 4)
                else:
                    num_gb = round(num, 2)
                return NormalizedSpecification(
                    group=spec.group,
                    key=key,
                    display_value=f"{int(num_gb) if num_gb.is_integer() else num_gb}GB",
                    normalized_value=num_gb,
                    unit="GB",
                )

        # Handle interfaces
        if "interface" in key.lower():
            interfaces = self._normalize_interfaces(val)
            return NormalizedSpecification(
                group=spec.group,
                key=key,
                display_value=", ".join(interfaces),
                normalized_value=None,
                unit=None,
            )

        return NormalizedSpecification(
            group=spec.group,
            key=key,
            display_value=val,
            normalized_value=None,
            unit=None,
        )

    def _normalize_interfaces(self, raw_interface_str: str) -> List[str]:
        """Parse and standardize multiple comma/slash separated interface names."""
        tokens = re.split(r"[,/|;]+", raw_interface_str)
        result = []
        for token in tokens:
            cleaned = token.strip()
            if not cleaned:
                continue
            lower = cleaned.lower()
            canonical = self.INTERFACE_CANONICAL.get(lower, cleaned)
            if canonical not in result:
                result.append(canonical)
        return result or [raw_interface_str.strip()]
