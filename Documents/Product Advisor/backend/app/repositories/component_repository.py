"""Component repository for electronic components and electrical parameter queries."""

import uuid
from typing import Optional, Sequence
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.components import Component, ComponentSpecification
from app.repositories.base import BaseRepository


class ComponentRepository(BaseRepository[Component]):
    def __init__(self, session: AsyncSession):
        super().__init__(Component, session)

    async def get_by_part_number(self, part_number: str) -> Optional[Component]:
        stmt = (
            select(Component)
            .where(Component.part_number == part_number)
            .options(
                selectinload(Component.specification),
                selectinload(Component.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_product_id(self, product_id: uuid.UUID) -> Optional[Component]:
        stmt = (
            select(Component)
            .where(Component.product_id == product_id)
            .options(selectinload(Component.specification))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def filter_by_electrical_parameters(
        self,
        operating_voltage: Optional[float] = None,
        max_current: Optional[float] = None,
        package_type: Optional[str] = None,
        interface: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Component]:
        """Find electronic components meeting specific electrical operating ranges."""
        stmt = (
            select(Component)
            .join(Component.specification)
            .options(
                selectinload(Component.specification),
                selectinload(Component.product),
            )
        )
        filters = []
        if operating_voltage is not None:
            # Check if operating voltage falls between voltage_min and voltage_max
            filters.append(ComponentSpecification.voltage_min <= operating_voltage)
            filters.append(ComponentSpecification.voltage_max >= operating_voltage)
        if max_current is not None:
            filters.append(ComponentSpecification.current_max <= max_current)
        if package_type is not None:
            filters.append(Component.package_type == package_type)
        if interface is not None:
            filters.append(ComponentSpecification.interface.ilike(f"%{interface}%"))

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
