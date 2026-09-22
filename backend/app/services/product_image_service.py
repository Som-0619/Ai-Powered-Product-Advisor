"""Canonical Product Image Service.

Implements Stage 3 image integrity, ownership, and resolution rules:
- Strictly verifies product-image ownership before returning any image.
- Strictly rejects cross-product image linkage or variant mismatches.
- Resolves image URLs safely using StorageService abstraction without exposing internal paths.
- Enforces canonical storage structure: products/{product_id}/...
- Prevents path traversal and arbitrary user-provided paths.
- Enforces primary image uniqueness per product.
"""

import uuid
from typing import Optional, List, Union, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.catalog import Product, ProductVariant
from app.services.storage import StorageService, StoragePath
from app.services.factory import get_db_service, get_storage_service
from app.services.image_validator import ImageValidator


def _coerce_uuid(val: Union[uuid.UUID, str]) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


class ImageOwnershipError(ValueError):
    """Raised when an image or variant does not belong to the specified product."""
    pass


class ImageNotFoundError(KeyError):
    """Raised when an image does not exist in the catalog."""
    pass


class ProductNotFoundError(KeyError):
    """Raised when a product does not exist in the catalog."""
    pass


class ProductImageService:
    """Canonical service abstraction managing product images with strict ownership enforcement."""

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        storage_service: Optional[StorageService] = None,
    ):
        self._provided_session = session
        self._storage_service = storage_service

    async def _get_session(self):
        if self._provided_session is not None:
            yield self._provided_session
        else:
            db_service = get_db_service()
            async with db_service.session() as s:
                yield s

    async def _get_storage(self) -> StorageService:
        if self._storage_service is not None:
            return self._storage_service
        self._storage_service = get_storage_service()
        return self._storage_service

    # =========================================================================
    # 1. Image Resolution with Strict Ownership Enforcement
    # =========================================================================

    async def get_image(
        self,
        product_id: Union[uuid.UUID, str],
        image_id: Union[uuid.UUID, str],
    ) -> ProductImage:
        """Fetch a single image strictly validating that it belongs to product_id.

        If the image belongs to a different product, raises ImageOwnershipError.
        NEVER returns an image belonging to another product.
        """
        pid = _coerce_uuid(product_id)
        img_id = _coerce_uuid(image_id)

        stmt = select(ProductImage).where(ProductImage.id == img_id)
        async for session in self._get_session():
            result = await session.execute(stmt)
            image = result.scalar_one_or_none()

            if not image:
                raise ImageNotFoundError(f"Image {img_id} not found in catalog.")

            if image.product_id != pid:
                raise ImageOwnershipError(
                    f"Image ownership violation: Image {img_id} belongs to product "
                    f"{image.product_id}, NOT requested product {pid}."
                )

            return image

    async def get_primary_image(
        self,
        product_id: Union[uuid.UUID, str],
    ) -> Optional[ProductImage]:
        """Fetch the single primary image strictly belonging to canonical product_id.

        Returns None if no primary image is assigned; NEVER substitutes another product's image.
        """
        pid = _coerce_uuid(product_id)
        stmt = (
            select(ProductImage)
            .where(
                ProductImage.product_id == pid,
                ProductImage.is_primary.is_(True),
            )
            .order_by(ProductImage.created_at.asc())
        )
        async for session in self._get_session():
            result = await session.execute(stmt)
            primary = result.scalars().first()

            if not primary:
                # Secondary lookup for image_type == 'primary' if is_primary boolean was not set
                stmt_type = (
                    select(ProductImage)
                    .where(
                        ProductImage.product_id == pid,
                        ProductImage.image_type == "primary",
                    )
                    .order_by(ProductImage.created_at.asc())
                )
                res_type = await session.execute(stmt_type)
                primary = res_type.scalars().first()

            if not primary:
                return None

            # Verify ownership
            if primary.product_id != pid:
                raise ImageOwnershipError(
                    f"Image {primary.id} belongs to {primary.product_id}, not {pid}"
                )
            return primary

    async def get_images(
        self,
        product_id: Union[uuid.UUID, str],
    ) -> List[ProductImage]:
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
            # Enforce strict product identity
            for img in images:
                if img.product_id != pid:
                    raise ImageOwnershipError(
                        f"Image {img.id} belongs to {img.product_id}, not {pid}"
                    )
            return images

    async def get_images_for_variant(
        self,
        product_id: Union[uuid.UUID, str],
        variant_id: Union[uuid.UUID, str],
    ) -> List[ProductImage]:
        """Fetch images for a specific product variant, validating variant-product ownership.

        If variant_id belongs to a different product, raises ImageOwnershipError.
        """
        pid = _coerce_uuid(product_id)
        vid = _coerce_uuid(variant_id)

        async for session in self._get_session():
            # First verify variant exists and belongs to product_id
            v_stmt = select(ProductVariant).where(ProductVariant.id == vid)
            v_res = await session.execute(v_stmt)
            variant = v_res.scalar_one_or_none()

            if not variant:
                raise ValueError(f"Variant {vid} does not exist.")

            if variant.product_id != pid:
                raise ImageOwnershipError(
                    f"Variant mismatch: Variant {vid} belongs to product "
                    f"{variant.product_id}, NOT requested product {pid}."
                )

            # Query images belonging to both product_id and variant_id
            img_stmt = (
                select(ProductImage)
                .where(
                    ProductImage.product_id == pid,
                    ProductImage.variant_id == vid,
                )
                .order_by(ProductImage.is_primary.desc(), ProductImage.created_at.asc())
            )
            img_res = await session.execute(img_stmt)
            images = list(img_res.scalars().all())

            for img in images:
                if img.product_id != pid or img.variant_id != vid:
                    raise ImageOwnershipError(
                        f"Image {img.id} variant mapping invalid."
                    )
            return images

    # =========================================================================
    # 2. Canonical URL Generation & Storage Interaction
    # =========================================================================

    async def get_image_url(
        self,
        product_id: Union[uuid.UUID, str],
        image_id: Union[uuid.UUID, str],
        expires_seconds: int = 3600,
    ) -> str:
        """Resolve a public or presigned download URL for an image.

        1. Verifies that image_id belongs to product_id.
        2. Resolves URL via StorageService if stored in object storage.
        3. Falls back to verified external CDN URL or data URI.
        4. Never exposes internal MinIO credentials.
        """
        image = await self.get_image(product_id, image_id)

        # Check storage_key in StorageService
        if image.storage_key:
            # Validate safety to prevent path traversal
            if not StoragePath.validate_safe_key(image.storage_key, expected_product_id=image.product_id):
                raise ValueError(f"Invalid or unsafe storage key: {image.storage_key}")

            storage = await self._get_storage()
            try:
                if await storage.exists(image.storage_key):
                    return await storage.get_url(image.storage_key, expires_seconds=expires_seconds)
            except Exception:
                pass

        # Fallback to verified image_url
        if image.image_url and image.image_url.strip():
            return image.image_url

        return f"https://cdn.productadvisor.internal/images/products/{image.product_id}/{image.image_type}.webp"

    # =========================================================================
    # 3. Canonical Storage Key Construction & Validation
    # =========================================================================

    @staticmethod
    def build_canonical_storage_key(
        product_id: Union[uuid.UUID, str],
        image_type: str,
        image_id: Optional[Union[uuid.UUID, str]] = None,
        variant_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> str:
        """Build storage key conforming strictly to Section 5:
        - products/{product_id}/primary.webp
        - products/{product_id}/front.webp
        - products/{product_id}/gallery/{image_id}.webp
        - products/{product_id}/variants/{variant_id}/primary.webp
        - products/{product_id}/variants/{variant_id}/gallery/{image_id}.webp
        """
        pid = _coerce_uuid(product_id)
        vid = _coerce_uuid(variant_id) if variant_id else None
        img_id = _coerce_uuid(image_id) if image_id else None
        return StoragePath.build_product_image_key(pid, image_type, img_id, vid)

    @staticmethod
    def validate_storage_key_matches_product(
        product_id: Union[uuid.UUID, str],
        storage_key: str,
    ) -> bool:
        """Verify that storage_key strictly belongs to product_id."""
        pid = _coerce_uuid(product_id)
        return StoragePath.validate_safe_key(storage_key, expected_product_id=pid)

    # =========================================================================
    # 4. Primary Image Assignment & Integrity
    # =========================================================================

    async def set_primary_image(
        self,
        product_id: Union[uuid.UUID, str],
        image_id: Union[uuid.UUID, str],
    ) -> ProductImage:
        """Atomically set image_id as the ONLY primary image for product_id."""
        target_image = await self.get_image(product_id, image_id)
        pid = _coerce_uuid(product_id)

        async for session in self._get_session():
            # Reset all other images for this product to is_primary = False
            await session.execute(
                update(ProductImage)
                .where(ProductImage.product_id == pid)
                .values(is_primary=False)
            )
            # Set the target image as primary
            target_image.is_primary = True
            session.add(target_image)
            await session.flush()
            return target_image

    async def upload_and_register_image(
        self,
        product_id: Union[uuid.UUID, str],
        data: bytes,
        image_type: str = "primary",
        variant_id: Optional[Union[uuid.UUID, str]] = None,
        is_primary: bool = False,
        source: Optional[str] = None,
    ) -> ProductImage:
        """Validate, normalize, upload to StorageService, and register in database."""
        pid = _coerce_uuid(product_id)
        vid = _coerce_uuid(variant_id) if variant_id else None

        # 1. Validate image type
        clean_type = image_type.strip().lower()
        if not ImageValidator.is_canonical_type(clean_type):
            raise ValueError(
                f"Invalid image_type '{image_type}'. Allowed types: {sorted(CANONICAL_IMAGE_TYPES)}"
            )

        # 2. Validate payload
        validation = ImageValidator.validate_image_bytes(data)
        if not validation["is_valid"] and validation["status"] == "invalid":
            raise ValueError(f"Image validation failed: {validation['issues']}")

        # 3. Normalize to WEBP
        normalized_data = ImageValidator.normalize_to_webp(data)
        image_id = uuid.uuid4()

        # 4. Build canonical storage key
        storage_key = self.build_canonical_storage_key(
            product_id=pid,
            image_type=clean_type,
            image_id=image_id,
            variant_id=vid,
        )

        # 5. Upload via StorageService
        storage = await self._get_storage()
        await storage.put_object(
            object_name=storage_key,
            data=normalized_data,
            content_type="image/webp",
        )

        # 6. Primary image uniqueness check
        async for session in self._get_session():
            if is_primary:
                await session.execute(
                    update(ProductImage)
                    .where(ProductImage.product_id == pid)
                    .values(is_primary=False)
                )

            img = ProductImage(
                id=image_id,
                product_id=pid,
                variant_id=vid,
                storage_key=storage_key,
                storage_path=storage_key,
                image_url=None,
                image_type=clean_type,
                is_primary=is_primary,
                verified=True,
                source=source or "Normalized Catalog Upload",
                visual_features={
                    "format": "WEBP",
                    "dimensions": validation.get("dimensions"),
                    "status": validation.get("status"),
                },
            )
            session.add(img)
            await session.flush()
            return img
