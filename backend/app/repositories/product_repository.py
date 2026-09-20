"""Product repository with specialized queries for electronics and components."""

import uuid
from typing import Optional, Sequence, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog import Product, Specification
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        stmt = select(Product).where(Product.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_details(self, product_id: uuid.UUID) -> Optional[Product]:
        """Fetch product with all variants, specifications, and component profile preloaded."""
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.category_rel),
                selectinload(Product.brand_rel),
                selectinload(Product.variants),
                selectinload(Product.specifications),
                selectinload(Product.component_profile),
                selectinload(Product.prices),
                selectinload(Product.availabilities),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_category(
        self,
        category_id: uuid.UUID,
        is_component: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Product]:
        stmt = select(Product).where(Product.category_id == category_id)
        if is_component is not None:
            stmt = stmt.where(Product.is_component == is_component)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_specifications(
        self, product_id: uuid.UUID, specs: List[Specification]
    ) -> List[Specification]:
        for s in specs:
            s.product_id = product_id
            self.session.add(s)
        await self.session.flush()
        return specs
