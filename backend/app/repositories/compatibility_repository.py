"""Compatibility repository for checking compatibility rules and product relationships."""

import uuid
from typing import Sequence, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.relationships import CompatibilityRule, ProductRelationship
from app.repositories.base import BaseRepository


class CompatibilityRepository(BaseRepository[CompatibilityRule]):
    def __init__(self, session: AsyncSession):
        super().__init__(CompatibilityRule, session)

    async def get_rules_for_categories(
        self, category_a_id: uuid.UUID, category_b_id: uuid.UUID
    ) -> Sequence[CompatibilityRule]:
        """Fetch all bidirectional rules applying to two categories."""
        stmt = select(CompatibilityRule).where(
            or_(
                and_(
                    CompatibilityRule.category_a_id == category_a_id,
                    CompatibilityRule.category_b_id == category_b_id,
                ),
                and_(
                    CompatibilityRule.category_a_id == category_b_id,
                    CompatibilityRule.category_b_id == category_a_id,
                ),
                # Global rules
                and_(
                    CompatibilityRule.category_a_id.is_(None),
                    CompatibilityRule.category_b_id.is_(None),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_product_relationships(
        self, product_id: uuid.UUID
    ) -> Sequence[ProductRelationship]:
        """Fetch all mapped direct relationships for a product."""
        stmt = select(ProductRelationship).where(
            or_(
                ProductRelationship.product_a_id == product_id,
                ProductRelationship.product_b_id == product_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def check_direct_relationship(
        self, product_a_id: uuid.UUID, product_b_id: uuid.UUID
    ) -> Optional[ProductRelationship]:
        """Check if a direct relationship exists between two specific products."""
        stmt = select(ProductRelationship).where(
            or_(
                and_(
                    ProductRelationship.product_a_id == product_a_id,
                    ProductRelationship.product_b_id == product_b_id,
                ),
                and_(
                    ProductRelationship.product_a_id == product_b_id,
                    ProductRelationship.product_b_id == product_a_id,
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
