"""canonical_product_catalog

Revision ID: c1a010000001
Revises: 3b610152cf34
Create Date: 2026-09-20 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1a010000001'
down_revision: Union[str, None] = '3b610152cf34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update products table with canonical columns
    op.add_column('products', sa.Column('brand', sa.String(length=100), nullable=True))
    op.add_column('products', sa.Column('model', sa.String(length=150), nullable=True))
    op.add_column('products', sa.Column('variant', sa.String(length=150), nullable=True))
    op.add_column('products', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('products', sa.Column('subcategory', sa.String(length=100), nullable=True))
    op.add_column('products', sa.Column('external_product_id', sa.String(length=100), nullable=True))
    op.alter_column('products', 'category_id', nullable=True)

    op.create_index(op.f('ix_products_brand'), 'products', ['brand'], unique=False)
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)
    op.create_index(op.f('ix_products_external_product_id'), 'products', ['external_product_id'], unique=False)
    op.create_index(op.f('ix_products_model'), 'products', ['model'], unique=False)

    # Backfill products from joined brands and categories
    op.execute("""
        UPDATE products p
        SET brand = b.name
        FROM brands b
        WHERE p.brand_id = b.id AND p.brand IS NULL;
    """)
    op.execute("""
        UPDATE products p
        SET category = c.name
        FROM categories c
        WHERE p.category_id = c.id AND p.category IS NULL;
    """)
    op.execute("""
        UPDATE products
        SET model = COALESCE(model_number, title)
        WHERE model IS NULL;
    """)
    op.execute("""
        UPDATE products p
        SET external_product_id = ps.external_sku
        FROM product_sources ps
        WHERE p.id = ps.product_id AND ps.external_sku IS NOT NULL AND p.external_product_id IS NULL;
    """)

    # 2. Update product_variants with canonical columns
    op.add_column('product_variants', sa.Column('variant_name', sa.String(length=200), nullable=True))
    op.add_column('product_variants', sa.Column('external_variant_id', sa.String(length=120), nullable=True))
    op.add_column('product_variants', sa.Column('specifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.execute("""
        UPDATE product_variants
        SET variant_name = title, specifications = attributes
        WHERE variant_name IS NULL;
    """)

    op.alter_column('product_variants', 'variant_name', nullable=False, server_default='')
    op.alter_column('product_variants', 'specifications', nullable=False, server_default='{}')
    op.create_index(op.f('ix_product_variants_external_variant_id'), 'product_variants', ['external_variant_id'], unique=False)

    # 3. Rename images -> product_images and add canonical columns
    op.rename_table('images', 'product_images')
    op.add_column('product_images', sa.Column('variant_id', sa.UUID(), nullable=True))
    op.add_column('product_images', sa.Column('image_url', sa.String(length=500), nullable=True))
    op.add_column('product_images', sa.Column('storage_key', sa.String(length=500), nullable=True))
    op.add_column('product_images', sa.Column('source', sa.String(length=100), nullable=True))
    op.add_column('product_images', sa.Column('verified', sa.Boolean(), server_default=sa.text('true'), nullable=False))

    op.alter_column('product_images', 'product_id', nullable=False)
    op.alter_column('product_images', 'storage_path', nullable=True)

    op.create_foreign_key('fk_product_images_variant_id', 'product_images', 'product_variants', ['variant_id'], ['id'], ondelete='SET NULL')

    op.execute("""
        UPDATE product_images
        SET image_url = COALESCE(source_url, storage_path), storage_key = storage_path, verified = TRUE
        WHERE image_url IS NULL;
    """)

    op.create_index(op.f('ix_product_images_variant_id'), 'product_images', ['variant_id'], unique=False)

    # Backward compatible VIEW so any raw SQL queries looking for table "images" continue to work
    op.execute("CREATE OR REPLACE VIEW images AS SELECT * FROM product_images;")

    # 4. Create retailer_offers table
    op.create_table(
        'retailer_offers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('retailer', sa.String(length=50), nullable=False),
        sa.Column('external_product_id', sa.String(length=100), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
        sa.Column('availability_status', sa.String(length=40), server_default='available', nullable=False),
        sa.Column('verification_status', sa.String(length=40), server_default='unverified', nullable=False),
        sa.Column('last_verified', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("retailer IN ('amazon', 'flipkart')", name='check_retailer_offer_retailer'),
        sa.CheckConstraint("availability_status IN ('available', 'unavailable', 'unknown')", name='check_retailer_offer_availability'),
        sa.CheckConstraint("verification_status IN ('verified', 'unverified', 'broken', 'not_available')", name='check_retailer_offer_verification'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_retailer_offers_id'), 'retailer_offers', ['id'], unique=False)
    op.create_index(op.f('ix_retailer_offers_product_id'), 'retailer_offers', ['product_id'], unique=False)
    op.create_index(op.f('ix_retailer_offers_variant_id'), 'retailer_offers', ['variant_id'], unique=False)
    op.create_index(op.f('ix_retailer_offers_retailer'), 'retailer_offers', ['retailer'], unique=False)
    op.create_index(op.f('ix_retailer_offers_external_product_id'), 'retailer_offers', ['external_product_id'], unique=False)
    op.create_index(op.f('ix_retailer_offers_availability_status'), 'retailer_offers', ['availability_status'], unique=False)
    op.create_index(op.f('ix_retailer_offers_verification_status'), 'retailer_offers', ['verification_status'], unique=False)
    op.create_index('ix_retailer_offers_prod_retailer', 'retailer_offers', ['product_id', 'retailer', 'external_product_id'], unique=False)

    # 5. Update product_sources table
    op.add_column('product_sources', sa.Column('source_type', sa.String(length=50), server_default='dataset', nullable=False))
    op.add_column('product_sources', sa.Column('external_product_id', sa.String(length=120), nullable=True))
    op.add_column('product_sources', sa.Column('trust_score', sa.Float(), server_default='1.0', nullable=False))
    op.add_column('product_sources', sa.Column('last_checked', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('product_sources', 'source_id', nullable=True)

    op.execute("""
        UPDATE product_sources
        SET external_product_id = external_sku
        WHERE external_product_id IS NULL AND external_sku IS NOT NULL;
    """)

    op.create_index(op.f('ix_product_sources_source_type'), 'product_sources', ['source_type'], unique=False)
    op.create_index(op.f('ix_product_sources_external_product_id'), 'product_sources', ['external_product_id'], unique=False)


def downgrade() -> None:
    # Revert product_sources
    op.drop_index(op.f('ix_product_sources_external_product_id'), table_name='product_sources')
    op.drop_index(op.f('ix_product_sources_source_type'), table_name='product_sources')
    op.drop_column('product_sources', 'last_checked')
    op.drop_column('product_sources', 'trust_score')
    op.drop_column('product_sources', 'external_product_id')
    op.drop_column('product_sources', 'source_type')

    # Revert retailer_offers
    op.drop_index('ix_retailer_offers_prod_retailer', table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_verification_status'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_availability_status'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_external_product_id'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_retailer'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_variant_id'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_product_id'), table_name='retailer_offers')
    op.drop_index(op.f('ix_retailer_offers_id'), table_name='retailer_offers')
    op.drop_table('retailer_offers')

    # Revert product_images
    op.execute("DROP VIEW IF EXISTS images;")
    op.drop_index(op.f('ix_product_images_variant_id'), table_name='product_images')
    op.drop_constraint('fk_product_images_variant_id', 'product_images', type_='foreignkey')
    op.drop_column('product_images', 'verified')
    op.drop_column('product_images', 'source')
    op.drop_column('product_images', 'storage_key')
    op.drop_column('product_images', 'image_url')
    op.drop_column('product_images', 'variant_id')
    op.rename_table('product_images', 'images')

    # Revert product_variants
    op.drop_index(op.f('ix_product_variants_external_variant_id'), table_name='product_variants')
    op.drop_column('product_variants', 'specifications')
    op.drop_column('product_variants', 'external_variant_id')
    op.drop_column('product_variants', 'variant_name')

    # Revert products
    op.drop_index(op.f('ix_products_model'), table_name='products')
    op.drop_index(op.f('ix_products_external_product_id'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_index(op.f('ix_products_brand'), table_name='products')
    op.drop_column('products', 'external_product_id')
    op.drop_column('products', 'subcategory')
    op.drop_column('products', 'category')
    op.drop_column('products', 'variant')
    op.drop_column('products', 'model')
    op.drop_column('products', 'brand')
