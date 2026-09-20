"""Deterministic compatibility service for electronics and electronic components."""

import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product_repository import ProductRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.compatibility_repository import CompatibilityRepository


class CompatibilityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(session)
        self.components = ComponentRepository(session)
        self.compat_repo = CompatibilityRepository(session)

    async def evaluate_compatibility(
        self, product_a_id: uuid.UUID, product_b_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Deterministically evaluate whether two products/components can work together.
        Returns:
            status: "compatible" | "possibly_compatible" | "incompatible" | "unknown"
            reasons: list of verification claims
            evidence: source evidence
        """
        # 1. Check direct product relationship
        direct_rel = await self.compat_repo.check_direct_relationship(product_a_id, product_b_id)
        if direct_rel:
            return {
                "status": direct_rel.relationship_type,
                "confidence": direct_rel.confidence,
                "reason": direct_rel.evidence or f"Direct relationship defined: {direct_rel.relationship_type}",
                "method": "direct_relationship_mapping",
            }

        # 2. Fetch products and component specifications
        prod_a = await self.products.get_by_id(product_a_id)
        prod_b = await self.products.get_by_id(product_b_id)
        if not prod_a or not prod_b:
            return {
                "status": "unknown",
                "confidence": 0.0,
                "reason": "One or both products not found.",
                "method": "missing_data",
            }

        # 3. Check category compatibility rules
        rules = await self.compat_repo.get_rules_for_categories(prod_a.category_id, prod_b.category_id)

        # 4. Check component electrical compatibility if both are components
        comp_a = await self.components.get_by_product_id(product_a_id)
        comp_b = await self.components.get_by_product_id(product_b_id)

        if comp_a and comp_b and comp_a.specification and comp_b.specification:
            spec_a = comp_a.specification
            spec_b = comp_b.specification

            # Check operating voltage overlap
            if (
                spec_a.voltage_min is not None
                and spec_a.voltage_max is not None
                and spec_b.voltage_min is not None
                and spec_b.voltage_max is not None
            ):
                # Check if voltage ranges overlap
                overlap = max(spec_a.voltage_min, spec_b.voltage_min) <= min(
                    spec_a.voltage_max, spec_b.voltage_max
                )
                if not overlap:
                    return {
                        "status": "incompatible",
                        "confidence": 0.95,
                        "reason": (
                            f"Voltage mismatch: {prod_a.title} operates at {spec_a.voltage_min}-{spec_a.voltage_max}{spec_a.voltage_unit}, "
                            f"while {prod_b.title} operates at {spec_b.voltage_min}-{spec_b.voltage_max}{spec_b.voltage_unit}."
                        ),
                        "method": "voltage_range_analysis",
                    }
                else:
                    return {
                        "status": "compatible",
                        "confidence": 0.90,
                        "reason": (
                            f"Operating voltage ranges are compatible ({max(spec_a.voltage_min, spec_b.voltage_min)}V - "
                            f"{min(spec_a.voltage_max, spec_b.voltage_max)}V overlap)."
                        ),
                        "method": "voltage_range_analysis",
                    }

        return {
            "status": "unknown",
            "confidence": 0.3,
            "reason": "Deterministic compatibility rules and electrical parameters inconclusive.",
            "method": "default_unknown",
        }
