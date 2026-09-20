"""Validation service ensuring data integrity of ingested records."""

import re
from typing import List
from app.schemas.ingestion import NormalizedEntity


class IngestionValidationError(ValueError):
    """Raised when an ingested entity fails integrity or schema validation rules."""
    pass


class ValidationService:
    """Validates normalized entities before persistence and indexing."""

    HEX_HASH_RE = re.compile(r"^[a-f0-9]{64}$")

    def validate(self, entity: NormalizedEntity) -> None:
        """Run comprehensive validation checks on normalized entity."""
        errors: List[str] = []

        # 1. Title validation
        if not entity.title or len(entity.title.strip()) < 3:
            errors.append("Entity title must be at least 3 characters long.")
        if len(entity.title) > 300:
            errors.append("Entity title exceeds maximum 300 characters.")

        # 2. Content hash validation
        if not entity.content_hash or not self.HEX_HASH_RE.match(entity.content_hash):
            errors.append("Entity must have a valid 64-character SHA-256 content hash.")

        # 3. Source metadata validation
        meta = entity.source_metadata
        if not meta:
            errors.append("Source metadata is missing.")
        else:
            if not meta.source_url:
                errors.append("Source URL is missing in metadata.")
            if not meta.domain:
                errors.append("Domain is missing in metadata.")
            if not (0.0 <= meta.trust_score <= 1.0):
                errors.append(f"Trust score {meta.trust_score} must be between 0.0 and 1.0.")

        # 4. Price validation
        if entity.price is not None and entity.price < 0.0:
            errors.append(f"Price cannot be negative (got {entity.price}).")

        # 5. Electrical parameters validation
        elec = entity.electrical_parameters
        if "voltage" in elec:
            v = elec["voltage"]
            if not isinstance(v, (int, float)) or v <= 0 or v > 100000:
                errors.append(f"Voltage {v} is out of realistic physical range (0, 100000].")

        if "current" in elec:
            c = elec["current"]
            if not isinstance(c, (int, float)) or c < 0 or c > 10000:
                errors.append(f"Current {c} is out of realistic physical range [0, 10000].")

        if errors:
            raise IngestionValidationError(
                f"Validation failed for '{entity.title}' with {len(errors)} error(s): {'; '.join(errors)}"
            )
