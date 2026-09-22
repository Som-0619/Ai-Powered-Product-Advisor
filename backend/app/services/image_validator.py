"""Image File, Format, and Quality Validation Service.

Implements Stage 3 image integrity rules:
- Existence, readability, non-empty payload check
- MIME type and image format validation (JPEG, PNG, WEBP)
- Dimension checks (prevent zero or micro resolutions)
- Detection of HTML masquerading as images
- Detection of placeholder or broken images
- Safe normalization to WEBP format
"""

import io
from typing import Any, Dict, Optional, Tuple, Set
try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    Image = None
    class UnidentifiedImageError(Exception):
        pass


from app.models.media import CANONICAL_IMAGE_TYPES

ALLOWED_FORMATS: Set[str] = {"JPEG", "PNG", "WEBP"}
ALLOWED_MIME_TYPES: Set[str] = {"image/jpeg", "image/png", "image/webp"}

FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


class ImageValidationError(ValueError):
    """Raised when an image payload fails integrity or safety validation."""
    pass


class ImageValidator:
    """Validates image payloads for format, dimensions, readability, and security."""

    MIN_WIDTH: int = 50
    MIN_HEIGHT: int = 50

    @classmethod
    def is_canonical_type(cls, image_type: str) -> bool:
        """Check if an image type is in the allowed canonical set."""
        if not image_type or not isinstance(image_type, str):
            return False
        return image_type.strip().lower() in CANONICAL_IMAGE_TYPES

    @classmethod
    def validate_image_bytes(
        cls,
        data: bytes,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Exhaustively validate binary image payload.

        Returns:
            Dict containing:
                is_valid: bool
                status: 'valid' | 'invalid' | 'needs_review'
                format: Optional[str] ('JPEG', 'PNG', 'WEBP')
                mime_type: Optional[str]
                dimensions: Optional[Tuple[int, int]]
                issues: List[str]
        """
        issues = []
        min_w = min_width if min_width is not None else cls.MIN_WIDTH
        min_h = min_height if min_height is not None else cls.MIN_HEIGHT

        if not data or len(data) == 0:
            return {
                "is_valid": False,
                "status": "invalid",
                "format": None,
                "mime_type": None,
                "dimensions": None,
                "issues": ["zero_byte_file"],
            }

        # Check for HTML masquerading as an image (e.g. 404/login crawler pages)
        header_sample = data[:512].lstrip()
        lower_header = header_sample.lower()
        if (
            lower_header.startswith(b"<!doctype html")
            or lower_header.startswith(b"<html")
            or b"<body" in lower_header
            or b"<script" in lower_header
        ):
            return {
                "is_valid": False,
                "status": "invalid",
                "format": None,
                "mime_type": "text/html",
                "dimensions": None,
                "issues": ["html_file_pretending_to_be_image"],
            }

        # Verify readability and extract dimensions via Pillow
        try:
            stream = io.BytesIO(data)
            with Image.open(stream) as img:
                img_format = (img.format or "").upper()
                width, height = img.size

                if img_format not in ALLOWED_FORMATS:
                    return {
                        "is_valid": False,
                        "status": "invalid",
                        "format": img_format,
                        "mime_type": None,
                        "dimensions": (width, height),
                        "issues": [f"unsupported_format_{img_format}"],
                    }

                mime_type = FORMAT_TO_MIME.get(img_format, f"image/{img_format.lower()}")

                # Check dimensions
                if width < min_w or height < min_h:
                    issues.append(f"extremely_low_resolution_{width}x{height}")
                    return {
                        "is_valid": False,
                        "status": "needs_review",
                        "format": img_format,
                        "mime_type": mime_type,
                        "dimensions": (width, height),
                        "issues": issues,
                    }

                # Check if image appears to be a solid placeholder
                if width > 0 and height > 0:
                    extrema = img.getextrema()
                    # If grayscale or RGB image has zero variance across channels
                    if extrema:
                        if isinstance(extrema[0], tuple):
                            is_uniform = all(min_val == max_val for min_val, max_val in extrema)
                        else:
                            is_uniform = extrema[0] == extrema[1]
                        if is_uniform:
                            issues.append("uniform_solid_placeholder")
                            return {
                                "is_valid": True,
                                "status": "needs_review",
                                "format": img_format,
                                "mime_type": mime_type,
                                "dimensions": (width, height),
                                "issues": issues,
                            }

                return {
                    "is_valid": True,
                    "status": "valid",
                    "format": img_format,
                    "mime_type": mime_type,
                    "dimensions": (width, height),
                    "issues": [],
                }
        except (UnidentifiedImageError, OSError, Exception) as exc:
            return {
                "is_valid": False,
                "status": "invalid",
                "format": None,
                "mime_type": None,
                "dimensions": None,
                "issues": [f"broken_or_unreadable_image: {str(exc)}"],
            }

    @classmethod
    def normalize_to_webp(cls, data: bytes, quality: int = 85) -> bytes:
        """Convert any valid image byte payload safely to normalized WEBP bytes."""
        val = cls.validate_image_bytes(data)
        if not val["is_valid"] and val["status"] == "invalid":
            raise ImageValidationError(f"Cannot normalize invalid image: {val['issues']}")

        stream = io.BytesIO(data)
        with Image.open(stream) as img:
            # If already WEBP, return as-is
            if (img.format or "").upper() == "WEBP":
                return data

            # Convert to RGB if RGBA/P/other unsupported by default lossy WEBP
            converted = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
            out_stream = io.BytesIO()
            converted.save(out_stream, format="WEBP", quality=quality)
            return out_stream.getvalue()

    @classmethod
    def create_synthetic_webp(
        cls,
        width: int = 300,
        height: int = 300,
        color: Tuple[int, int, int] = (64, 128, 192),
    ) -> bytes:
        """Helper to create a valid, readable WEBP payload for testing and storage verification."""
        img = Image.new("RGB", (width, height), color=color)
        out = io.BytesIO()
        img.save(out, format="WEBP", quality=90)
        return out.getvalue()
