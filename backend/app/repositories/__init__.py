"""Repositories package exporting data access classes."""

from app.repositories.base import BaseRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.compatibility_repository import CompatibilityRepository

__all__ = [
    "BaseRepository",
    "ProductRepository",
    "ComponentRepository",
    "ReviewRepository",
    "CompatibilityRepository",
]
