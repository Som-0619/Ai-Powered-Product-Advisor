"""Review repository with fraud score and sentiment filtering."""

import uuid
from typing import Optional, Sequence, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reviews import Review, Reviewer
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: AsyncSession):
        super().__init__(Review, session)

    async def list_for_product(
        self,
        product_id: uuid.UUID,
        min_rating: Optional[float] = None,
        sentiment: Optional[str] = None,
        max_fraud_score: float = 0.5,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Review]:
        """Fetch verified/clean reviews for a shortlisted product."""
        stmt = (
            select(Review)
            .where(Review.product_id == product_id)
            .where(Review.fraud_score <= max_fraud_score)
            .options(selectinload(Review.reviewer))
        )
        if min_rating is not None:
            stmt = stmt.where(Review.rating >= min_rating)
        if sentiment is not None:
            stmt = stmt.where(Review.sentiment == sentiment)

        stmt = stmt.order_by(Review.reviewed_at.desc().nullslast()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_product_review_summary(self, product_id: uuid.UUID) -> Dict[str, Any]:
        """Compute average rating and count of clean vs suspicious reviews."""
        stmt = select(
            func.count(Review.id).label("total_reviews"),
            func.avg(Review.rating).label("avg_rating"),
            func.count().filter(Review.fraud_score > 0.5).label("suspicious_count"),
        ).where(Review.product_id == product_id)
        result = await self.session.execute(stmt)
        row = result.first()
        return {
            "total_reviews": row.total_reviews if row else 0,
            "avg_rating": round(float(row.avg_rating), 2) if row and row.avg_rating else None,
            "suspicious_count": row.suspicious_count if row else 0,
        }
