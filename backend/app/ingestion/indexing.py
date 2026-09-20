"""Indexing service coordinating MinIO storage, PostgreSQL persistence, and OpenSearch indexing."""

import datetime
import uuid
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import select
from app.core.logging import logger
from app.services.storage import StorageService, StoragePath
from app.services.database import DatabaseService
from app.services.search import SearchService
from app.schemas.ingestion import NormalizedEntity, RawCrawlPayload
from app.models.catalog import Brand, Category, Product, Specification
from app.models.components import Component, ComponentSpecification
from app.models.pricing import Price
from app.models.sources import Source, ProductSource, CrawlJob
from app.models.media import Document


class IndexingService:
    """Coordinates persistence across Object Storage, PostgreSQL, and OpenSearch."""

    def __init__(
        self,
        storage_service: StorageService,
        db_service: DatabaseService,
        search_service: SearchService,
    ):
        self.storage_service = storage_service
        self.db_service = db_service
        self.search_service = search_service

    async def persist_raw_content(self, payload: RawCrawlPayload) -> str:
        """Store raw crawl payload in StorageService under raw/ logical path."""
        date_str = datetime.date.today().isoformat()
        object_name = StoragePath.build(StoragePath.RAW, "crawl", date_str, f"{payload.content_hash}.html")

        content_bytes = payload.content.encode("utf-8")
        await self.storage_service.put_object(
            object_name=object_name,
            data=content_bytes,
            content_type=payload.content_type,
        )
        return object_name


    async def persist_and_index(
        self,
        entity: NormalizedEntity,
        raw_storage_path: str,
    ) -> Dict[str, Any]:
        """Persist structured entity to PostgreSQL and index into OpenSearch."""
        # 1. PostgreSQL Relational Persistence
        product_id, doc_id = await self._persist_to_postgres(entity, raw_storage_path)

        # 2. OpenSearch Vector and Keyword Indexing
        indexed_info = await self._index_to_opensearch(entity, product_id, doc_id, raw_storage_path)

        return {
            "product_id": str(product_id),
            "document_id": str(doc_id),
            "raw_storage_path": raw_storage_path,
            "opensearch": indexed_info,
        }

    async def _persist_to_postgres(
        self,
        entity: NormalizedEntity,
        raw_storage_path: str,
    ) -> Tuple[uuid.UUID, uuid.UUID]:
        """Save normalized entity to PostgreSQL with ACID consistency."""
        specs_dict = {s.key: s.display_value for s in entity.specifications}
        async with self.db_service.session() as session:

            # 1. Source entity
            meta = entity.source_metadata
            source_stmt = select(Source).where(
                (Source.name.ilike(meta.domain)) | (Source.base_url.ilike(f"%{meta.domain}%"))
            ).limit(1)
            source_res = await session.execute(source_stmt)
            source = source_res.scalar_one_or_none()
            if not source:
                source = Source(
                    name=meta.domain,
                    base_url=f"https://{meta.domain}",
                    source_type=meta.source_type,
                    trust_rating=meta.trust_score,
                )
                session.add(source)
                await session.flush()

            # 2. Category entity
            cat_slug = entity.category_name.lower().replace(" ", "-")
            cat_stmt = select(Category).where(
                (Category.name.ilike(entity.category_name)) | (Category.slug == cat_slug)
            ).limit(1)
            cat_res = await session.execute(cat_stmt)
            category = cat_res.scalar_one_or_none()
            if not category:
                cat_type = "electronic_component" if entity.entity_type == "component" else "consumer_electronics"
                category = Category(
                    name=entity.category_name,
                    slug=cat_slug,
                    category_type=cat_type,
                )
                session.add(category)
                await session.flush()

            # 3. Brand entity (if provided)
            brand_id = None
            if entity.brand:
                brand_slug = entity.brand.lower().replace(" ", "-")
                brand_stmt = select(Brand).where(
                    (Brand.name.ilike(entity.brand)) | (Brand.slug == brand_slug)
                ).limit(1)
                brand_res = await session.execute(brand_stmt)
                brand = brand_res.scalar_one_or_none()
                if not brand:
                    brand = Brand(
                        name=entity.brand,
                        slug=brand_slug,
                    )
                    session.add(brand)
                    await session.flush()
                brand_id = brand.id


            # 4. Product / Component entity
            # Generate deterministic slug based on title and content hash prefix
            clean_slug = (
                f"{entity.title.lower().replace(' ', '-')[:80]}-{entity.content_hash[:8]}"
            )
            # Check if product with this slug already exists
            prod_stmt = select(Product).where(Product.slug == clean_slug).limit(1)
            prod_res = await session.execute(prod_stmt)
            product = prod_res.scalar_one_or_none()

            is_comp = entity.entity_type == "component"

            if not product:
                product = Product(
                    title=entity.title,
                    slug=clean_slug,
                    description=entity.description,
                    model_number=entity.model_number,
                    sku=entity.sku,
                    status="active",
                    is_component=is_comp,
                    category_id=category.id,
                    brand_id=brand_id,
                )
                session.add(product)
                await session.flush()
            else:
                product.title = entity.title
                product.description = entity.description
                product.model_number = entity.model_number
                product.sku = entity.sku
                product.is_component = is_comp

            # 5. Specifications
            # Remove old specs for product to avoid duplicates on update
            for spec in entity.specifications:
                spec_model = Specification(
                    product_id=product.id,
                    spec_group=spec.group,
                    key=spec.key,
                    value=spec.display_value,
                    raw_value={"value": spec.normalized_value, "unit": spec.unit}
                    if spec.normalized_value is not None
                    else None,
                )
                session.add(spec_model)

            # 6. Component profile (if component)
            if is_comp:
                comp_stmt = select(Component).where(Component.product_id == product.id).limit(1)
                comp_res = await session.execute(comp_stmt)
                component = comp_res.scalar_one_or_none()

                elec = entity.electrical_parameters
                voltage_val = elec.get("voltage")
                current_val = elec.get("current")
                interfaces = elec.get("interface", [])
                interface_str = ", ".join(interfaces) if isinstance(interfaces, list) else str(interfaces)
                part_no = entity.model_number or entity.sku or f"{clean_slug[:30]}-{entity.content_hash[:6]}"

                if not component:
                    component = Component(
                        product_id=product.id,
                        part_number=part_no,
                        package_type=elec.get("package", "Standard"),
                        datasheet_url=meta.source_url,
                    )
                    session.add(component)
                    await session.flush()

                    comp_spec = ComponentSpecification(
                        component_id=component.id,
                        voltage_min=voltage_val,
                        voltage_max=voltage_val,
                        voltage_unit="V",
                        current_min=current_val,
                        current_max=current_val,
                        current_unit="A",
                        interface=interface_str,
                        package=elec.get("package", "Standard"),
                        extra_specs=specs_dict,
                    )
                    session.add(comp_spec)
                else:
                    component.part_number = part_no
                    component.package_type = elec.get("package", "Standard")
                    # Update specification if present
                    cs_stmt = select(ComponentSpecification).where(ComponentSpecification.component_id == component.id).limit(1)
                    cs_res = await session.execute(cs_stmt)
                    comp_spec = cs_res.scalar_one_or_none()
                    if comp_spec:
                        comp_spec.voltage_min = voltage_val
                        comp_spec.voltage_max = voltage_val
                        comp_spec.current_min = current_val
                        comp_spec.current_max = current_val
                        comp_spec.interface = interface_str


            # 7. Price
            if entity.price is not None:
                price_record = Price(
                    product_id=product.id,
                    source_id=source.id,
                    amount=entity.price,
                    currency=entity.currency,
                )
                session.add(price_record)


            # 8. ProductSource junction
            ps_stmt = (
                select(ProductSource)
                .where(
                    (ProductSource.source_url == meta.source_url)
                    | (
                        (ProductSource.product_id == product.id)
                        & (ProductSource.source_id == source.id)
                    )
                )
                .limit(1)
            )
            ps_res = await session.execute(ps_stmt)
            product_source = ps_res.scalar_one_or_none()
            crawl_metadata_dict = {
                "domain": meta.domain,
                "content_hash": entity.content_hash,
                "crawl_time": meta.crawl_time,
                "last_seen": meta.last_seen,
                "trust_score": meta.trust_score,
                "source_type": meta.source_type,
            }
            if not product_source:
                product_source = ProductSource(
                    product_id=product.id,
                    source_id=source.id,
                    source_url=meta.source_url,
                    crawl_metadata=crawl_metadata_dict,
                )
                session.add(product_source)
            else:
                product_source.product_id = product.id
                product_source.source_id = source.id
                product_source.source_url = meta.source_url
                product_source.crawl_metadata = crawl_metadata_dict


            # 9. Document media record
            doc = Document(
                product_id=product.id,
                title=f"Datasheet & Specs: {entity.title}",
                doc_type="datasheet" if is_comp else "product_spec",
                storage_path=raw_storage_path,
                source_url=meta.source_url,
                extracted_text=entity.cleaned_text[:5000],
                metadata_json={
                    "content_hash": entity.content_hash,
                    "trust_score": meta.trust_score,
                    "domain": meta.domain,
                },
            )
            session.add(doc)

            # 10. CrawlJob record
            job = CrawlJob(
                url=meta.source_url,
                source_id=source.id,
                status="completed",
                attempts=1,
                raw_storage_path=raw_storage_path,
            )
            session.add(job)

            await session.commit()
            return product.id, doc.id

    async def _index_to_opensearch(
        self,
        entity: NormalizedEntity,
        product_id: uuid.UUID,
        doc_id: uuid.UUID,
        raw_storage_path: str,
    ) -> Dict[str, Any]:
        """Index newly ingested records into OpenSearch indexes."""
        p_id_str = str(product_id)
        d_id_str = str(doc_id)
        elec = entity.electrical_parameters
        specs_dict = {s.key: s.display_value for s in entity.specifications}

        results = {}

        # 1. Index into 'products'
        product_doc = {
            "id": p_id_str,
            "title": entity.title,
            "slug": f"{entity.title.lower().replace(' ', '-')[:80]}-{entity.content_hash[:8]}",
            "brand": entity.brand or "Generic",
            "category": entity.category_name,
            "description": entity.description,
            "price": entity.price,
            "currency": entity.currency,
            "is_component": entity.entity_type == "component",
            "specs": specs_dict,
        }
        res_p = await self.search_service.index_document(
            index_name="products",
            doc_id=p_id_str,
            document=product_doc,
            generate_embedding=True,
        )
        results["products"] = res_p

        # 2. Index into 'components' if entity is a component
        if entity.entity_type == "component":
            interfaces = elec.get("interface", [])
            interface_str = ", ".join(interfaces) if isinstance(interfaces, list) else str(interfaces)
            voltage_val = elec.get("voltage")
            current_val = elec.get("current")

            comp_doc = {
                "id": p_id_str,
                "product_id": p_id_str,
                "title": entity.title,
                "description": entity.description,
                "voltage_display": elec.get("voltage_display", f"{voltage_val}V" if voltage_val else ""),
                "part_number": entity.model_number or entity.sku or entity.title,
                "component_type": elec.get("component_type", "Microcontroller"),
                "package": elec.get("package", "Standard"),
                "package_type": elec.get("package", "Standard"),
                "voltage_min": voltage_val,
                "voltage_max": voltage_val,
                "voltage_unit": "V",
                "current_min": current_val,
                "current_max": current_val,
                "current_unit": "A",
                "interface": interface_str,
                "extra_specs": specs_dict,
            }
            res_c = await self.search_service.index_document(
                index_name="components",
                doc_id=p_id_str,
                document=comp_doc,
                generate_embedding=True,
            )
            results["components"] = res_c

        # 3. Index into 'documents'
        doc_doc = {
            "id": d_id_str,
            "product_id": p_id_str,
            "title": f"Datasheet & Specs: {entity.title}",
            "doc_type": "datasheet" if entity.entity_type == "component" else "product_spec",
            "storage_path": raw_storage_path,
            "extracted_text": entity.cleaned_text[:4000],
            "metadata": {
                "content_hash": entity.content_hash,
                "source_url": entity.source_metadata.source_url,
                "domain": entity.source_metadata.domain,
                "trust_score": entity.source_metadata.trust_score,
            },
        }
        res_d = await self.search_service.index_document(
            index_name="documents",
            doc_id=d_id_str,
            document=doc_doc,
            generate_embedding=True,
        )
        results["documents"] = res_d

        return results
