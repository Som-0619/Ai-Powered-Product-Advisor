"""canonical_electronics_catalog

Revision ID: c2b010000002
Revises: c1a010000001
Create Date: 2026-09-21 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c2b010000002'
down_revision: Union[str, None] = 'c1a010000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update products table with release_year, JSONB specifications, and canonical identity indexes
    op.add_column('products', sa.Column('release_year', sa.Integer(), nullable=True))
    op.add_column(
        'products',
        sa.Column(
            'specifications',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.create_index(op.f('ix_products_release_year'), 'products', ['release_year'], unique=False)
    op.create_index('ix_products_brand_model_variant', 'products', ['brand', 'model', 'variant'], unique=False)

    # 2. Update product_variants with external_product_id
    op.add_column('product_variants', sa.Column('external_product_id', sa.String(length=120), nullable=True))
    op.execute("""
        UPDATE product_variants
        SET external_product_id = external_variant_id
        WHERE external_product_id IS NULL AND external_variant_id IS NOT NULL;
    """)
    op.create_index(op.f('ix_product_variants_external_product_id'), 'product_variants', ['external_product_id'], unique=False)

    # 3. Normalize reviews table to product_reviews with canonical view
    # Rename reviews -> product_reviews
    op.rename_table('reviews', 'product_reviews')
    op.add_column('product_reviews', sa.Column('source', sa.String(length=100), nullable=True))

    # Backward-compatible view so legacy queries referencing "reviews" continue to function
    op.execute("CREATE OR REPLACE VIEW reviews AS SELECT * FROM product_reviews;")

    # 4. Update product_sources with last_verified
    op.add_column('product_sources', sa.Column('last_verified', sa.DateTime(timezone=True), nullable=True))
    op.execute("""
        UPDATE product_sources
        SET last_verified = last_checked
        WHERE last_verified IS NULL AND last_checked IS NOT NULL;
    """)


def downgrade() -> None:
    # Revert product_sources
    op.drop_column('product_sources', 'last_verified')

    # Revert product_reviews -> reviews
    op.execute("DROP VIEW IF EXISTS reviews;")
    op.drop_column('product_reviews', 'source')
    op.rename_table('product_reviews', 'reviews')

    # Revert product_variants
    op.drop_index(op.f('ix_product_variants_external_product_id'), table_name='product_variants')
    op.drop_column('product_variants', 'external_product_id')

    # Revert products
    op.drop_index('ix_products_brand_model_variant', table_name='products')
    op.drop_index(op.f('ix_products_release_year'), table_name='products')
    op.drop_column('products', 'specifications')
    op.drop_column('products', 'release_year')
