"""Extraction service for structured product and component information from crawled HTML."""

import json
import re
from html import unescape
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.ingestion import (
    ExtractedEntity,
    ExtractedSpecification,
    RawCrawlPayload,
    SourceMetadata,
)
from app.core.logging import logger


class HTMLDataExtractor(HTMLParser):
    """Safe SAX HTML parser extracting text, meta tags, JSON-LD, tables, and definition lists."""

    def __init__(self):
        super().__init__()
        self.title: Optional[str] = None
        self.meta_tags: Dict[str, str] = {}
        self.json_ld_blocks: List[Dict[str, Any]] = []
        self.tables: List[List[List[str]]] = []  # table -> rows -> cells
        self.definition_lists: List[Tuple[str, str]] = []  # (dt, dd)

        # Internal state
        self._current_tag: Optional[str] = None
        self._in_script_json_ld = False
        self._script_buffer: List[str] = []
        self._in_title = False
        self._title_buffer: List[str] = []

        self._in_table = False
        self._current_table: List[List[str]] = []
        self._current_row: List[str] = []
        self._current_cell: List[str] = []

        self._current_dt: Optional[str] = None
        self._current_dd: Optional[str] = None
        self._in_dt = False
        self._in_dd = False

        self._text_chunks: List[str] = []
        self._skip_depth = 0  # To skip script, style, nav, footer contents

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag_lower in ("script", "style", "nav", "footer", "header", "noscript"):
            if tag_lower == "script" and attr_dict.get("type") == "application/ld+json":
                self._in_script_json_ld = True
                self._script_buffer = []
            else:
                self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        if tag_lower == "title":
            self._in_title = True
            self._title_buffer = []
        elif tag_lower == "meta":
            prop = attr_dict.get("property") or attr_dict.get("name")
            content = attr_dict.get("content")
            if prop and content:
                self.meta_tags[prop.lower()] = content
        elif tag_lower == "table":
            self._in_table = True
            self._current_table = []
        elif tag_lower == "tr":
            if self._in_table:
                self._current_row = []
        elif tag_lower in ("td", "th"):
            if self._in_table:
                self._current_cell = []
        elif tag_lower == "dt":
            self._in_dt = True
            self._current_dt = ""
        elif tag_lower == "dd":
            self._in_dd = True
            self._current_dd = ""

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()

        if tag_lower == "script" and self._in_script_json_ld:
            self._in_script_json_ld = False
            raw_script = "".join(self._script_buffer).strip()
            if raw_script:
                try:
                    parsed = json.loads(raw_script)
                    if isinstance(parsed, list):
                        self.json_ld_blocks.extend(parsed)
                    elif isinstance(parsed, dict):
                        self.json_ld_blocks.append(parsed)
                except Exception:
                    pass
            return

        if tag_lower in ("script", "style", "nav", "footer", "header", "noscript"):
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return

        if self._skip_depth > 0:
            return

        if tag_lower == "title":
            self._in_title = False
            self.title = " ".join("".join(self._title_buffer).split())
        elif tag_lower in ("td", "th"):
            if self._in_table:
                cell_text = " ".join("".join(self._current_cell).split())
                self._current_row.append(cell_text)
        elif tag_lower == "tr":
            if self._in_table and self._current_row:
                self._current_table.append(self._current_row)
        elif tag_lower == "table":
            self._in_table = False
            if self._current_table:
                self.tables.append(self._current_table)
        elif tag_lower == "dt":
            self._in_dt = False
        elif tag_lower == "dd":
            self._in_dd = False
            if self._current_dt and self._current_dd:
                self.definition_lists.append((self._current_dt.strip(), self._current_dd.strip()))
                self._current_dt = None
                self._current_dd = None

    def handle_data(self, data: str):
        if self._in_script_json_ld:
            self._script_buffer.append(data)
            return

        if self._skip_depth > 0:
            return

        if self._in_title:
            self._title_buffer.append(data)
            return

        if self._in_table and hasattr(self, "_current_cell"):
            self._current_cell.append(data)

        if self._in_dt and self._current_dt is not None:
            self._current_dt += data
            return

        if self._in_dd and self._current_dd is not None:
            self._current_dd += data
            return

        cleaned = data.strip()
        if cleaned:
            self._text_chunks.append(cleaned)

    def get_clean_text(self) -> str:
        return "\n".join(self._text_chunks)


class ExtractionService:
    """Extracts structured entities, specs, and metadata from raw payloads."""

    # Patterns for electrical & technical specs
    VOLTAGE_PATTERN = re.compile(
        r"(?:Operating\s+Voltage|Supply\s+Voltage|Voltage|VCC|Input\s+Voltage)[\s:]+([0-9.]+(?:\s*V|\s*to\s*[0-9.]+\s*V|\s*mV))",
        re.IGNORECASE,
    )
    CURRENT_PATTERN = re.compile(
        r"(?:Operating\s+Current|Current|Max\s+Current|Supply\s+Current)[\s:]+([0-9.]+\s*(?:mA|A|uA))",
        re.IGNORECASE,
    )
    INTERFACE_PATTERN = re.compile(
        r"\b(I2C|SPI|UART|USB-C|USB\s+Type-C|GPIO|CAN|Bluetooth\s+[0-9.]+|Wi-Fi\s+[0-9a-z/]+|PCIe\s+[0-9.]+)\b",
        re.IGNORECASE,
    )
    RAM_PATTERN = re.compile(
        r"\b([0-9]+\s*(?:GB|MB)\s*(?:RAM|DDR[0-9]*|LPDDR[0-9]*|Unified\s+Memory))\b",
        re.IGNORECASE,
    )
    GPU_PATTERN = re.compile(
        r"\b(RTX\s*[0-9]{4}(?:\s*Ti|\s*Super)?|Radeon\s+RX\s*[0-9]{4}|Apple\s+M[0-9](?:\s*Pro|\s*Max)?)\b",
        re.IGNORECASE,
    )
    PACKAGE_PATTERN = re.compile(
        r"\b(QFN-?[0-9]+|SOIC-?[0-9]+|DIP-?[0-9]+|SOT-?[0-9]+|BGA-?[0-9]+|LQFP-?[0-9]+|TQFP-?[0-9]+)\b",
        re.IGNORECASE,
    )

    def extract(self, payload: RawCrawlPayload, metadata: SourceMetadata) -> ExtractedEntity:
        """Parse raw crawled content and produce structured ExtractedEntity."""
        parser = HTMLDataExtractor()
        try:
            parser.feed(payload.content)
        except Exception as exc:
            logger.warning(f"HTML parsing had errors for {payload.url}: {exc}")

        title: Optional[str] = None
        description: Optional[str] = None
        brand: Optional[str] = None
        model_number: Optional[str] = None
        sku: Optional[str] = None
        price: Optional[float] = None
        currency: str = "USD"
        availability: Optional[str] = None
        raw_specs: List[ExtractedSpecification] = []

        # 1. Inspect Schema.org JSON-LD blocks
        for block in parser.json_ld_blocks:
            b_type = str(block.get("@type", "")).lower()
            if "product" in b_type or "individualproduct" in b_type:
                title = title or block.get("name")
                description = description or block.get("description")
                sku = sku or block.get("sku")
                model_number = model_number or block.get("model") or block.get("mpn")
                if isinstance(block.get("brand"), dict):
                    brand = brand or block["brand"].get("name")
                elif isinstance(block.get("brand"), str):
                    brand = brand or block.get("brand")

                # Offers / Price
                offers = block.get("offers")
                if isinstance(offers, dict):
                    try:
                        p_val = offers.get("price")
                        if p_val:
                            price = float(p_val)
                        currency = offers.get("priceCurrency", "USD")
                        availability = offers.get("availability")
                    except (ValueError, TypeError):
                        pass
                elif isinstance(offers, list) and offers:
                    first_offer = offers[0]
                    if isinstance(first_offer, dict):
                        try:
                            p_val = first_offer.get("price")
                            if p_val:
                                price = float(p_val)
                            currency = first_offer.get("priceCurrency", "USD")
                            availability = first_offer.get("availability")
                        except (ValueError, TypeError):
                            pass

        # 2. Inspect Meta Tags
        title = (
            title
            or parser.meta_tags.get("og:title")
            or parser.meta_tags.get("twitter:title")
            or parser.title
        )
        description = (
            description
            or parser.meta_tags.get("og:description")
            or parser.meta_tags.get("description")
            or parser.meta_tags.get("twitter:description")
        )

        # Fallback title from first H1 or URL
        if not title:
            title = payload.url.rstrip("/").split("/")[-1].replace("-", " ").title()

        # 3. Extract specifications from HTML Tables
        for table in parser.tables:
            for row in table:
                if len(row) == 2:
                    k, v = row[0].strip(), row[1].strip()
                    if k and v and len(k) < 60 and len(v) < 255:
                        raw_specs.append(
                            ExtractedSpecification(group="Specifications", key=k, raw_value=v)
                        )

        # 4. Extract specifications from Definition Lists
        for dt, dd in parser.definition_lists:
            if dt and dd and len(dt) < 60 and len(dd) < 255:
                raw_specs.append(
                    ExtractedSpecification(group="Specifications", key=dt, raw_value=dd)
                )

        full_text = parser.get_clean_text()

        # 5. Regex extraction for electrical parameters if not found in tables
        existing_keys = {s.key.lower() for s in raw_specs}

        # Voltage
        if "voltage" not in existing_keys:
            v_match = self.VOLTAGE_PATTERN.search(full_text)
            if v_match:
                raw_specs.append(
                    ExtractedSpecification(group="Electrical", key="voltage", raw_value=v_match.group(1))
                )

        # Current
        if "current" not in existing_keys:
            c_match = self.CURRENT_PATTERN.search(full_text)
            if c_match:
                raw_specs.append(
                    ExtractedSpecification(group="Electrical", key="current", raw_value=c_match.group(1))
                )

        # Interfaces
        interfaces_found = list(set(self.INTERFACE_PATTERN.findall(full_text)))
        if interfaces_found and "interface" not in existing_keys:
            raw_specs.append(
                ExtractedSpecification(
                    group="Electrical", key="interface", raw_value=", ".join(interfaces_found)
                )
            )

        # RAM
        ram_match = self.RAM_PATTERN.search(full_text)
        if ram_match and "ram" not in existing_keys:
            raw_specs.append(
                ExtractedSpecification(group="Hardware", key="ram", raw_value=ram_match.group(1))
            )

        # GPU
        gpu_match = self.GPU_PATTERN.search(full_text)
        if gpu_match and "gpu" not in existing_keys:
            raw_specs.append(
                ExtractedSpecification(group="Hardware", key="gpu", raw_value=gpu_match.group(1))
            )

        # Package
        pkg_match = self.PACKAGE_PATTERN.search(full_text)
        if pkg_match and "package" not in existing_keys:
            raw_specs.append(
                ExtractedSpecification(group="Mechanical", key="package", raw_value=pkg_match.group(1))
            )

        # Determine entity type
        lower_title = title.lower()
        lower_text = full_text.lower()
        is_component = (
            "esp32" in lower_title
            or "microcontroller" in lower_text
            or "sensor" in lower_text
            or "resistor" in lower_text
            or "transistor" in lower_text
            or "ic " in lower_text
            or "module" in lower_title
            or "breakout" in lower_title
            or any(s.group == "Electrical" for s in raw_specs)
        )
        entity_type = "component" if is_component else "product"

        return ExtractedEntity(
            entity_type=entity_type,
            title=title,
            brand=brand,
            model_number=model_number,
            sku=sku,
            category_name="Electronic Components" if is_component else "Consumer Electronics",
            description=description or full_text[:400],
            specifications=raw_specs,
            price=price,
            currency=currency,
            availability=availability or "in_stock",
            raw_text=full_text,
            source_metadata=metadata,
        )
