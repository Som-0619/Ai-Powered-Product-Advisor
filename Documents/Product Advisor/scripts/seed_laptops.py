"""Seed realistic laptops catalog into PostgreSQL and sync with OpenSearch.

Includes:
1. Budget Gaming laptops under ₹50,000 (ASUS TUF Gaming F15, Lenovo IdeaPad Gaming 3, Acer Aspire 7)
2. Coding & ML laptops under ₹80,000 (ASUS Vivobook Pro 15 OLED, HP Victus 15, Acer Nitro 5, Lenovo IdeaPad Slim 5)
3. RTX 4060 laptops > ₹50,000 (Lenovo Legion Slim 5, ASUS ROG Zephyrus G14, Acer Predator Helios Neo 16)
4. Visual verification & ports laptop (Dell XPS 15 9530, Lenovo ThinkPad X1 Carbon Gen 11)
5. Apple MacBook Air M2
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.core.config import settings
from app.models import (
    Brand,
    Category,
    Product,
    ProductVariant,
    Specification,
    Price,
    Availability,
    Review,
    Reviewer,
    Source,
    Document,
    Image,
)
from app.services.factory import get_search_service


async def seed_laptops():
    print(f"Connecting to database: {settings.async_database_url}")
    engine = create_async_engine(settings.async_database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Ensure Categories
        cat_stmt = select(Category).where(Category.slug == "laptops-ultrabooks")
        laptop_cat = (await session.execute(cat_stmt)).scalar_one_or_none()
        if not laptop_cat:
            laptop_cat = Category(
                id=uuid.uuid4(),
                name="Laptops & Ultrabooks",
                slug="laptops-ultrabooks",
                description="Portable personal computers, ultrabooks, and gaming laptops",
                category_type="consumer",
            )
            session.add(laptop_cat)
            await session.flush()

        # 2. Ensure Brands
        brand_names = {
            "asus": ("ASUS", "Taiwan"),
            "lenovo": ("Lenovo", "China"),
            "acer": ("Acer", "Taiwan"),
            "hp": ("HP", "USA"),
            "dell": ("Dell", "USA"),
            "apple": ("Apple", "USA"),
        }
        brand_map = {}
        for slug, (name, country) in brand_names.items():
            b_stmt = select(Brand).where(Brand.slug == slug)
            b = (await session.execute(b_stmt)).scalar_one_or_none()
            if not b:
                b = Brand(
                    id=uuid.uuid4(),
                    name=name,
                    slug=slug,
                    website=f"https://www.{slug}.com",
                    country=country,
                )
                session.add(b)
                await session.flush()
            brand_map[slug] = b

        # 3. Ensure Sources & Reviewer
        src_stmt = select(Source).where(Source.name == "Amazon India")
        amazon_in = (await session.execute(src_stmt)).scalar_one_or_none()
        if not amazon_in:
            amazon_in = Source(
                id=uuid.uuid4(),
                name="Amazon India",
                base_url="https://www.amazon.in",
                source_type="marketplace",
                trust_rating=0.92,
            )
            session.add(amazon_in)
            await session.flush()

        rev_stmt = select(Reviewer).where(Reviewer.external_id == "tech_editor")
        reviewer = (await session.execute(rev_stmt)).scalar_one_or_none()
        if not reviewer:
            reviewer = Reviewer(
                id=uuid.uuid4(),
                external_id="tech_editor",
                name="Hardware Benchmark Lab",
                trust_score=0.95,
            )
            session.add(reviewer)
            await session.flush()

        # 4. Define Laptops Catalog
        laptops_data = [
            # --- Budget Gaming Laptops (Under ₹50,000) ---
            {
                "id": "c1000000-0000-0000-0000-000000000001",
                "title": "ASUS TUF Gaming F15 (Intel i5-11400H / RTX 2050 / 8GB / 512GB SSD)",
                "slug": "asus-tuf-gaming-f15-rtx2050",
                "model_number": "FX506HF-HN024W",
                "sku": "ASUS-TUF-F15-2050",
                "brand": "asus",
                "description": "Durable military-grade gaming laptop with 11th Gen Intel Core i5-11400H (6 cores/12 threads), 4GB NVIDIA GeForce RTX 2050 GPU, 8GB DDR4 RAM (expandable to 32GB), 512GB NVMe SSD, and 144Hz FHD IPS display.",
                "price": 49990.0,
                "currency": "INR",
                "specs": {
                    "processor": "Intel Core i5-11400H (6 cores, up to 4.5 GHz)",
                    "gpu": "NVIDIA GeForce RTX 2050 (4GB GDDR6, 70W TGP)",
                    "ram": "8GB DDR4 3200MHz",
                    "storage": "512GB PCIe 3.0 NVMe SSD",
                    "display": "15.6-inch FHD (1920x1080) 144Hz IPS Level",
                    "ports": "1x USB 3.2 Gen 2 Type-C (DisplayPort), 3x USB 3.2 Gen 1 Type-A, 1x HDMI 2.0b, 1x RJ45 LAN, 1x 3.5mm combo audio",
                    "battery": "48WHr 3-cell Li-ion",
                    "weight": "2.30 kg",
                },
                "review": "Best budget gaming laptop under 50k. Plays GTA V, Valorant, and CS2 smoothly above 100 FPS. Cooling fans get loud under sustained load but thermals remain well below 80C.",
            },
            {
                "id": "c1000000-0000-0000-0000-000000000002",
                "title": "Lenovo IdeaPad Gaming 3 (AMD Ryzen 5 5500H / RTX 2050 / 8GB / 512GB)",
                "slug": "lenovo-ideapad-gaming-3-5500h-rtx2050",
                "model_number": "15ACH6-82K2028YIN",
                "sku": "LNV-IPG3-2050",
                "brand": "lenovo",
                "description": "Affordable entry gaming and creative laptop powered by AMD Ryzen 5 5500H, dedicated NVIDIA RTX 2050 graphics, 8GB DDR4 RAM, 512GB NVMe M.2 SSD, 120Hz IPS display, and signature Lenovo soft-landing keyboard.",
                "price": 47990.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 5 5500H (4 cores/8 threads, up to 4.0 GHz)",
                    "gpu": "NVIDIA GeForce RTX 2050 (4GB GDDR6)",
                    "ram": "8GB DDR4 3200MHz",
                    "storage": "512GB SSD M.2 2242 PCIe 3.0x4 NVMe",
                    "display": "15.6-inch FHD (1920x1080) IPS 250nits Anti-glare, 120Hz",
                    "ports": "2x USB 3.2 Gen 1, 1x USB-C 3.2 Gen 1 (data transfer), 1x HDMI 2.0, 1x RJ45, 1x Headphone jack",
                    "battery": "45Wh, Rapid Charge Pro (50% in 30 mins)",
                    "weight": "2.25 kg",
                },
                "review": "Solid gaming performance under 50000 rupees. Upgraded to 16GB RAM for dual-channel boost. Clean thermals, comfortable keyboard, and reliable build quality.",
            },
            {
                "id": "c1000000-0000-0000-0000-000000000003",
                "title": "Acer Aspire 7 Gaming Laptop (Ryzen 5 5500U / RTX 2050 / 16GB / 512GB)",
                "slug": "acer-aspire-7-ryzen5-rtx2050-16gb",
                "model_number": "A715-43G",
                "sku": "ACR-ASP7-16GB",
                "brand": "acer",
                "description": "Stealth gaming and productivity laptop with 16GB RAM out of the box, AMD Ryzen 5 5500U, NVIDIA GeForce RTX 2050 GPU, 512GB SSD, Wi-Fi 6, and dual fans for quiet cooling.",
                "price": 49490.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 5 5500U (6 cores/12 threads, up to 4.0 GHz)",
                    "gpu": "NVIDIA GeForce RTX 2050 (4GB GDDR6)",
                    "ram": "16GB DDR4 Dual Channel",
                    "storage": "512GB PCIe NVMe SSD",
                    "display": "15.6-inch Full HD 144Hz LED-backlit TFT LCD",
                    "ports": "1x USB Type-C (USB 3.2 Gen 1), 2x USB 3.2 Gen 1, 1x USB 2.0, 1x HDMI, 1x RJ-45",
                    "battery": "50Wh Li-ion",
                    "weight": "2.15 kg",
                },
                "review": "Incredible value with 16GB RAM included under 50k. Handles 1080p gaming and programming workloads effortlessly.",
            },

            # --- Coding & Machine Learning Laptops (Under ₹80,000) ---
            {
                "id": "c1000000-0000-0000-0000-000000000004",
                "title": "ASUS Vivobook Pro 15 OLED (AMD Ryzen 7 5800H / RTX 3050 / 16GB / 512GB)",
                "slug": "asus-vivobook-pro-15-oled-ryzen7-rtx3050",
                "model_number": "M6500QC-HN741WS",
                "sku": "ASUS-VIVO-PRO15",
                "brand": "asus",
                "description": "Powerhouse laptop for software development, machine learning, and content creation. Features AMD Ryzen 7 5800H 8-core CPU, dedicated 4GB NVIDIA GeForce RTX 3050 GPU with CUDA acceleration for PyTorch/TensorFlow, 16GB RAM, 512GB SSD, and stunning 100% DCI-P3 display.",
                "price": 68990.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 7 5800H (8 cores/16 threads, 3.2 GHz up to 4.4 GHz, 16MB Cache)",
                    "gpu": "NVIDIA GeForce RTX 3050 (4GB GDDR6 with CUDA & Tensor Cores)",
                    "ram": "16GB DDR4 on board",
                    "storage": "512GB M.2 NVMe PCIe 3.0 SSD",
                    "display": "15.6-inch FHD (1920x1080) OLED 600nits peak, 100% DCI-P3, Pantone Validated",
                    "ports": "1x USB 3.2 Gen 1 Type-C, 1x USB 3.2 Gen 1 Type-A, 2x USB 2.0, 1x HDMI 1.4, 1x 3.5mm combo, Micro SD card reader",
                    "battery": "70WHrs 3-cell Li-ion",
                    "weight": "1.80 kg",
                },
                "review": "Exceptional coding and ML machine. Training PyTorch CNN models on the RTX 3050 with CUDA works out of the box. OLED display is gorgeous for long IDE sessions without eye strain.",
            },
            {
                "id": "c1000000-0000-0000-0000-000000000005",
                "title": "HP Victus Gaming Laptop 15 (AMD Ryzen 7 7735HS / RTX 3050 6GB / 16GB / 512GB)",
                "slug": "hp-victus-15-ryzen7-7735hs-rtx3050-6gb",
                "model_number": "15-fb1018AX",
                "sku": "HP-VIC15-7735",
                "brand": "hp",
                "description": "High-performance laptop equipped with 8-core AMD Ryzen 7 7735HS, updated 6GB NVIDIA RTX 3050 GPU (extra VRAM for larger ML model batch sizes), 16GB DDR5 4800MHz memory, 512GB Gen4 SSD, and upgraded dual-heatpipe cooling system.",
                "price": 74990.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 7 7735HS (8 cores/16 threads, up to 4.75 GHz, 16MB L3 cache)",
                    "gpu": "NVIDIA GeForce RTX 3050 (6GB GDDR6 dedicated VRAM)",
                    "ram": "16GB DDR5-4800 MHz RAM (2 x 8GB)",
                    "storage": "512GB PCIe Gen4 NVMe TLC M.2 SSD",
                    "display": "15.6-inch FHD 144Hz IPS micro-edge anti-glare",
                    "ports": "1x USB Type-C (5Gbps signaling rate, DisplayPort 1.4), 2x USB Type-A (5Gbps), 1x HDMI 2.1, 1x RJ-45, 1x Multi-format SD media card reader",
                    "battery": "70Wh 4-cell Li-ion polymer",
                    "weight": "2.29 kg",
                },
                "review": "The 6GB VRAM on this RTX 3050 makes a noticeable difference when running local LLMs and HuggingFace models. Thermals stay cool around 74C under heavy training scripts.",
            },
            {
                "id": "c1000000-0000-0000-0000-000000000006",
                "title": "Acer Nitro 5 (Intel Core i7-12650H / RTX 3050 / 16GB RAM / 512GB SSD)",
                "slug": "acer-nitro-5-i7-12650h-rtx3050",
                "model_number": "AN515-58",
                "sku": "ACR-NIT5-12650",
                "brand": "acer",
                "description": "Intense computing power with 10-core Intel Core i7-12650H processor (6 Performance + 4 Efficient cores), NVIDIA GeForce RTX 3050 GPU, 16GB DDR4 RAM, 512GB SSD, dual-fan cooling with quad exhaust ports, and CoolBoost technology.",
                "price": 77990.0,
                "currency": "INR",
                "specs": {
                    "processor": "Intel Core i7-12650H (10 cores, up to 4.7 GHz, 24MB Cache)",
                    "gpu": "NVIDIA GeForce RTX 3050 (4GB GDDR6, 95W Max TGP)",
                    "ram": "16GB DDR4 3200MHz (up to 32GB)",
                    "storage": "512GB PCIe NVMe SSD (dual M.2 slots)",
                    "display": "15.6-inch FHD 144Hz IPS display",
                    "ports": "1x Thunderbolt 4 / USB Type-C, 3x USB 3.2 Gen 2 Type-A, 1x HDMI 2.1, 1x RJ-45 Ethernet, 1x 3.5mm combo",
                    "battery": "57.5Wh 4-cell Li-ion",
                    "weight": "2.50 kg",
                },
                "review": "Raw CPU performance is unmatched in this price bracket. Compiles large C++ and Rust codebases in seconds. Dual fan quad-exhaust cooling keeps thermals remarkably steady.",
            },

            # --- RTX 4060 Laptops (> ₹50,000) ---
            {
                "id": "c1000000-0000-0000-0000-000000000007",
                "title": "Lenovo Legion Slim 5 (AMD Ryzen 7 7840HS / RTX 4060 8GB / 16GB / 1TB SSD)",
                "slug": "lenovo-legion-slim-5-ryzen7-rtx4060",
                "model_number": "16APH8-82Y9009JIN",
                "sku": "LNV-LEG-SLIM5-4060",
                "brand": "lenovo",
                "description": "Premium AI-tuned powerhouse featuring AMD Ryzen 7 7840HS processor with Ryzen AI, NVIDIA GeForce RTX 4060 8GB GDDR6 (140W Max TGP, DLSS 3, ray tracing), 16GB DDR5 5600MHz RAM, 1TB Gen4 SSD, and Legion Coldfront 5.0 thermal system.",
                "price": 98990.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 7 7840HS (8 cores/16 threads, 3.8 GHz up to 5.1 GHz)",
                    "gpu": "NVIDIA GeForce RTX 4060 (8GB GDDR6, 140W TGP, Boost Clock 2370MHz)",
                    "ram": "16GB DDR5-5600MHz (2x 8GB SO-DIMM)",
                    "storage": "1TB SSD M.2 2280 PCIe Gen4 NVMe",
                    "display": "16-inch WQXGA (2560x1600) IPS 300nits Anti-glare, 100% sRGB, 165Hz, G-SYNC",
                    "ports": "2x USB-C 3.2 Gen 2 (10Gbps, DisplayPort 1.4, 140W Power Delivery), 2x USB-A 3.2 Gen 2, 1x HDMI 2.1 (8K 60Hz), 1x 4-in-1 SD card reader, 1x RJ-45",
                    "battery": "80Wh with Super Rapid Charge Pro (80% in 30 mins)",
                    "weight": "2.40 kg",
                },
                "review": "Best RTX 4060 laptop on the market. The 140W TGP RTX 4060 runs Cyberpunk 2077 and Black Myth Wukong on Ultra with DLSS 3 Frame Gen at 90+ FPS. Coldfront 5.0 thermals are phenomenal.",
            },
            {
                "id": "c1000000-0000-0000-0000-000000000008",
                "title": "ASUS ROG Zephyrus G14 (AMD Ryzen 9 8945HS / RTX 4060 8GB / 16GB / 1TB OLED)",
                "slug": "asus-rog-zephyrus-g14-2024-rtx4060",
                "model_number": "GA403UV-QS084W",
                "sku": "ASUS-G14-4060-OLED",
                "brand": "asus",
                "description": "Ultraportable CNC aluminum marvel with AMD Ryzen 9 8945HS with AMD XDNA NPU (39 TOPS AI), 8GB NVIDIA GeForce RTX 4060, ROG Nebula Display 3K 120Hz OLED, 16GB LPDDR5X RAM, 1TB PCIe 4.0 SSD, and quad speakers with Dolby Atmos.",
                "price": 129990.0,
                "currency": "INR",
                "specs": {
                    "processor": "AMD Ryzen 9 8945HS (8 cores/16 threads, up to 5.2 GHz, 24MB Cache)",
                    "gpu": "NVIDIA GeForce RTX 4060 (8GB GDDR6, 90W TGP)",
                    "ram": "16GB LPDDR5X 6400MHz",
                    "storage": "1TB PCIe 4.0 NVMe M.2 SSD",
                    "display": "14.0-inch 3K (2880 x 1800) OLED 16:10 120Hz 0.2ms, 100% DCI-P3, G-SYNC",
                    "ports": "1x Type-C USB4 (DisplayPort/power delivery), 1x USB 3.2 Gen 2 Type-C, 2x USB 3.2 Gen 2 Type-A, 1x HDMI 2.1 FRL, 1x UHS-II MicroSD card reader, 1x 3.5mm combo audio",
                    "battery": "73WHrs 4-cell Li-ion",
                    "weight": "1.50 kg",
                },
                "review": "Premium craftsmanship in a 1.5kg chassis. The 3K OLED is stunning. Handles intense gaming and local AI inference with ease.",
            },

            # --- Visual Verification & Hardware Connectors (Dell XPS 15 9530) ---
            {
                "id": "c1000000-0000-0000-0000-000000000009",
                "title": "Dell XPS 15 9530 (Intel Core i7-13700H / Arc A370M / 16GB / 512GB SSD / OLED)",
                "slug": "dell-xps-15-9530-i7-13700h-oled",
                "model_number": "XPS 15 9530",
                "sku": "DELL-XPS15-9530",
                "brand": "dell",
                "description": "Flagship Dell XPS creator laptop with CNC machined aluminum and carbon fiber palm rest. Featuring Intel Core i7-13700H 14-core processor, dual Thunderbolt 4 physical ports, dedicated USB-C 3.2 Gen 2 with DisplayPort and Power Delivery, full-size SD Card reader v6.0, 3.5mm headphone/microphone audio jack, and included USB-C to USB-A v3.0 and HDMI v2.0 adapter dongle.",
                "price": 145000.0,
                "currency": "INR",
                "specs": {
                    "processor": "13th Gen Intel Core i7-13700H (14 cores/20 threads, up to 5.0 GHz, 24MB Cache)",
                    "gpu": "Intel Arc A370M (4GB GDDR6)",
                    "ram": "16GB DDR5 4800MHz (2x 8GB)",
                    "storage": "512GB M.2 PCIe NVMe SSD",
                    "display": "15.6-inch 3.5K (3456x2160) OLED InfinityEdge Touch, 400-nit, 100% DCI-P3",
                    "physical_ports": "2x Thunderbolt 4 (USB Type-C) with DisplayPort and Power Delivery, 1x USB-C 3.2 Gen 2 with DisplayPort and Power Delivery, 1x Full-size SD Card Reader v6.0, 1x 3.5mm Headphone/Microphone combo jack, 1x Wedge-shaped lock slot. In the box: USB-C to USB-A and HDMI adapter.",
                    "display_connectors": "Dual Thunderbolt 4 / DisplayPort 1.4 multi-stream transport, HDMI via adapter",
                    "battery": "86Wh 6-cell integrated",
                    "weight": "1.92 kg",
                },
                "review": "The build quality of the Dell XPS 15 is second to none. Physical ports include two high-speed Thunderbolt 4 ports on the left, an additional USB-C on the right, and a full-size high-speed SD card slot essential for photography. Clean port spacing and rock solid audio jack.",
            },

            # --- Apple Developer Workhorse ---
            {
                "id": "c1000000-0000-0000-0000-000000000010",
                "title": "Apple MacBook Air 13-inch (M2 chip / 16GB Unified Memory / 512GB SSD)",
                "slug": "apple-macbook-air-m2-16gb-512gb",
                "model_number": "MLXX3HN/A",
                "sku": "APL-MBA-M2-16",
                "brand": "apple",
                "description": "Redesigned ultrathin Apple MacBook Air powered by M2 chip with 8-core CPU and 10-core GPU, 16GB Unified Memory, 512GB fast SSD, MagSafe 3 dedicated charging port, two Thunderbolt / USB 4 ports, 13.6-inch Liquid Retina display, and up to 18 hours of battery life.",
                "price": 89900.0,
                "currency": "INR",
                "specs": {
                    "processor": "Apple M2 chip (8-core CPU with 4 performance cores and 4 efficiency cores, 16-core Neural Engine)",
                    "gpu": "10-core GPU, Hardware-accelerated ProRes",
                    "ram": "16GB Unified Memory",
                    "storage": "512GB SSD",
                    "display": "13.6-inch Liquid Retina display with True Tone, 500 nits, P3 wide color",
                    "ports": "MagSafe 3 charging port, 2x Thunderbolt / USB 4 ports (charging, DisplayPort, Thunderbolt 3 up to 40Gbps), 3.5mm headphone jack with advanced support for high-impedance headphones",
                    "battery": "52.6-watt-hour lithium-polymer, up to 18 hours Apple TV app movie playback",
                    "weight": "1.24 kg",
                },
                "review": "The benchmark laptop for developers. 18 hour battery life is real, 16GB unified memory handles Docker, VS Code, and dozens of browser tabs without throttling, and fanless silent design means zero noise.",
            },
        ]

        # 5. Insert/Update Products into Postgres
        print("\n--- Seeding Laptops into Postgres ---")
        for item in laptops_data:
            p_id = uuid.UUID(item["id"])
            stmt = select(Product).where(Product.id == p_id)
            prod = (await session.execute(stmt)).scalar_one_or_none()
            if not prod:
                prod = Product(
                    id=p_id,
                    title=item["title"],
                    slug=item["slug"],
                    model_number=item["model_number"],
                    sku=item["sku"],
                    description=item["description"],
                    status="active",
                    is_component=False,
                    category_id=laptop_cat.id,
                    brand_id=brand_map[item["brand"]].id,
                )
                session.add(prod)
                await session.flush()
                print(f"Created product: {prod.title}")
            else:
                prod.title = item["title"]
                prod.description = item["description"]
                prod.model_number = item["model_number"]
                prod.sku = item["sku"]

            # Add / update price
            price_stmt = select(Price).where(Price.product_id == p_id)
            existing_price = (await session.execute(price_stmt)).scalar_one_or_none()
            if not existing_price:
                price_obj = Price(
                    id=uuid.uuid4(),
                    product_id=p_id,
                    source_id=amazon_in.id,
                    amount=item["price"],
                    currency=item["currency"],
                )
                session.add(price_obj)
            else:
                existing_price.amount = item["price"]
                existing_price.currency = item["currency"]

            # Add specifications
            for k, v in item["specs"].items():
                spec_stmt = select(Specification).where(
                    Specification.product_id == p_id,
                    Specification.key == k,
                )
                spec_obj = (await session.execute(spec_stmt)).scalar_one_or_none()
                if not spec_obj:
                    spec_obj = Specification(
                        id=uuid.uuid4(),
                        product_id=p_id,
                        spec_group="General",
                        key=k,
                        value=str(v)[:250],
                    )
                    session.add(spec_obj)

            # Add review
            rev_check = select(Review).where(Review.product_id == p_id)
            rev_existing = (await session.execute(rev_check)).scalar_one_or_none()
            if not rev_existing:
                rev = Review(
                    id=uuid.uuid4(),
                    product_id=p_id,
                    reviewer_id=reviewer.id,
                    source_id=amazon_in.id,
                    rating=5,
                    title="Verified Editorial Review",
                    body=item["review"],
                    is_verified_purchase=True,
                    sentiment="positive",
                    fraud_score=0.01,
                )
                session.add(rev)

        await session.commit()
        print("Postgres laptop seeding successfully committed.")

    # 6. Synchronize into OpenSearch
    print("\n--- Synchronizing Laptops to OpenSearch ---")
    search = get_search_service()
    await search.connect()

    os_docs = []
    for item in laptops_data:
        os_docs.append({
            "id": item["id"],
            "title": item["title"],
            "slug": item["slug"],
            "description": item["description"],
            "model_number": item["model_number"],
            "sku": item["sku"],
            "brand": brand_names[item["brand"]][0],
            "category": "laptops-ultrabooks",
            "subcategory": "Laptops & Ultrabooks",
            "price": item["price"],
            "currency": item["currency"],
            "is_component": False,
            "specs": item["specs"],
        })

    indexed = await search.bulk_index("products", os_docs)
    print(f"Indexed {indexed} laptops directly into OpenSearch 'products' index.")


if __name__ == "__main__":
    asyncio.run(seed_laptops())
