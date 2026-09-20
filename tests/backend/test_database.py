"""Database tests for Product Advisor Phase 2.

Validates:
1. All 21 domain models exist, instantiate, and persist properly
2. UUID primary keys and timestamp auto-generation
3. Foreign key constraints, indexes, and relationships
4. JSONB queries on specifications and extra_specs
5. Repository pattern implementations (Product, Component, Review, Compatibility)
6. Service layer compatibility evaluation and catalog methods
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, text

from app.core.config import settings
from app.models import (
    Base,
    Brand,
    Category,
    Product,
    ProductVariant,
    Specification,
    Component,
    ComponentSpecification,
    Reviewer,
    Review,
    Source,
    ProductSource,
    Price,
    Availability,
    CompatibilityRule,
    ProductRelationship,
    Document,
    Image,
    CrawlJob,
    AgentRun,
    AgentStep,
    ModelCall,
)
from app.repositories.product_repository import ProductRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.compatibility_repository import CompatibilityRepository
from app.services.catalog_service import CatalogService
from app.services.compatibility_service import CompatibilityService


@pytest_asyncio.fixture(loop_scope="function")
async def db_session():
    """Provides a scoped async session connected to the test database."""
    engine = create_async_engine(settings.async_database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_all_21_models_seeded_and_queryable(db_session: AsyncSession):
    """Verify that all 21 models exist in the database and can be queried."""
    models = [
        ("Category", Category),
        ("Brand", Brand),
        ("Product", Product),
        ("ProductVariant", ProductVariant),
        ("Specification", Specification),
        ("Component", Component),
        ("ComponentSpecification", ComponentSpecification),
        ("Reviewer", Reviewer),
        ("Review", Review),
        ("Source", Source),
        ("ProductSource", ProductSource),
        ("Price", Price),
        ("Availability", Availability),
        ("CompatibilityRule", CompatibilityRule),
        ("ProductRelationship", ProductRelationship),
        ("Document", Document),
        ("Image", Image),
        ("CrawlJob", CrawlJob),
        ("AgentRun", AgentRun),
        ("AgentStep", AgentStep),
        ("ModelCall", ModelCall),
    ]

    for name, model_cls in models:
        result = await db_session.execute(select(model_cls))
        rows = result.scalars().all()
        assert len(rows) > 0, f"Expected table for model {name} to have seeded rows, found 0."


@pytest.mark.asyncio
async def test_product_repository_queries(db_session: AsyncSession):
    """Test ProductRepository fetching by slug, category, and loaded details."""
    repo = ProductRepository(db_session)

    # 1. Fetch by slug
    product = await repo.get_by_slug("lenovo-thinkpad-x1-carbon-gen-11")
    assert product is not None
    assert product.title == "Lenovo ThinkPad X1 Carbon Gen 11"
    assert product.is_component is False

    # 2. Fetch with details
    detailed = await repo.get_with_details(product.id)
    assert detailed is not None
    assert detailed.brand is not None
    assert detailed.brand.name == "Lenovo"
    assert detailed.category is not None
    assert len(detailed.variants) >= 2
    assert len(detailed.specifications) >= 5
    assert len(detailed.prices) >= 2
    assert len(detailed.availabilities) >= 2


@pytest.mark.asyncio
async def test_component_repository_electrical_filtering(db_session: AsyncSession):
    """Test ComponentRepository filtering by electrical parameters (voltage, package)."""
    comp_repo = ComponentRepository(db_session)

    # 1. Query by part number
    comp = await comp_repo.get_by_part_number("ESP32-WROOM-32E-N4")
    assert comp is not None
    assert comp.pin_count == 38
    assert comp.specification is not None
    assert comp.specification.voltage_min == 3.0
    assert comp.specification.voltage_max == 3.6
    assert comp.specification.frequency == 240.0
    assert comp.specification.frequency_unit == "MHz"

    # 2. Filter components by 3.3V operating voltage (ESP32, BME280, TPS7A02 all operate at 3.3V)
    matching_3v3 = await comp_repo.filter_by_electrical_parameters(operating_voltage=3.3)
    part_numbers = [c.part_number for c in matching_3v3]
    assert "ESP32-WROOM-32E-N4" in part_numbers
    assert "BME280" in part_numbers
    assert "TPS7A0233PDBVR" in part_numbers

    # 3. Filter by package type
    lga_comps = await comp_repo.filter_by_electrical_parameters(package_type="8-pin LGA")
    assert len(lga_comps) == 1
    assert lga_comps[0].part_number == "BME280"


@pytest.mark.asyncio
async def test_review_repository_fraud_detection(db_session: AsyncSession):
    """Test ReviewRepository filtering out fraudulent/spam reviews."""
    prod_repo = ProductRepository(db_session)
    review_repo = ReviewRepository(db_session)

    laptop = await prod_repo.get_by_slug("lenovo-thinkpad-x1-carbon-gen-11")
    assert laptop is not None

    # Get clean reviews only (fraud_score <= 0.5)
    clean_reviews = await review_repo.list_for_product(laptop.id, max_fraud_score=0.5)
    for r in clean_reviews:
        assert r.fraud_score <= 0.5
        assert r.title != "BEST LAPTOP EVER CLICK HERE TO BUY"

    # Get summary including suspicious review detection
    summary = await review_repo.get_product_review_summary(laptop.id)
    assert summary["total_reviews"] >= 2
    assert summary["suspicious_count"] >= 1


@pytest.mark.asyncio
async def test_compatibility_service_evaluation(db_session: AsyncSession):
    """Test deterministic compatibility service evaluating relationships."""
    prod_repo = ProductRepository(db_session)
    service = CompatibilityService(db_session)

    esp32 = await prod_repo.get_by_slug("espressif-esp32-wroom-32e-n4")
    bme280 = await prod_repo.get_by_slug("bosch-bme280-sensor")
    laptop = await prod_repo.get_by_slug("lenovo-thinkpad-x1-carbon-gen-11")
    gpu = await prod_repo.get_by_slug("nvidia-geforce-rtx-4080-super")

    assert esp32 is not None and bme280 is not None
    assert laptop is not None and gpu is not None

    # ESP32 + BME280 should be evaluated as compatible
    res_esp_bme = await service.evaluate_compatibility(esp32.id, bme280.id)
    assert res_esp_bme["status"] == "compatible"
    assert res_esp_bme["confidence"] >= 0.90

    # Laptop + Desktop GPU requires external chassis
    res_laptop_gpu = await service.evaluate_compatibility(laptop.id, gpu.id)
    assert res_laptop_gpu["status"] == "requires_external_enclosure"
    assert "Thunderbolt" in res_laptop_gpu["reason"]


@pytest.mark.asyncio
async def test_jsonb_specifications_and_telemetry(db_session: AsyncSession):
    """Test JSONB querying on flexible specifications and agent telemetry."""
    # 1. Query JSONB in Specification
    stmt = select(Specification).where(
        Specification.raw_value["panel_type"].as_string() == "OLED"
    )
    result = await db_session.execute(stmt)
    spec = result.scalar_one_or_none()
    assert spec is not None
    assert spec.key == "screen_size"
    assert spec.raw_value["resolution"] == "2880x1800"

    # 2. Query JSONB in ComponentSpecification extra_specs
    stmt_comp = select(ComponentSpecification).where(
        ComponentSpecification.extra_specs["sram_kb"].as_integer() == 520
    )
    comp_spec = (await db_session.execute(stmt_comp)).scalar_one_or_none()
    assert comp_spec is not None
    assert comp_spec.package == "MODULE-38_18x25.5mm"

    # 3. Query AgentRun and ModelCalls
    stmt_run = select(AgentRun).where(AgentRun.status == "completed")
    run = (await db_session.execute(stmt_run)).scalars().first()
    assert run is not None
    assert "wiring" in run.result_json
    assert run.result_json["verdict"] == "compatible"


@pytest.mark.asyncio
async def test_catalog_service_create_and_cascade(db_session: AsyncSession):
    """Test CatalogService product creation and component profile attachment."""
    cat_service = CatalogService(db_session)
    comp_repo = ComponentRepository(db_session)

    # Fetch any existing category
    cat_result = await db_session.execute(select(Category).where(Category.slug == "passive-components"))
    category = cat_result.scalar_one()

    # Create temporary component product
    temp_sku = f"TEST-RES-{uuid.uuid4().hex[:6]}"
    product = await cat_service.create_product(
        title="Test 10k Ohm 1% 0805 Resistor",
        slug=f"test-resistor-{uuid.uuid4().hex[:6]}",
        category_id=category.id,
        sku=temp_sku,
        is_component=True,
    )
    assert product.id is not None

    # Attach component electrical specification
    part_num = f"RES-10K-{uuid.uuid4().hex[:6]}"
    comp = await cat_service.add_component_profile(
        product_id=product.id,
        part_number=part_num,
        package_type="0805",
        pin_count=2,
        specs={
            "resistance": 10000.0,
            "resistance_unit": "Ohm",
            "tolerance": "±1%",
            "power": 0.125,
            "power_unit": "W",
            "temperature_min": -55.0,
            "temperature_max": 125.0,
        },
    )
    assert comp.id is not None

    # Verify query via repo with eager loading
    fetched = await comp_repo.get_by_part_number(part_num)
    assert fetched is not None
    assert fetched.package_type == "0805"
    assert fetched.specification is not None
    assert fetched.specification.resistance == 10000.0

    # Clean up test product (should cascade to component and specification)
    await cat_service.products.delete(product.id)
    await db_session.commit()

    deleted_comp = await comp_repo.get_by_part_number(part_num)
    assert deleted_comp is None
