"""Realistic Seed Data for Product Advisor (Phase 2).

Populates all 21 models with realistic data for both:
1. Consumer Electronics (Laptops, GPUs, Ultrabooks)
2. Electronic Components (Microcontrollers, Sensors, Passives)
Includes prices, availabilities, specs, compatibility rules, relationships,
reviews, documents, images, and telemetry runs.
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add backend to sys.path so app modules are resolvable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, delete

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


async def seed_database():
    print(f"Connecting to database: {settings.async_database_url}")
    engine = create_async_engine(settings.async_database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        print("Cleaning up any existing seed data...")
        # Clean in reverse dependency order
        for model in [
            ModelCall,
            AgentStep,
            AgentRun,
            ProductRelationship,
            CompatibilityRule,
            Price,
            Availability,
            Review,
            Reviewer,
            Document,
            Image,
            ComponentSpecification,
            Component,
            Specification,
            ProductVariant,
            ProductSource,
            CrawlJob,
            Product,
            Brand,
            Category,
            Source,
        ]:
            await session.execute(delete(model))
        await session.commit()

        print("\n--- 1. Seeding Sources ---")
        sources = {
            "digikey": Source(
                name="DigiKey",
                base_url="https://www.digikey.com",
                source_type="distributor",
                trust_rating=0.98,
            ),
            "mouser": Source(
                name="Mouser Electronics",
                base_url="https://www.mouser.com",
                source_type="distributor",
                trust_rating=0.97,
            ),
            "bestbuy": Source(
                name="Best Buy",
                base_url="https://www.bestbuy.com",
                source_type="retailer",
                trust_rating=0.92,
            ),
            "amazon": Source(
                name="Amazon",
                base_url="https://www.amazon.com",
                source_type="marketplace",
                trust_rating=0.88,
            ),
            "espressif_direct": Source(
                name="Espressif Official",
                base_url="https://www.espressif.com",
                source_type="manufacturer",
                trust_rating=0.99,
            ),
            "ti_store": Source(
                name="TI Store",
                base_url="https://www.ti.com",
                source_type="manufacturer",
                trust_rating=0.99,
            ),
        }
        session.add_all(sources.values())
        await session.flush()
        print(f"Added {len(sources)} sources.")

        print("\n--- 2. Seeding Categories ---")
        categories = {
            # Consumer categories
            "laptops": Category(
                name="Laptops & Ultrabooks",
                slug="laptops-ultrabooks",
                description="Portable personal computers and ultrabooks for work and gaming",
                category_type="consumer",
            ),
            "gpus": Category(
                name="Graphics Cards (GPUs)",
                slug="graphics-cards-gpus",
                description="Dedicated graphic processing units for gaming and AI workloads",
                category_type="consumer",
            ),
            # Component categories
            "mcus": Category(
                name="Microcontrollers & SoCs",
                slug="microcontrollers-socs",
                description="Embedded microcontrollers, Wi-Fi/Bluetooth SoCs, and system boards",
                category_type="component",
            ),
            "sensors": Category(
                name="Sensors & Transducers",
                slug="sensors-transducers",
                description="Environmental, inertial, optical, and biometric sensor modules",
                category_type="component",
            ),
            "passives": Category(
                name="Passive Components",
                slug="passive-components",
                description="Capacitors, resistors, inductors, and filters",
                category_type="component",
            ),
            "power": Category(
                name="Power Management ICs",
                slug="power-management-ics",
                description="Linear regulators, buck/boost converters, and battery chargers",
                category_type="component",
            ),
        }
        session.add_all(categories.values())
        await session.flush()
        print(f"Added {len(categories)} categories.")

        print("\n--- 3. Seeding Brands ---")
        brands = {
            "lenovo": Brand(name="Lenovo", slug="lenovo", website="https://www.lenovo.com", country="China"),
            "nvidia": Brand(name="NVIDIA", slug="nvidia", website="https://www.nvidia.com", country="USA"),
            "apple": Brand(name="Apple", slug="apple", website="https://www.apple.com", country="USA"),
            "espressif": Brand(name="Espressif Systems", slug="espressif", website="https://www.espressif.com", country="China"),
            "bosch": Brand(name="Bosch Sensortec", slug="bosch-sensortec", website="https://www.bosch-sensortec.com", country="Germany"),
            "murata": Brand(name="Murata Manufacturing", slug="murata", website="https://www.murata.com", country="Japan"),
            "ti": Brand(name="Texas Instruments", slug="texas-instruments", website="https://www.ti.com", country="USA"),
        }
        session.add_all(brands.values())
        await session.flush()
        print(f"Added {len(brands)} brands.")

        print("\n--- 4. Seeding Products & Variants ---")
        # Product 1: Consumer Laptop
        laptop = Product(
            title="Lenovo ThinkPad X1 Carbon Gen 11",
            slug="lenovo-thinkpad-x1-carbon-gen-11",
            description="Ultra-lightweight enterprise laptop featuring Intel Core i7 13th Gen, 14-inch OLED display, and military-grade durability.",
            model_number="21HM000DUS",
            sku="LNV-X1C11-001",
            status="active",
            is_component=False,
            category_id=categories["laptops"].id,
            brand_id=brands["lenovo"].id,
        )
        session.add(laptop)
        await session.flush()

        laptop_var1 = ProductVariant(
            product_id=laptop.id,
            sku="LNV-X1C11-16-512",
            title="ThinkPad X1 Carbon Gen 11 (16GB RAM / 512GB SSD / Core i7-1365U)",
            attributes={"ram_gb": 16, "storage_gb": 512, "cpu": "Intel Core i7-1365U", "color": "Deep Black"},
        )
        laptop_var2 = ProductVariant(
            product_id=laptop.id,
            sku="LNV-X1C11-32-1TB",
            title="ThinkPad X1 Carbon Gen 11 (32GB RAM / 1TB SSD / Core i7-1370P)",
            attributes={"ram_gb": 32, "storage_gb": 1024, "cpu": "Intel Core i7-1370P", "color": "Deep Black"},
        )
        session.add_all([laptop_var1, laptop_var2])

        # Product 2: Consumer GPU
        gpu = Product(
            title="NVIDIA GeForce RTX 4080 Super Founders Edition",
            slug="nvidia-geforce-rtx-4080-super",
            description="High-performance Ada Lovelace GPU with 16GB GDDR6X VRAM, ray tracing, DLSS 3.5, and dual ball bearing fans.",
            model_number="900-1G136-2555-000",
            sku="NV-RTX4080S-FE",
            status="active",
            is_component=False,
            category_id=categories["gpus"].id,
            brand_id=brands["nvidia"].id,
        )
        session.add(gpu)

        # Product 3: Component - ESP32 Microcontroller
        esp32 = Product(
            title="Espressif ESP32-WROOM-32E Wi-Fi + BLE Microcontroller Module",
            slug="espressif-esp32-wroom-32e-n4",
            description="Powerful Wi-Fi+Bluetooth+Bluetooth LE MCU module powered by Xtensa dual-core 32-bit LX6 microprocessor.",
            model_number="ESP32-WROOM-32E (4MB)",
            sku="ESP32-WROOM-32E-N4",
            status="active",
            is_component=True,
            category_id=categories["mcus"].id,
            brand_id=brands["espressif"].id,
        )
        session.add(esp32)

        # Product 4: Component - Bosch BME280 Sensor
        bme280 = Product(
            title="Bosch BME280 Combined Temperature, Humidity, and Pressure Sensor",
            slug="bosch-bme280-sensor",
            description="Digital environmental sensor with ultra-low power consumption and high accuracy for IoT mobile and wearable devices.",
            model_number="BME280",
            sku="BST-BME280",
            status="active",
            is_component=True,
            category_id=categories["sensors"].id,
            brand_id=brands["bosch"].id,
        )
        session.add(bme280)

        # Product 5: Component - Murata Ceramic Capacitor
        capacitor = Product(
            title="Murata 10µF 10V X5R 0603 Ceramic Capacitor",
            slug="murata-10uf-10v-0603-capacitor",
            description="High capacitance multilayer ceramic capacitor (MLCC) for power supply decoupling and noise suppression.",
            model_number="GRM188R61A106KE69D",
            sku="MUR-GRM188-10UF",
            status="active",
            is_component=True,
            category_id=categories["passives"].id,
            brand_id=brands["murata"].id,
        )
        session.add(capacitor)

        # Product 6: Component - TI LDO Regulator
        ldo = Product(
            title="Texas Instruments TPS7A02 200mA Ultra-Low Iq LDO Regulator",
            slug="ti-tps7a02-ldo-regulator",
            description="25-nA quiescent current, 200-mA low-dropout linear regulator with high PSRR for battery-powered IoT devices.",
            model_number="TPS7A0233PDBVR",
            sku="TI-TPS7A0233",
            status="active",
            is_component=True,
            category_id=categories["power"].id,
            brand_id=brands["ti"].id,
        )
        session.add(ldo)
        await session.flush()
        print("Added 6 products and product variants.")

        print("\n--- 5. Seeding Component Entities & Specifications ---")
        # Component 1: ESP32
        esp32_comp = Component(
            product_id=esp32.id,
            part_number="ESP32-WROOM-32E-N4",
            package_type="SMD Module (38-pin)",
            pin_count=38,
            mounting_type="Surface Mount",
            lifecycle_status="active",
            datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf",
        )
        session.add(esp32_comp)
        await session.flush()

        esp32_spec = ComponentSpecification(
            component_id=esp32_comp.id,
            voltage_min=3.0,
            voltage_max=3.6,
            voltage_unit="V",
            current_min=0.005,
            current_max=0.500,
            current_unit="A",
            power=1.65,
            power_unit="W",
            interface="SPI, I2C, UART, PWM, ADC, DAC, I2S",
            package="MODULE-38_18x25.5mm",
            frequency=240.0,
            frequency_unit="MHz",
            temperature_min=-40.0,
            temperature_max=85.0,
            extra_specs={
                "core": "Xtensa dual-core 32-bit LX6",
                "flash_mb": 4,
                "sram_kb": 520,
                "wireless": ["Wi-Fi 802.11 b/g/n", "Bluetooth v4.2 BR/EDR and BLE"],
                "gpio_pins": 26,
            },
        )
        session.add(esp32_spec)

        # Component 2: BME280 Sensor
        bme280_comp = Component(
            product_id=bme280.id,
            part_number="BME280",
            package_type="8-pin LGA",
            pin_count=8,
            mounting_type="Surface Mount",
            lifecycle_status="active",
            datasheet_url="https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
        )
        session.add(bme280_comp)
        await session.flush()

        bme280_spec = ComponentSpecification(
            component_id=bme280_comp.id,
            voltage_min=1.71,
            voltage_max=3.60,
            voltage_unit="V",
            current_min=0.0000001,
            current_max=0.0036,
            current_unit="A",
            power=0.013,
            power_unit="W",
            interface="I2C (up to 3.4MHz), SPI (3-wire/4-wire up to 10MHz)",
            package="LGA-8_2.5x2.5x0.93mm",
            frequency=10.0,
            frequency_unit="MHz",
            temperature_min=-40.0,
            temperature_max=85.0,
            extra_specs={
                "pressure_range_hpa": [300, 1100],
                "humidity_range_pct": [0, 100],
                "temp_accuracy_c": 0.5,
                "pressure_accuracy_hpa": 1.0,
                "response_time_s": 1.0,
            },
        )
        session.add(bme280_spec)

        # Component 3: Murata Capacitor
        cap_comp = Component(
            product_id=capacitor.id,
            part_number="GRM188R61A106KE69D",
            package_type="0603 (1608 Metric)",
            pin_count=2,
            mounting_type="Surface Mount",
            lifecycle_status="active",
            datasheet_url="https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188R61A106KE69-01.pdf",
        )
        session.add(cap_comp)
        await session.flush()

        cap_spec = ComponentSpecification(
            component_id=cap_comp.id,
            voltage_min=0.0,
            voltage_max=10.0,
            voltage_unit="V",
            capacitance=0.000010,
            capacitance_unit="F",
            tolerance="±10%",
            package="0603",
            temperature_min=-55.0,
            temperature_max=85.0,
            extra_specs={
                "dielectric": "X5R",
                "esr_mohm": 12.5,
                "dissipation_factor_pct": 10.0,
            },
        )
        session.add(cap_spec)

        # Component 4: TI LDO Regulator
        ldo_comp = Component(
            product_id=ldo.id,
            part_number="TPS7A0233PDBVR",
            package_type="SOT-23-5",
            pin_count=5,
            mounting_type="Surface Mount",
            lifecycle_status="active",
            datasheet_url="https://www.ti.com/lit/ds/symlink/tps7a02.pdf",
        )
        session.add(ldo_comp)
        await session.flush()

        ldo_spec = ComponentSpecification(
            component_id=ldo_comp.id,
            voltage_min=1.4,
            voltage_max=6.0,
            voltage_unit="V",
            current_min=0.000000025,
            current_max=0.200,
            current_unit="A",
            power=0.66,
            power_unit="W",
            interface="Analog Power",
            package="SOT-23-5",
            temperature_min=-40.0,
            temperature_max=125.0,
            extra_specs={
                "output_voltage_v": 3.3,
                "quiescent_current_na": 25,
                "dropout_voltage_mv": 145,
                "psrr_db": 64,
            },
        )
        session.add(ldo_spec)

        print("\n--- 6. Seeding Consumer Product Specifications (JSONB/EAV) ---")
        laptop_specs = [
            Specification(product_id=laptop.id, spec_group="Processor", key="cpu_model", value="Intel Core i7-1365U", raw_value={"cores": 10, "threads": 12, "base_ghz": 1.8, "boost_ghz": 5.2}),
            Specification(product_id=laptop.id, spec_group="Display", key="screen_size", value="14.0 inch", raw_value={"resolution": "2880x1800", "panel_type": "OLED", "refresh_rate_hz": 90, "brightness_nits": 400}),
            Specification(product_id=laptop.id, spec_group="Battery", key="capacity_wh", value="57 Whr", raw_value={"chemistry": "Li-Polymer", "fast_charge": True, "charger_w": 65}),
            Specification(product_id=laptop.id, spec_group="Connectivity", key="ports", value="2x Thunderbolt 4, 2x USB-A 3.2, HDMI 2.1, Audio Jack", raw_value={"thunderbolt_ports": 2, "wifi": "Wi-Fi 6E AX211", "bluetooth": "5.3"}),
            Specification(product_id=laptop.id, spec_group="Dimensions", key="weight_kg", value="1.12 kg", raw_value={"weight_lbs": 2.48, "thickness_mm": 15.36}),
        ]
        session.add_all(laptop_specs)

        gpu_specs = [
            Specification(product_id=gpu.id, spec_group="Performance", key="cuda_cores", value="10240", raw_value={"cuda_cores": 10240, "tensor_cores": 320, "rt_cores": 80}),
            Specification(product_id=gpu.id, spec_group="Memory", key="vram", value="16 GB GDDR6X", raw_value={"bus_width_bit": 256, "bandwidth_gbps": 736}),
            Specification(product_id=gpu.id, spec_group="Clocks", key="boost_clock_mhz", value="2550 MHz", raw_value={"base_mhz": 2295, "boost_mhz": 2550}),
            Specification(product_id=gpu.id, spec_group="Power", key="tgp_w", value="320 W", raw_value={"recommended_psu_w": 750, "power_connectors": "1x 16-pin (12VHPWR)"}),
            Specification(product_id=gpu.id, spec_group="Form Factor", key="dimensions", value="304 x 137 x 61 mm (3-slot)", raw_value={"slots": 3, "length_mm": 304}),
        ]
        session.add_all(gpu_specs)

        print("\n--- 7. Seeding Prices & Availabilities ---")
        now = datetime.now(timezone.utc)
        prices = [
            Price(product_id=laptop.id, variant_id=laptop_var1.id, source_id=sources["bestbuy"].id, amount=1429.99, currency="USD", recorded_at=now),
            Price(product_id=laptop.id, variant_id=laptop_var1.id, source_id=sources["amazon"].id, amount=1399.00, currency="USD", recorded_at=now),
            Price(product_id=laptop.id, variant_id=laptop_var2.id, source_id=sources["bestbuy"].id, amount=1799.99, currency="USD", recorded_at=now),
            Price(product_id=gpu.id, source_id=sources["bestbuy"].id, amount=999.99, currency="USD", recorded_at=now),
            Price(product_id=esp32.id, source_id=sources["digikey"].id, amount=2.95, currency="USD", recorded_at=now),
            Price(product_id=esp32.id, source_id=sources["mouser"].id, amount=2.90, currency="USD", recorded_at=now),
            Price(product_id=bme280.id, source_id=sources["digikey"].id, amount=4.48, currency="USD", recorded_at=now),
            Price(product_id=bme280.id, source_id=sources["mouser"].id, amount=4.52, currency="USD", recorded_at=now),
            Price(product_id=capacitor.id, source_id=sources["digikey"].id, amount=0.12, currency="USD", recorded_at=now),
            Price(product_id=ldo.id, source_id=sources["ti_store"].id, amount=0.48, currency="USD", recorded_at=now),
        ]
        session.add_all(prices)

        availabilities = [
            Availability(product_id=laptop.id, variant_id=laptop_var1.id, source_id=sources["bestbuy"].id, status="in_stock", stock_quantity=18),
            Availability(product_id=laptop.id, variant_id=laptop_var1.id, source_id=sources["amazon"].id, status="in_stock", stock_quantity=42),
            Availability(product_id=gpu.id, source_id=sources["bestbuy"].id, status="in_stock", stock_quantity=6),
            Availability(product_id=esp32.id, source_id=sources["digikey"].id, status="in_stock", stock_quantity=14200),
            Availability(product_id=esp32.id, source_id=sources["mouser"].id, status="in_stock", stock_quantity=9150),
            Availability(product_id=bme280.id, source_id=sources["digikey"].id, status="in_stock", stock_quantity=3250),
            Availability(product_id=capacitor.id, source_id=sources["digikey"].id, status="in_stock", stock_quantity=45000),
            Availability(product_id=ldo.id, source_id=sources["ti_store"].id, status="in_stock", stock_quantity=12000),
        ]
        session.add_all(availabilities)

        print("\n--- 8. Seeding Reviewers & Reviews ---")
        reviewer_tech = Reviewer(name="Alex Chen", external_id="rev_alex_88", is_verified=True, trust_score=0.96, metadata_json={"domain": "embedded_iot", "total_reviews": 34})
        reviewer_cad = Reviewer(name="Elena Rostova", external_id="rev_elena_cad", is_verified=True, trust_score=0.91, metadata_json={"domain": "hardware_engineer", "total_reviews": 19})
        reviewer_bot = Reviewer(name="DealSeeker992", external_id="rev_bot_992", is_verified=False, trust_score=0.15, metadata_json={"flagged_spam": True})
        session.add_all([reviewer_tech, reviewer_cad, reviewer_bot])
        await session.flush()

        reviews = [
            Review(
                product_id=laptop.id,
                reviewer_id=reviewer_cad.id,
                source_id=sources["bestbuy"].id,
                rating=4.8,
                title="Superb build quality, exceptional keyboard",
                body="The 11th Gen X1 Carbon continues to set the benchmark for enterprise ultrabooks. Thermal management is stable under sustained code compilation, though battery drops faster on the OLED panel.",
                sentiment="positive",
                use_case="Software Engineering & CAD",
                is_verified_purchase=True,
                fraud_score=0.03,
                attributes_analyzed={"keyboard": 5.0, "display": 4.9, "battery": 3.8, "thermals": 4.2},
                reviewed_at=now,
            ),
            Review(
                product_id=esp32.id,
                reviewer_id=reviewer_tech.id,
                source_id=sources["digikey"].id,
                rating=5.0,
                title="Rock solid Wi-Fi and Bluetooth MCU module",
                body="We have deployed over 500 units in remote weather sensor nodes. Flashing via esptool is effortless, deep sleep current draws under 10µA when configured properly, and RF range with PCB antenna is impressive.",
                sentiment="positive",
                use_case="Industrial IoT Weather Stations",
                is_verified_purchase=True,
                fraud_score=0.01,
                attributes_analyzed={"reliability": 5.0, "power_efficiency": 4.8, "rf_performance": 4.7},
                reviewed_at=now,
            ),
            Review(
                product_id=laptop.id,
                reviewer_id=reviewer_bot.id,
                source_id=sources["amazon"].id,
                rating=5.0,
                title="BEST LAPTOP EVER CLICK HERE TO BUY",
                body="AMAZING WOW SO FAST VERY COOL CHEAPEST LAPTOP EVER",
                sentiment="positive",
                use_case="Spam",
                is_verified_purchase=False,
                fraud_score=0.94,  # Flagged by fraud detector!
                attributes_analyzed={"suspicious_patterns": True},
                reviewed_at=now,
            ),
        ]
        session.add_all(reviews)

        print("\n--- 9. Seeding Documents & Images ---")
        documents = [
            Document(
                product_id=esp32.id,
                title="ESP32-WROOM-32E Datasheet v1.4",
                doc_type="datasheet",
                storage_path="documents/components/esp32-wroom-32e-datasheet.pdf",
                source_url="https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_datasheet_en.pdf",
                extracted_text="The ESP32-WROOM-32E is a powerful, generic Wi-Fi + Bluetooth + Bluetooth LE MCU module...",
                metadata_json={"pages": 31, "file_size_kb": 1420, "sha256": "8a7c2b4d..."},
            ),
            Document(
                product_id=bme280.id,
                title="BME280 Environmental Sensor Technical Reference",
                doc_type="datasheet",
                storage_path="documents/components/bme280-datasheet.pdf",
                source_url="https://www.bosch-sensortec.com/bme280.pdf",
                extracted_text="The BME280 is an integrated environmental sensor developed specifically for mobile applications...",
                metadata_json={"pages": 55, "file_size_kb": 1840, "sha256": "f3e1a90c..."},
            ),
            Document(
                product_id=laptop.id,
                title="ThinkPad X1 Carbon Gen 11 User & Hardware Maintenance Guide",
                doc_type="manual",
                storage_path="documents/consumer/thinkpad-x1-gen11-manual.pdf",
                source_url="https://download.lenovo.com/x1_carbon_gen11_ug.pdf",
                extracted_text="Lenovo ThinkPad X1 Carbon Gen 11 user guide and disassembly procedures...",
                metadata_json={"pages": 94, "file_size_kb": 4200},
            ),
        ]
        session.add_all(documents)

        images = [
            Image(
                product_id=laptop.id,
                storage_path="images/consumer/thinkpad-x1-front.webp",
                image_type="hero",
                is_primary=True,
                visual_features={"color_palette": ["black", "red_dot"], "angle": "front_open"},
            ),
            Image(
                product_id=esp32.id,
                storage_path="images/components/esp32-wroom-top.webp",
                image_type="package_top",
                is_primary=True,
                visual_features={"form_factor": "smd_module", "shielding_can": True, "pcb_antenna": True},
            ),
            Image(
                product_id=esp32.id,
                storage_path="images/components/esp32-pinout-diagram.webp",
                image_type="pinout",
                is_primary=False,
                visual_features={"diagram_type": "pinout", "pin_count": 38},
            ),
        ]
        session.add_all(images)

        print("\n--- 10. Seeding Compatibility Rules & Product Relationships ---")
        rules = [
            CompatibilityRule(
                category_a_id=categories["mcus"].id,
                category_b_id=categories["sensors"].id,
                rule_type="voltage_level_match",
                parameter_key="voltage",
                operator="subset_or_equal",
                description="Peripheral operating voltage range must overlap with MCU GPIO operating voltage range (3.3V).",
            ),
            CompatibilityRule(
                category_a_id=categories["mcus"].id,
                category_b_id=categories["sensors"].id,
                rule_type="communication_interface",
                parameter_key="interface",
                operator="intersects",
                description="MCU and Sensor must share at least one physical bus protocol (e.g. I2C or SPI).",
            ),
            CompatibilityRule(
                category_a_id=categories["laptops"].id,
                category_b_id=categories["gpus"].id,
                rule_type="external_chassis_required",
                parameter_key="thunderbolt",
                operator="requires_enclosure",
                description="Consumer laptops cannot install desktop PCIe GPUs directly; requires external Thunderbolt eGPU enclosure.",
            ),
        ]
        session.add_all(rules)

        relationships = [
            ProductRelationship(
                product_a_id=esp32.id,
                product_b_id=bme280.id,
                relationship_type="compatible",
                confidence=0.99,
                evidence="ESP32 GPIO operates at 3.3V, exactly matching BME280 VDD. Both support standard I2C bus (SDA/SCL) and SPI.",
            ),
            ProductRelationship(
                product_a_id=esp32.id,
                product_b_id=ldo.id,
                relationship_type="compatible",
                confidence=0.98,
                evidence="TI TPS7A02 supplies steady 3.3V output suitable for powering ESP32 in low-power IoT sensing configurations.",
            ),
            ProductRelationship(
                product_a_id=esp32.id,
                product_b_id=capacitor.id,
                relationship_type="recommended_accessory",
                confidence=0.97,
                evidence="10µF ceramic capacitor is recommended across ESP32 VDD and GND pins to absorb transient Wi-Fi current spikes.",
            ),
            ProductRelationship(
                product_a_id=laptop.id,
                product_b_id=gpu.id,
                relationship_type="requires_external_enclosure",
                confidence=0.95,
                evidence="ThinkPad X1 Carbon Gen 11 features dual Thunderbolt 4 ports (40 Gbps), enabling connection to RTX 4080 Super via external eGPU chassis.",
            ),
        ]
        session.add_all(relationships)

        print("\n--- 11. Seeding Product Sources & Crawl Jobs ---")
        prod_sources = [
            ProductSource(product_id=esp32.id, source_id=sources["digikey"].id, external_sku="1904-1023-1-ND", source_url="https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613135", crawl_metadata={"status": "parsed", "in_stock": True}),
            ProductSource(product_id=bme280.id, source_id=sources["mouser"].id, external_sku="262-BME280", source_url="https://www.mouser.com/ProductDetail/Bosch-Sensortec/BME280?qs=sGAEpiMZZMuqVf55WP224Q%3D%3D", crawl_metadata={"status": "parsed", "in_stock": True}),
            ProductSource(product_id=laptop.id, source_id=sources["bestbuy"].id, external_sku="BB-6538392", source_url="https://www.bestbuy.com/site/lenovo-thinkpad-x1-carbon-gen-11/6538392.p", crawl_metadata={"status": "parsed", "in_stock": True}),
        ]
        session.add_all(prod_sources)

        crawl_jobs = [
            CrawlJob(url="https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613135", source_id=sources["digikey"].id, status="completed", attempts=1, raw_storage_path="crawls/digikey_esp32.html"),
            CrawlJob(url="https://www.mouser.com/ProductDetail/Bosch-Sensortec/BME280", source_id=sources["mouser"].id, status="completed", attempts=1, raw_storage_path="crawls/mouser_bme280.html"),
            CrawlJob(url="https://www.bestbuy.com/site/lenovo-thinkpad-x1-carbon-gen-11/6538392.p", source_id=sources["bestbuy"].id, status="pending", attempts=0),
        ]
        session.add_all(crawl_jobs)

        print("\n--- 12. Seeding Telemetry: Agent Runs, Steps, and Model Calls ---")
        run = AgentRun(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            user_query="Can I connect the Bosch BME280 environmental sensor to an ESP32 microcontroller?",
            status="completed",
            total_latency_ms=1240.5,
            result_json={
                "verdict": "compatible",
                "confidence": 0.99,
                "summary": "Yes, BME280 and ESP32 are fully compatible over both I2C (GPIO21/22) and SPI at 3.3V logic levels.",
                "wiring": {"VCC": "3V3", "GND": "GND", "SDA": "GPIO 21", "SCL": "GPIO 22"},
            },
        )
        session.add(run)
        await session.flush()

        step1 = AgentStep(
            run_id=run.id,
            agent_name="SpecExtractionAgent",
            step_order=1,
            status="completed",
            input_payload={"target_a": "ESP32", "target_b": "BME280"},
            output_payload={"specs_a": {"voltage": [3.0, 3.6], "i2c": True}, "specs_b": {"voltage": [1.71, 3.6], "i2c": True}},
            latency_ms=420.0,
        )
        step2 = AgentStep(
            run_id=run.id,
            agent_name="CompatibilityVerificationAgent",
            step_order=2,
            status="completed",
            input_payload={"rule": "voltage_and_bus_match"},
            output_payload={"voltage_overlap": [3.0, 3.6], "shared_bus": ["I2C", "SPI"], "is_compatible": True},
            latency_ms=820.5,
        )
        session.add_all([step1, step2])
        await session.flush()

        call1 = ModelCall(
            step_id=step1.id,
            model_name="qwen2.5:4b",
            model_type="fast",
            prompt_tokens=450,
            completion_tokens=180,
            latency_ms=395.2,
            success=True,
        )
        call2 = ModelCall(
            step_id=step2.id,
            model_name="qwen2.5:8b",
            model_type="reasoning",
            prompt_tokens=780,
            completion_tokens=320,
            latency_ms=780.0,
            success=True,
        )
        session.add_all([call1, call2])

        await session.commit()
        print("\nAll seed data committed successfully!")

    # Verify counts
    async with session_factory() as session:
        print("\n=== Table Row Counts After Seeding ===")
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
        for name, model in models:
            res = await session.execute(select(model))
            count = len(res.scalars().all())
            print(f"  {name:<25}: {count:>3} rows")

    await engine.dispose()
    print("\nDatabase seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
