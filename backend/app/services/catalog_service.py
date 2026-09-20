"""Catalog service for domain operations on products, components, and specifications."""

import uuid
from typing import Optional, List, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog import Product, Category, Brand, ProductVariant, Specification
from app.models.components import Component, ComponentSpecification
from app.repositories.product_repository import ProductRepository
from app.repositories.component_repository import ComponentRepository
from app.services.product_catalog_service import ProductCatalogService


class CatalogService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(session)
        self.components = ComponentRepository(session)

    async def get_product_details(self, product_id: uuid.UUID) -> Optional[Product]:
        """Fetch full product graph including specifications and component profiles."""
        return await self.products.get_with_details(product_id)

    async def create_product(
        self,
        title: str,
        slug: str,
        category_id: uuid.UUID,
        brand_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        model_number: Optional[str] = None,
        sku: Optional[str] = None,
        is_component: bool = False,
    ) -> Product:
        product = Product(
            title=title,
            slug=slug,
            category_id=category_id,
            brand_id=brand_id,
            description=description,
            model_number=model_number,
            sku=sku,
            is_component=is_component,
        )
        return await self.products.create(product)

    async def add_component_profile(
        self,
        product_id: uuid.UUID,
        part_number: str,
        package_type: Optional[str] = None,
        pin_count: Optional[int] = None,
        mounting_type: Optional[str] = None,
        datasheet_url: Optional[str] = None,
        specs: Optional[Dict[str, Any]] = None,
    ) -> Component:
        """Attach electronic component electrical specs to a product."""
        component = Component(
            product_id=product_id,
            part_number=part_number,
            package_type=package_type,
            pin_count=pin_count,
            mounting_type=mounting_type,
            datasheet_url=datasheet_url,
        )
        self.session.add(component)
        await self.session.flush()

        if specs:
            comp_spec = ComponentSpecification(
                component_id=component.id,
                voltage_min=specs.get("voltage_min"),
                voltage_max=specs.get("voltage_max"),
                voltage_unit=specs.get("voltage_unit", "V"),
                current_min=specs.get("current_min"),
                current_max=specs.get("current_max"),
                current_unit=specs.get("current_unit", "A"),
                resistance=specs.get("resistance"),
                resistance_unit=specs.get("resistance_unit"),
                capacitance=specs.get("capacitance"),
                capacitance_unit=specs.get("capacitance_unit"),
                power=specs.get("power"),
                power_unit=specs.get("power_unit"),
                tolerance=specs.get("tolerance"),
                interface=specs.get("interface"),
                package=specs.get("package"),
                frequency=specs.get("frequency"),
                frequency_unit=specs.get("frequency_unit"),
                temperature_min=specs.get("temperature_min"),
                temperature_max=specs.get("temperature_max"),
                extra_specs=specs.get("extra_specs", {}),
            )
            self.session.add(comp_spec)
            await self.session.flush()
            component.specification = comp_spec

        return component
