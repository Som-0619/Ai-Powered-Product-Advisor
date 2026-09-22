"""Canonical Product Catalog Service.

PostgreSQL canonical source of truth service for:
- Product identity
- Product variants
- Product images
- Retailer offers
- Product sources
"""

import uuid
from typing import Optional, List, Sequence, Dict, Any, Union
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Product, ProductVariant, Specification
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.retailer_offers import RetailerOffer
from app.models.sources import ProductSource
from app.models.reviews import ProductReview
from app.services.factory import get_db_service
from sqlalchemy import or_


def _coerce_uuid(val: Union[uuid.UUID, str]) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


class ProductCatalogService:
    """Canonical service abstraction managing PostgreSQL product catalog data."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self._provided_session = session

    async def _get_session(self):
        if self._provided_session is not None:
            yield self._provided_session
        else:
            db_service = get_db_service()
            async with db_service.session() as s:
                yield s

    async def get_product(self, product_id: Union[uuid.UUID, str]) -> Optional[Product]:
        """Fetch canonical product entity by stable product_id with full graph preloaded."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(Product)
            .where(Product.id == pid)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.retailer_offers),
                selectinload(Product.sources),
                selectinload(Product.reviews),
            )
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_products_by_ids(
        self, product_ids: Sequence[Union[uuid.UUID, str]]
    ) -> List[Product]:
        """Fetch canonical products for given IDs, preserving input order with full graph preloaded."""
        if not product_ids:
            return []
        pids = [_coerce_uuid(pid) for pid in product_ids]
        stmt = (
            select(Product)
            .where(Product.id.in_(pids))
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.retailer_offers),
                selectinload(Product.sources),
                selectinload(Product.reviews),
            )
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            prods = list(result.scalars().all())
            prod_map = {p.id: p for p in prods}
            return [prod_map[pid] for pid in pids if pid in prod_map]

    async def get_all_products(self) -> List[Product]:
        """Fetch all canonical products with variants and images for indexing."""
        stmt = select(Product).options(
            selectinload(Product.variants),
            selectinload(Product.images),
            selectinload(Product.retailer_offers),
            selectinload(Product.sources),
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            return list(result.scalars().all())


    async def get_products(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Product]:
        """Fetch canonical products, optionally filtered by category name or slug."""
        stmt = select(Product)
        if category:
            clean_cat = category.strip().lower()
            stmt = stmt.where(
                or_(
                    Product.category.ilike(clean_cat),
                    Product.subcategory.ilike(clean_cat),
                    Product.slug.ilike(f"%{clean_cat}%"),
                )
            )
        stmt = (
            stmt.offset(skip)
            .limit(limit)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.retailer_offers),
            )
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_variant(self, variant_id: Union[uuid.UUID, str]) -> Optional[ProductVariant]:
        """Fetch product variant by variant_id."""
        vid = _coerce_uuid(variant_id)
        stmt = (
            select(ProductVariant)
            .where(ProductVariant.id == vid)
            .options(
                selectinload(ProductVariant.product),
                selectinload(ProductVariant.retailer_offers),
            )
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_product_variants(self, product_id: Union[uuid.UUID, str]) -> List[ProductVariant]:
        """Fetch all variants strictly belonging to canonical product_id."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(ProductVariant)
            .where(ProductVariant.product_id == pid)
            .order_by(ProductVariant.created_at.asc())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            variants = list(result.scalars().all())
            for v in variants:
                assert v.product_id == pid, f"Variant {v.id} product_id mismatch: expected {pid}, got {v.product_id}"
            return variants

    async def get_product_images(self, product_id: Union[uuid.UUID, str]) -> List[ProductImage]:
        """Fetch all images strictly belonging to canonical product_id."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(ProductImage)
            .where(ProductImage.product_id == pid)
            .order_by(ProductImage.is_primary.desc(), ProductImage.created_at.asc())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            images = list(result.scalars().all())
            # Enforce strict product identity: every image MUST belong to product_id
            for img in images:
                assert img.product_id == pid, f"Image {img.id} product_id mismatch: expected {pid}, got {img.product_id}"
            return images

    async def get_product_reviews(self, product_id: Union[uuid.UUID, str]) -> List[ProductReview]:
        """Fetch all reviews strictly belonging to canonical product_id."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(ProductReview)
            .where(ProductReview.product_id == pid)
            .order_by(ProductReview.created_at.desc())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            reviews = list(result.scalars().all())
            for r in reviews:
                assert r.product_id == pid, f"Review {r.id} product_id mismatch: expected {pid}, got {r.product_id}"
            return reviews

    async def get_retailer_offers(self, product_id: Union[uuid.UUID, str]) -> List[RetailerOffer]:
        """Fetch all external retailer offers strictly belonging to canonical product_id."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(RetailerOffer)
            .where(RetailerOffer.product_id == pid)
            .order_by(RetailerOffer.price.asc().nulls_last())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            offers = list(result.scalars().all())
            # Enforce strict product identity: every offer MUST belong to product_id
            for offer in offers:
                assert offer.product_id == pid, f"Offer {offer.id} product_id mismatch: expected {pid}, got {offer.product_id}"
            return offers

    async def get_product_sources(self, product_id: Union[uuid.UUID, str]) -> List[ProductSource]:
        """Fetch all provenance sources strictly belonging to canonical product_id."""
        pid = _coerce_uuid(product_id)
        stmt = (
            select(ProductSource)
            .where(ProductSource.product_id == pid)
            .order_by(ProductSource.trust_score.desc())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            sources = list(result.scalars().all())
            # Enforce strict product identity
            for src in sources:
                assert src.product_id == pid, f"Source {src.id} product_id mismatch: expected {pid}, got {src.product_id}"
            return sources

    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 50,
    ) -> List[Product]:
        """Perform search across title, brand, model, description with filters."""
        stmt = select(Product)
        q = query.strip()
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Product.title.ilike(pattern),
                    Product.brand.ilike(pattern),
                    Product.model.ilike(pattern),
                    Product.description.ilike(pattern),
                    Product.sku.ilike(pattern),
                )
            )
        if category:
            stmt = stmt.where(Product.category.ilike(category.strip()))
        if brand:
            stmt = stmt.where(Product.brand.ilike(brand.strip()))
        stmt = stmt.limit(limit)
        async for session in self._get_session():
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def create_product(
        self,
        title: str,
        slug: str,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        variant: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        description: Optional[str] = None,
        external_product_id: Optional[str] = None,
        model_number: Optional[str] = None,
        sku: Optional[str] = None,
        product_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        brand_id: Optional[uuid.UUID] = None,
        is_component: bool = False,
        specifications: Optional[Dict[str, Any]] = None,
        release_year: Optional[int] = None,
    ) -> Product:
        """Create a new canonical product entity."""
        prod = Product(
            id=product_id or uuid.uuid4(),
            title=title,
            slug=slug,
            brand=brand,
            model=model,
            variant=variant,
            category=category,
            subcategory=subcategory,
            description=description,
            external_product_id=external_product_id,
            model_number=model_number,
            sku=sku,
            category_id=category_id,
            brand_id=brand_id,
            is_component=is_component,
            specifications=specifications or {},
            release_year=release_year,
        )
        async for session in self._get_session():
            session.add(prod)
            await session.flush()
            return prod

    async def create_variant(
        self,
        product_id: Union[uuid.UUID, str],
        variant_name: str,
        sku: str,
        specifications: Optional[Dict[str, Any]] = None,
        external_variant_id: Optional[str] = None,
        variant_id: Optional[uuid.UUID] = None,
    ) -> ProductVariant:
        """Create a new product variant entity strictly attached to product_id."""
        pid = _coerce_uuid(product_id)
        specs = specifications or {}
        var = ProductVariant(
            id=variant_id or uuid.uuid4(),
            product_id=pid,
            sku=sku,
            title=variant_name,
            variant_name=variant_name,
            external_variant_id=external_variant_id,
            attributes=specs,
            specifications=specs,
        )
        async for session in self._get_session():
            session.add(var)
            await session.flush()
            return var

    async def add_image(
        self,
        product_id: Union[uuid.UUID, str],
        image_url: str,
        image_type: str = "primary",
        variant_id: Optional[Union[uuid.UUID, str]] = None,
        source: Optional[str] = None,
        source_url: Optional[str] = None,
        storage_key: Optional[str] = None,
        is_primary: bool = False,
        verified: bool = True,
        image_id: Optional[uuid.UUID] = None,
    ) -> ProductImage:
        """Add a canonical product image strictly attached to product_id."""
        pid = _coerce_uuid(product_id)
        vid = _coerce_uuid(variant_id) if variant_id else None
        clean_type = image_type.lower().strip()
        if clean_type not in CANONICAL_IMAGE_TYPES:
            raise ValueError(
                f"Invalid image_type '{image_type}'. Allowed types: {sorted(CANONICAL_IMAGE_TYPES)}"
            )

        async for session in self._get_session():
            if vid:
                v_res = await session.execute(
                    select(ProductVariant).where(ProductVariant.id == vid)
                )
                variant_obj = v_res.scalar_one_or_none()
                if variant_obj and variant_obj.product_id != pid:
                    raise ValueError(
                        f"Variant ownership mismatch: variant {vid} belongs to {variant_obj.product_id}, not {pid}"
                    )

            if is_primary:
                await session.execute(
                    update(ProductImage)
                    .where(ProductImage.product_id == pid)
                    .values(is_primary=False)
                )

            img = ProductImage(
                id=image_id or uuid.uuid4(),
                product_id=pid,
                variant_id=vid,
                image_url=image_url,
                storage_key=storage_key or image_url,
                storage_path=storage_key or image_url,
                source=source,
                source_url=source_url or image_url,
                image_type=clean_type,
                is_primary=is_primary,
                verified=verified,
            )
            session.add(img)
            await session.flush()
            return img

    async def add_retailer_offer(
        self,
        product_id: Union[uuid.UUID, str],
        retailer: str,
        external_product_id: Optional[str] = None,
        url: Optional[str] = None,
        price: Optional[float] = None,
        currency: str = "INR",
        availability_status: str = "available",
        verification_status: str = "unverified",
        variant_id: Optional[Union[uuid.UUID, str]] = None,
        offer_id: Optional[uuid.UUID] = None,
    ) -> RetailerOffer:
        """Add a canonical retailer offer strictly attached to product_id."""
        pid = _coerce_uuid(product_id)
        vid = _coerce_uuid(variant_id) if variant_id else None
        offer = RetailerOffer(
            id=offer_id or uuid.uuid4(),
            product_id=pid,
            variant_id=vid,
            retailer=retailer.lower(),
            external_product_id=external_product_id,
            url=url,
            price=price,
            currency=currency,
            availability_status=availability_status.lower(),
            verification_status=verification_status.lower(),
        )
        async for session in self._get_session():
            session.add(offer)
            await session.flush()
            return offer

    async def add_product_source(
        self,
        product_id: Union[uuid.UUID, str],
        source_url: str,
        source_type: str = "dataset",
        external_product_id: Optional[str] = None,
        trust_score: float = 1.0,
        source_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> ProductSource:
        """Add provenance record strictly attached to product_id."""
        pid = _coerce_uuid(product_id)
        sid = _coerce_uuid(source_id) if source_id else None
        ps = ProductSource(
            id=uuid.uuid4(),
            product_id=pid,
            source_id=sid,
            source_type=source_type.lower(),
            source_url=source_url,
            external_product_id=external_product_id,
            external_sku=external_product_id,
            trust_score=trust_score,
            crawl_metadata={},
        )
        async for session in self._get_session():
            session.add(ps)
            await session.flush()
            return ps

    async def add_review(
        self,
        product_id: Union[uuid.UUID, str],
        body: str,
        rating: Optional[float] = None,
        title: Optional[str] = None,
        source: Optional[str] = None,
        verified_purchase: bool = False,
        reviewer_id: Optional[Union[uuid.UUID, str]] = None,
        review_id: Optional[uuid.UUID] = None,
    ) -> ProductReview:
        """Add a canonical review strictly attached to product_id."""
        pid = _coerce_uuid(product_id)
        rid = _coerce_uuid(reviewer_id) if reviewer_id else None
        rev = ProductReview(
            id=review_id or uuid.uuid4(),
            product_id=pid,
            reviewer_id=rid,
            rating=rating,
            title=title,
            body=body,
            source=source,
            is_verified_purchase=verified_purchase,
            attributes_analyzed={},
        )
        async for session in self._get_session():
            session.add(rev)
            await session.flush()
            return rev

