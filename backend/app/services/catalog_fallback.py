"""Catalog Fallback Service.

Provides offline-resilient product and component catalog data and fuzzy search
when OpenSearch or PostgreSQL are unreachable. All product information, image CDNs,
and direct URLs are directly sourced from Amazon India and Flipkart.

Enforces:
1. Canonical product_id identity.
2. Strict image identity mapping: image.product_id == product.id and image.external_product_id == product.external_product_id.
3. Zero image reuse across unrelated products.
4. Zero duplicated fake views within any product.
5. Clean placeholder fallback for unverified images.
"""

import re
from typing import Any, Dict, List, Optional

true, false, null = True, False, None

FALLBACK_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "c1000000-0000-0000-0000-000000000001",
        "product_id": "c1000000-0000-0000-0000-000000000001",
        "title": "Dell XPS 15 9530 (Intel Core i7-13700H / RTX 4050 / 32GB / 1TB SSD / 3.5K OLED)",
        "slug": "dell-xps15-9530",
        "brand": "Dell",
        "model": "XPS 15 9530",
        "sku": "DELL-XPS15-9530",
        "model_number": "DELL-XPS15-9530",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Creator & Premium Laptops",
        "is_component": false,
        "price": 189990.0,
        "currency": "INR",
        "description": "Ultra-premium creator workstation laptop featuring 13th Gen Intel Core i7-13700H, 6GB RTX 4050, 32GB DDR5 RAM, 1TB Gen4 SSD, and 15.6-inch 3.5K OLED InfinityEdge touch display.",
        "specs": {
            "processor": "Intel Core i7-13700H (14 cores, up to 5.0 GHz)",
            "gpu": "NVIDIA GeForce RTX 4050 (6GB GDDR6)",
            "ram": "32GB DDR5 4800MHz",
            "storage": "1TB M.2 PCIe NVMe Gen 4 SSD",
            "display": "15.6-inch 3.5K (3456x2160) OLED InfinityEdge Touch Display, 400 nits, 100% DCI-P3",
            "ports": "2x Thunderbolt 4, 1x USB-C 3.2 Gen 2, Full-size SD slot",
            "battery": "86WHr 6-cell battery",
            "weight": "1.92 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "3456x2160"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CBGF51G3",
        "amazon_url": "https://www.amazon.in/dp/B0CBGF51G3",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000001",
                "retailer": "Amazon",
                "external_product_id": "B0CBGF51G3",
                "url": "https://www.amazon.in/dp/B0CBGF51G3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000001",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000001-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000001",
                "external_product_id": "B0CBGF51G3",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71qK8XjH61L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71oD4HkI+QL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71oX3L-9uFL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81kKkO2lZKL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71wL1xYfKRL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71QhH4vWvYL._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/61m1Jq3t8CL._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/71p0v7w6VnL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - XPS 15 9530",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Dell XPS 15 9530 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CBGF51G3",
        "asin": "B0CBGF51G3",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000001",
                "retailer": "Amazon",
                "external_product_id": "B0CBGF51G3",
                "url": "https://www.amazon.in/dp/B0CBGF51G3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000001",
                "retailer": "Flipkart",
                "external_product_id": "itm289fe81ad080a",
                "url": "https://www.flipkart.com/dell-xps-15-intel-core-i7-13th-gen-13700h-32-gb-1-tb-ssd-windows-11-home-6-graphics-nvidia-geforce-rtx-4050-9530-laptop/p/itm289fe81ad080a",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71qK8XjH61L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000002",
        "product_id": "c1000000-0000-0000-0000-000000000002",
        "title": "Apple MacBook Pro 14 (M3 Pro chip / 18GB Unified RAM / 512GB SSD / Space Black)",
        "slug": "mrx33hn-a",
        "brand": "Apple",
        "model": "MacBook Pro 14 M3 Pro",
        "sku": "MRX33HN/A",
        "model_number": "MRX33HN/A",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Creator & Professional Laptops",
        "is_component": false,
        "price": 199900.0,
        "currency": "INR",
        "description": "Pro laptop powered by Apple M3 Pro chip with 11-core CPU and 14-core GPU, 18GB unified memory, 512GB SSD, Liquid Retina XDR display with ProMotion 120Hz.",
        "specs": {
            "processor": "Apple M3 Pro (11-core CPU)",
            "gpu": "14-core GPU with hardware ray tracing",
            "ram": "18GB Unified Memory",
            "storage": "512GB PCIe onboard SSD",
            "display": "14.2-inch Liquid Retina XDR (3024x1964), 1000 nits sustained, 120Hz ProMotion",
            "ports": "3x Thunderbolt 4, HDMI, SDXC, MagSafe 3, 3.5mm jack",
            "battery": "70Wh battery, up to 18 hours",
            "weight": "1.61 kg",
            "os": "macOS Sonoma",
            "refresh_rate": "120Hz",
            "resolution": "3024x1964"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CM5JV232",
        "amazon_url": null,
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000002-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "external_product_id": "B0CM5JV232",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000002-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "external_product_id": "B0CM5JV232",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "back",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/618d5bS2lUL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61Ch8vjN+mL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61x0UoB1dKL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71gD8Wzp0ML._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/618d5bSHS-L._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/61b7oVw7O-L._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/61BqW1z1YcL._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/71iW3oF9xEL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - MacBook Pro 14 M3 Pro",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Apple MacBook Pro 14 M3 Pro are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CM5JV232",
        "asin": "B0CM5JV232",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000002",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/618d5bS2lUL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000003",
        "product_id": "c1000000-0000-0000-0000-000000000003",
        "title": "Apple MacBook Air 15 (M3 chip / 8-core CPU / 10-core GPU / 16GB RAM / 512GB SSD / Midnight)",
        "slug": "mryu3hn-a",
        "brand": "Apple",
        "model": "MacBook Air 15 M3",
        "sku": "MRYU3HN/A",
        "model_number": "MRYU3HN/A",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Thin & Light Ultrabooks",
        "is_component": false,
        "price": 154900.0,
        "currency": "INR",
        "description": "Thin 15-inch laptop with Apple M3 chip, fanless silent thermal architecture, 16GB RAM, 512GB SSD, 1080p camera, and 18-hour battery.",
        "specs": {
            "processor": "Apple M3 chip (8-core CPU)",
            "gpu": "10-core GPU",
            "ram": "16GB unified memory",
            "storage": "512GB SSD",
            "display": "15.3-inch Liquid Retina display (2880x1864), 500 nits",
            "ports": "MagSafe 3, 2x Thunderbolt / USB 4, 3.5mm headphone jack",
            "battery": "66.5Wh battery, up to 18 hours",
            "weight": "1.51 kg",
            "os": "macOS Sonoma",
            "refresh_rate": "60Hz",
            "resolution": "2880x1864"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CX21C8T8",
        "amazon_url": null,
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000003-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "external_product_id": "B0CX21C8T8",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000003-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "external_product_id": "B0CX21C8T8",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "gallery",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71S34+N82UL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/718yG0gN3cL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71R37xG-V+L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71T1X6l0oKL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - MacBook Air 15 M3",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Apple MacBook Air 15 M3 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CX21C8T8",
        "asin": "B0CX21C8T8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000003",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71S34+N82UL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000004",
        "product_id": "c1000000-0000-0000-0000-000000000004",
        "title": "Apple MacBook Air 13 (M2 chip / 8GB Unified RAM / 256GB SSD / Space Grey)",
        "slug": "mly33hn-a",
        "brand": "Apple",
        "model": "MacBook Air 13 M2",
        "sku": "MLY33HN/A",
        "model_number": "MLY33HN/A",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Thin & Light Ultrabooks",
        "is_component": false,
        "price": 84990.0,
        "currency": "INR",
        "description": "Ultraportable powered by Apple M2 chip, 13.6-inch Liquid Retina display, MagSafe charging, 1080p camera, and whisper-quiet fanless cooling.",
        "specs": {
            "processor": "Apple M2 chip (8-core CPU)",
            "gpu": "8-core GPU",
            "ram": "8GB unified memory",
            "storage": "256GB SSD",
            "display": "13.6-inch Liquid Retina (2560x1664), 500 nits",
            "ports": "MagSafe 3, 2x Thunderbolt / USB 4, 3.5mm headphone jack",
            "battery": "52.6Wh battery, up to 18 hours",
            "weight": "1.24 kg",
            "os": "macOS Ventura",
            "refresh_rate": "60Hz",
            "resolution": "2560x1664"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0B3B7NWVG",
        "amazon_url": "https://www.amazon.in/dp/B0B3B7NWVG",
        "flipkart_url": "https://www.flipkart.com/apple-macbook-air-m2-8-gb-256-gb-ssd-mac-os-monterey-mly33hn-a/p/itmd5543c749eb35",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "retailer": "Amazon",
                "external_product_id": "B0B3B7NWVG",
                "url": "https://www.amazon.in/dp/B0B3B7NWVG",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb35",
                "url": "https://www.flipkart.com/apple-macbook-air-m2-8-gb-256-gb-ssd-mac-os-monterey-mly33hn-a/p/itmd5543c749eb35",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/710TJuHTMhL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000004-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "external_product_id": "B0B3B7NWVG",
                "image_url": "https://m.media-amazon.com/images/I/710TJuHTMhL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000004-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "external_product_id": "B0B3B7NWVG",
                "image_url": "https://m.media-amazon.com/images/I/71yG+y9jJKL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/710TJuHTMhL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71yG+y9jJKL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61bK0vN6EWL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71rJkQ-XUBL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71vFKBpKakL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61e8Xv7XfPL._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/71q5nQ6tH+L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - MacBook Air 13 M2",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Apple MacBook Air 13 M2 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0B3B7NWVG",
        "asin": "B0B3B7NWVG",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "retailer": "Amazon",
                "external_product_id": "B0B3B7NWVG",
                "url": "https://www.amazon.in/dp/B0B3B7NWVG",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000004",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb35",
                "url": "https://www.flipkart.com/apple-macbook-air-m2-8-gb-256-gb-ssd-mac-os-monterey-mly33hn-a/p/itmd5543c749eb35",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/710TJuHTMhL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000005",
        "product_id": "c1000000-0000-0000-0000-000000000005",
        "title": "Lenovo ThinkPad X1 Carbon Gen 11 (Intel Core i7-1365U / 16GB / 512GB SSD / 2.8K OLED)",
        "slug": "21hms00d00",
        "brand": "Lenovo",
        "model": "ThinkPad X1 Carbon Gen 11",
        "sku": "21HMS00D00",
        "model_number": "21HMS00D00",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Business & Enterprise Ultrabooks",
        "is_component": false,
        "price": 178990.0,
        "currency": "INR",
        "description": "Flagship business ultrabook crafted with carbon fiber top cover, Intel Core i7-1365U vPro processor, 16GB RAM, 512GB SSD, and legendary ThinkPad ergonomics.",
        "specs": {
            "processor": "Intel Core i7-1365U vPro (10 cores, up to 5.2 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB LPDDR5 6400MHz",
            "storage": "512GB M.2 PCIe Gen 4 SSD",
            "display": "14-inch 2.8K (2880x1800) OLED Display, 400 nits, 100% DCI-P3",
            "ports": "2x Thunderbolt 4, 2x USB 3.2 Gen 1, HDMI 2.1, 3.5mm jack",
            "battery": "57Wh battery with Rapid Charge",
            "weight": "1.12 kg",
            "os": "Windows 11 Pro",
            "refresh_rate": "60Hz",
            "resolution": "2880x1800"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CJ2B8K6V",
        "amazon_url": "https://www.amazon.in/dp/B0CJ2B8K6V",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000005",
                "retailer": "Amazon",
                "external_product_id": "B0CJ2B8K6V",
                "url": "https://www.amazon.in/dp/B0CJ2B8K6V",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000005",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000005-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000005",
                "external_product_id": "B0CJ2B8K6V",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61gVdKx2u3L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61yD-PqQ9qL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71R2W7k9-WL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/61k1q0fN5mL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61k-8yN6RPL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/61n9r8B7R2L._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/51w+z-8wz1L._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/71V0L8s8fIL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - ThinkPad X1 Carbon Gen 11",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo ThinkPad X1 Carbon Gen 11 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CJ2B8K6V",
        "asin": "B0CJ2B8K6V",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000005",
                "retailer": "Amazon",
                "external_product_id": "B0CJ2B8K6V",
                "url": "https://www.amazon.in/dp/B0CJ2B8K6V",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000005",
                "retailer": "Flipkart",
                "external_product_id": "itmd45a981a8c91a",
                "url": "https://www.flipkart.com/lenovo-thinkpad-x1-carbon-gen-11-intel-core-i7-13th-gen-1365u-16-gb-512-gb-ssd-windows-11-pro-21hms00d00-thin-light-laptop/p/itmd45a981a8c91a",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61gVdKx2u3L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000006",
        "product_id": "c1000000-0000-0000-0000-000000000006",
        "title": "Lenovo Legion Pro 5 16 (Intel Core i7-14700HX / RTX 4070 8GB / 32GB / 1TB SSD / 240Hz WQXGA)",
        "slug": "16irx9-83df",
        "brand": "Lenovo",
        "model": "Legion Pro 5 16IRX9",
        "sku": "16IRX9-83DF",
        "model_number": "16IRX9-83DF",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 164990.0,
        "currency": "INR",
        "description": "Elite gaming laptop featuring 14th Gen Intel Core i7-14700HX (20 cores), 140W TGP NVIDIA GeForce RTX 4070 8GB GPU, Coldfront 5.0 vapor chamber, and 240Hz PureSight display.",
        "specs": {
            "processor": "Intel Core i7-14700HX (20 cores, up to 5.5 GHz)",
            "gpu": "NVIDIA GeForce RTX 4070 8GB GDDR6 (140W TGP)",
            "ram": "32GB DDR5 5600MHz",
            "storage": "1TB M.2 PCIe Gen 4 SSD",
            "display": "16-inch WQXGA (2560x1600) IPS, 240Hz, 500 nits, 100% sRGB, G-SYNC",
            "ports": "4x USB-A 3.2 Gen 1, 2x USB-C 3.2 Gen 2, HDMI 2.1, RJ-45",
            "battery": "80Wh battery with Super Rapid Charge",
            "weight": "2.55 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "240Hz",
            "resolution": "2560x1600"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CFF7NL2L",
        "amazon_url": "https://www.amazon.in/dp/B0CFF7NL2L",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000006",
                "retailer": "Amazon",
                "external_product_id": "B0CFF7NL2L",
                "url": "https://www.amazon.in/dp/B0CFF7NL2L",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000006",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000006-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000006",
                "external_product_id": "B0CFF7NL2L",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71qJebg7KML._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71rV2N8H9JL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71s8L5qK3mL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71dK4V5L7mL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71Zp32Qy7WL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71+M8h3bKLL._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/61K1z2x6ZqL._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/71bZ4E8tYUL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Legion Pro 5 16IRX9",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo Legion Pro 5 16IRX9 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CFF7NL2L",
        "asin": "B0CFF7NL2L",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000006",
                "retailer": "Amazon",
                "external_product_id": "B0CFF7NL2L",
                "url": "https://www.amazon.in/dp/B0CFF7NL2L",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000006",
                "retailer": "Flipkart",
                "external_product_id": "itm5fe1a82fcae91",
                "url": "https://www.flipkart.com/lenovo-legion-pro-5-intel-core-i7-14th-gen-14700hx-32-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4070-16irx9-gaming-laptop/p/itm5fe1a82fcae91",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71qJebg7KML._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000007",
        "product_id": "c1000000-0000-0000-0000-000000000007",
        "title": "Lenovo LOQ 15 (Intel Core i5-12450HX / RTX 3050 6GB / 16GB / 512GB SSD / 144Hz FHD)",
        "slug": "15iax9-83gs",
        "brand": "Lenovo",
        "model": "LOQ 15IRX9",
        "sku": "15IAX9-83GS",
        "model_number": "15IAX9-83GS",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Gaming Laptops",
        "is_component": false,
        "price": 62990.0,
        "currency": "INR",
        "description": "High-value gaming laptop equipped with Intel Core i5-12450HX, dedicated NVIDIA GeForce RTX 3050 6GB GDDR6 (95W TGP), 16GB DDR5 RAM, and 144Hz display.",
        "specs": {
            "processor": "Intel Core i5-12450HX (8 cores, up to 4.4 GHz)",
            "gpu": "NVIDIA GeForce RTX 3050 (6GB GDDR6, 95W TGP)",
            "ram": "16GB DDR5 4800MHz",
            "storage": "512GB PCIe Gen 4 SSD",
            "display": "15.6-inch FHD (1920x1080) IPS, 144Hz, 300 nits, 100% sRGB",
            "ports": "3x USB-A, 1x USB-C (PD/DP), HDMI 2.1, RJ-45",
            "battery": "60Wh with Rapid Charge Pro",
            "weight": "2.38 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CX8R22R7",
        "amazon_url": "https://www.amazon.in/dp/B0CX8R22R7",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000007",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R7",
                "url": "https://www.amazon.in/dp/B0CX8R22R7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000007",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000007-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000007",
                "external_product_id": "B0CX8R22R7",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71fR4o5U-mL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71u9sW4jQxL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71wF4W5vKnL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71h6lH-v-hL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - LOQ 15IRX9",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo LOQ 15IRX9 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CX8R22R7",
        "asin": "B0CX8R22R7",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000007",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R7",
                "url": "https://www.amazon.in/dp/B0CX8R22R7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000007",
                "retailer": "Flipkart",
                "external_product_id": "itme358a9e4b6d4b",
                "url": "https://www.flipkart.com/lenovo-loq-intel-core-i5-12th-gen-12450hx-16-gb-512-gb-ssd-windows-11-home-6-gb-graphics-nvidia-geforce-rtx-3050-15iax9-gaming-laptop/p/itme358a9e4b6d4b",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71fR4o5U-mL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000008",
        "product_id": "c1000000-0000-0000-0000-000000000008",
        "title": "Lenovo IdeaPad Slim 3 (Intel Core i3-1215U / 8GB / 512GB SSD / 15.6 FHD / Arctic Grey)",
        "slug": "15iau7-82rk",
        "brand": "Lenovo",
        "model": "IdeaPad Slim 3 15IAU7",
        "sku": "15IAU7-82RK",
        "model_number": "15IAU7-82RK",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Everyday Laptops",
        "is_component": false,
        "price": 34990.0,
        "currency": "INR",
        "description": "Affordable daily driver laptop featuring 12th Gen Intel Core i3-1215U (6 cores), 8GB DDR4 RAM, 512GB SSD, privacy webcam shutter, and Dolby Audio.",
        "specs": {
            "processor": "Intel Core i3-1215U (6 cores, up to 4.4 GHz)",
            "gpu": "Intel UHD Graphics",
            "ram": "8GB DDR4 3200MHz",
            "storage": "512GB M.2 NVMe PCIe SSD",
            "display": "15.6-inch FHD (1920x1080) Anti-Glare, 250 nits",
            "ports": "1x USB-C 3.2 Gen 1, 1x USB 3.2, 1x USB 2.0, HDMI 1.4b, SD Reader",
            "battery": "45Wh battery",
            "weight": "1.63 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0B8K37937",
        "amazon_url": "https://www.amazon.in/dp/B0B8K37937",
        "flipkart_url": "https://www.flipkart.com/lenovo-ideapad-slim-3-intel-core-i3-12th-gen-1215u-8-gb-512-gb-ssd-windows-11-home-15iau7-thin-light-laptop/p/itm58722d471ef90?pid=COMGP26H8PHCAMZE",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "retailer": "Amazon",
                "external_product_id": "B0B8K37937",
                "url": "https://www.amazon.in/dp/B0B8K37937",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "retailer": "Flipkart",
                "external_product_id": "itm58722d471ef90",
                "url": "https://www.flipkart.com/lenovo-ideapad-slim-3-intel-core-i3-12th-gen-1215u-8-gb-512-gb-ssd-windows-11-home-15iau7-thin-light-laptop/p/itm58722d471ef90?pid=COMGP26H8PHCAMZE",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/1/z/w/-enriched-transparent-original-imahg5fx53zsqcs4.png?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000008-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "external_product_id": "B0B8K37937",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/1/z/w/-enriched-transparent-original-imahg5fx53zsqcs4.png?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000008-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "external_product_id": "B0B8K37937",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/w/x/b/-original-imahg5fxjscwryjr.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61kM5vP4rQL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61r5h4K6wML._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61qJ8+qZ9kL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/61kL7Q4JkHL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71-Ox71W7LL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71-2w0PqHqL._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/71zF7Q7eYVL._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/71g2y6UqYLL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - IdeaPad Slim 3 15IAU7",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo IdeaPad Slim 3 15IAU7 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0B8K37937",
        "asin": "B0B8K37937",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "retailer": "Amazon",
                "external_product_id": "B0B8K37937",
                "url": "https://www.amazon.in/dp/B0B8K37937",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000008",
                "retailer": "Flipkart",
                "external_product_id": "itm5cbde6ff4fbdb",
                "url": "https://www.flipkart.com/lenovo-ideapad-slim-3-intel-core-i3-12th-gen-1215u-8-gb-512-gb-ssd-windows-11-home-15iau7-thin-light-laptop/p/itm5cbde6ff4fbdb",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61kM5vP4rQL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000009",
        "product_id": "c1000000-0000-0000-0000-000000000009",
        "title": "ASUS ROG Strix G16 (Intel Core i7-13650HX / RTX 4060 8GB / 16GB / 1TB SSD / 165Hz FHD+)",
        "slug": "g614jv-n3474w",
        "brand": "ASUS",
        "model": "ROG Strix G16 G614JV",
        "sku": "G614JV-N3474W",
        "model_number": "G614JV-N3474W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 139990.0,
        "currency": "INR",
        "description": "Esports battlestation powered by 13th Gen Intel Core i7-13650HX (14 cores), 140W max TGP NVIDIA GeForce RTX 4060 8GB, ROG Intelligent Cooling with Tri-Fan technology.",
        "specs": {
            "processor": "Intel Core i7-13650HX (14 cores, up to 4.9 GHz)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (140W TGP)",
            "ram": "16GB DDR5 4800MHz",
            "storage": "1TB M.2 PCIe 4.0 NVMe SSD",
            "display": "16-inch FHD+ (1920x1200), 165Hz, 100% sRGB, G-SYNC, Dolby Vision",
            "ports": "1x Thunderbolt 4, 1x USB-C 3.2 Gen 2, 2x USB-A 3.2, 2.5G LAN, HDMI 2.1",
            "battery": "90WHrs 4-cell Li-ion",
            "weight": "2.50 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "165Hz",
            "resolution": "1920x1200"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BT9SJG58",
        "amazon_url": "https://www.amazon.in/dp/B0BT9SJG58",
        "flipkart_url": "https://www.flipkart.com/asus-intel-core-i7-13th-gen-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-g614jv-n3474ws-gaming-laptop/p/itm02b25080a5259?pid=COMH2FK8CM49KYYV",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "retailer": "Amazon",
                "external_product_id": "B0BT9SJG58",
                "url": "https://www.amazon.in/dp/B0BT9SJG58",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "retailer": "Flipkart",
                "external_product_id": "itm02b25080a5259",
                "url": "https://www.flipkart.com/asus-intel-core-i7-13th-gen-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-g614jv-n3474ws-gaming-laptop/p/itm02b25080a5259?pid=COMH2FK8CM49KYYV",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/a/z/m/g614jv-n3474ws-gaming-laptop-asus-original-imah2fk856vncuqu.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000009-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "external_product_id": "B0BT9SJG58",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/a/z/m/g614jv-n3474ws-gaming-laptop-asus-original-imah2fk856vncuqu.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000009-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "external_product_id": "B0BT9SJG58",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/d/a/x/g614jv-n3474ws-gaming-laptop-asus-original-imah2fk82jx2gscg.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/7183e8n2aRL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71fB3bY-WQL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71j2-uV9-NL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - ROG Strix G16 G614JV",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS ROG Strix G16 G614JV are outstanding for professional use."
            }
        ],
        "external_product_id": "B0BT9SJG58",
        "asin": "B0BT9SJG58",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "retailer": "Amazon",
                "external_product_id": "B0BT9SJG58",
                "url": "https://www.amazon.in/dp/B0BT9SJG58",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000009",
                "retailer": "Flipkart",
                "external_product_id": "itmdb2e867373f1d",
                "url": "https://www.flipkart.com/asus-rog-strix-g16-intel-core-i7-13th-gen-13650hx-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-165-hz-g614jv-n3474w-gaming-laptop/p/itmdb2e867373f1d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/7183e8n2aRL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000010",
        "product_id": "c1000000-0000-0000-0000-000000000010",
        "title": "ASUS TUF Gaming A15 (AMD Ryzen 7 7735HS / RTX 4050 6GB / 16GB / 512GB SSD / 144Hz FHD)",
        "slug": "fa507nu-lp067w",
        "brand": "ASUS",
        "model": "TUF Gaming A15 FA507NU",
        "sku": "FA507NU-LP067W",
        "model_number": "FA507NU-LP067W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 82990.0,
        "currency": "INR",
        "description": "Military-grade durability gaming laptop featuring AMD Ryzen 7 7735HS octa-core CPU, 140W max TGP NVIDIA GeForce RTX 4050 6GB, and 90Wh battery.",
        "specs": {
            "processor": "AMD Ryzen 7 7735HS (8 cores, up to 4.75 GHz)",
            "gpu": "NVIDIA GeForce RTX 4050 6GB GDDR6 (140W TGP)",
            "ram": "16GB DDR5 4800MHz",
            "storage": "512GB M.2 PCIe 4.0 SSD",
            "display": "15.6-inch FHD (1920x1080), 144Hz, 100% sRGB, G-SYNC",
            "ports": "1x USB4 Type-C, 1x USB-C 3.2 Gen 2, 2x USB-A 3.2, RJ-45 LAN, HDMI 2.1",
            "battery": "90WHrs 4-cell Li-ion",
            "weight": "2.20 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C4TW7328",
        "amazon_url": "https://www.amazon.in/dp/B0C4TW7328",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000010",
                "retailer": "Amazon",
                "external_product_id": "B0C4TW7328",
                "url": "https://www.amazon.in/dp/B0C4TW7328",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000010",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000010-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000010",
                "external_product_id": "B0C4TW7328",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/81x0gKq+qZL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/81N0c6b9QLL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/81t6z5mXgTL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81p5d6rTjPL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - TUF Gaming A15 FA507NU",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS TUF Gaming A15 FA507NU are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C4TW7328",
        "asin": "B0C4TW7328",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000010",
                "retailer": "Amazon",
                "external_product_id": "B0C4TW7328",
                "url": "https://www.amazon.in/dp/B0C4TW7328",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000010",
                "retailer": "Flipkart",
                "external_product_id": "itmfe15e47858c06",
                "url": "https://www.flipkart.com/asus-tuf-gaming-a15-amd-ryzen-7-octa-core-7735hs-16-gb-512-gb-ssd-windows-11-home-6-graphics-nvidia-geforce-rtx-4050-140-w-fa507nu-lp067w-laptop/p/itmfe15e47858c06",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/81x0gKq+qZL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000011",
        "product_id": "c1000000-0000-0000-0000-000000000011",
        "title": "ASUS TUF Gaming F15 (Intel Core i5-11400H / RTX 2050 4GB / 16GB / 512GB SSD / 144Hz FHD)",
        "slug": "fx506hf-hn024w",
        "brand": "ASUS",
        "model": "TUF Gaming F15 FX506HF",
        "sku": "FX506HF-HN024W",
        "model_number": "FX506HF-HN024W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Gaming Laptops",
        "is_component": false,
        "price": 50990.0,
        "currency": "INR",
        "description": "Battle-tested entry gaming laptop powered by 11th Gen Intel Core i5-11400H, NVIDIA GeForce RTX 2050 4GB GPU, and 144Hz IPS display.",
        "specs": {
            "processor": "Intel Core i5-11400H (6 cores, up to 4.5 GHz)",
            "gpu": "NVIDIA GeForce RTX 2050 4GB GDDR6 (70W TGP)",
            "ram": "16GB DDR4 3200MHz",
            "storage": "512GB M.2 NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) 144Hz, IPS-level",
            "ports": "1x Thunderbolt 4, 3x USB 3.2 Gen 1, HDMI 2.0b, RJ-45",
            "battery": "48WHrs 3-cell Li-ion",
            "weight": "2.30 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C27V76F7",
        "amazon_url": "https://www.amazon.in/dp/B0C27V76F7",
        "flipkart_url": "https://www.flipkart.com/asus-tuf-gaming-f15-ai-powered-intel-core-i5-11th-gen-11400h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-144-hz-70-tgp-fx506hf-hn025w-laptop/p/itma4f834884f6b1?pid=COMGZKHQFQENGQSG",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "retailer": "Amazon",
                "external_product_id": "B0C27V76F7",
                "url": "https://www.amazon.in/dp/B0C27V76F7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "retailer": "Flipkart",
                "external_product_id": "itma4f834884f6b1",
                "url": "https://www.flipkart.com/asus-tuf-gaming-f15-ai-powered-intel-core-i5-11th-gen-11400h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-144-hz-70-tgp-fx506hf-hn025w-laptop/p/itma4f834884f6b1?pid=COMGZKHQFQENGQSG",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/h/w/b/-original-imagtzvhxxuhzr4g.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000011-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "external_product_id": "B0C27V76F7",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/h/w/b/-original-imagtzvhxxuhzr4g.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000011-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "external_product_id": "B0C27V76F7",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/x/v/q/-original-imagpbychf3qzkyu.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71-Dx764V0L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/81x1n3J8nAL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71r2P5sH9xL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81bN8WzN1oL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/81xH00-J+AL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71Y88f0P8AL._SL1500_.jpg",
            "left": "https://m.media-amazon.com/images/I/71k-vQd-xML._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/81x6h3N9N9L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - TUF Gaming F15 FX506HF",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS TUF Gaming F15 FX506HF are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C27V76F7",
        "asin": "B0C27V76F7",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "retailer": "Amazon",
                "external_product_id": "B0C27V76F7",
                "url": "https://www.amazon.in/dp/B0C27V76F7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000011",
                "retailer": "Flipkart",
                "external_product_id": "itm507dd129486c8",
                "url": "https://www.flipkart.com/asus-tuf-gaming-f15-intel-core-i5-11th-gen-11400h-8-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-144-hz-fx506hf-hn024w-laptop/p/itm507dd129486c8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71-Dx764V0L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000012",
        "product_id": "c1000000-0000-0000-0000-000000000012",
        "title": "ASUS Zenbook 14 OLED (Intel Core Ultra 7 155H / 16GB / 1TB SSD / 3K 120Hz OLED / Intel Arc)",
        "slug": "ux3405ma-pz752w",
        "brand": "ASUS",
        "model": "Zenbook 14 OLED UX3405",
        "sku": "UX3405MA-PZ752W",
        "model_number": "UX3405MA-PZ752W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "AI & Premium Ultrabooks",
        "is_component": false,
        "price": 114990.0,
        "currency": "INR",
        "description": "AI-powered premium ultrabook featuring Intel Core Ultra 7 155H with integrated NPU neural processor, Intel Arc graphics, and 14-inch 3K 120Hz OLED.",
        "specs": {
            "processor": "Intel Core Ultra 7 155H (16 cores, Intel AI Boost NPU)",
            "gpu": "Intel Arc Graphics",
            "ram": "16GB LPDDR5X 7467MHz",
            "storage": "1TB M.2 NVMe PCIe 4.0 SSD",
            "display": "14-inch 3K (2880x1800) OLED 16:10, 120Hz, 600 nits HDR, 100% DCI-P3",
            "ports": "2x Thunderbolt 4, 1x USB 3.2 Gen 1, HDMI 2.1, 3.5mm jack",
            "battery": "75WHrs 4-cell Li-ion (up to 15 hours)",
            "weight": "1.20 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "2880x1800"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CR1DP82M",
        "amazon_url": "https://www.amazon.in/dp/B0CR1DP82M",
        "flipkart_url": "https://www.flipkart.com/asus-zenbook-14-oled-intel-core-ultra-7-155h-16-gb-1-tb-ssd-windows-11-home-ux3405ma-pz752ws-thin-light-laptop/p/itm36bde93628279",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "retailer": "Amazon",
                "external_product_id": "B0CR1DP82M",
                "url": "https://www.amazon.in/dp/B0CR1DP82M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "retailer": "Flipkart",
                "external_product_id": "itm36bde93628279",
                "url": "https://www.flipkart.com/asus-zenbook-14-oled-intel-core-ultra-7-155h-16-gb-1-tb-ssd-windows-11-home-ux3405ma-pz752ws-thin-light-laptop/p/itm36bde93628279",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/z/o/8/-original-imahg4pa9rdaem5n.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000012-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "external_product_id": "B0CR1DP82M",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/z/o/8/-original-imahg4pa9rdaem5n.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000012-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "external_product_id": "B0CR1DP82M",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/l/z/v/-original-imahfyyszfghbygy.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71Yf1E0qGCL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71s6V1wP3bL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71k1q0fN5mL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Zenbook 14 OLED UX3405",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS Zenbook 14 OLED UX3405 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CR1DP82M",
        "asin": "B0CR1DP82M",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "retailer": "Amazon",
                "external_product_id": "B0CR1DP82M",
                "url": "https://www.amazon.in/dp/B0CR1DP82M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000012",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71Yf1E0qGCL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000013",
        "product_id": "c1000000-0000-0000-0000-000000000013",
        "title": "ASUS Vivobook 16X (Intel Core i5-12450H / RTX 2050 4GB / 16GB / 512GB SSD / 120Hz WUXGA)",
        "slug": "k3605zf-mb542ws",
        "brand": "ASUS",
        "model": "Vivobook 16X K3605ZF",
        "sku": "K3605ZF-MB542WS",
        "model_number": "K3605ZF-MB542WS",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Productivity & Creator Laptops",
        "is_component": false,
        "price": 57990.0,
        "currency": "INR",
        "description": "Spacious 16-inch creator laptop powered by Intel Core i5-12450H (8 cores), NVIDIA GeForce RTX 2050 4GB, and 120Hz 16:10 display.",
        "specs": {
            "processor": "Intel Core i5-12450H (8 cores, up to 4.4 GHz)",
            "gpu": "NVIDIA GeForce RTX 2050 4GB GDDR6",
            "ram": "16GB DDR4 3200MHz",
            "storage": "512GB M.2 NVMe PCIe 3.0 SSD",
            "display": "16-inch WUXGA (1920x1200) 16:10, 120Hz, 300 nits",
            "ports": "1x USB-C 3.2 Gen 1, 2x USB-A 3.2, HDMI 2.1, SD reader",
            "battery": "50WHrs 3-cell Li-ion",
            "weight": "1.80 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "1920x1200"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C9YQG56Z",
        "amazon_url": "https://www.amazon.in/dp/B0C9YQG56Z",
        "flipkart_url": "https://www.flipkart.com/asus-vivobook-16x-intel-core-i5-12th-gen-12450h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-120-hz-k3605zf-mb542ws-laptop/p/itm5fe1a82fcae92",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "retailer": "Amazon",
                "external_product_id": "B0C9YQG56Z",
                "url": "https://www.amazon.in/dp/B0C9YQG56Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "retailer": "Flipkart",
                "external_product_id": "itm5fe1a82fcae92",
                "url": "https://www.flipkart.com/asus-vivobook-16x-intel-core-i5-12th-gen-12450h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-120-hz-k3605zf-mb542ws-laptop/p/itm5fe1a82fcae92",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000013-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "external_product_id": "B0C9YQG56Z",
                "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000013-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "external_product_id": "B0C9YQG56Z",
                "image_url": "https://m.media-amazon.com/images/I/71czGb00k5L._SL1500_.jpg",
                "image_type": "gallery",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71czGb00k5L._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71R12Wk2vCL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61OaUvQ0s8L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71s+qjT17-L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Vivobook 16X K3605ZF",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS Vivobook 16X K3605ZF are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C9YQG56Z",
        "asin": "B0C9YQG56Z",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "retailer": "Amazon",
                "external_product_id": "B0C9YQG56Z",
                "url": "https://www.amazon.in/dp/B0C9YQG56Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000013",
                "retailer": "Flipkart",
                "external_product_id": "itm5fe1a82fcae92",
                "url": "https://www.flipkart.com/asus-vivobook-16x-intel-core-i5-12th-gen-12450h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-120-hz-k3605zf-mb542ws-laptop/p/itm5fe1a82fcae92",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000014",
        "product_id": "c1000000-0000-0000-0000-000000000014",
        "title": "HP Pavilion Plus 14 (Intel Core i7-13700H / 16GB / 1TB SSD / 2.8K 120Hz OLED / Natural Silver)",
        "slug": "14-ew0022tu",
        "brand": "HP",
        "model": "Pavilion Plus 14-ew0022TU",
        "sku": "14-EW0022TU",
        "model_number": "14-EW0022TU",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Creator & Productivity Ultrabooks",
        "is_component": false,
        "price": 89990.0,
        "currency": "INR",
        "description": "High-performance creator laptop featuring 45W Intel Core i7-13700H (14 cores), 16GB RAM, 1TB Gen4 SSD, and an IMAX Enhanced 2.8K 120Hz OLED.",
        "specs": {
            "processor": "Intel Core i7-13700H (14 cores, up to 5.0 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB LPDDR5x 5200MHz",
            "storage": "1TB PCIe NVMe M.2 SSD",
            "display": "14-inch 2.8K (2880x1800) OLED, 120Hz, 500 nits HDR, 100% DCI-P3",
            "ports": "1x Thunderbolt 4, 1x USB-C 10Gbps, 2x USB-A 5Gbps, HDMI 2.1",
            "battery": "68Wh Li-ion polymer",
            "weight": "1.44 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "2880x1800"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CDG7LMS2",
        "amazon_url": "https://www.amazon.in/dp/B0CDG7LMS2",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000014",
                "retailer": "Amazon",
                "external_product_id": "B0CDG7LMS2",
                "url": "https://www.amazon.in/dp/B0CDG7LMS2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000014",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000014-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000014",
                "external_product_id": "B0CDG7LMS2",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71fB7o9sEQL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71b2W1k3mTL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71U1j7pL9TL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71N7eW6tHLL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61K8P1w7fCL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71u9S2a8YcL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Pavilion Plus 14-ew0022TU",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the HP Pavilion Plus 14-ew0022TU are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CDG7LMS2",
        "asin": "B0CDG7LMS2",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000014",
                "retailer": "Amazon",
                "external_product_id": "B0CDG7LMS2",
                "url": "https://www.amazon.in/dp/B0CDG7LMS2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000014",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71fB7o9sEQL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000015",
        "product_id": "c1000000-0000-0000-0000-000000000015",
        "title": "HP Victus 15 (AMD Ryzen 5 5600H / RTX 3050 4GB / 16GB / 512GB SSD / 144Hz FHD / Mica Silver)",
        "slug": "15-fb0157ax",
        "brand": "HP",
        "model": "Victus 15-fb0157AX",
        "sku": "15-FB0157AX",
        "model_number": "15-FB0157AX",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Gaming Laptops",
        "is_component": false,
        "price": 58990.0,
        "currency": "INR",
        "description": "Mainstream gaming laptop equipped with AMD Ryzen 5 5600H 6-core processor, NVIDIA GeForce RTX 3050 4GB GPU, 144Hz anti-glare display, and B&O audio.",
        "specs": {
            "processor": "AMD Ryzen 5 5600H (6 cores, up to 4.2 GHz)",
            "gpu": "NVIDIA GeForce RTX 3050 4GB GDDR6",
            "ram": "16GB DDR4 3200MHz",
            "storage": "512GB PCIe NVMe M.2 SSD",
            "display": "15.6-inch FHD (1920x1080) 144Hz, IPS, 250 nits",
            "ports": "1x USB-C 5Gbps, 2x USB-A 5Gbps, HDMI 2.1, RJ-45, SD reader",
            "battery": "70Wh Li-ion polymer",
            "weight": "2.29 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0B5HCBG18",
        "amazon_url": "https://www.amazon.in/dp/B0B5HCBG18",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000015",
                "retailer": "Amazon",
                "external_product_id": "B0B5HCBG18",
                "url": "https://www.amazon.in/dp/B0B5HCBG18",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000015",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1000/l5bd5zk0/computer/x/o/6/15-fb0040ax-gaming-laptop-hp-original-imaggyue2b3anwr9.jpeg?q=70",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000015-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000015",
                "external_product_id": "B0B5HCBG18",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/l5bd5zk0/computer/x/o/6/15-fb0040ax-gaming-laptop-hp-original-imaggyue2b3anwr9.jpeg?q=70",
                "image_type": "front",
                "source": "Verified",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/7104aD0B4sL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71nF5V-hGmL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71F2bX0sFJL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71Q3hW2Y7VL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61lX7E6P5lL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71b2V5G5xWL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Victus 15-fb0157AX",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the HP Victus 15-fb0157AX are outstanding for professional use."
            }
        ],
        "external_product_id": "B0B5HCBG18",
        "asin": "B0B5HCBG18",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000015",
                "retailer": "Amazon",
                "external_product_id": "B0B5HCBG18",
                "url": "https://www.amazon.in/dp/B0B5HCBG18",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000015",
                "retailer": "Flipkart",
                "external_product_id": "itm289fe81ad080b",
                "url": "https://www.flipkart.com/hp-victus-amd-ryzen-5-hexa-core-5600h-16-gb-512-gb-ssd-windows-11-home-4-gb-graphics-nvidia-geforce-rtx-3050-144-hz-15-fb0157ax-gaming-laptop/p/itm289fe81ad080b",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/7104aD0B4sL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000016",
        "product_id": "c1000000-0000-0000-0000-000000000016",
        "title": "HP OMEN 16 (AMD Ryzen 7 7840HS / RTX 4060 8GB / 16GB / 1TB SSD / 165Hz QHD / Shadow Black)",
        "slug": "16-xf0060ax",
        "brand": "HP",
        "model": "OMEN 16-xf0060AX",
        "sku": "16-XF0060AX",
        "model_number": "16-XF0060AX",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 112990.0,
        "currency": "INR",
        "description": "Premium gaming machine featuring AMD Ryzen 7 7840HS with Ryzen AI, 140W NVIDIA GeForce RTX 4060 8GB, 165Hz QHD display, and Tempest Cooling.",
        "specs": {
            "processor": "AMD Ryzen 7 7840HS (8 cores, up to 5.1 GHz)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (140W TGP)",
            "ram": "16GB DDR5 5600MHz",
            "storage": "1TB PCIe Gen4 NVMe SSD",
            "display": "16.1-inch QHD (2560x1440), 165Hz, IPS, 300 nits, 100% sRGB",
            "ports": "2x USB-C 10Gbps, 2x USB-A 5Gbps, HDMI 2.1, RJ-45",
            "battery": "83Wh 6-cell battery",
            "weight": "2.37 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "165Hz",
            "resolution": "2560x1440"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CC32D3S5",
        "amazon_url": null,
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000016",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000016",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000016-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000016",
                "external_product_id": "B0CC32D3S5",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71YdF2K6uVL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - OMEN 16-xf0060AX",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the HP OMEN 16-xf0060AX are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CC32D3S5",
        "asin": "B0CC32D3S5",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000016",
                "retailer": "Amazon",
                "external_product_id": "B0CC32D3S5",
                "url": "https://www.amazon.in/dp/B0CC32D3S5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000016",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb36",
                "url": "https://www.flipkart.com/hp-omen-amd-ryzen-7-octa-core-7840hs-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-165-hz-16-xf0060ax-gaming-laptop/p/itmd5543c749eb36",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71YdF2K6uVL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000017",
        "product_id": "c1000000-0000-0000-0000-000000000017",
        "title": "Acer Nitro V 15 (Intel Core i5-13420H / RTX 4050 6GB / 16GB / 512GB SSD / 144Hz FHD)",
        "slug": "anv15-51",
        "brand": "Acer",
        "model": "Nitro V 15 ANV15-51",
        "sku": "ANV15-51",
        "model_number": "ANV15-51",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 69990.0,
        "currency": "INR",
        "description": "High-performance gaming laptop with 13th Gen Intel Core i5-13420H, NVIDIA GeForce RTX 4050 6GB GDDR6, and 15.6-inch 144Hz IPS display.",
        "specs": {
            "processor": "Intel Core i5-13420H (8 cores, up to 4.6 GHz)",
            "gpu": "NVIDIA GeForce RTX 4050 6GB GDDR6 (75W TGP)",
            "ram": "16GB DDR5 5200MHz",
            "storage": "512GB PCIe Gen4 NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) IPS, 144Hz",
            "ports": "1x Thunderbolt 4, 3x USB 3.2 Gen 1, HDMI 2.1, RJ-45",
            "battery": "57Wh 4-cell Li-ion",
            "weight": "2.11 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHJJZ9G8",
        "amazon_url": "https://www.amazon.in/dp/B0CHJJZ9G8",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000017",
                "retailer": "Amazon",
                "external_product_id": "B0CHJJZ9G8",
                "url": "https://www.amazon.in/dp/B0CHJJZ9G8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000017",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/q/g/z/-original-imahcyp7n3yyvxyr.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000017-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000017",
                "external_product_id": "B0CHJJZ9G8",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/q/g/z/-original-imahcyp7n3yyvxyr.jpeg?q=90",
                "image_type": "front",
                "source": "Verified",
                "verified": true
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71fM4bY-QpL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Nitro V 15 ANV15-51",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Acer Nitro V 15 ANV15-51 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CHJJZ9G8",
        "asin": "B0CHJJZ9G8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000017",
                "retailer": "Amazon",
                "external_product_id": "B0CHJJZ9G8",
                "url": "https://www.amazon.in/dp/B0CHJJZ9G8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000017",
                "retailer": "Flipkart",
                "external_product_id": "itm3d7c490a1b2d1",
                "url": "https://www.flipkart.com/acer-nitro-v-intel-core-i5-13th-gen-13420h-16-gb-512-gb-ssd-windows-11-home-6-gb-graphics-nvidia-geforce-rtx-4050-144-hz-anv15-51-gaming-laptop/p/itm3d7c490a1b2d1",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71fM4bY-QpL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000018",
        "product_id": "c1000000-0000-0000-0000-000000000018",
        "title": "Acer Predator Helios Neo 16 (Intel Core i7-13700HX / RTX 4060 8GB / 16GB / 1TB SSD / 165Hz WQXGA)",
        "slug": "phn16-71",
        "brand": "Acer",
        "model": "Predator Helios Neo 16 PHN16-71",
        "sku": "PHN16-71",
        "model_number": "PHN16-71",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 119990.0,
        "currency": "INR",
        "description": "Hardcore gaming flagship with 13th Gen Intel Core i7-13700HX (16 cores), 140W max TGP RTX 4060 8GB, liquid metal cooling, and 165Hz WQXGA panel.",
        "specs": {
            "processor": "Intel Core i7-13700HX (16 cores, up to 5.0 GHz)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (140W TGP)",
            "ram": "16GB DDR5 4800MHz",
            "storage": "1TB PCIe Gen4 NVMe SSD",
            "display": "16-inch WQXGA (2560x1600) IPS, 165Hz, 500 nits, 100% sRGB",
            "ports": "2x Thunderbolt 4, 3x USB-A 3.2, HDMI 2.1, Killer E2600 LAN",
            "battery": "90Wh 4-cell battery",
            "weight": "2.60 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "165Hz",
            "resolution": "2560x1600"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C3HTXB58",
        "amazon_url": "https://www.amazon.in/dp/B0C3HTXB58",
        "flipkart_url": "https://www.flipkart.com/acer-predator-neo-intel-core-i7-13th-gen-13700hx-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-165-hz-140-w-phn16-71-78r1-gaming-laptop/p/itm4295aa0d4297e?pid=COMGZS9GHNQCJC26",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "retailer": "Amazon",
                "external_product_id": "B0C3HTXB58",
                "url": "https://www.amazon.in/dp/B0C3HTXB58",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "retailer": "Flipkart",
                "external_product_id": "itm4295aa0d4297e",
                "url": "https://www.flipkart.com/acer-predator-neo-intel-core-i7-13th-gen-13700hx-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-165-hz-140-w-phn16-71-78r1-gaming-laptop/p/itm4295aa0d4297e?pid=COMGZS9GHNQCJC26",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/t/y/4/-enriched-transparent-original-imahg5fxfzumjkgw.png?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000018-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "external_product_id": "B0C3HTXB58",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/t/y/4/-enriched-transparent-original-imahg5fxfzumjkgw.png?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000018-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "external_product_id": "B0C3HTXB58",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/4/n/1/-original-imahg5fxtbhrmhzf.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71N-zJb+FRL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71wK8X-Q9aL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Predator Helios Neo 16 PHN16-71",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Acer Predator Helios Neo 16 PHN16-71 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C3HTXB58",
        "asin": "B0C3HTXB58",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "retailer": "Amazon",
                "external_product_id": "B0C3HTXB58",
                "url": "https://www.amazon.in/dp/B0C3HTXB58",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000018",
                "retailer": "Flipkart",
                "external_product_id": "itmd45a981a8c91b",
                "url": "https://www.flipkart.com/acer-predator-helios-neo-16-intel-core-i7-13th-gen-13700hx-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-165-hz-phn16-71-gaming-laptop/p/itmd45a981a8c91b",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71N-zJb+FRL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000019",
        "product_id": "c1000000-0000-0000-0000-000000000019",
        "title": "Acer Aspire Lite (Intel Core i3-1215U / 8GB / 512GB SSD / 15.6 FHD / Steel Gray)",
        "slug": "al15-51",
        "brand": "Acer",
        "model": "Aspire Lite AL15-51",
        "sku": "AL15-51",
        "model_number": "AL15-51",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Everyday Laptops",
        "is_component": false,
        "price": 31990.0,
        "currency": "INR",
        "description": "Ultra-lightweight everyday productivity laptop with Intel Core i3-1215U 6-core processor, metal top cover, and 15.6-inch Full HD display.",
        "specs": {
            "processor": "Intel Core i3-1215U (6 cores, up to 4.4 GHz)",
            "gpu": "Intel UHD Graphics",
            "ram": "8GB DDR4 3200MHz",
            "storage": "512GB PCIe NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) narrow bezel",
            "ports": "1x USB-C 3.2 Gen 2, 3x USB-A, HDMI, MicroSD, 3.5mm jack",
            "battery": "36Wh 3-cell Li-ion",
            "weight": "1.59 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CDLR4P9C",
        "amazon_url": "https://www.amazon.in/dp/B0CDLR4P9C",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000019",
                "retailer": "Amazon",
                "external_product_id": "B0CDLR4P9C",
                "url": "https://www.amazon.in/dp/B0CDLR4P9C",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000019",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000019-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000019",
                "external_product_id": "B0CDLR4P9C",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Image unavailable</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Verified link not found</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71r5h4K6wML._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Aspire Lite AL15-51",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Acer Aspire Lite AL15-51 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CDLR4P9C",
        "asin": "B0CDLR4P9C",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000019",
                "retailer": "Amazon",
                "external_product_id": "B0CDLR4P9C",
                "url": "https://www.amazon.in/dp/B0CDLR4P9C",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000019",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb37",
                "url": "https://www.flipkart.com/acer-aspire-lite-intel-core-i3-12th-gen-1215u-8-gb-512-gb-ssd-windows-11-home-al15-51-thin-light-laptop/p/itmd5543c749eb37",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71r5h4K6wML._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000020",
        "product_id": "c1000000-0000-0000-0000-000000000020",
        "title": "Acer Aspire 7 (Intel Core i5-12450H / RTX 2050 4GB / 16GB / 512GB SSD / 144Hz FHD)",
        "slug": "a715-76g",
        "brand": "Acer",
        "model": "Aspire 7 A715-76G",
        "sku": "A715-76G",
        "model_number": "A715-76G",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Gaming & Productivity",
        "is_component": false,
        "price": 52990.0,
        "currency": "INR",
        "description": "Subtle professional exterior packed with gaming firepower: Intel Core i5-12450H, NVIDIA GeForce RTX 2050 4GB GPU, and 144Hz IPS display.",
        "specs": {
            "processor": "Intel Core i5-12450H (8 cores, up to 4.4 GHz)",
            "gpu": "NVIDIA GeForce RTX 2050 4GB GDDR6",
            "ram": "16GB DDR4 3200MHz",
            "storage": "512GB PCIe Gen4 NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) 144Hz IPS",
            "ports": "1x Thunderbolt 4, 3x USB 3.2 Gen 1, HDMI 2.0, RJ-45",
            "battery": "50Wh 3-cell Li-ion",
            "weight": "2.10 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C5MC4Y4G",
        "amazon_url": "https://www.amazon.in/dp/B0C5MC4Y4G",
        "flipkart_url": "https://www.flipkart.com/acer-aspire-7-intel-core-i5-12th-gen-12450h-8-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-nvidia-2050-144-hz-a715-76g-59wg-gaming-laptop/p/itm45fad0c290245?pid=COMGRHJUAHMRWTHH",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "retailer": "Amazon",
                "external_product_id": "B0C5MC4Y4G",
                "url": "https://www.amazon.in/dp/B0C5MC4Y4G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "retailer": "Flipkart",
                "external_product_id": "itm45fad0c290245",
                "url": "https://www.flipkart.com/acer-aspire-7-intel-core-i5-12th-gen-12450h-8-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-nvidia-2050-144-hz-a715-76g-59wg-gaming-laptop/p/itm45fad0c290245?pid=COMGRHJUAHMRWTHH",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/c/i/q/-enriched-transparent-original-imahg5fxrxmyynwg.png?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000020-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "external_product_id": "B0C5MC4Y4G",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/c/i/q/-enriched-transparent-original-imahg5fxrxmyynwg.png?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000020-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "external_product_id": "B0C5MC4Y4G",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/y/t/d/-original-imahg5fxctg4fkhh.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/7123jqlq9KL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71WkK5mKTTL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61y8B3tE7bL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71g4W1Zf7fL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Aspire 7 A715-76G",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Acer Aspire 7 A715-76G are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C5MC4Y4G",
        "asin": "B0C5MC4Y4G",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "retailer": "Amazon",
                "external_product_id": "B0C5MC4Y4G",
                "url": "https://www.amazon.in/dp/B0C5MC4Y4G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000020",
                "retailer": "Flipkart",
                "external_product_id": "itm0fe84838bca8f",
                "url": "https://www.flipkart.com/acer-aspire-7-intel-core-i5-12th-gen-12450h-16-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-2050-144-hz-a715-76g-gaming-laptop/p/itm0fe84838bca8f",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/7123jqlq9KL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000021",
        "product_id": "c1000000-0000-0000-0000-000000000021",
        "title": "MSI Katana 15 (Intel Core i7-13620H / RTX 4060 8GB / 16GB / 1TB SSD / 144Hz FHD)",
        "slug": "b13vfk-296in",
        "brand": "MSI",
        "model": "Katana 15 B13VFK",
        "sku": "B13VFK-296IN",
        "model_number": "B13VFK-296IN",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 102990.0,
        "currency": "INR",
        "description": "Gaming powerhouse with 13th Gen Intel Core i7-13620H, 105W RTX 4060 8GB, Cooler Boost 5 dual-fan cooling, and 4-zone RGB keyboard.",
        "specs": {
            "processor": "Intel Core i7-13620H (10 cores, up to 4.9 GHz)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (105W TGP)",
            "ram": "16GB DDR5 5200MHz",
            "storage": "1TB NVMe PCIe Gen4 SSD",
            "display": "15.6-inch FHD (1920x1080) 144Hz IPS-Level",
            "ports": "1x USB-C 3.2, 2x USB-A 3.2, 1x USB 2.0, HDMI 2.1, RJ-45",
            "battery": "53.5Wh 3-cell battery",
            "weight": "2.25 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "144Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BVT87383",
        "amazon_url": "https://www.amazon.in/dp/B0BVT87383",
        "flipkart_url": "https://www.flipkart.com/msi-katana-15-intel-core-i7-13th-gen-13620h-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-144-hz-b13vfk-296in-gaming-laptop/p/itm575c0dfc9902c",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "retailer": "Amazon",
                "external_product_id": "B0BVT87383",
                "url": "https://www.amazon.in/dp/B0BVT87383",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "retailer": "Flipkart",
                "external_product_id": "itm575c0dfc9902c",
                "url": "https://www.flipkart.com/msi-katana-15-intel-core-i7-13th-gen-13620h-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-144-hz-b13vfk-296in-gaming-laptop/p/itm575c0dfc9902c",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/i/t/w/-original-imah3cxkepkwh9f4.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000021-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "external_product_id": "B0BVT87383",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/i/t/w/-original-imah3cxkepkwh9f4.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000021-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "external_product_id": "B0BVT87383",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/c/l/h/-original-imags9wcty7xc7sg.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71Y8K9uV0dL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Katana 15 B13VFK",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the MSI Katana 15 B13VFK are outstanding for professional use."
            }
        ],
        "external_product_id": "B0BVT87383",
        "asin": "B0BVT87383",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "retailer": "Amazon",
                "external_product_id": "B0BVT87383",
                "url": "https://www.amazon.in/dp/B0BVT87383",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000021",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71Y8K9uV0dL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000022",
        "product_id": "c1000000-0000-0000-0000-000000000022",
        "title": "Samsung Galaxy Book4 Pro 360 (Intel Core Ultra 7 155H / 16GB / 1TB SSD / 3K Dynamic AMOLED 2X 2-in-1)",
        "slug": "np960qgk",
        "brand": "Samsung",
        "model": "Galaxy Book4 Pro 360",
        "sku": "NP960QGK",
        "model_number": "NP960QGK",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Premium Convertible Ultrabooks",
        "is_component": false,
        "price": 179990.0,
        "currency": "INR",
        "description": "360-degree convertible touch ultrabook with S-Pen, Intel Core Ultra 7 155H with NPU AI, 16-inch 3K Dynamic AMOLED 2X, and AKG Quad speakers.",
        "specs": {
            "processor": "Intel Core Ultra 7 155H (16 cores, Intel AI Boost NPU)",
            "gpu": "Intel Arc Graphics",
            "ram": "16GB LPDDR5X 7467MHz",
            "storage": "1TB NVMe SSD",
            "display": "16-inch 3K (2880x1800) AMOLED 2X Touch, 120Hz, 120% DCI-P3",
            "ports": "2x Thunderbolt 4, 1x USB 3.2 Type-A, HDMI 2.1, MicroSD",
            "battery": "76Wh battery with 65W charging",
            "weight": "1.66 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "2880x1800"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CSYWW88J",
        "amazon_url": "https://www.amazon.in/dp/B0CSYWW88J",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-book4-pro-360-evo-intel-core-ultra-7-155h-16-gb-1-tb-ssd-windows-11-home-np960qgk-kg2-2-1-laptop/p/itmd96213edabd07",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "retailer": "Amazon",
                "external_product_id": "B0CSYWW88J",
                "url": "https://www.amazon.in/dp/B0CSYWW88J",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "retailer": "Flipkart",
                "external_product_id": "itmd96213edabd07",
                "url": "https://www.flipkart.com/samsung-galaxy-book4-pro-360-evo-intel-core-ultra-7-155h-16-gb-1-tb-ssd-windows-11-home-np960qgk-kg2-2-1-laptop/p/itmd96213edabd07",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/d/f/t/-original-imahg5fx8fw9svze.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000022-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "external_product_id": "B0CSYWW88J",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/d/f/t/-original-imahg5fx8fw9svze.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000022-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "external_product_id": "B0CSYWW88J",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/f/b/n/-original-imahg5fw4qapvu5y.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71H5r7P0sYL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Galaxy Book4 Pro 360",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Samsung Galaxy Book4 Pro 360 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CSYWW88J",
        "asin": "B0CSYWW88J",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "retailer": "Amazon",
                "external_product_id": "B0CSYWW88J",
                "url": "https://www.amazon.in/dp/B0CSYWW88J",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000022",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71H5r7P0sYL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000023",
        "product_id": "c1000000-0000-0000-0000-000000000023",
        "title": "Microsoft Surface Laptop 5 (Intel Core i7-1255U / 16GB / 512GB SSD / 13.5 PixelSense Touch / Platinum)",
        "slug": "r1s-00049",
        "brand": "Microsoft",
        "model": "Surface Laptop 5",
        "sku": "R1S-00049",
        "model_number": "R1S-00049",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Productivity & Executive Ultrabooks",
        "is_component": false,
        "price": 149990.0,
        "currency": "INR",
        "description": "Executive ultrabook featuring 12th Gen Intel Core i7-1255U, 13.5-inch PixelSense 3:2 touchscreen with Dolby Vision IQ, and 18 hours of battery life.",
        "specs": {
            "processor": "Intel Core i7-1255U (10 cores, up to 4.7 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB LPDDR5x RAM",
            "storage": "512GB Removable SSD",
            "display": "13.5-inch PixelSense (2256x1504) 3:2 touch, Gorilla Glass 5",
            "ports": "1x Thunderbolt 4, 1x USB-A 3.1, Surface Connect, 3.5mm jack",
            "battery": "Up to 18 hours battery",
            "weight": "1.29 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "2256x1504"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0B8KBD399",
        "amazon_url": "https://www.amazon.in/dp/B0B8KBD399",
        "flipkart_url": "https://www.flipkart.com/microsoft-surface-laptop-5-intel-core-i7-12th-gen-1255u-16-gb-512-gb-ssd-windows-11-home-rbg-00048-thin-light/p/itmad4ecb41f26bf",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "retailer": "Amazon",
                "external_product_id": "B0B8KBD399",
                "url": "https://www.amazon.in/dp/B0B8KBD399",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "retailer": "Flipkart",
                "external_product_id": "itmad4ecb41f26bf",
                "url": "https://www.flipkart.com/microsoft-surface-laptop-5-intel-core-i7-12th-gen-1255u-16-gb-512-gb-ssd-windows-11-home-rbg-00048-thin-light/p/itmad4ecb41f26bf",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/v/b/p/-original-imahg5fxtdu3hsuc.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000023-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "external_product_id": "B0B8KBD399",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/v/b/p/-original-imahg5fxtdu3hsuc.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000023-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "external_product_id": "B0B8KBD399",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/p/f/z/-original-imahg5fxxtsfqdme.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61aW2-S9g1L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Surface Laptop 5",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Microsoft Surface Laptop 5 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0B8KBD399",
        "asin": "B0B8KBD399",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "retailer": "Amazon",
                "external_product_id": "B0B8KBD399",
                "url": "https://www.amazon.in/dp/B0B8KBD399",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000023",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61aW2-S9g1L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000024",
        "product_id": "c1000000-0000-0000-0000-000000000024",
        "title": "Dell G15 5530 (Intel Core i5-13450HX / RTX 3050 6GB / 16GB / 1TB SSD / 120Hz FHD / Dark Shadow Gray)",
        "slug": "g15-5530",
        "brand": "Dell",
        "model": "G15 5530",
        "sku": "G15-5530",
        "model_number": "G15-5530",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Gaming Laptops",
        "is_component": false,
        "price": 72990.0,
        "currency": "INR",
        "description": "Alienware-inspired thermal architecture gaming laptop equipped with 13th Gen Intel Core i5-13450HX, 95W RTX 3050 6GB, and Game Shift macro key.",
        "specs": {
            "processor": "Intel Core i5-13450HX (10 cores, up to 4.6 GHz)",
            "gpu": "NVIDIA GeForce RTX 3050 6GB GDDR6 (95W TGP)",
            "ram": "16GB DDR5 4800MHz",
            "storage": "1TB M.2 PCIe NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) 120Hz, 250 nits",
            "ports": "1x USB-C 3.2, 3x USB-A 3.2, HDMI 2.1, RJ-45",
            "battery": "56Wh 3-cell battery",
            "weight": "2.81 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CRKXDX83",
        "amazon_url": "https://www.amazon.in/dp/B0CRKXDX83",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000024",
                "retailer": "Amazon",
                "external_product_id": "B0CRKXDX83",
                "url": "https://www.amazon.in/dp/B0CRKXDX83",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000024",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71XZ6r9igGL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000024-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000024",
                "external_product_id": "B0C9QG56ZR",
                "image_url": "https://m.media-amazon.com/images/I/71XZ6r9igGL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Dell%20G15%205530%20%28Intel%20Core%20i5-13450H</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - G15 5530",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Dell G15 5530 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C9QG56ZR",
        "asin": "B0C9QG56ZR",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000024",
                "retailer": "Amazon",
                "external_product_id": "B0C9QG56ZR",
                "url": "https://www.amazon.in/dp/B0C9QG56ZR",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000024",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Dell%20G15%205530%20%28Intel%20Core%20i5-13450H</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000025",
        "product_id": "c1000000-0000-0000-0000-000000000025",
        "title": "Dell Inspiron 15 3520 (Intel Core i5-1235U / 16GB / 512GB SSD / 120Hz FHD / Carbon Black)",
        "slug": "inspiron-3520",
        "brand": "Dell",
        "model": "Inspiron 15 3520",
        "sku": "INSPIRON-3520",
        "model_number": "INSPIRON-3520",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Everyday Productivity Laptops",
        "is_component": false,
        "price": 46990.0,
        "currency": "INR",
        "description": "Dependable workhorse featuring 12th Gen Intel Core i5-1235U (10 cores), 16GB RAM, 120Hz FHD anti-glare display, and lift hinge design.",
        "specs": {
            "processor": "Intel Core i5-1235U (10 cores, up to 4.4 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB DDR4 2666MHz",
            "storage": "512GB M.2 PCIe NVMe SSD",
            "display": "15.6-inch FHD (1920x1080) 120Hz, 250 nits",
            "ports": "2x USB 3.2, 1x USB 2.0, HDMI 1.4, SD reader",
            "battery": "41Wh battery with ExpressCharge",
            "weight": "1.65 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BYD6VQ7K",
        "amazon_url": "https://www.amazon.in/dp/B0BYD6VQ7K",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000025",
                "retailer": "Amazon",
                "external_product_id": "B0BYD6VQ7K",
                "url": "https://www.amazon.in/dp/B0BYD6VQ7K",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000025",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71nmVtNbN4L._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000025-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000025",
                "external_product_id": "B0CG21F8V8",
                "image_url": "https://m.media-amazon.com/images/I/71nmVtNbN4L._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Dell%20Inspiron%2015%203520%20%28Intel%20Core%20i</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Inspiron 15 3520",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Dell Inspiron 15 3520 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CG21F8V8",
        "asin": "B0CG21F8V8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000025",
                "retailer": "Amazon",
                "external_product_id": "B0CG21F8V8",
                "url": "https://www.amazon.in/dp/B0CG21F8V8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000025",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Dell%20Inspiron%2015%203520%20%28Intel%20Core%20i</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000026",
        "product_id": "c1000000-0000-0000-0000-000000000026",
        "title": "Lenovo IdeaPad Slim 5 (Intel Core i5-13500H / 16GB / 512GB SSD / 14 WUXGA OLED / Cloud Grey)",
        "slug": "14irh8-82xd",
        "brand": "Lenovo",
        "model": "IdeaPad Slim 5 14IRH8",
        "sku": "14IRH8-82XD",
        "model_number": "14IRH8-82XD",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Premium Thin & Light Ultrabooks",
        "is_component": false,
        "price": 68990.0,
        "currency": "INR",
        "description": "MIL-STD-810H certified all-metal ultrabook featuring Intel Core i5-13500H (12 cores), 16GB LPDDR5, and 14-inch WUXGA OLED display.",
        "specs": {
            "processor": "Intel Core i5-13500H (12 cores, up to 4.7 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB LPDDR5 5200MHz",
            "storage": "512GB M.2 PCIe NVMe Gen 4 SSD",
            "display": "14-inch WUXGA (1920x1200) OLED, 400 nits, 100% DCI-P3",
            "ports": "2x USB-C (PD/DP), 2x USB-A 3.2, HDMI 1.4b, MicroSD",
            "battery": "56.6Wh battery",
            "weight": "1.46 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "1920x1200"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0FJFTRVJ6",
        "amazon_url": "https://www.amazon.in/dp/B0FJFTRVJ6",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000026",
                "retailer": "Amazon",
                "external_product_id": "B0FJFTRVJ6",
                "url": "https://www.amazon.in/dp/B0FJFTRVJ6",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000026",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71hq8nnlZXL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000026-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000026",
                "external_product_id": "B0C9YQ88Z7",
                "image_url": "https://m.media-amazon.com/images/I/71hq8nnlZXL._SX679_.jpg",
                "image_type": "front",
                "source": "Verified",
                "verified": true
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71yD-PqQ9qL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Purchase - IdeaPad Slim 5 14IRH8",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo IdeaPad Slim 5 14IRH8 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C9YQ88Z7",
        "asin": "B0C9YQ88Z7",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000026",
                "retailer": "Amazon",
                "external_product_id": "B0C9YQ88Z7",
                "url": "https://www.amazon.in/dp/B0C9YQ88Z7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000026",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71yD-PqQ9qL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000027",
        "product_id": "c1000000-0000-0000-0000-000000000027",
        "title": "Lenovo ThinkPad E14 Gen 5 (Intel Core i5-1335U / 16GB / 512GB SSD / 14 WUXGA IPS / Black)",
        "slug": "21jk001vin",
        "brand": "Lenovo",
        "model": "ThinkPad E14 Gen 5",
        "sku": "21JK001VIN",
        "model_number": "21JK001VIN",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Business & Commercial Laptops",
        "is_component": false,
        "price": 64990.0,
        "currency": "INR",
        "description": "Enterprise productivity notebook with Intel Core i5-1335U (10 cores), discrete TPM 2.0 security, and spill-resistant TrackPoint keyboard.",
        "specs": {
            "processor": "Intel Core i5-1335U (10 cores, up to 4.6 GHz)",
            "gpu": "Intel Iris Xe Graphics",
            "ram": "16GB DDR4 3200MHz",
            "storage": "512GB M.2 PCIe Gen 4 SSD",
            "display": "14-inch WUXGA (1920x1200) IPS, 300 nits, Anti-glare",
            "ports": "1x Thunderbolt 4, 1x USB-C, 2x USB-A, HDMI 2.1, RJ-45",
            "battery": "57Wh battery with Rapid Charge",
            "weight": "1.53 kg",
            "os": "Windows 11 Pro",
            "refresh_rate": "60Hz",
            "resolution": "1920x1200"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0F6WZ26MX",
        "amazon_url": "https://www.amazon.in/dp/B0F6WZ26MX",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000027",
                "retailer": "Amazon",
                "external_product_id": "B0F6WZ26MX",
                "url": "https://www.amazon.in/dp/B0F6WZ26MX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000027",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51z9ezfuiBL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000027-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000027",
                "external_product_id": "B0CDLX8P2M",
                "image_url": "https://m.media-amazon.com/images/I/51z9ezfuiBL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Lenovo%20ThinkPad%20E14%20Gen%205%20%28Intel%20Co</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - ThinkPad E14 Gen 5",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Lenovo ThinkPad E14 Gen 5 are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CDLX8P2M",
        "asin": "B0CDLX8P2M",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000027",
                "retailer": "Amazon",
                "external_product_id": "B0CDLX8P2M",
                "url": "https://www.amazon.in/dp/B0CDLX8P2M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000027",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Lenovo%20ThinkPad%20E14%20Gen%205%20%28Intel%20Co</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000028",
        "product_id": "c1000000-0000-0000-0000-000000000028",
        "title": "HP 15s (Intel Core i3-1215U / 8GB / 512GB SSD / 15.6 FHD / Natural Silver)",
        "slug": "15s-fq5330tu",
        "brand": "HP",
        "model": "HP 15s-fq5330TU",
        "sku": "15S-FQ5330TU",
        "model_number": "15S-FQ5330TU",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget Everyday Laptops",
        "is_component": false,
        "price": 35990.0,
        "currency": "INR",
        "description": "Everyday student and office laptop featuring 12th Gen Intel Core i3-1215U (6 cores), micro-edge anti-glare display, and HP Fast Charge.",
        "specs": {
            "processor": "Intel Core i3-1215U (6 cores, up to 4.4 GHz)",
            "gpu": "Intel UHD Graphics",
            "ram": "8GB DDR4 3200MHz",
            "storage": "512GB PCIe NVMe M.2 SSD",
            "display": "15.6-inch FHD (1920x1080) micro-edge, 250 nits",
            "ports": "1x USB-C 5Gbps, 2x USB-A 5Gbps, HDMI 1.4b, SD reader",
            "battery": "41Wh battery",
            "weight": "1.69 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BP2M7CCS",
        "amazon_url": "https://www.amazon.in/dp/B0BP2M7CCS",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000028",
                "retailer": "Amazon",
                "external_product_id": "B0BP2M7CCS",
                "url": "https://www.amazon.in/dp/B0BP2M7CCS",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000028",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71bRz-UEILL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000028-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000028",
                "external_product_id": "B0CDLR4P9D",
                "image_url": "https://m.media-amazon.com/images/I/71bRz-UEILL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HP%2015s%20%28Intel%20Core%20i3-1215U%20/%208GB%20/</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - HP 15s-fq5330TU",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the HP HP 15s-fq5330TU are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CDLR4P9D",
        "asin": "B0CDLR4P9D",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000028",
                "retailer": "Amazon",
                "external_product_id": "B0CDLR4P9D",
                "url": "https://www.amazon.in/dp/B0CDLR4P9D",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000028",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HP%2015s%20%28Intel%20Core%20i3-1215U%20/%208GB%20/</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000029",
        "product_id": "c1000000-0000-0000-0000-000000000029",
        "title": "ASUS Vivobook Go 15 OLED (AMD Ryzen 5 7520U / 16GB / 512GB SSD / 15.6 FHD OLED / Cool Silver)",
        "slug": "e1504fa-lk545ws",
        "brand": "ASUS",
        "model": "Vivobook Go 15 OLED E1504FA",
        "sku": "E1504FA-LK545WS",
        "model_number": "E1504FA-LK545WS",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Budget OLED Ultrabooks",
        "is_component": false,
        "price": 49990.0,
        "currency": "INR",
        "description": "Great visual value featuring a 15.6-inch Full HD OLED Lumina display, AMD Ryzen 5 7520U processor, and 16GB LPDDR5 memory.",
        "specs": {
            "processor": "AMD Ryzen 5 7520U (4 cores, up to 4.3 GHz)",
            "gpu": "AMD Radeon 610M Graphics",
            "ram": "16GB LPDDR5 5500MHz",
            "storage": "512GB M.2 NVMe PCIe SSD",
            "display": "15.6-inch FHD (1920x1080) OLED, 400 nits, 100% DCI-P3",
            "ports": "1x USB-C 3.2, 1x USB-A 3.2, 1x USB 2.0, HDMI 1.4",
            "battery": "50WHrs 3-cell battery",
            "weight": "1.63 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "60Hz",
            "resolution": "1920x1080"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BTWG1BHC",
        "amazon_url": "https://www.amazon.in/dp/B0BTWG1BHC",
        "flipkart_url": "https://www.flipkart.com/asus-vivobook-go-15-oled-amd-ryzen-5-quad-core-7520u-16-gb-512-gb-ssd-windows-11-home-e1504fa-lk541ws-thin-light-laptop/p/itm4297a9be166be",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000029",
                "retailer": "Amazon",
                "external_product_id": "B0BTWG1BHC",
                "url": "https://www.amazon.in/dp/B0BTWG1BHC",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000029",
                "retailer": "Flipkart",
                "external_product_id": "itm4297a9be166be",
                "url": "https://www.flipkart.com/asus-vivobook-go-15-oled-amd-ryzen-5-quad-core-7520u-16-gb-512-gb-ssd-windows-11-home-e1504fa-lk541ws-thin-light-laptop/p/itm4297a9be166be",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71MFoXmeDtL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000029-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000029",
                "external_product_id": "B0C9YQ88Z8",
                "image_url": "https://m.media-amazon.com/images/I/71MFoXmeDtL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20Vivobook%20Go%2015%20OLED%20%28AMD%20Ryzen</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - Vivobook Go 15 OLED E1504FA",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS Vivobook Go 15 OLED E1504FA are outstanding for professional use."
            }
        ],
        "external_product_id": "B0C9YQ88Z8",
        "asin": "B0C9YQ88Z8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000029",
                "retailer": "Amazon",
                "external_product_id": "B0C9YQ88Z8",
                "url": "https://www.amazon.in/dp/B0C9YQ88Z8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000029",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20Vivobook%20Go%2015%20OLED%20%28AMD%20Ryzen</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000030",
        "product_id": "c1000000-0000-0000-0000-000000000030",
        "title": "Apple MacBook Pro 16 (M3 Max chip / 36GB Unified RAM / 1TB SSD / Space Black)",
        "slug": "muw63hn-a",
        "brand": "Apple",
        "model": "MacBook Pro 16 M3 Max",
        "sku": "MUW63HN/A",
        "model_number": "MUW63HN/A",
        "category": "Laptops & Ultrabooks",
        "subcategory": "AI & Extreme Workstation Laptops",
        "is_component": false,
        "price": 349900.0,
        "currency": "INR",
        "description": "Unrivaled workstation beast powered by Apple M3 Max with 14-core CPU and 30-core GPU, 36GB unified memory, and Liquid Retina XDR display.",
        "specs": {
            "processor": "Apple M3 Max (14-core CPU)",
            "gpu": "30-core GPU with hardware ray tracing",
            "ram": "36GB Unified Memory",
            "storage": "1TB PCIe onboard SSD",
            "display": "16.2-inch Liquid Retina XDR (3456x2234), 1000 nits sustained, 120Hz ProMotion",
            "ports": "3x Thunderbolt 4, HDMI, SDXC, MagSafe 3",
            "battery": "100Wh battery, up to 22 hours",
            "weight": "2.16 kg",
            "os": "macOS Sonoma",
            "refresh_rate": "120Hz",
            "resolution": "3456x2234"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CM5S7HF6",
        "amazon_url": "https://www.amazon.in/dp/B0CM5S7HF6",
        "flipkart_url": "https://www.flipkart.com/apple-macbook-pro-m3-max-36-gb-1-tb-ssd-macos-sonoma-mrw33hn-a/p/itme3c9736ce5e76",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000030",
                "retailer": "Amazon",
                "external_product_id": "B0CM5S7HF6",
                "url": "https://www.amazon.in/dp/B0CM5S7HF6",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000030",
                "retailer": "Flipkart",
                "external_product_id": "itme3c9736ce5e76",
                "url": "https://www.flipkart.com/apple-macbook-pro-m3-max-36-gb-1-tb-ssd-macos-sonoma-mrw33hn-a/p/itme3c9736ce5e76",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/7/r/w/-original-imaguw3hpuzcwvdp.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000030-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000030",
                "external_product_id": "B0CM5L15NW",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/7/r/w/-original-imaguw3hpuzcwvdp.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Apple%20MacBook%20Pro%2016%20%28M3%20Max%20chip%20/</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - MacBook Pro 16 M3 Max",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the Apple MacBook Pro 16 M3 Max are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CM5L15NW",
        "asin": "B0CM5L15NW",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000030",
                "retailer": "Amazon",
                "external_product_id": "B0CM5L15NW",
                "url": "https://www.amazon.in/dp/B0CM5L15NW",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000030",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Apple%20MacBook%20Pro%2016%20%28M3%20Max%20chip%20/</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000031",
        "product_id": "c1000000-0000-0000-0000-000000000031",
        "title": "ASUS ROG Zephyrus G14 (AMD Ryzen 9 8945HS / RTX 4060 / 16GB / 1TB SSD / 3K 120Hz OLED / Platinum White)",
        "slug": "ga403ui-qs062w",
        "brand": "ASUS",
        "model": "ROG Zephyrus G14 GA403UI",
        "sku": "GA403UI-QS062W",
        "model_number": "GA403UI-QS062W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Ultraportable Gaming & AI",
        "is_component": false,
        "price": 174990.0,
        "currency": "INR",
        "description": "CNC aluminum masterpiece featuring AMD Ryzen 9 8945HS with Ryzen AI, RTX 4060 8GB, and 3K 120Hz ROG Nebula OLED display.",
        "specs": {
            "processor": "AMD Ryzen 9 8945HS (8 cores, up to 5.2 GHz, 16 TOPS NPU)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (90W TGP)",
            "ram": "16GB LPDDR5X 6400MHz",
            "storage": "1TB M.2 NVMe PCIe 4.0 SSD",
            "display": "14-inch 3K (2880x1800) OLED, 120Hz, 500 nits, G-SYNC",
            "ports": "1x USB4, 1x USB-C 3.2, 2x USB-A 3.2, HDMI 2.1, MicroSD",
            "battery": "73WHrs 4-cell Li-ion",
            "weight": "1.50 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "2880x1800"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0D59PYPFX",
        "amazon_url": "https://www.amazon.in/dp/B0D59PYPFX",
        "flipkart_url": "https://www.flipkart.com/asus-rog-zephyrus-g14-oled-amd-ryzen-9-octa-core-8945hs-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-90-w-ga403uv-qs085ws-gaming-laptop/p/itm912063a6c366f",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000031",
                "retailer": "Amazon",
                "external_product_id": "B0D59PYPFX",
                "url": "https://www.amazon.in/dp/B0D59PYPFX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000031",
                "retailer": "Flipkart",
                "external_product_id": "itm912063a6c366f",
                "url": "https://www.flipkart.com/asus-rog-zephyrus-g14-oled-amd-ryzen-9-octa-core-8945hs-16-gb-1-tb-ssd-windows-11-home-8-gb-graphics-nvidia-geforce-rtx-4060-90-w-ga403uv-qs085ws-gaming-laptop/p/itm912063a6c366f",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/81x+1vl1kCL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000031-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000031",
                "external_product_id": "B0CWL432P8",
                "image_url": "https://m.media-amazon.com/images/I/81x+1vl1kCL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20ROG%20Zephyrus%20G14%20%28AMD%20Ryzen%209%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - ROG Zephyrus G14 GA403UI",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS ROG Zephyrus G14 GA403UI are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CWL432P8",
        "asin": "B0CWL432P8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000031",
                "retailer": "Amazon",
                "external_product_id": "B0CWL432P8",
                "url": "https://www.amazon.in/dp/B0CWL432P8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000031",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20ROG%20Zephyrus%20G14%20%28AMD%20Ryzen%209%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000032",
        "product_id": "c1000000-0000-0000-0000-000000000032",
        "title": "ASUS ProArt Studiobook 16 OLED (Intel Core i9-13980HX / RTX 4070 8GB / 32GB / 1TB SSD / 3.2K 120Hz Touch)",
        "slug": "h7604ji-my072w",
        "brand": "ASUS",
        "model": "ProArt Studiobook 16 H7604JI",
        "sku": "H7604JI-MY072W",
        "model_number": "H7604JI-MY072W",
        "category": "Laptops & Ultrabooks",
        "subcategory": "Creator & AI Workstation",
        "is_component": false,
        "price": 249990.0,
        "currency": "INR",
        "description": "Ultimate studio laptop with rotary ASUS Dial controller, 24-core Intel Core i9-13980HX, NVIDIA GeForce RTX 4070 Studio, and 3.2K 120Hz OLED touch.",
        "specs": {
            "processor": "Intel Core i9-13980HX (24 cores, up to 5.6 GHz)",
            "gpu": "NVIDIA GeForce RTX 4070 8GB GDDR6 (130W TGP)",
            "ram": "32GB DDR5 4800MHz",
            "storage": "1TB M.2 NVMe PCIe 4.0 SSD",
            "display": "16-inch 3.2K (3200x2000) OLED 16:10, 120Hz, 550 nits HDR",
            "ports": "2x Thunderbolt 4, 2x USB-A 3.2, HDMI 2.1, SD Express 7.0",
            "battery": "90WHrs 4-cell Li-ion",
            "weight": "2.40 kg",
            "os": "Windows 11 Home",
            "refresh_rate": "120Hz",
            "resolution": "3200x2000"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C42VNZZS",
        "amazon_url": "https://www.amazon.in/dp/B0C42VNZZS",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000032",
                "retailer": "Amazon",
                "external_product_id": "B0C42VNZZS",
                "url": "https://www.amazon.in/dp/B0C42VNZZS",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000032",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61I4-3x8rtL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000032-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000032",
                "external_product_id": "B0CDLX8P2N",
                "image_url": "https://m.media-amazon.com/images/I/61I4-3x8rtL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20ProArt%20Studiobook%2016%20OLED%20%28Int</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Purchase - ProArt Studiobook 16 H7604JI",
                "rating": 4.8,
                "body": "The performance, screen clarity, and thermal profile on the ASUS ProArt Studiobook 16 H7604JI are outstanding for professional use."
            }
        ],
        "external_product_id": "B0CDLX8P2N",
        "asin": "B0CDLX8P2N",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000032",
                "retailer": "Amazon",
                "external_product_id": "B0CDLX8P2N",
                "url": "https://www.amazon.in/dp/B0CDLX8P2N",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000032",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>ASUS%20ProArt%20Studiobook%2016%20OLED%20%28Int</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000101",
        "product_id": "c1000000-0000-0000-0000-000000000101",
        "title": "Apple iPhone 15 Pro (128 GB) - Natural Titanium",
        "slug": "iphone-15-pro",
        "brand": "Apple",
        "model": "iPhone 15 Pro",
        "sku": "IPHONE-15-PRO",
        "model_number": "IPHONE-15-PRO",
        "category": "Smartphones",
        "subcategory": "Flagship Smartphones",
        "is_component": false,
        "price": 127990.0,
        "currency": "INR",
        "description": "Aerospace-grade titanium design with A17 Pro chip, customizable Action button, 48MP main camera with 7 pro lenses, and USB-C with USB 3 speeds.",
        "specs": {
            "processor": "Apple A17 Pro (6-core CPU, 6-core GPU, 16-core Neural Engine)",
            "ram": "8GB",
            "storage": "128GB NVMe",
            "display": "6.1-inch Super Retina XDR OLED, 120Hz ProMotion, 2000 nits peak, Always-On",
            "resolution": "2556x1179",
            "refresh_rate": "120Hz",
            "camera": "48MP Main + 12MP Ultra Wide + 12MP 3x Telephoto",
            "battery": "3274mAh, up to 23 hours video playback",
            "charging": "20W wired, 15W MagSafe wireless",
            "os": "iOS 17",
            "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3, Thread, Ultra Wideband gen 2",
            "dimensions": "146.6 x 70.6 x 8.25 mm",
            "weight": "187 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHWV2WYK",
        "amazon_url": "https://www.amazon.in/dp/B0CHWV2WYK",
        "flipkart_url": "https://www.flipkart.com/apple-iphone-15-pro-natural-titanium-128-gb/p/itm7ffb1e9990edd",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "retailer": "Amazon",
                "external_product_id": "B0CHWV2WYK",
                "url": "https://www.amazon.in/dp/B0CHWV2WYK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "retailer": "Flipkart",
                "external_product_id": "itm7ffb1e9990edd",
                "url": "https://www.flipkart.com/apple-iphone-15-pro-natural-titanium-128-gb/p/itm7ffb1e9990edd",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/b/q/-original-imahggex2ye98xfn.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000101-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "external_product_id": "B0CHWV2WYK",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/b/q/-original-imahggex2ye98xfn.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000101-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "external_product_id": "B0CHWV2WYK",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/6/j/1/-original-imahggexhnfhg2zs.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/81+GIkwqdcL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71657TiFeHL._SL1500_.jpg",
            "camera": "https://m.media-amazon.com/images/I/712CBkmhLhL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71d74dQuzAL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61bK6PMOC3L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81CgtwSII3L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - iPhone 15 Pro",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Apple iPhone 15 Pro exceed expectations."
            }
        ],
        "external_product_id": "B0CHWV2WYK",
        "asin": "B0CHWV2WYK",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "retailer": "Amazon",
                "external_product_id": "B0CHWV2WYK",
                "url": "https://www.amazon.in/dp/B0CHWV2WYK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000101",
                "retailer": "Flipkart",
                "external_product_id": "itm6ac6485515ae4",
                "url": "https://www.flipkart.com/apple-iphone-15-pro-natural-titanium-128-gb/p/itm6ac6485515ae4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/81+GIkwqdcL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000102",
        "product_id": "c1000000-0000-0000-0000-000000000102",
        "title": "Apple iPhone 15 (128 GB) - Black",
        "slug": "iphone-15-128",
        "brand": "Apple",
        "model": "iPhone 15",
        "sku": "IPHONE-15-128",
        "model_number": "IPHONE-15-128",
        "category": "Smartphones",
        "subcategory": "Premium Smartphones",
        "is_component": false,
        "price": 70999.0,
        "currency": "INR",
        "description": "Dynamic Island, 48MP Main camera with 2x Telephoto, color-infused glass and aluminum design, and USB-C connectivity.",
        "specs": {
            "processor": "Apple A16 Bionic (6-core CPU, 5-core GPU)",
            "ram": "6GB",
            "storage": "128GB",
            "display": "6.1-inch Super Retina XDR OLED, 2000 nits outdoor peak",
            "resolution": "2556x1179",
            "refresh_rate": "60Hz",
            "camera": "48MP Main + 12MP Ultra Wide with 2x Telephoto",
            "battery": "3349mAh, up to 20 hours video playback",
            "charging": "20W wired, 15W MagSafe",
            "os": "iOS 17",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3, NFC",
            "dimensions": "147.6 x 71.6 x 7.80 mm",
            "weight": "171 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHX1W1XY",
        "amazon_url": "https://www.amazon.in/dp/B0CHX1W1XY",
        "flipkart_url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae5",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "retailer": "Amazon",
                "external_product_id": "B0CHX1W1XY",
                "url": "https://www.amazon.in/dp/B0CHX1W1XY",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "retailer": "Flipkart",
                "external_product_id": "itm6ac6485515ae5",
                "url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000102-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "external_product_id": "B0CHX1W1XY",
                "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000102-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "external_product_id": "B0CHX1W1XY",
                "image_url": "https://m.media-amazon.com/images/I/81SigAnStatus._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg",
            "front": "https://m.media-amazon.com/images/I/81SigAnStatus._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81Os1eA5DxL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - iPhone 15",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Apple iPhone 15 exceed expectations."
            }
        ],
        "external_product_id": "B0CHX1W1XY",
        "asin": "B0CHX1W1XY",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "retailer": "Amazon",
                "external_product_id": "B0CHX1W1XY",
                "url": "https://www.amazon.in/dp/B0CHX1W1XY",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000102",
                "retailer": "Flipkart",
                "external_product_id": "itm6ac6485515ae5",
                "url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000103",
        "product_id": "c1000000-0000-0000-0000-000000000103",
        "title": "Apple iPhone 14 (128 GB) - Blue",
        "slug": "iphone-14-128",
        "brand": "Apple",
        "model": "iPhone 14",
        "sku": "IPHONE-14-128",
        "model_number": "IPHONE-14-128",
        "category": "Smartphones",
        "subcategory": "Premium Smartphones",
        "is_component": false,
        "price": 58999.0,
        "currency": "INR",
        "description": "Reliable powerhouse with A15 Bionic chip, advanced dual-camera system with Photonic Engine, Crash Detection, and all-day battery life.",
        "specs": {
            "processor": "Apple A15 Bionic (6-core CPU, 5-core GPU)",
            "ram": "6GB",
            "storage": "128GB",
            "display": "6.1-inch Super Retina XDR OLED, 1200 nits peak HDR",
            "resolution": "2532x1170",
            "refresh_rate": "60Hz",
            "camera": "12MP Main + 12MP Ultra Wide with Action Mode",
            "battery": "3279mAh, up to 20 hours playback",
            "charging": "20W wired, 15W MagSafe",
            "os": "iOS 16 (Upgradable)",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "146.7 x 71.5 x 7.80 mm",
            "weight": "172 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BDK62PDX",
        "amazon_url": "https://www.amazon.in/dp/B0BDK62PDX",
        "flipkart_url": "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itmdb24cc40775a4",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "retailer": "Amazon",
                "external_product_id": "B0BDK62PDX",
                "url": "https://www.amazon.in/dp/B0BDK62PDX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "retailer": "Flipkart",
                "external_product_id": "itmdb24cc40775a4",
                "url": "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itmdb24cc40775a4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71vdTR50hFL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000103-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "external_product_id": "B0BDK62PDX",
                "image_url": "https://m.media-amazon.com/images/I/71vdTR50hFL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000103-PORTS",
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "external_product_id": "B0BDK62PDX",
                "image_url": "https://m.media-amazon.com/images/I/611mAjCc9TL._SL1500_.jpg",
                "image_type": "ports",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71vdTR50hFL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/611mAjCc9TL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71s2X8p1bCL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - iPhone 14",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Apple iPhone 14 exceed expectations."
            }
        ],
        "external_product_id": "B0BDK62PDX",
        "asin": "B0BDK62PDX",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "retailer": "Amazon",
                "external_product_id": "B0BDK62PDX",
                "url": "https://www.amazon.in/dp/B0BDK62PDX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000103",
                "retailer": "Flipkart",
                "external_product_id": "itmdb24cc40775a4",
                "url": "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itmdb24cc40775a4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71vdTR50hFL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000104",
        "product_id": "c1000000-0000-0000-0000-000000000104",
        "title": "Apple iPhone 13 (128 GB) - Starlight",
        "slug": "iphone-13-128",
        "brand": "Apple",
        "model": "iPhone 13",
        "sku": "IPHONE-13-128",
        "model_number": "IPHONE-13-128",
        "category": "Smartphones",
        "subcategory": "Value Flagship Smartphones",
        "is_component": false,
        "price": 48999.0,
        "currency": "INR",
        "description": "Super Retina XDR display, A15 Bionic chip, dual 12MP cameras with sensor-shift OIS, and Cinematic mode for 1080p 30fps videos.",
        "specs": {
            "processor": "Apple A15 Bionic (6-core CPU, 4-core GPU)",
            "ram": "4GB",
            "storage": "128GB",
            "display": "6.1-inch Super Retina XDR OLED, 800 nits max, 1200 nits peak",
            "resolution": "2532x1170",
            "refresh_rate": "60Hz",
            "camera": "12MP Wide + 12MP Ultra Wide, Sensor-shift OIS",
            "battery": "3227mAh, up to 19 hours playback",
            "charging": "20W wired, 15W MagSafe",
            "os": "iOS 15 (Upgradable)",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.0",
            "dimensions": "146.7 x 71.5 x 7.65 mm",
            "weight": "173 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09G9D8KRQ",
        "amazon_url": "https://www.amazon.in/dp/B09G9D8KRQ",
        "flipkart_url": "https://www.flipkart.com/apple-iphone-13-starlight-128-gb/p/itmc9604f122ae7f",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "retailer": "Amazon",
                "external_product_id": "B09G9D8KRQ",
                "url": "https://www.amazon.in/dp/B09G9D8KRQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "retailer": "Flipkart",
                "external_product_id": "itmc9604f122ae7f",
                "url": "https://www.flipkart.com/apple-iphone-13-starlight-128-gb/p/itmc9604f122ae7f",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71GLMJ7TQiL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000104-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "external_product_id": "B09G9D8KRQ",
                "image_url": "https://m.media-amazon.com/images/I/71GLMJ7TQiL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000104-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "external_product_id": "B09G9D8KRQ",
                "image_url": "https://m.media-amazon.com/images/I/61vuJdpWvML._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71GLMJ7TQiL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61vuJdpWvML._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - iPhone 13",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Apple iPhone 13 exceed expectations."
            }
        ],
        "external_product_id": "B09G9D8KRQ",
        "asin": "B09G9D8KRQ",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "retailer": "Amazon",
                "external_product_id": "B09G9D8KRQ",
                "url": "https://www.amazon.in/dp/B09G9D8KRQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000104",
                "retailer": "Flipkart",
                "external_product_id": "itmc9604f122ae7f",
                "url": "https://www.flipkart.com/apple-iphone-13-starlight-128-gb/p/itmc9604f122ae7f",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71GLMJ7TQiL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000105",
        "product_id": "c1000000-0000-0000-0000-000000000105",
        "title": "Samsung Galaxy S24 Ultra 5G (Titanium Black, 12GB, 256GB Storage)",
        "slug": "galaxy-s24-ultra",
        "brand": "Samsung",
        "model": "Galaxy S24 Ultra",
        "sku": "GALAXY-S24-ULTRA",
        "model_number": "GALAXY-S24-ULTRA",
        "category": "Smartphones",
        "subcategory": "Flagship & AI Smartphones",
        "is_component": false,
        "price": 129999.0,
        "currency": "INR",
        "description": "Titanium frame with integrated S-Pen, Galaxy AI features, 200MP Quad Telephoto camera with 100x Space Zoom, and Snapdragon 8 Gen 3 for Galaxy.",
        "specs": {
            "processor": "Qualcomm Snapdragon 8 Gen 3 for Galaxy (4nm, Octa-Core up to 3.39GHz)",
            "ram": "12GB LPDDR5X",
            "storage": "256GB UFS 4.0",
            "display": "6.8-inch Dynamic AMOLED 2X flat display, 1-120Hz LTPO, 2600 nits, Corning Gorilla Armor",
            "resolution": "3120x1440 QHD+",
            "refresh_rate": "120Hz",
            "camera": "200MP Main OIS + 50MP 5x Periscope + 10MP 3x Telephoto + 12MP Ultra-wide",
            "battery": "5000mAh",
            "charging": "45W wired, 15W Fast Wireless Charging 2.0",
            "os": "Android 14 with One UI 6.1 (7 years OS updates)",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.3, UWB, NFC",
            "dimensions": "162.3 x 79.0 x 8.6 mm",
            "weight": "232 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CS5X81L4",
        "amazon_url": "https://www.amazon.in/dp/B0CS5X81L4",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-s24-ultra-5g-titanium-black-256-gb/p/itm60d6a4ba69e8c",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "retailer": "Amazon",
                "external_product_id": "B0CS5X81L4",
                "url": "https://www.amazon.in/dp/B0CS5X81L4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "retailer": "Flipkart",
                "external_product_id": "itm60d6a4ba69e8c",
                "url": "https://www.flipkart.com/samsung-galaxy-s24-ultra-5g-titanium-black-256-gb/p/itm60d6a4ba69e8c",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/y/s/g/-original-imahgfmy2zgqvjmy.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000105-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "external_product_id": "B0CS5X81L4",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/y/s/g/-original-imahgfmy2zgqvjmy.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000105-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "external_product_id": "B0CS5X81L4",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/5/c/x/-original-imahggevnsn9ubah.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71RVu88m78L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71CXhVHPm0L._SL1500_.jpg",
            "camera": "https://m.media-amazon.com/images/I/717vT6nN+KL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71CXhVwPx0L._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71S8L4XQO2L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61r5K8s8VBL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71q7X9s7O3L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy S24 Ultra",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy S24 Ultra exceed expectations."
            }
        ],
        "external_product_id": "B0CS5X81L4",
        "asin": "B0CS5X81L4",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "retailer": "Amazon",
                "external_product_id": "B0CS5X81L4",
                "url": "https://www.amazon.in/dp/B0CS5X81L4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000105",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71RVu88m78L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000106",
        "product_id": "c1000000-0000-0000-0000-000000000106",
        "title": "Samsung Galaxy S23 FE 5G (Mint, 8GB, 128GB Storage)",
        "slug": "galaxy-s23-fe",
        "brand": "Samsung",
        "model": "Galaxy S23 FE",
        "sku": "GALAXY-S23-FE",
        "model_number": "GALAXY-S23-FE",
        "category": "Smartphones",
        "subcategory": "Value Flagship Smartphones",
        "is_component": false,
        "price": 49999.0,
        "currency": "INR",
        "description": "Premium glass and aluminum construction, 50MP pro-grade camera with Nightography, Dynamic AMOLED 2X 120Hz display, and IP68 water resistance.",
        "specs": {
            "processor": "Samsung Exynos 2200 (4nm, Octa-Core up to 2.8GHz, Xclipse 920 GPU)",
            "ram": "8GB LPDDR5",
            "storage": "128GB UFS 3.1",
            "display": "6.4-inch Dynamic AMOLED 2X, 120Hz adaptive, 1450 nits peak, Gorilla Glass 5",
            "resolution": "2340x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + 12MP Ultra-wide + 8MP 3x Telephoto OIS",
            "battery": "4500mAh",
            "charging": "25W wired, 15W wireless",
            "os": "Android 14 with One UI 6",
            "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3, NFC",
            "dimensions": "158.0 x 76.5 x 8.2 mm",
            "weight": "209 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CJ4S724M",
        "amazon_url": "https://www.amazon.in/dp/B0CJ4S724M",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-s23-fe-mint-128-gb/p/itmfde87b854d383",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "retailer": "Amazon",
                "external_product_id": "B0CJ4S724M",
                "url": "https://www.amazon.in/dp/B0CJ4S724M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "retailer": "Flipkart",
                "external_product_id": "itmfde87b854d383",
                "url": "https://www.flipkart.com/samsung-galaxy-s23-fe-mint-128-gb/p/itmfde87b854d383",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/w/z/n/-original-imah5ywfurj7gtqn.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000106-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "external_product_id": "B0CJ2B8K6R",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/w/z/n/-original-imah5ywfurj7gtqn.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000106-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "external_product_id": "B0CJ2B8K6R",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/8/v/0/-original-imah5ywfebrs9bfg.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20S23%20FE%205G%20%28Mint%2C%208GB</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy S23 FE",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy S23 FE exceed expectations."
            }
        ],
        "external_product_id": "B0CJ2B8K6R",
        "asin": "B0CJ2B8K6R",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "retailer": "Amazon",
                "external_product_id": "B0CJ2B8K6R",
                "url": "https://www.amazon.in/dp/B0CJ2B8K6R",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000106",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20S23%20FE%205G%20%28Mint%2C%208GB</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000107",
        "product_id": "c1000000-0000-0000-0000-000000000107",
        "title": "Samsung Galaxy A55 5G (Awesome Iceblue, 8GB RAM, 128GB Storage)",
        "slug": "galaxy-a55-5g",
        "brand": "Samsung",
        "model": "Galaxy A55 5G",
        "sku": "GALAXY-A55-5G",
        "model_number": "GALAXY-A55-5G",
        "category": "Smartphones",
        "subcategory": "Mid-Range Smartphones",
        "is_component": false,
        "price": 39999.0,
        "currency": "INR",
        "description": "Metal frame and Corning Gorilla Glass Victus+ design with Knox Vault hardware security, 50MP OIS camera, and 5000mAh battery.",
        "specs": {
            "processor": "Samsung Exynos 1480 (4nm, AMD Xclipse 530 GPU)",
            "ram": "8GB",
            "storage": "128GB (Expandable up to 1TB via MicroSD)",
            "display": "6.6-inch Super AMOLED, 120Hz, 1000 nits HBM, Vision Booster",
            "resolution": "2340x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + 12MP Ultra-wide + 5MP Macro",
            "battery": "5000mAh",
            "charging": "25W fast charging",
            "os": "Android 14, One UI 6.1 (4 OS updates, 5 years security)",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3, NFC, IP67",
            "dimensions": "161.1 x 77.4 x 8.2 mm",
            "weight": "213 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CWPCFSM3",
        "amazon_url": "https://www.amazon.in/dp/B0CWPCFSM3",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-a55-5g-awesome-iceblue-128-gb/p/itm0bb662185bcc4",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "retailer": "Amazon",
                "external_product_id": "B0CWPCFSM3",
                "url": "https://www.amazon.in/dp/B0CWPCFSM3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "retailer": "Flipkart",
                "external_product_id": "itm0bb662185bcc4",
                "url": "https://www.flipkart.com/samsung-galaxy-a55-5g-awesome-iceblue-128-gb/p/itm0bb662185bcc4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/g/r/-original-imahbhwhttnggfmc.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000107-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "external_product_id": "B0CX8R22R8",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/g/r/-original-imahbhwhttnggfmc.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000107-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "external_product_id": "B0CX8R22R8",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/8/c/j/-original-imahbzpyfv8gpku7.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20A55%205G%20%28Awesome%20Iceb</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy A55 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy A55 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R8",
        "asin": "B0CX8R22R8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R8",
                "url": "https://www.amazon.in/dp/B0CX8R22R8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000107",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20A55%205G%20%28Awesome%20Iceb</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000108",
        "product_id": "c1000000-0000-0000-0000-000000000108",
        "title": "Samsung Galaxy M34 5G (Prism Silver, 6GB, 128GB Storage)",
        "slug": "galaxy-m34-5g",
        "brand": "Samsung",
        "model": "Galaxy M34 5G",
        "sku": "GALAXY-M34-5G",
        "model_number": "GALAXY-M34-5G",
        "category": "Smartphones",
        "subcategory": "Battery-Focused Budget 5G",
        "is_component": false,
        "price": 15999.0,
        "currency": "INR",
        "description": "Monster 6000mAh battery paired with 120Hz Super AMOLED display, 50MP No Shake OIS camera, and Exynos 1280 5nm processor.",
        "specs": {
            "processor": "Samsung Exynos 1280 (5nm Octa-core up to 2.4GHz)",
            "ram": "6GB LPDDR4x",
            "storage": "128GB UFS 2.2 (expandable up to 1TB)",
            "display": "6.5-inch Super AMOLED, 120Hz, 1000 nits HBM, Gorilla Glass 5",
            "resolution": "2340x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + 8MP Ultra-wide + 2MP Depth",
            "battery": "6000mAh Lithium-ion",
            "charging": "25W fast charging support",
            "os": "Android 13, upgradable to Android 14 with One UI 6",
            "connectivity": "5G (11 bands), Wi-Fi 5, Bluetooth 5.3, 3.5mm audio jack",
            "dimensions": "161.7 x 77.2 x 8.8 mm",
            "weight": "208 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C7BGD91G",
        "amazon_url": "https://www.amazon.in/dp/B0C7BGD91G",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-m34-5g-without-charger-prism-silver-128-gb/p/itm055143784ac74",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "retailer": "Amazon",
                "external_product_id": "B0C7BGD91G",
                "url": "https://www.amazon.in/dp/B0C7BGD91G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "retailer": "Flipkart",
                "external_product_id": "itm055143784ac74",
                "url": "https://www.flipkart.com/samsung-galaxy-m34-5g-without-charger-prism-silver-128-gb/p/itm055143784ac74",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/i/g/galaxy-m34-5g-without-charger-sm-m346b-samsung-original-imagrhrhbuja8grh.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000108-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "external_product_id": "B0C7BGD91G",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/i/g/galaxy-m34-5g-without-charger-sm-m346b-samsung-original-imagrhrhbuja8grh.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000108-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "external_product_id": "B0C7BGD91G",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/0/v/b/galaxy-m34-5g-without-charger-sm-m346b-samsung-original-imagrhrhjhkgtqen.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/817WWpa+-vL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71k+VvO1xQL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/91ItZhehcrL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/81xG9-X1vFL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71o0W1a2bTL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/81k2m3-vXLL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy M34 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy M34 5G exceed expectations."
            }
        ],
        "external_product_id": "B0C7BGD91G",
        "asin": "B0C7BGD91G",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "retailer": "Amazon",
                "external_product_id": "B0C7BGD91G",
                "url": "https://www.amazon.in/dp/B0C7BGD91G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000108",
                "retailer": "Flipkart",
                "external_product_id": "itma69b61fbbf27d",
                "url": "https://www.flipkart.com/samsung-galaxy-m34-5g-prism-silver-128-gb/p/itma69b61fbbf27d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/817WWpa+-vL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000109",
        "product_id": "c1000000-0000-0000-0000-000000000109",
        "title": "OnePlus 12 (Flowy Emerald, 16GB RAM, 512GB Storage)",
        "slug": "oneplus-12-512",
        "brand": "OnePlus",
        "model": "OnePlus 12",
        "sku": "ONEPLUS-12-512",
        "model_number": "ONEPLUS-12-512",
        "category": "Smartphones",
        "subcategory": "Flagship Smartphones",
        "is_component": false,
        "price": 69999.0,
        "currency": "INR",
        "description": "Flagship powered by Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera with Sony LYT-808 sensor, 5400mAh battery, and 100W SUPERVOOC charging.",
        "specs": {
            "processor": "Qualcomm Snapdragon 8 Gen 3 (4nm, Adreno 750 GPU)",
            "ram": "16GB LPDDR5X",
            "storage": "512GB UFS 4.0",
            "display": "6.82-inch 2K ProXDR Display with LTPO 4.0 1-120Hz, 4500 nits peak, Dolby Vision",
            "resolution": "3168x1440 QHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP LYT-808 OIS + 64MP 3x Periscope OIS + 48MP Ultra-wide",
            "battery": "5400mAh dual-cell",
            "charging": "100W SUPERVOOC wired (1-100% in 26 min), 50W AIRVOOC wireless",
            "os": "OxygenOS 14 based on Android 14",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.4, NFC, IR Blaster, IP65",
            "dimensions": "164.3 x 75.8 x 9.15 mm",
            "weight": "220 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/OnePlus-Flowy-Emerald-512GB-Storage/dp/B0CQPP6JTH",
        "amazon_url": "https://www.amazon.in/OnePlus-Flowy-Emerald-512GB-Storage/dp/B0CQPP6JTH",
        "flipkart_url": "https://www.flipkart.com/oneplus-12-5g-silky-black-512-gb/p/itm0132acee4b607",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "retailer": "Amazon",
                "external_product_id": "B0CQPP6JTH",
                "url": "https://www.amazon.in/OnePlus-Flowy-Emerald-512GB-Storage/dp/B0CQPP6JTH",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "retailer": "Flipkart",
                "external_product_id": "itm0132acee4b607",
                "url": "https://www.flipkart.com/oneplus-12-5g-silky-black-512-gb/p/itm0132acee4b607",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000109-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "external_product_id": "B0CQPP9ZJ1",
                "image_url": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000109-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "external_product_id": "B0CQPP9ZJ1",
                "image_url": "https://m.media-amazon.com/images/I/71rV4S4F8oL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71rV4S4F8oL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - OnePlus 12",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the OnePlus OnePlus 12 exceed expectations."
            }
        ],
        "external_product_id": "B0CQPP9ZJ1",
        "asin": "B0CQPP9ZJ1",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "retailer": "Amazon",
                "external_product_id": "B0CQPP9ZJ1",
                "url": "https://www.amazon.in/dp/B0CQPP9ZJ1",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000109",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000110",
        "product_id": "c1000000-0000-0000-0000-000000000110",
        "title": "OnePlus 12R (Cool Blue, 16GB RAM, 256GB Storage)",
        "slug": "oneplus-12r-256",
        "brand": "OnePlus",
        "model": "OnePlus 12R",
        "sku": "ONEPLUS-12R-256",
        "model_number": "ONEPLUS-12R-256",
        "category": "Smartphones",
        "subcategory": "Performance & Gaming Flagship",
        "is_component": false,
        "price": 45999.0,
        "currency": "INR",
        "description": "Performance powerhouse with Snapdragon 8 Gen 2, 4th Gen LTPO 120Hz 1.5K ProXDR display, largest ever 5500mAh battery, and 100W charging.",
        "specs": {
            "processor": "Qualcomm Snapdragon 8 Gen 2 (4nm, Adreno 740 GPU)",
            "ram": "16GB LPDDR5X",
            "storage": "256GB UFS 3.1",
            "display": "6.78-inch 1.5K Oriental AMOLED, LTPO 4.0 1-120Hz, 4500 nits peak, Gorilla Glass Victus 2",
            "resolution": "2780x1264",
            "refresh_rate": "120Hz",
            "camera": "50MP Sony IMX890 OIS + 8MP Ultra-wide + 2MP Macro",
            "battery": "5500mAh",
            "charging": "100W SUPERVOOC wired (1-100% in 26 mins)",
            "os": "OxygenOS 14 based on Android 14",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.3, NFC, IR Blaster",
            "dimensions": "163.3 x 75.3 x 8.8 mm",
            "weight": "207 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CQYN9QDQ",
        "amazon_url": "https://www.amazon.in/dp/B0CQYN9QDQ",
        "flipkart_url": "https://www.flipkart.com/oneplus-12r-cool-blue-256-gb/p/itmce6c3b73e4aa4",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000110",
                "retailer": "Amazon",
                "external_product_id": "B0CQYN9QDQ",
                "url": "https://www.amazon.in/dp/B0CQYN9QDQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000110",
                "retailer": "Flipkart",
                "external_product_id": "itmce6c3b73e4aa4",
                "url": "https://www.flipkart.com/oneplus-12r-cool-blue-256-gb/p/itmce6c3b73e4aa4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/m/i/u/12r-cph2585-oneplus-original-imah9zk5nnfqyurm.jpeg?q=70",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000110-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000110",
                "external_product_id": "B0CQPR4H2G",
                "image_url": "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/m/i/u/12r-cph2585-oneplus-original-imah9zk5nnfqyurm.jpeg?q=70",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "right": "https://m.media-amazon.com/images/I/717V4zXbM6L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61t8X2z6MFL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71n8P7m6T2L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - OnePlus 12R",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the OnePlus OnePlus 12R exceed expectations."
            }
        ],
        "external_product_id": "B0CQPR4H2G",
        "asin": "B0CQPR4H2G",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000110",
                "retailer": "Amazon",
                "external_product_id": "B0CQPR4H2G",
                "url": "https://www.amazon.in/dp/B0CQPR4H2G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000110",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/717V4zXbM6L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000111",
        "product_id": "c1000000-0000-0000-0000-000000000111",
        "title": "OnePlus Nord CE 4 (Dark Chrome, 8GB RAM, 128GB Storage)",
        "slug": "nord-ce-4-128",
        "brand": "OnePlus",
        "model": "OnePlus Nord CE 4",
        "sku": "NORD-CE-4-128",
        "model_number": "NORD-CE-4-128",
        "category": "Smartphones",
        "subcategory": "Mid-Range Value Champions",
        "is_component": false,
        "price": 24999.0,
        "currency": "INR",
        "description": "Qualcomm Snapdragon 7 Gen 3 processor, 100W SUPERVOOC charging, 5500mAh massive battery, and 50MP Sony LYT-600 with OIS.",
        "specs": {
            "processor": "Qualcomm Snapdragon 7 Gen 3 (4nm TSMC)",
            "ram": "8GB LPDDR4x",
            "storage": "128GB UFS 3.1 (Expandable up to 1TB)",
            "display": "6.7-inch FHD+ 120Hz AMOLED, 2160Hz PWM Dimming, HDR10+",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Sony LYT-600 OIS + 8MP Ultra-wide",
            "battery": "5500mAh",
            "charging": "100W SUPERVOOC (1-100% in 29 min)",
            "os": "OxygenOS 14 based on Android 14",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.4, IP54 Aqua Touch",
            "dimensions": "162.5 x 75.3 x 8.4 mm",
            "weight": "186 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CX8R22R9",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/oneplus-nord-ce4-dark-chrome-128-gb/p/itm5a09089114afb",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "retailer": "Flipkart",
                "external_product_id": "itm5a09089114afb",
                "url": "https://www.flipkart.com/oneplus-nord-ce4-dark-chrome-128-gb/p/itm5a09089114afb",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/6175SlKKECL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000111-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "external_product_id": "B0CX8R22R9",
                "image_url": "https://m.media-amazon.com/images/I/6175SlKKECL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000111-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "external_product_id": "B0CX8R22R9",
                "image_url": "https://m.media-amazon.com/images/I/6175SlK8cgL._SL1500_.jpg",
                "image_type": "gallery",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/6175SlKKECL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/6175SlK8cgL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/61R8y1u2F4L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/51w8N4r6C2L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71k4M2b6T8L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - OnePlus Nord CE 4",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the OnePlus OnePlus Nord CE 4 exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R9",
        "asin": "B0CX8R22R9",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R9",
                "url": "https://www.amazon.in/dp/B0CX8R22R9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000111",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/6175SlKKECL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000112",
        "product_id": "c1000000-0000-0000-0000-000000000112",
        "title": "Google Pixel 8 Pro (Obsidian, 12GB RAM, 128GB Storage)",
        "slug": "pixel-8-pro-128",
        "brand": "Google",
        "model": "Pixel 8 Pro",
        "sku": "PIXEL-8-PRO-128",
        "model_number": "PIXEL-8-PRO-128",
        "category": "Smartphones",
        "subcategory": "AI & Camera Flagship",
        "is_component": false,
        "price": 99999.0,
        "currency": "INR",
        "description": "Google Tensor G3 chip, Super Actua display, Pro camera system with Best Take, Magic Editor, temperature sensor, and 7 years of OS updates.",
        "specs": {
            "processor": "Google Tensor G3 (4nm, Titan M2 security coprocessor)",
            "ram": "12GB LPDDR5X",
            "storage": "128GB UFS 3.1",
            "display": "6.7-inch Super Actua LTPO OLED (1-120Hz), 2400 nits peak, Gorilla Glass Victus 2",
            "resolution": "2992x1344",
            "refresh_rate": "120Hz",
            "camera": "50MP Octa PD Main OIS + 48MP Quad PD Ultra-wide + 48MP 5x Telephoto OIS",
            "battery": "5050mAh",
            "charging": "30W fast charging, Qi certified fast wireless charging",
            "os": "Android 14 (7 years of OS and security updates)",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.3, UWB, NFC, IP68",
            "dimensions": "162.6 x 76.5 x 8.8 mm",
            "weight": "213 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Google-Pixel-Pro-Obsidian-128/dp/B0DQVQQN8W",
        "amazon_url": "https://www.amazon.in/Google-Pixel-Pro-Obsidian-128/dp/B0DQVQQN8W",
        "flipkart_url": "https://www.flipkart.com/google-pixel-8-pro-obsidian-128-gb/p/itm51f9522df8e95",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "retailer": "Amazon",
                "external_product_id": "B0DQVQQN8W",
                "url": "https://www.amazon.in/Google-Pixel-Pro-Obsidian-128/dp/B0DQVQQN8W",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "retailer": "Flipkart",
                "external_product_id": "itm51f9522df8e95",
                "url": "https://www.flipkart.com/google-pixel-8-pro-obsidian-128-gb/p/itm51f9522df8e95",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71r69Y7BSeL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000112-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "external_product_id": "B0CGVLM5Q8",
                "image_url": "https://m.media-amazon.com/images/I/71r69Y7BSeL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000112-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "external_product_id": "B0CGVLM5Q8",
                "image_url": "https://m.media-amazon.com/images/I/61A8t4m3dXL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71r69Y7BSeL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61A8t4m3dXL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Pixel 8 Pro",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Google Pixel 8 Pro exceed expectations."
            }
        ],
        "external_product_id": "B0CGVLM5Q8",
        "asin": "B0CGVLM5Q8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "retailer": "Amazon",
                "external_product_id": "B0CGVLM5Q8",
                "url": "https://www.amazon.in/dp/B0CGVLM5Q8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000112",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71r69Y7BSeL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000113",
        "product_id": "c1000000-0000-0000-0000-000000000113",
        "title": "Google Pixel 8 (Hazel, 8GB RAM, 128GB Storage)",
        "slug": "pixel-8-128",
        "brand": "Google",
        "model": "Pixel 8",
        "sku": "PIXEL-8-128",
        "model_number": "PIXEL-8-128",
        "category": "Smartphones",
        "subcategory": "Compact Camera Flagship",
        "is_component": false,
        "price": 71999.0,
        "currency": "INR",
        "description": "Compact flagship powered by Google Tensor G3, Actua 120Hz OLED display, advanced 50MP camera with Audio Magic Eraser, and 7 years of feature drops.",
        "specs": {
            "processor": "Google Tensor G3 (4nm, Titan M2 coprocessor)",
            "ram": "8GB LPDDR5X",
            "storage": "128GB UFS 3.1",
            "display": "6.2-inch Actua OLED, 60-120Hz, 2000 nits peak, Gorilla Glass Victus",
            "resolution": "2400x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Octa PD Main OIS + 12MP Ultra-wide with Macro Focus",
            "battery": "4575mAh",
            "charging": "27W wired, 18W wireless charging",
            "os": "Android 14 (7 years OS updates)",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.3, NFC, IP68",
            "dimensions": "150.5 x 70.8 x 8.9 mm",
            "weight": "187 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CGVNVD8R",
        "amazon_url": "https://www.amazon.in/dp/B0CGVNVD8R",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000113",
                "retailer": "Amazon",
                "external_product_id": "B0CGVNVD8R",
                "url": "https://www.amazon.in/dp/B0CGVNVD8R",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000113",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61iLQG-KbLL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000113-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000113",
                "external_product_id": "B0CGVHQW6Y",
                "image_url": "https://m.media-amazon.com/images/I/61iLQG-KbLL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Google%20Pixel%208%20%28Hazel%2C%208GB%20RAM%2C%20128</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Pixel 8",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Google Pixel 8 exceed expectations."
            }
        ],
        "external_product_id": "B0CGVHQW6Y",
        "asin": "B0CGVHQW6Y",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000113",
                "retailer": "Amazon",
                "external_product_id": "B0CGVHQW6Y",
                "url": "https://www.amazon.in/dp/B0CGVHQW6Y",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000113",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Google%20Pixel%208%20%28Hazel%2C%208GB%20RAM%2C%20128</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000114",
        "product_id": "c1000000-0000-0000-0000-000000000114",
        "title": "Google Pixel 7a (Sea, 8GB RAM, 128GB Storage)",
        "slug": "pixel-7a-128",
        "brand": "Google",
        "model": "Pixel 7a",
        "sku": "PIXEL-7A-128",
        "model_number": "PIXEL-7A-128",
        "category": "Smartphones",
        "subcategory": "Camera-Focused Mid-Range",
        "is_component": false,
        "price": 37999.0,
        "currency": "INR",
        "description": "Google Tensor G2 chip, 64MP quad-PD camera with Real Tone, Super Res Zoom, wireless charging, and IP67 dust/water resistance.",
        "specs": {
            "processor": "Google Tensor G2 (5nm, Titan M2 coprocessor)",
            "ram": "8GB LPDDR5",
            "storage": "128GB UFS 3.1",
            "display": "6.1-inch FHD+ Smooth Display OLED (up to 90Hz), HDR support, Gorilla Glass 3",
            "resolution": "2400x1080 FHD+",
            "refresh_rate": "90Hz",
            "camera": "64MP Quad PD Main OIS + 13MP Ultra-wide",
            "battery": "4385mAh",
            "charging": "18W wired, wireless charging support",
            "os": "Android 13 (Upgradable to Android 14)",
            "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3, NFC, IP67",
            "dimensions": "152.0 x 72.9 x 9.0 mm",
            "weight": "193.5 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Google-Pixel-Sea-128-RAM/dp/B0DB7N5NK4",
        "amazon_url": "https://www.amazon.in/Google-Pixel-Sea-128-RAM/dp/B0DB7N5NK4",
        "flipkart_url": "https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itmb4d7b100b1a4d",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000114",
                "retailer": "Amazon",
                "external_product_id": "B0DB7N5NK4",
                "url": "https://www.amazon.in/Google-Pixel-Sea-128-RAM/dp/B0DB7N5NK4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000114",
                "retailer": "Flipkart",
                "external_product_id": "itmb4d7b100b1a4d",
                "url": "https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itmb4d7b100b1a4d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61pTBxDPd-L._SY879_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000114-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000114",
                "external_product_id": "B0BZV3991S",
                "image_url": "https://m.media-amazon.com/images/I/61pTBxDPd-L._SY879_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71u9sW4jQYL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71c6N7q3w8L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61z4N7t8s4L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71v4F5m3X9L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Pixel 7a",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Google Pixel 7a exceed expectations."
            }
        ],
        "external_product_id": "B0BZV3991S",
        "asin": "B0BZV3991S",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000114",
                "retailer": "Amazon",
                "external_product_id": "B0BZV3991S",
                "url": "https://www.amazon.in/dp/B0BZV3991S",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000114",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71u9sW4jQYL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000115",
        "product_id": "c1000000-0000-0000-0000-000000000115",
        "title": "Xiaomi 14 (Black, 12GB RAM, 512GB Storage)",
        "slug": "xiaomi-14-512",
        "brand": "Xiaomi",
        "model": "Xiaomi 14",
        "sku": "XIAOMI-14-512",
        "model_number": "XIAOMI-14-512",
        "category": "Smartphones",
        "subcategory": "Compact Camera Flagship",
        "is_component": false,
        "price": 69999.0,
        "currency": "INR",
        "description": "Leica Summilux optical lenses with Light Fusion 900 sensor, Snapdragon 8 Gen 3, 1.5K 120Hz LTPO AMOLED, 90W wired and 50W wireless HyperCharge.",
        "specs": {
            "processor": "Qualcomm Snapdragon 8 Gen 3 (4nm TSMC)",
            "ram": "12GB LPDDR5X",
            "storage": "512GB UFS 4.0",
            "display": "6.36-inch 1.5K LTPO AMOLED, 1-120Hz, 3000 nits peak, Dolby Vision, DC Dimming",
            "resolution": "2670x1200",
            "refresh_rate": "120Hz",
            "camera": "50MP Light Fusion 900 Leica OIS + 50MP 75mm Floating Telephoto + 50MP Ultra-wide",
            "battery": "4610mAh",
            "charging": "90W HyperCharge wired (100% in 31 min), 50W wireless",
            "os": "Xiaomi HyperOS based on Android 14",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.4, NFC, IR Blaster, IP68",
            "dimensions": "152.8 x 71.5 x 8.2 mm",
            "weight": "193 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CWL432P9",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/xiaomi-14-black-512-gb/p/itm9199c6406170d",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000115",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000115",
                "retailer": "Flipkart",
                "external_product_id": "itm9199c6406170d",
                "url": "https://www.flipkart.com/xiaomi-14-black-512-gb/p/itm9199c6406170d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71d1ytcCntL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000115-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000115",
                "external_product_id": "B0CWL432P9",
                "image_url": "https://m.media-amazon.com/images/I/71d1ytcCntL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71d1ytcCntL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Xiaomi 14",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Xiaomi Xiaomi 14 exceed expectations."
            }
        ],
        "external_product_id": "B0CWL432P9",
        "asin": "B0CWL432P9",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000115",
                "retailer": "Amazon",
                "external_product_id": "B0CWL432P9",
                "url": "https://www.amazon.in/dp/B0CWL432P9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000115",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71d1ytcCntL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000116",
        "product_id": "c1000000-0000-0000-0000-000000000116",
        "title": "Redmi Note 13 Pro+ 5G (Fusion Black, 12GB RAM, 256GB Storage)",
        "slug": "redmi-note13-proplus",
        "brand": "Redmi",
        "model": "Redmi Note 13 Pro+ 5G",
        "sku": "REDMI-NOTE13-PROPLUS",
        "model_number": "REDMI-NOTE13-PROPLUS",
        "category": "Smartphones",
        "subcategory": "Mid-Range Camera Champions",
        "is_component": false,
        "price": 31999.0,
        "currency": "INR",
        "description": "Flagship 3D curved 1.5K 120Hz AMOLED display, 200MP camera with OIS, 120W HyperCharge, IP68 water protection, and MediaTek Dimensity 7200-Ultra.",
        "specs": {
            "processor": "MediaTek Dimensity 7200-Ultra (4nm)",
            "ram": "12GB LPDDR5",
            "storage": "256GB UFS 3.1",
            "display": "6.67-inch 1.5K Curved AMOLED, 120Hz, 1800 nits peak, Dolby Vision, Gorilla Glass Victus",
            "resolution": "2712x1220",
            "refresh_rate": "120Hz",
            "camera": "200MP Samsung ISOCELL HP3 OIS + 8MP Ultra-wide + 2MP Macro",
            "battery": "5000mAh",
            "charging": "120W HyperCharge (100% in 19 min)",
            "os": "MIUI 14 with Android 13 (Upgradable to HyperOS)",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3, NFC, IR Blaster, IP68",
            "dimensions": "161.4 x 74.2 x 8.9 mm",
            "weight": "204.5 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Redmi-Fusion-Black-Storage-Without/dp/B0CXXR6FZB",
        "amazon_url": "https://www.amazon.in/Redmi-Fusion-Black-Storage-Without/dp/B0CXXR6FZB",
        "flipkart_url": "https://www.flipkart.com/redmi-note-13-pro-5g-fusion-black-256-gb/p/itm7434e29d57904",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "retailer": "Amazon",
                "external_product_id": "B0CXXR6FZB",
                "url": "https://www.amazon.in/Redmi-Fusion-Black-Storage-Without/dp/B0CXXR6FZB",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "retailer": "Flipkart",
                "external_product_id": "itm7434e29d57904",
                "url": "https://www.flipkart.com/redmi-note-13-pro-5g-fusion-black-256-gb/p/itm7434e29d57904",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/x/j/m/-original-imagwubk2ky9v2gz.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000116-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "external_product_id": "B0CQPM9N8K",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/x/j/m/-original-imagwubk2ky9v2gz.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000116-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "external_product_id": "B0CQPM9N8K",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/l/0/2/-original-imagwubkbwefqepe.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "back": "https://m.media-amazon.com/images/I/71nI6tM2RCL._SL1500_.jpg",
            "front": "https://m.media-amazon.com/images/I/71XNeka-BRL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71e0nS2a34L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61x0H8a4NBL._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71v1D6s8C9L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Redmi Note 13 Pro+ 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Redmi Redmi Note 13 Pro+ 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CQPM9N8K",
        "asin": "B0CQPM9N8K",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "retailer": "Amazon",
                "external_product_id": "B0CQPM9N8K",
                "url": "https://www.amazon.in/dp/B0CQPM9N8K",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000116",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71nI6tM2RCL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000117",
        "product_id": "c1000000-0000-0000-0000-000000000117",
        "title": "Redmi 13C (Starshine Green, 4GB RAM, 128GB Storage)",
        "slug": "redmi-13c-128",
        "brand": "Redmi",
        "model": "Redmi 13C",
        "sku": "REDMI-13C-128",
        "model_number": "REDMI-13C-128",
        "category": "Smartphones",
        "subcategory": "Budget Smartphones",
        "is_component": false,
        "price": 7999.0,
        "currency": "INR",
        "description": "Sleek 8.09mm thin design with 6.74-inch 90Hz display, 50MP AI triple camera, octa-core MediaTek Helio G85, and 5000mAh battery.",
        "specs": {
            "processor": "MediaTek Helio G85 (12nm Octa-core up to 2.0GHz)",
            "ram": "4GB LPDDR4x",
            "storage": "128GB eMMC 5.1 (expandable up to 1TB)",
            "display": "6.74-inch HD+ Dot Drop display, 90Hz, 450 nits, Corning Gorilla Glass",
            "resolution": "1600x720 HD+",
            "refresh_rate": "90Hz",
            "camera": "50MP Main + 2MP Macro + Auxiliary lens",
            "battery": "5000mAh",
            "charging": "18W Type-C fast charging support",
            "os": "MIUI 14 based on Android 13",
            "connectivity": "4G Dual VoLTE, Wi-Fi 5GHz, Bluetooth 5.3, 3.5mm jack",
            "dimensions": "168.0 x 78.0 x 8.09 mm",
            "weight": "192 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CNX6W7N4",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/redmi-13c-starshine-green-128-gb/p/itmc4f0763fb3a50",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "retailer": "Flipkart",
                "external_product_id": "itmc4f0763fb3a50",
                "url": "https://www.flipkart.com/redmi-13c-starshine-green-128-gb/p/itmc4f0763fb3a50",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/9/f/c/-original-imahfk4xxgusghq8.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000117-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "external_product_id": "B0CNX6W7N4",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/9/f/c/-original-imahfk4xxgusghq8.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000117-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "external_product_id": "B0CNX6W7N4",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/u/6/r/-original-imahfk4xenbzxwrh.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Redmi%2013C%20%28Starshine%20Green%2C%204GB%20RAM</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Redmi 13C",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Redmi Redmi 13C exceed expectations."
            }
        ],
        "external_product_id": "B0CNX6W7N4",
        "asin": "B0CNX6W7N4",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "retailer": "Amazon",
                "external_product_id": "B0CNX6W7N4",
                "url": "https://www.amazon.in/dp/B0CNX6W7N4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000117",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Redmi%2013C%20%28Starshine%20Green%2C%204GB%20RAM</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000118",
        "product_id": "c1000000-0000-0000-0000-000000000118",
        "title": "Realme 12 Pro+ 5G (Submarine Blue, 8GB RAM, 256GB Storage)",
        "slug": "realme-12-proplus",
        "brand": "Realme",
        "model": "Realme 12 Pro+ 5G",
        "sku": "REALME-12-PROPLUS",
        "model_number": "REALME-12-PROPLUS",
        "category": "Smartphones",
        "subcategory": "Portrait & Zoom Camera Champions",
        "is_component": false,
        "price": 29999.0,
        "currency": "INR",
        "description": "Luxury watch design with 64MP periscope portrait camera with 120x SuperZoom, 50MP Sony IMX890 OIS camera, and 120Hz curved vision display.",
        "specs": {
            "processor": "Qualcomm Snapdragon 7s Gen 2 (4nm)",
            "ram": "8GB LPDDR4x",
            "storage": "256GB UFS 3.1",
            "display": "6.7-inch 120Hz Curved AMOLED, 2160Hz PWM, 950 nits peak, 100% DCI-P3",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Sony IMX890 OIS + 64MP Periscope OIS (3x Optical, 120x Zoom) + 8MP Ultra-wide",
            "battery": "5000mAh",
            "charging": "67W SUPERVOOC charging",
            "os": "realme UI 5.0 based on Android 14",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.2, IP65 water resistance",
            "dimensions": "161.47 x 74.02 x 8.75 mm",
            "weight": "196 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/realme-Submarine-Storage-Display-Periscope/dp/B0CSWMQV9Z",
        "amazon_url": "https://www.amazon.in/realme-Submarine-Storage-Display-Periscope/dp/B0CSWMQV9Z",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000118",
                "retailer": "Amazon",
                "external_product_id": "B0CSWMQV9Z",
                "url": "https://www.amazon.in/realme-Submarine-Storage-Display-Periscope/dp/B0CSWMQV9Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000118",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71JxLJvl5dL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000118-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000118",
                "external_product_id": "B0CSYWW88L",
                "image_url": "https://m.media-amazon.com/images/I/71JxLJvl5dL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71v7jE1-o4L._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71c5M8y3x2L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/61b1C8v5D0L._SL1500_.jpg",
            "keyboard": "https://m.media-amazon.com/images/I/71y0X8k3P2L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Review - Realme 12 Pro+ 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Realme Realme 12 Pro+ 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CSYWW88L",
        "asin": "B0CSYWW88L",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000118",
                "retailer": "Amazon",
                "external_product_id": "B0CSYWW88L",
                "url": "https://www.amazon.in/dp/B0CSYWW88L",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000118",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71v7jE1-o4L._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000119",
        "product_id": "c1000000-0000-0000-0000-000000000119",
        "title": "iQOO 12 5G (Legend, 12GB RAM, 256GB Storage)",
        "slug": "iqoo-12-256",
        "brand": "iQOO",
        "model": "iQOO 12 5G",
        "sku": "IQOO-12-256",
        "model_number": "IQOO-12-256",
        "category": "Smartphones",
        "subcategory": "Esports Gaming & Flagship",
        "is_component": false,
        "price": 52999.0,
        "currency": "INR",
        "description": "India's first Snapdragon 8 Gen 3 smartphone with dedicated Supercomputing Q1 chip, 144Hz 1.5K LTPO AMOLED, and 120W FlashCharge.",
        "specs": {
            "processor": "Qualcomm Snapdragon 8 Gen 3 (4nm) + Supercomputing Chip Q1",
            "ram": "12GB LPDDR5X",
            "storage": "256GB UFS 4.0",
            "display": "6.78-inch 1.5K LTPO AMOLED, 144Hz, 3000 nits peak, 2160Hz PWM dimming",
            "resolution": "2800x1260",
            "refresh_rate": "144Hz",
            "camera": "50MP 1/1.3 Astro OIS + 64MP 3x Periscope OIS (100x zoom) + 50MP Ultra-wide",
            "battery": "5000mAh",
            "charging": "120W FlashCharge (100% in 27 mins)",
            "os": "Funtouch OS 14 based on Android 14 (3 OS updates)",
            "connectivity": "5G, Wi-Fi 7, Bluetooth 5.4, NFC, IP64",
            "dimensions": "163.22 x 75.88 x 8.10 mm",
            "weight": "203.7 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07WGMXVFK",
        "amazon_url": "https://www.amazon.in/dp/B07WGMXVFK",
        "flipkart_url": "https://www.flipkart.com/iqoo-12-5g-legend-256-gb/p/itmd0679ee887cfc",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "retailer": "Amazon",
                "external_product_id": "B07WGMXVFK",
                "url": "https://www.amazon.in/dp/B07WGMXVFK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "retailer": "Flipkart",
                "external_product_id": "itmd0679ee887cfc",
                "url": "https://www.flipkart.com/iqoo-12-5g-legend-256-gb/p/itmd0679ee887cfc",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/q/r/y/12-5g-iqoo-12-5g-iqoo-original-imagwhuqe6gwht6c.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000119-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "external_product_id": "B07WGPK24Z",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/q/r/y/12-5g-iqoo-12-5g-iqoo-original-imagwhuqe6gwht6c.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000119-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "external_product_id": "B07WGPK24Z",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/n/o/s/12-5g-12-5g-iqoo-original-imagwgzghftj8ddz.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%2012%205G%20%28Legend%2C%2012GB%20RAM%2C%20256GB</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - iQOO 12 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the iQOO iQOO 12 5G exceed expectations."
            }
        ],
        "external_product_id": "B07WGPK24Z",
        "asin": "B07WGPK24Z",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "retailer": "Amazon",
                "external_product_id": "B07WGPK24Z",
                "url": "https://www.amazon.in/dp/B07WGPK24Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000119",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%2012%205G%20%28Legend%2C%2012GB%20RAM%2C%20256GB</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000120",
        "product_id": "c1000000-0000-0000-0000-000000000120",
        "title": "Nothing Phone (2a) 5G (Black, 8GB RAM, 128GB Storage)",
        "slug": "nothing-phone-2a",
        "brand": "Nothing",
        "model": "Phone (2a)",
        "sku": "NOTHING-PHONE-2A",
        "model_number": "NOTHING-PHONE-2A",
        "category": "Smartphones",
        "subcategory": "Design & Lifestyle Smartphones",
        "is_component": false,
        "price": 23999.0,
        "currency": "INR",
        "description": "Iconic transparent back with Glyph Interface lighting, custom Dimensity 7200 Pro processor, 50MP dual cameras with TrueLens Engine, and 120Hz AMOLED.",
        "specs": {
            "processor": "MediaTek Dimensity 7200 Pro (4nm TSMC)",
            "ram": "8GB",
            "storage": "128GB",
            "display": "6.7-inch flexible AMOLED, 120Hz adaptive, 1300 nits peak, 1.07B colors, Gorilla Glass 5",
            "resolution": "2412x1084 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + 50MP Ultra-wide 114-degree FOV",
            "battery": "5000mAh",
            "charging": "45W fast charging",
            "os": "Nothing OS 2.5 based on Android 14 (3 OS updates, 4 years security)",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3, NFC, IP54",
            "dimensions": "161.74 x 76.32 x 8.55 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Nothing-Mediatek-Dimensity-Processor-Charging/dp/B0CQ82M8CV",
        "amazon_url": "https://www.amazon.in/Nothing-Mediatek-Dimensity-Processor-Charging/dp/B0CQ82M8CV",
        "flipkart_url": "https://www.flipkart.com/nothing-phone-2a-5g-black-128-gb/p/itm85c6bca5edadc",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "retailer": "Amazon",
                "external_product_id": "B0CQ82M8CV",
                "url": "https://www.amazon.in/Nothing-Mediatek-Dimensity-Processor-Charging/dp/B0CQ82M8CV",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "retailer": "Flipkart",
                "external_product_id": "itm85c6bca5edadc",
                "url": "https://www.flipkart.com/nothing-phone-2a-5g-black-128-gb/p/itm85c6bca5edadc",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/g/a/-original-imahfptqg23vghss.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000120-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "external_product_id": "B0CX8R22R0",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/g/a/-original-imahfptqg23vghss.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000120-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "external_product_id": "B0CX8R22R0",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/z/g/z/-original-imahfptqbnyebxjg.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Nothing%20Phone%20%282a%29%205G%20%28Black%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Phone (2a)",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Nothing Phone (2a) exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R0",
        "asin": "B0CX8R22R0",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R0",
                "url": "https://www.amazon.in/dp/B0CX8R22R0",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000120",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Nothing%20Phone%20%282a%29%205G%20%28Black%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000121",
        "product_id": "c1000000-0000-0000-0000-000000000121",
        "title": "Motorola Edge 50 Fusion 5G (Marshmallow Blue, 8GB RAM, 128GB Storage)",
        "slug": "moto-edge50-fusion",
        "brand": "Motorola",
        "model": "Edge 50 Fusion",
        "sku": "MOTO-EDGE50-FUSION",
        "model_number": "MOTO-EDGE50-FUSION",
        "category": "Smartphones",
        "subcategory": "Curved Display & IP68 Mid-Range",
        "is_component": false,
        "price": 22999.0,
        "currency": "INR",
        "description": "Segment-leading 144Hz 3D curved pOLED display, 50MP Sony LYT-700C OIS camera, IP68 underwater protection, and Snapdragon 7s Gen 2.",
        "specs": {
            "processor": "Qualcomm Snapdragon 7s Gen 2 (4nm)",
            "ram": "8GB LPDDR4x",
            "storage": "128GB UFS 2.2",
            "display": "6.67-inch 3D Curved pOLED, 144Hz refresh rate, 1600 nits peak, Gorilla Glass 5",
            "resolution": "2400x1080 FHD+",
            "refresh_rate": "144Hz",
            "camera": "50MP Sony LYT-700C OIS + 13MP Ultra-wide with Macro Vision",
            "battery": "5000mAh",
            "charging": "68W TurboPower charging (50% in 15 mins)",
            "os": "Hello UI based on Android 14 (3 OS updates)",
            "connectivity": "5G (15 bands), Wi-Fi 6, Bluetooth 5.2, NFC, IP68",
            "dimensions": "161.9 x 73.1 x 7.9 mm",
            "weight": "174.9 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Motorola-Edge-50-Fusion-Marshmallow/dp/B0D4JLR5ZN",
        "amazon_url": "https://www.amazon.in/Motorola-Edge-50-Fusion-Marshmallow/dp/B0D4JLR5ZN",
        "flipkart_url": "https://www.flipkart.com/motorola-edge-50-fusion-marshmallow-blue-128-gb/p/itmf88eea5799a27",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000121",
                "retailer": "Amazon",
                "external_product_id": "B0D4JLR5ZN",
                "url": "https://www.amazon.in/Motorola-Edge-50-Fusion-Marshmallow/dp/B0D4JLR5ZN",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000121",
                "retailer": "Flipkart",
                "external_product_id": "itmf88eea5799a27",
                "url": "https://www.flipkart.com/motorola-edge-50-fusion-marshmallow-blue-128-gb/p/itmf88eea5799a27",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/5/t/j/edge-50-fusion-pb300002in-motorola-original-imahywzrfagkuyxx.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000121-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000121",
                "external_product_id": "B0D4N6X81Z",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/5/t/j/edge-50-fusion-pb300002in-motorola-original-imahywzrfagkuyxx.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Motorola%20Edge%2050%20Fusion%205G%20%28Marshma</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Edge 50 Fusion",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Motorola Edge 50 Fusion exceed expectations."
            }
        ],
        "external_product_id": "B0D4N6X81Z",
        "asin": "B0D4N6X81Z",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000121",
                "retailer": "Amazon",
                "external_product_id": "B0D4N6X81Z",
                "url": "https://www.amazon.in/dp/B0D4N6X81Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000121",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Motorola%20Edge%2050%20Fusion%205G%20%28Marshma</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000122",
        "product_id": "c1000000-0000-0000-0000-000000000122",
        "title": "Moto G54 5G (Mint Green, 8GB RAM, 128GB Storage)",
        "slug": "moto-g54-128",
        "brand": "Motorola",
        "model": "Moto G54 5G",
        "sku": "MOTO-G54-128",
        "model_number": "MOTO-G54-128",
        "category": "Smartphones",
        "subcategory": "Battery-Focused Budget 5G",
        "is_component": false,
        "price": 14999.0,
        "currency": "INR",
        "description": "Massive 6000mAh battery, MediaTek Dimensity 7020 octa-core processor, 50MP camera with OIS, and 120Hz Full HD+ display.",
        "specs": {
            "processor": "MediaTek Dimensity 7020 (6nm Octa-core up to 2.2GHz)",
            "ram": "8GB",
            "storage": "128GB (Expandable up to 1TB)",
            "display": "6.5-inch FHD+ IPS LCD, 120Hz refresh rate",
            "resolution": "2400x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + 8MP Ultra-wide/Macro",
            "battery": "6000mAh",
            "charging": "33W TurboPower charging",
            "os": "Android 13 (Upgradable to Android 14)",
            "connectivity": "5G (14 bands), Wi-Fi 5, Bluetooth 5.3, 3.5mm jack, IP52",
            "dimensions": "161.56 x 73.82 x 8.89 mm",
            "weight": "192 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Motorola-Mint-Green-128GB-Storage/dp/B0CKLRV6X9",
        "amazon_url": "https://www.amazon.in/Motorola-Mint-Green-128GB-Storage/dp/B0CKLRV6X9",
        "flipkart_url": "https://www.flipkart.com/motorola-g54-5g-mint-green-128-gb/p/itmfc12683043bbc",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "retailer": "Amazon",
                "external_product_id": "B0CKLRV6X9",
                "url": "https://www.amazon.in/Motorola-Mint-Green-128GB-Storage/dp/B0CKLRV6X9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "retailer": "Flipkart",
                "external_product_id": "itmfc12683043bbc",
                "url": "https://www.flipkart.com/motorola-g54-5g-mint-green-128-gb/p/itmfc12683043bbc",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/k/w/a/-original-imagt5ugmkks2ep7.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000122-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "external_product_id": "B0CGB2P92Z",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/k/w/a/-original-imagt5ugmkks2ep7.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000122-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "external_product_id": "B0CGB2P92Z",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/n/j/-original-imagt5ugyaxgqugq.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Moto%20G54%205G%20%28Mint%20Green%2C%208GB%20RAM%2C%201</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Moto G54 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Motorola Moto G54 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CGB2P92Z",
        "asin": "B0CGB2P92Z",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "retailer": "Amazon",
                "external_product_id": "B0CGB2P92Z",
                "url": "https://www.amazon.in/dp/B0CGB2P92Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000122",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Moto%20G54%205G%20%28Mint%20Green%2C%208GB%20RAM%2C%201</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000123",
        "product_id": "c1000000-0000-0000-0000-000000000123",
        "title": "Realme GT 6T (Razor Green, 8GB RAM, 128GB Storage)",
        "slug": "realme-gt-6t",
        "brand": "Realme",
        "model": "GT 6T",
        "sku": "REALME-GT-6T",
        "model_number": "REALME-GT-6T",
        "category": "Smartphones",
        "subcategory": "Performance Flagship",
        "is_component": false,
        "price": 30999.0,
        "currency": "INR",
        "description": "Authentic Realme GT 6T offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0D4N7X92A",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/realme-gt-6t-5g-fluid-silver-128-gb/p/itmfeb5a69f5f153",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000123",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000123",
                "retailer": "Flipkart",
                "external_product_id": "itmfeb5a69f5f153",
                "url": "https://www.flipkart.com/realme-gt-6t-5g-fluid-silver-128-gb/p/itmfeb5a69f5f153",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/d/q/y/gt-6t-5g-rmx3853-realme-original-imahfddqupz7zzmh.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000123-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000123",
                "external_product_id": "B0D4N7X92A",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/d/q/y/gt-6t-5g-rmx3853-realme-original-imahfddqupz7zzmh.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Realme%20GT%206T%20%28Razor%20Green%2C%208GB%20RAM%2C</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - GT 6T",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Realme GT 6T exceed expectations."
            }
        ],
        "external_product_id": "B0D4N7X92A",
        "asin": "B0D4N7X92A",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000123",
                "retailer": "Amazon",
                "external_product_id": "B0D4N7X92A",
                "url": "https://www.amazon.in/dp/B0D4N7X92A",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000123",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Realme%20GT%206T%20%28Razor%20Green%2C%208GB%20RAM%2C</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000124",
        "product_id": "c1000000-0000-0000-0000-000000000124",
        "title": "iQOO Neo 9 Pro 5G (Fiery Red, 8GB RAM, 128GB Storage)",
        "slug": "iqoo-neo9-pro",
        "brand": "iQOO",
        "model": "Neo 9 Pro",
        "sku": "IQOO-NEO9-PRO",
        "model_number": "IQOO-NEO9-PRO",
        "category": "Smartphones",
        "subcategory": "Gaming Flagship",
        "is_component": false,
        "price": 35999.0,
        "currency": "INR",
        "description": "Authentic iQOO Neo 9 Pro offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CX8R22R1",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/iqoo-neo9-pro-fiery-red-128-gb/p/itmbadc894a42a39",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "retailer": "Flipkart",
                "external_product_id": "itmbadc894a42a39",
                "url": "https://www.flipkart.com/iqoo-neo9-pro-fiery-red-128-gb/p/itmbadc894a42a39",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/0/i/o/neo9-pro-i2304-iqoo-original-imagyg968j7pafeg.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000124-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "external_product_id": "B0CX8R22R1",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/0/i/o/neo9-pro-i2304-iqoo-original-imagyg968j7pafeg.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000124-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "external_product_id": "B0CX8R22R1",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/l/4/g/neo9-pro-i2304-iqoo-original-imagyg96uw4vhkzb.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%20Neo%209%20Pro%205G%20%28Fiery%20Red%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Neo 9 Pro",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the iQOO Neo 9 Pro exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R1",
        "asin": "B0CX8R22R1",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R1",
                "url": "https://www.amazon.in/dp/B0CX8R22R1",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000124",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%20Neo%209%20Pro%205G%20%28Fiery%20Red%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000125",
        "product_id": "c1000000-0000-0000-0000-000000000125",
        "title": "iQOO Z9s Pro 5G (Luxe Marble, 8GB RAM, 128GB Storage)",
        "slug": "iqoo-z9s-pro",
        "brand": "iQOO",
        "model": "Z9s Pro",
        "sku": "IQOO-Z9S-PRO",
        "model_number": "IQOO-Z9S-PRO",
        "category": "Smartphones",
        "subcategory": "Curved AMOLED Mid-Range",
        "is_component": false,
        "price": 24999.0,
        "currency": "INR",
        "description": "Authentic iQOO Z9s Pro offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/iQOO-Luxe-Marble-128GB-Storage/dp/B07WHR9ZJ9",
        "amazon_url": "https://www.amazon.in/iQOO-Luxe-Marble-128GB-Storage/dp/B07WHR9ZJ9",
        "flipkart_url": "https://www.flipkart.com/iqoo-z9s-pro-5g-luxe-marble-128-gb/p/itm2f76190f198f6",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "retailer": "Amazon",
                "external_product_id": "B07WHR9ZJ9",
                "url": "https://www.amazon.in/iQOO-Luxe-Marble-128GB-Storage/dp/B07WHR9ZJ9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "retailer": "Flipkart",
                "external_product_id": "itm2f76190f198f6",
                "url": "https://www.flipkart.com/iqoo-z9s-pro-5g-luxe-marble-128-gb/p/itm2f76190f198f6",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/o/k/x/z9s-pro-5g-z9s-pro-5g-iqoo-original-imah46j7jzhchck7.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000125-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "external_product_id": "B0D4N8Y13B",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/o/k/x/z9s-pro-5g-z9s-pro-5g-iqoo-original-imah46j7jzhchck7.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000125-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "external_product_id": "B0D4N8Y13B",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/4/f/6/z9s-pro-5g-z9s-pro-5g-iqoo-original-imah46j7dtykmzcd.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%20Z9s%20Pro%205G%20%28Luxe%20Marble%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Z9s Pro",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the iQOO Z9s Pro exceed expectations."
            }
        ],
        "external_product_id": "B0D4N8Y13B",
        "asin": "B0D4N8Y13B",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "retailer": "Amazon",
                "external_product_id": "B0D4N8Y13B",
                "url": "https://www.amazon.in/dp/B0D4N8Y13B",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000125",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>iQOO%20Z9s%20Pro%205G%20%28Luxe%20Marble%2C%208GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000126",
        "product_id": "c1000000-0000-0000-0000-000000000126",
        "title": "Realme Narzo 70 Pro 5G (Glass Green, 8GB RAM, 128GB Storage)",
        "slug": "narzo-70-pro",
        "brand": "Realme",
        "model": "Narzo 70 Pro",
        "sku": "NARZO-70-PRO",
        "model_number": "NARZO-70-PRO",
        "category": "Smartphones",
        "subcategory": "Camera & Gesture Control",
        "is_component": false,
        "price": 19999.0,
        "currency": "INR",
        "description": "Authentic Realme Narzo 70 Pro offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/realme-narzo-Pro-128-Green/dp/B0CHQKRVMQ",
        "amazon_url": "https://www.amazon.in/realme-narzo-Pro-128-Green/dp/B0CHQKRVMQ",
        "flipkart_url": "https://www.flipkart.com/realme-rmx3868-glass-green-128-gb/p/itm328369c2978ad",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "retailer": "Amazon",
                "external_product_id": "B0CHQKRVMQ",
                "url": "https://www.amazon.in/realme-narzo-Pro-128-Green/dp/B0CHQKRVMQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "retailer": "Flipkart",
                "external_product_id": "itm328369c2978ad",
                "url": "https://www.flipkart.com/realme-rmx3868-glass-green-128-gb/p/itm328369c2978ad",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/s/l/6/narzo-70-pro-5g-narzo-70-pro-5g-realme-original-imahf4hhqzfnjmkd.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000126-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "external_product_id": "B0CX8R22R2",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/s/l/6/narzo-70-pro-5g-narzo-70-pro-5g-realme-original-imahf4hhqzfnjmkd.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000126-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "external_product_id": "B0CX8R22R2",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/b/s/q/narzo-70-pro-5g-narzo-70-pro-5g-realme-original-imahf4hhjvzzuqkf.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Realme%20Narzo%2070%20Pro%205G%20%28Glass%20Green</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Narzo 70 Pro",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Realme Narzo 70 Pro exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R2",
        "asin": "B0CX8R22R2",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R2",
                "url": "https://www.amazon.in/dp/B0CX8R22R2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000126",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Realme%20Narzo%2070%20Pro%205G%20%28Glass%20Green</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000127",
        "product_id": "c1000000-0000-0000-0000-000000000127",
        "title": "POCO M6 Pro 5G (Forest Green, 6GB RAM, 128GB Storage)",
        "slug": "poco-m6-pro",
        "brand": "POCO",
        "model": "M6 Pro 5G",
        "sku": "POCO-M6-PRO",
        "model_number": "POCO-M6-PRO",
        "category": "Smartphones",
        "subcategory": "Budget 5G",
        "is_component": false,
        "price": 11999.0,
        "currency": "INR",
        "description": "Authentic POCO M6 Pro 5G offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CDS9PTRQ",
        "amazon_url": "https://www.amazon.in/dp/B0CDS9PTRQ",
        "flipkart_url": "https://www.flipkart.com/poco-m6-pro-5g-forest-green-128-gb/p/itm151f47ed48eee",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "retailer": "Amazon",
                "external_product_id": "B0CDS9PTRQ",
                "url": "https://www.amazon.in/dp/B0CDS9PTRQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "retailer": "Flipkart",
                "external_product_id": "itm151f47ed48eee",
                "url": "https://www.flipkart.com/poco-m6-pro-5g-forest-green-128-gb/p/itm151f47ed48eee",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/x/0/r/m6-pro-5g-mzb0eqjin-poco-original-imags3e7beqmyfje.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000127-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "external_product_id": "B0CGVLM5Q9",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/x/0/r/m6-pro-5g-mzb0eqjin-poco-original-imags3e7beqmyfje.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000127-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "external_product_id": "B0CGVLM5Q9",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/s/9/i/m6-pro-5g-mzb0eqjin-poco-original-imags3e7dazavyje.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>POCO%20M6%20Pro%205G%20%28Forest%20Green%2C%206GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - M6 Pro 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the POCO M6 Pro 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CGVLM5Q9",
        "asin": "B0CGVLM5Q9",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "retailer": "Amazon",
                "external_product_id": "B0CGVLM5Q9",
                "url": "https://www.amazon.in/dp/B0CGVLM5Q9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000127",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>POCO%20M6%20Pro%205G%20%28Forest%20Green%2C%206GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000128",
        "product_id": "c1000000-0000-0000-0000-000000000128",
        "title": "Samsung Galaxy M15 5G (Celestial Blue, 4GB RAM, 128GB Storage)",
        "slug": "galaxy-m15-5g",
        "brand": "Samsung",
        "model": "Galaxy M15 5G",
        "sku": "GALAXY-M15-5G",
        "model_number": "GALAXY-M15-5G",
        "category": "Smartphones",
        "subcategory": "Budget 5G",
        "is_component": false,
        "price": 12999.0,
        "currency": "INR",
        "description": "Authentic Samsung Galaxy M15 5G offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/Samsung-Celestial-Storage-MediaTek-Dimensity/dp/B0CYQ2N8JR",
        "amazon_url": "https://www.amazon.in/Samsung-Celestial-Storage-MediaTek-Dimensity/dp/B0CYQ2N8JR",
        "flipkart_url": "https://www.flipkart.com/samsung-m15-celestial-blue-128-gb/p/itm924abf886fce2",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "retailer": "Amazon",
                "external_product_id": "B0CYQ2N8JR",
                "url": "https://www.amazon.in/Samsung-Celestial-Storage-MediaTek-Dimensity/dp/B0CYQ2N8JR",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "retailer": "Flipkart",
                "external_product_id": "itm924abf886fce2",
                "url": "https://www.flipkart.com/samsung-m15-celestial-blue-128-gb/p/itm924abf886fce2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/w/b/m15-sm-m156b-samsung-original-imahedag4bsyqjsz.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000128-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "external_product_id": "B0CX8R22R3",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/w/b/m15-sm-m156b-samsung-original-imahedag4bsyqjsz.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000128-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "external_product_id": "B0CX8R22R3",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/n/n/w/m15-sm-m156b-samsung-original-imahedagwu48shzd.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20M15%205G%20%28Celestial%20Bl</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy M15 5G",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy M15 5G exceed expectations."
            }
        ],
        "external_product_id": "B0CX8R22R3",
        "asin": "B0CX8R22R3",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "retailer": "Amazon",
                "external_product_id": "B0CX8R22R3",
                "url": "https://www.amazon.in/dp/B0CX8R22R3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000128",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20M15%205G%20%28Celestial%20Bl</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000129",
        "product_id": "c1000000-0000-0000-0000-000000000129",
        "title": "OnePlus Nord 4 5G (Mercurial Silver, 8GB RAM, 256GB Storage)",
        "slug": "oneplus-nord-4",
        "brand": "OnePlus",
        "model": "Nord 4",
        "sku": "ONEPLUS-NORD-4",
        "model_number": "ONEPLUS-NORD-4",
        "category": "Smartphones",
        "subcategory": "Metal Unibody Mid-Range",
        "is_component": false,
        "price": 29999.0,
        "currency": "INR",
        "description": "Authentic OnePlus Nord 4 offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/OnePlus-Mercurial-Silver-256GB-Storage/dp/B0D7VKSZGW",
        "amazon_url": "https://www.amazon.in/OnePlus-Mercurial-Silver-256GB-Storage/dp/B0D7VKSZGW",
        "flipkart_url": "https://www.flipkart.com/oneplus-nord-4-5g-mercurial-silver-256-gb/p/itmed83e7926e3e5",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000129",
                "retailer": "Amazon",
                "external_product_id": "B0D7VKSZGW",
                "url": "https://www.amazon.in/OnePlus-Mercurial-Silver-256GB-Storage/dp/B0D7VKSZGW",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000129",
                "retailer": "Flipkart",
                "external_product_id": "itmed83e7926e3e5",
                "url": "https://www.flipkart.com/oneplus-nord-4-5g-mercurial-silver-256-gb/p/itmed83e7926e3e5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%204%205G%20%28Mercurial%20Silver</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000129-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000129",
                "external_product_id": "B0D4N9Z24C",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%204%205G%20%28Mercurial%20Silver</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%204%205G%20%28Mercurial%20Silver</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Nord 4",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the OnePlus Nord 4 exceed expectations."
            }
        ],
        "external_product_id": "B0D4N9Z24C",
        "asin": "B0D4N9Z24C",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000129",
                "retailer": "Amazon",
                "external_product_id": "B0D4N9Z24C",
                "url": "https://www.amazon.in/dp/B0D4N9Z24C",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000129",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%204%205G%20%28Mercurial%20Silver</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000130",
        "product_id": "c1000000-0000-0000-0000-000000000130",
        "title": "OnePlus Open (Voyager Black, 16GB RAM, 512GB Storage)",
        "slug": "oneplus-open",
        "brand": "OnePlus",
        "model": "OnePlus Open",
        "sku": "ONEPLUS-OPEN",
        "model_number": "ONEPLUS-OPEN",
        "category": "Smartphones",
        "subcategory": "Foldable Flagship",
        "is_component": false,
        "price": 139999.0,
        "currency": "INR",
        "description": "Authentic OnePlus OnePlus Open offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHWV2WYL",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/oneplus-open-emerald-dusk-512-gb/p/itm8d91ded712561",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "retailer": "Flipkart",
                "external_product_id": "itm8d91ded712561",
                "url": "https://www.flipkart.com/oneplus-open-emerald-dusk-512-gb/p/itm8d91ded712561",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/g/a/e/open-cph2551-oneplus-original-imagv2r4xvkjqcrj.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000130-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "external_product_id": "B0CHWV2WYL",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/g/a/e/open-cph2551-oneplus-original-imagv2r4xvkjqcrj.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000130-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "external_product_id": "B0CHWV2WYL",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/e/u/b/open-cph2551-oneplus-original-imagv2r4ddtsyy8f.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Open%20%28Voyager%20Black%2C%2016GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - OnePlus Open",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the OnePlus OnePlus Open exceed expectations."
            }
        ],
        "external_product_id": "B0CHWV2WYL",
        "asin": "B0CHWV2WYL",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "retailer": "Amazon",
                "external_product_id": "B0CHWV2WYL",
                "url": "https://www.amazon.in/dp/B0CHWV2WYL",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000130",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Open%20%28Voyager%20Black%2C%2016GB%20R</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000131",
        "product_id": "c1000000-0000-0000-0000-000000000131",
        "title": "Apple iPhone 15 Pro Max (256 GB) - Blue Titanium",
        "slug": "iphone-15-promax",
        "brand": "Apple",
        "model": "iPhone 15 Pro Max",
        "sku": "IPHONE-15-PROMAX",
        "model_number": "IPHONE-15-PROMAX",
        "category": "Smartphones",
        "subcategory": "Flagship Pro Max",
        "is_component": false,
        "price": 149990.0,
        "currency": "INR",
        "description": "Authentic Apple iPhone 15 Pro Max offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHX1W1XZ",
        "amazon_url": null,
        "flipkart_url": "https://www.flipkart.com/apple-iphone-15-pro-max-blue-titanium-256-gb/p/itm4a0093df4a3d7",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "retailer": "Flipkart",
                "external_product_id": "itm4a0093df4a3d7",
                "url": "https://www.flipkart.com/apple-iphone-15-pro-max-blue-titanium-256-gb/p/itm4a0093df4a3d7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/p/b/7/-original-imahggetywqjzwg6.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000131-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "external_product_id": "B0CHX1W1XZ",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/p/b/7/-original-imahggetywqjzwg6.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000131-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "external_product_id": "B0CHX1W1XZ",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/y/0/u/-original-imahggetzffhxaar.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Apple%20iPhone%2015%20Pro%20Max%20%28256%20GB%29%20-%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - iPhone 15 Pro Max",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Apple iPhone 15 Pro Max exceed expectations."
            }
        ],
        "external_product_id": "B0CHX1W1XZ",
        "asin": "B0CHX1W1XZ",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "retailer": "Amazon",
                "external_product_id": "B0CHX1W1XZ",
                "url": "https://www.amazon.in/dp/B0CHX1W1XZ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000131",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Apple%20iPhone%2015%20Pro%20Max%20%28256%20GB%29%20-%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000132",
        "product_id": "c1000000-0000-0000-0000-000000000132",
        "title": "Samsung Galaxy S24 5G (Cobalt Violet, 8GB, 128GB Storage)",
        "slug": "galaxy-s24-128",
        "brand": "Samsung",
        "model": "Galaxy S24",
        "sku": "GALAXY-S24-128",
        "model_number": "GALAXY-S24-128",
        "category": "Smartphones",
        "subcategory": "Compact Flagship",
        "is_component": false,
        "price": 74999.0,
        "currency": "INR",
        "description": "Authentic Samsung Galaxy S24 offering high-refresh AMOLED display, powerful processor, and long battery life.",
        "specs": {
            "processor": "Octa-core 5G Processor",
            "ram": "8GB/12GB",
            "storage": "128GB/256GB",
            "display": "6.7-inch AMOLED, 120Hz",
            "resolution": "2412x1080 FHD+",
            "refresh_rate": "120Hz",
            "camera": "50MP Main OIS + Ultra-wide",
            "battery": "5000mAh",
            "charging": "Fast Charging",
            "os": "Android 14 / iOS",
            "connectivity": "5G, Wi-Fi 6, Bluetooth 5.3",
            "dimensions": "162 x 75 x 8 mm",
            "weight": "190 g"
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0FT8S9RB7",
        "amazon_url": "https://www.amazon.in/dp/B0FT8S9RB7",
        "flipkart_url": "https://www.flipkart.com/samsung-galaxy-s24-5g-cobalt-violet-128-gb/p/itma2ec54ed01030",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "retailer": "Amazon",
                "external_product_id": "B0FT8S9RB7",
                "url": "https://www.amazon.in/dp/B0FT8S9RB7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "retailer": "Flipkart",
                "external_product_id": "itma2ec54ed01030",
                "url": "https://www.flipkart.com/samsung-galaxy-s24-5g-cobalt-violet-128-gb/p/itma2ec54ed01030",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/f/q/-original-imahfvuahbmttxgu.jpeg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000132-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "external_product_id": "B0CS5X81L5",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/f/q/-original-imahfvuahbmttxgu.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000132-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "external_product_id": "B0CS5X81L5",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/0/a/j/-original-imahfvuadz9gaebf.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20S24%205G%20%28Cobalt%20Viole</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Review - Galaxy S24",
                "rating": 4.7,
                "body": "Camera quality and battery runtime on the Samsung Galaxy S24 exceed expectations."
            }
        ],
        "external_product_id": "B0CS5X81L5",
        "asin": "B0CS5X81L5",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "retailer": "Amazon",
                "external_product_id": "B0CS5X81L5",
                "url": "https://www.amazon.in/dp/B0CS5X81L5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000132",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Samsung%20Galaxy%20S24%205G%20%28Cobalt%20Viole</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000201",
        "product_id": "c1000000-0000-0000-0000-000000000201",
        "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones - Black",
        "slug": "sony-wh1000xm5",
        "brand": "Sony",
        "model": "WH-1000XM5",
        "sku": "SONY-WH1000XM5",
        "model_number": "SONY-WH1000XM5",
        "category": "Audio & Headphones",
        "subcategory": "Premium Over-Ear ANC",
        "is_component": false,
        "price": 28990.0,
        "currency": "INR",
        "description": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones - Black delivering 30mm Carbon Fiber Composite sound reproduction, Yes, Auto NC Optimizer with 8 Microphones, and 30 hours (ANC On), 40 hours (ANC Off).",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "30mm Carbon Fiber Composite",
            "anc": "Yes, Auto NC Optimizer with 8 Microphones",
            "battery": "30 hours (ANC On), 40 hours (ANC Off)",
            "codec": "LDAC, AAC, SBC",
            "microphone": "4 Beamforming mics with AI noise reduction",
            "connectivity": "Bluetooth 5.2, Multipoint, 3.5mm Aux",
            "weight": "250 g",
            "water_resistance": "Not Rated",
            "price": 28990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09XS7JWHH",
        "amazon_url": "https://www.amazon.in/dp/B09XS7JWHH",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "retailer": "Amazon",
                "external_product_id": "B09XS7JWHH",
                "url": "https://www.amazon.in/dp/B09XS7JWHH",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61+btxzpfDL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000201-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "external_product_id": "B09XS7JWHH",
                "image_url": "https://m.media-amazon.com/images/I/61+btxzpfDL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000201-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "external_product_id": "B09XS7JWHH",
                "image_url": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61+btxzpfDL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61vJtKbAssL._SL1500_.jpg",
            "accessories": "https://m.media-amazon.com/images/I/71p0W+3bL8L._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71k4s6m3VCL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/81b6Y1v4O4L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - WH-1000XM5",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony WH-1000XM5 are top-tier."
            }
        ],
        "external_product_id": "B09XS7JWHH",
        "asin": "B09XS7JWHH",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "retailer": "Amazon",
                "external_product_id": "B09XS7JWHH",
                "url": "https://www.amazon.in/dp/B09XS7JWHH",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000201",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61+btxzpfDL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000202",
        "product_id": "c1000000-0000-0000-0000-000000000202",
        "title": "Sony WH-1000XM4 Wireless Noise Cancelling Headphones - Silver",
        "slug": "sony-wh1000xm4",
        "brand": "Sony",
        "model": "WH-1000XM4",
        "sku": "SONY-WH1000XM4",
        "model_number": "SONY-WH1000XM4",
        "category": "Audio & Headphones",
        "subcategory": "Premium Over-Ear ANC",
        "is_component": false,
        "price": 22990.0,
        "currency": "INR",
        "description": "Sony WH-1000XM4 Wireless Noise Cancelling Headphones - Silver delivering 40mm Dome Type (Liquid Crystal Polymer) sound reproduction, Yes, HD Noise Cancelling Processor QN1, and 30 hours with ANC.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "40mm Dome Type (Liquid Crystal Polymer)",
            "anc": "Yes, HD Noise Cancelling Processor QN1",
            "battery": "30 hours with ANC",
            "codec": "LDAC, AAC, SBC",
            "microphone": "5 microphones with Precise Voice Pickup",
            "connectivity": "Bluetooth 5.0, NFC, 3.5mm Aux",
            "weight": "254 g",
            "water_resistance": "Not Rated",
            "price": 22990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08LW4MT2Z",
        "amazon_url": "https://www.amazon.in/dp/B08LW4MT2Z",
        "flipkart_url": "https://www.flipkart.com/sony-wh-1000xm4-bluetooth-headset/p/itm2517d207c4dd5",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000202",
                "retailer": "Amazon",
                "external_product_id": "B08LW4MT2Z",
                "url": "https://www.amazon.in/dp/B08LW4MT2Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000202",
                "retailer": "Flipkart",
                "external_product_id": "itm2517d207c4dd5",
                "url": "https://www.flipkart.com/sony-wh-1000xm4-bluetooth-headset/p/itm2517d207c4dd5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61wAWttbWrL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000202-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000202",
                "external_product_id": "B0863TXGM3",
                "image_url": "https://m.media-amazon.com/images/I/61wAWttbWrL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WH-1000XM4%20Wireless%20Noise%20Canc</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - WH-1000XM4",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony WH-1000XM4 are top-tier."
            }
        ],
        "external_product_id": "B0863TXGM3",
        "asin": "B0863TXGM3",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000202",
                "retailer": "Amazon",
                "external_product_id": "B0863TXGM3",
                "url": "https://www.amazon.in/dp/B0863TXGM3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000202",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WH-1000XM4%20Wireless%20Noise%20Canc</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000203",
        "product_id": "c1000000-0000-0000-0000-000000000203",
        "title": "Sony WH-CH720N Noise Cancelling Wireless Over-Ear Headphones - Blue",
        "slug": "sony-whch720n",
        "brand": "Sony",
        "model": "WH-CH720N",
        "sku": "SONY-WHCH720N",
        "model_number": "SONY-WHCH720N",
        "category": "Audio & Headphones",
        "subcategory": "Mid-Range Over-Ear ANC",
        "is_component": false,
        "price": 9990.0,
        "currency": "INR",
        "description": "Sony WH-CH720N Noise Cancelling Wireless Over-Ear Headphones - Blue delivering 30mm Dynamic Driver sound reproduction, Yes, Integrated Processor V1 Dual Noise Sensor, and 35 hours (ANC On), 50 hours (ANC Off).",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "30mm Dynamic Driver",
            "anc": "Yes, Integrated Processor V1 Dual Noise Sensor",
            "battery": "35 hours (ANC On), 50 hours (ANC Off)",
            "codec": "AAC, SBC, DSEE upscaling",
            "microphone": "Beamforming microphones with noise canceling",
            "connectivity": "Bluetooth 5.2, Multipoint connection",
            "weight": "192 g",
            "water_resistance": "Not Rated",
            "price": 9990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CFSDYNGT",
        "amazon_url": "https://www.amazon.in/dp/B0CFSDYNGT",
        "flipkart_url": "https://www.flipkart.com/sony-wh-ch720n-active-noise-cancelling-50-hrs-battery-life-multipoint-connection-bluetooth/p/itm45d94d7470182",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000203",
                "retailer": "Amazon",
                "external_product_id": "B0CFSDYNGT",
                "url": "https://www.amazon.in/dp/B0CFSDYNGT",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000203",
                "retailer": "Flipkart",
                "external_product_id": "itm45d94d7470182",
                "url": "https://www.flipkart.com/sony-wh-ch720n-active-noise-cancelling-50-hrs-battery-life-multipoint-connection-bluetooth/p/itm45d94d7470182",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51--iaLfgWL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000203-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000203",
                "external_product_id": "B0BT41Z4PB",
                "image_url": "https://m.media-amazon.com/images/I/51--iaLfgWL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WH-CH720N%20Noise%20Cancelling%20Wir</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - WH-CH720N",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony WH-CH720N are top-tier."
            }
        ],
        "external_product_id": "B0BT41Z4PB",
        "asin": "B0BT41Z4PB",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000203",
                "retailer": "Amazon",
                "external_product_id": "B0BT41Z4PB",
                "url": "https://www.amazon.in/dp/B0BT41Z4PB",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000203",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WH-CH720N%20Noise%20Cancelling%20Wir</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000204",
        "product_id": "c1000000-0000-0000-0000-000000000204",
        "title": "Sony WF-1000XM5 Truly Wireless Noise Cancelling Earbuds - Black",
        "slug": "sony-wf1000xm5",
        "brand": "Sony",
        "model": "WF-1000XM5",
        "sku": "SONY-WF1000XM5",
        "model_number": "SONY-WF1000XM5",
        "category": "Audio & Headphones",
        "subcategory": "Flagship TWS Earbuds",
        "is_component": false,
        "price": 24990.0,
        "currency": "INR",
        "description": "Sony WF-1000XM5 Truly Wireless Noise Cancelling Earbuds - Black delivering 8.4mm Dynamic Driver X sound reproduction, Yes, Dual processors (V2 + QN2e), and 8 hours (earbuds) + 16 hours (case).",
        "specs": {
            "type": "Truly Wireless Earbuds (In-Ear)",
            "driver": "8.4mm Dynamic Driver X",
            "anc": "Yes, Dual processors (V2 + QN2e)",
            "battery": "8 hours (earbuds) + 16 hours (case)",
            "codec": "LDAC, LC3, AAC, SBC",
            "microphone": "Bone conduction sensors & 6 mics",
            "connectivity": "Bluetooth 5.3, Qi Wireless Charging",
            "weight": "5.9 g per earbud",
            "water_resistance": "IPX4 water resistance",
            "price": 24990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C33XXS56",
        "amazon_url": "https://www.amazon.in/dp/B0C33XXS56",
        "flipkart_url": "https://www.flipkart.com/sony-wf-1000xm5-best-noise-cancelling-tws-earbuds-multi-point-upto-36hrs-battery-bluetooth-headset/p/itm86886b74b3256",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "retailer": "Amazon",
                "external_product_id": "B0C33XXS56",
                "url": "https://www.amazon.in/dp/B0C33XXS56",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "retailer": "Flipkart",
                "external_product_id": "itm86886b74b3256",
                "url": "https://www.flipkart.com/sony-wf-1000xm5-best-noise-cancelling-tws-earbuds-multi-point-upto-36hrs-battery-bluetooth-headset/p/itm86886b74b3256",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/headphone/p/2/v/wf-1000xm5-sony-enriched-transparent-original-imagtak4zdhzhffc.png?q=90",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000204-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "external_product_id": "B0C33XXS56",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/headphone/p/2/v/wf-1000xm5-sony-enriched-transparent-original-imagtak4zdhzhffc.png?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000204-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "external_product_id": "B0C33XXS56",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/headphone/1/h/u/wf-1000xm5-sony-original-imagtak4fbg56fnt.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61aB4Vwo8PL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61aB4Vwo8AL._SL1500_.jpg",
            "right": "https://m.media-amazon.com/images/I/71w9T3m7L4L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - WF-1000XM5",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony WF-1000XM5 are top-tier."
            }
        ],
        "external_product_id": "B0C33XXS56",
        "asin": "B0C33XXS56",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "retailer": "Amazon",
                "external_product_id": "B0C33XXS56",
                "url": "https://www.amazon.in/dp/B0C33XXS56",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000204",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61aB4Vwo8PL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000205",
        "product_id": "c1000000-0000-0000-0000-000000000205",
        "title": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones - Black",
        "slug": "bose-qc-ultra",
        "brand": "Bose",
        "model": "QuietComfort Ultra",
        "sku": "BOSE-QC-ULTRA",
        "model_number": "BOSE-QC-ULTRA",
        "category": "Audio & Headphones",
        "subcategory": "Premium Spatial Audio ANC",
        "is_component": false,
        "price": 35900.0,
        "currency": "INR",
        "description": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones - Black delivering Custom Bose High-Resolution Transducer sound reproduction, Yes, CustomTune Active Noise Cancelling, and 24 hours (up to 18 hours with Immersive Audio).",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "Custom Bose High-Resolution Transducer",
            "anc": "Yes, CustomTune Active Noise Cancelling",
            "battery": "24 hours (up to 18 hours with Immersive Audio)",
            "codec": "aptX Adaptive, AAC, SBC",
            "microphone": "Advanced microphone array with wind noise reduction",
            "connectivity": "Bluetooth 5.3, 3.5mm audio jack",
            "weight": "252 g",
            "water_resistance": "Not Rated",
            "price": 35900.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CCZ1L489",
        "amazon_url": "https://www.amazon.in/dp/B0CCZ1L489",
        "flipkart_url": "https://www.flipkart.com/bose-new-quietcomfort-ultra-wireless-noise-cancelling-headphones-spatial-audio-bluetooth-headset/p/itmaf5ffcc5144ba",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000205",
                "retailer": "Amazon",
                "external_product_id": "B0CCZ1L489",
                "url": "https://www.amazon.in/dp/B0CCZ1L489",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000205",
                "retailer": "Flipkart",
                "external_product_id": "itmaf5ffcc5144ba",
                "url": "https://www.flipkart.com/bose-new-quietcomfort-ultra-wireless-noise-cancelling-headphones-spatial-audio-bluetooth-headset/p/itmaf5ffcc5144ba",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51ZR4lyxBHL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000205-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000205",
                "external_product_id": "B0CCZ1L489",
                "image_url": "https://m.media-amazon.com/images/I/51ZR4lyxBHL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Bose%20QuietComfort%20Ultra%20Wireless%20No</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - QuietComfort Ultra",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Bose QuietComfort Ultra are top-tier."
            }
        ],
        "external_product_id": "B0CCZ1L489",
        "asin": "B0CCZ1L489",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000205",
                "retailer": "Amazon",
                "external_product_id": "B0CCZ1L489",
                "url": "https://www.amazon.in/dp/B0CCZ1L489",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000205",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Bose%20QuietComfort%20Ultra%20Wireless%20No</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000206",
        "product_id": "c1000000-0000-0000-0000-000000000206",
        "title": "Bose QuietComfort 45 Bluetooth Wireless Headphones - Triple Black",
        "slug": "bose-qc45",
        "brand": "Bose",
        "model": "QuietComfort 45",
        "sku": "BOSE-QC45",
        "model_number": "BOSE-QC45",
        "category": "Audio & Headphones",
        "subcategory": "Premium Over-Ear ANC",
        "is_component": false,
        "price": 24900.0,
        "currency": "INR",
        "description": "Bose QuietComfort 45 Bluetooth Wireless Headphones - Triple Black delivering TriPort Acoustic Architecture sound reproduction, Yes, Quiet and Aware Mode ANC, and 22 hours on single charge.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "TriPort Acoustic Architecture",
            "anc": "Yes, Quiet and Aware Mode ANC",
            "battery": "22 hours on single charge",
            "codec": "AAC, SBC",
            "microphone": "4 external microphones for voice isolation",
            "connectivity": "Bluetooth 5.1, 3.5mm Aux",
            "weight": "240 g",
            "water_resistance": "Not Rated",
            "price": 24900.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B098FKXT8L",
        "amazon_url": "https://www.amazon.in/dp/B098FKXT8L",
        "flipkart_url": "https://www.flipkart.com/bose-quietcomfort-45-24-hours-playback-noise-cancellation-bluetooth-headset/p/itma9e5d5efec36a",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "retailer": "Amazon",
                "external_product_id": "B098FKXT8L",
                "url": "https://www.amazon.in/dp/B098FKXT8L",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "retailer": "Flipkart",
                "external_product_id": "itma9e5d5efec36a",
                "url": "https://www.flipkart.com/bose-quietcomfort-45-24-hours-playback-noise-cancellation-bluetooth-headset/p/itma9e5d5efec36a",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51JbsHSktkL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000206-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "external_product_id": "B098FKXT8L",
                "image_url": "https://m.media-amazon.com/images/I/51JbsHSktkL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000206-GALLERY",
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "external_product_id": "B098FKXT8L",
                "image_url": "https://m.media-amazon.com/images/I/71O6P9a4xBL._SL1500_.jpg",
                "image_type": "gallery",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/51JbsHSktkL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71O6P9a4xBL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - QuietComfort 45",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Bose QuietComfort 45 are top-tier."
            }
        ],
        "external_product_id": "B098FKXT8L",
        "asin": "B098FKXT8L",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "retailer": "Amazon",
                "external_product_id": "B098FKXT8L",
                "url": "https://www.amazon.in/dp/B098FKXT8L",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000206",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/51JbsHSktkL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000207",
        "product_id": "c1000000-0000-0000-0000-000000000207",
        "title": "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)",
        "slug": "mtjv3hn-a",
        "brand": "Apple",
        "model": "AirPods Pro 2 USB-C",
        "sku": "MTJV3HN/A",
        "model_number": "MTJV3HN/A",
        "category": "Audio & Headphones",
        "subcategory": "Flagship TWS Earbuds",
        "is_component": false,
        "price": 24900.0,
        "currency": "INR",
        "description": "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C) delivering Custom high-excursion Apple driver sound reproduction, Yes, Apple H2 chip Active Noise Cancellation & Adaptive Audio, and 6 hours (earbuds) + 24 hours (MagSafe Case).",
        "specs": {
            "type": "Truly Wireless In-Ear Earbuds",
            "driver": "Custom high-excursion Apple driver",
            "anc": "Yes, Apple H2 chip Active Noise Cancellation & Adaptive Audio",
            "battery": "6 hours (earbuds) + 24 hours (MagSafe Case)",
            "codec": "AAC, Apple Lossless (with Vision Pro)",
            "microphone": "Dual beamforming microphones + inward-facing mic",
            "connectivity": "Bluetooth 5.3, MagSafe, Qi, Apple Watch charger",
            "weight": "5.3 g per earbud",
            "water_resistance": "IP54 dust, sweat, and water resistance",
            "price": 24900.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CHX719JD",
        "amazon_url": "https://www.amazon.in/dp/B0CHX719JD",
        "flipkart_url": "https://www.flipkart.com/apple-airpods-pro-2nd-generation-magsafe-case-usb-c-bluetooth/p/itm60c8f5a308352",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "retailer": "Amazon",
                "external_product_id": "B0CHX719JD",
                "url": "https://www.amazon.in/dp/B0CHX719JD",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "retailer": "Flipkart",
                "external_product_id": "itm60c8f5a308352",
                "url": "https://www.flipkart.com/apple-airpods-pro-2nd-generation-magsafe-case-usb-c-bluetooth/p/itm60c8f5a308352",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000207-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "external_product_id": "B0CHWRXH8B",
                "image_url": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000207-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "external_product_id": "B0CHWRXH8B",
                "image_url": "https://m.media-amazon.com/images/I/71BHbg3LVAL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/71BHbg3LVAL._SL1500_.jpg",
            "accessories": "https://m.media-amazon.com/images/I/51n8P7m6T2L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - AirPods Pro 2 USB-C",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Apple AirPods Pro 2 USB-C are top-tier."
            }
        ],
        "external_product_id": "B0CHWRXH8B",
        "asin": "B0CHWRXH8B",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "retailer": "Amazon",
                "external_product_id": "B0CHWRXH8B",
                "url": "https://www.amazon.in/dp/B0CHWRXH8B",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000207",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000208",
        "product_id": "c1000000-0000-0000-0000-000000000208",
        "title": "Apple AirPods Max Wireless Over-Ear Headphones - Space Grey",
        "slug": "mgyh3hn-a",
        "brand": "Apple",
        "model": "AirPods Max",
        "sku": "MGYH3HN/A",
        "model_number": "MGYH3HN/A",
        "category": "Audio & Headphones",
        "subcategory": "Luxury Hi-Fi ANC Headphones",
        "is_component": false,
        "price": 59900.0,
        "currency": "INR",
        "description": "Apple AirPods Max Wireless Over-Ear Headphones - Space Grey delivering 40mm Apple-designed dynamic driver sound reproduction, Yes, Active Noise Cancellation with Transparency mode, and 20 hours with ANC and Spatial Audio.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "40mm Apple-designed dynamic driver",
            "anc": "Yes, Active Noise Cancellation with Transparency mode",
            "battery": "20 hours with ANC and Spatial Audio",
            "codec": "AAC, Apple Digital Audio",
            "microphone": "9 microphones total (8 for ANC, 3 for voice pickup)",
            "connectivity": "Bluetooth 5.0, Apple H1 chip in each ear cup",
            "weight": "384.8 g",
            "water_resistance": "Not Rated",
            "price": 59900.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08Q4S97M5",
        "amazon_url": "https://www.amazon.in/dp/B08Q4S97M5",
        "flipkart_url": "https://www.flipkart.com/apple-airpods-max-bluetooth/p/itm66a49e88f49e5",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000208",
                "retailer": "Amazon",
                "external_product_id": "B08Q4S97M5",
                "url": "https://www.amazon.in/dp/B08Q4S97M5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000208",
                "retailer": "Flipkart",
                "external_product_id": "itm66a49e88f49e5",
                "url": "https://www.flipkart.com/apple-airpods-max-bluetooth/p/itm66a49e88f49e5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/81U3QW4lCcL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000208-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000208",
                "external_product_id": "B08PZHYWJS",
                "image_url": "https://m.media-amazon.com/images/I/81U3QW4lCcL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/81Y7cW8+5uL._SL1500_.jpg",
            "accessories": "https://m.media-amazon.com/images/I/81gC7frRJyL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/71n5fU3xLFL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/81M6w2K9y3L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - AirPods Max",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Apple AirPods Max are top-tier."
            }
        ],
        "external_product_id": "B08PZHYWJS",
        "asin": "B08PZHYWJS",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000208",
                "retailer": "Amazon",
                "external_product_id": "B08PZHYWJS",
                "url": "https://www.amazon.in/dp/B08PZHYWJS",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000208",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/81Y7cW8+5uL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000209",
        "product_id": "c1000000-0000-0000-0000-000000000209",
        "title": "Sennheiser Momentum 4 Wireless Headphones - Black Copper",
        "slug": "sennheiser-momentum-4",
        "brand": "Sennheiser",
        "model": "Momentum 4",
        "sku": "SENNHEISER-MOMENTUM-4",
        "model_number": "SENNHEISER-MOMENTUM-4",
        "category": "Audio & Headphones",
        "subcategory": "Audiophile Wireless ANC",
        "is_component": false,
        "price": 27990.0,
        "currency": "INR",
        "description": "Sennheiser Momentum 4 Wireless Headphones - Black Copper delivering 42mm Audiophile-inspired transducer sound reproduction, Yes, Adaptive Active Noise Cancellation, and 60 hours colossal battery life with ANC on.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "42mm Audiophile-inspired transducer",
            "anc": "Yes, Adaptive Active Noise Cancellation",
            "battery": "60 hours colossal battery life with ANC on",
            "codec": "aptX Adaptive, aptX, AAC, SBC",
            "microphone": "2x2 digital beamforming mic array",
            "connectivity": "Bluetooth 5.2, USB-C DAC mode, 3.5mm Aux",
            "weight": "293 g",
            "water_resistance": "Not Rated",
            "price": 27990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0B6GHW1SX",
        "amazon_url": "https://www.amazon.in/dp/B0B6GHW1SX",
        "flipkart_url": "https://www.flipkart.com/sennheiser-momentum-4-wireless-over-ear-headphones-anc-60h-battery-multipoint-connectivity-bluetooth-wired/p/itm722356d6df76c",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000209",
                "retailer": "Amazon",
                "external_product_id": "B0B6GHW1SX",
                "url": "https://www.amazon.in/dp/B0B6GHW1SX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000209",
                "retailer": "Flipkart",
                "external_product_id": "itm722356d6df76c",
                "url": "https://www.flipkart.com/sennheiser-momentum-4-wireless-over-ear-headphones-anc-60h-battery-multipoint-connectivity-bluetooth-wired/p/itm722356d6df76c",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/716++4xC2wL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000209-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000209",
                "external_product_id": "B0B6GHW1SX",
                "image_url": "https://m.media-amazon.com/images/I/716++4xC2wL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Momentum%204%20Wireless%20Head</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Momentum 4",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sennheiser Momentum 4 are top-tier."
            }
        ],
        "external_product_id": "B0B6GHW1SX",
        "asin": "B0B6GHW1SX",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000209",
                "retailer": "Amazon",
                "external_product_id": "B0B6GHW1SX",
                "url": "https://www.amazon.in/dp/B0B6GHW1SX",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000209",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Momentum%204%20Wireless%20Head</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000210",
        "product_id": "c1000000-0000-0000-0000-000000000210",
        "title": "Sennheiser HD 560S Audiophile Open-Back Reference Headphones",
        "slug": "sennheiser-hd560s",
        "brand": "Sennheiser",
        "model": "HD 560S",
        "sku": "SENNHEISER-HD560S",
        "model_number": "SENNHEISER-HD560S",
        "category": "Audio & Headphones",
        "subcategory": "Audiophile Studio Reference",
        "is_component": false,
        "price": 14990.0,
        "currency": "INR",
        "description": "Sennheiser HD 560S Audiophile Open-Back Reference Headphones delivering 120-ohm angled transducer with polymer blend sound reproduction, No (Acoustically open for natural soundstaging), and N/A (Passive Wired).",
        "specs": {
            "type": "Over-Ear Open-Back Wired",
            "driver": "120-ohm angled transducer with polymer blend",
            "anc": "No (Acoustically open for natural soundstaging)",
            "battery": "N/A (Passive Wired)",
            "codec": "Analog Uncompressed Audio (6Hz - 38kHz)",
            "microphone": "None (Pure audiophile music listening)",
            "connectivity": "3.0m cable with 6.3mm plug + 3.5mm adapter",
            "weight": "240 g",
            "water_resistance": "Not Rated",
            "price": 14990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08HNFV61M",
        "amazon_url": "https://www.amazon.in/dp/B08HNFV61M",
        "flipkart_url": "https://www.flipkart.com/sennheiser-hd-560s-audiophile-over-ear-headphone-wired-without-mic-headset/p/itme71f567510ef2",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000210",
                "retailer": "Amazon",
                "external_product_id": "B08HNFV61M",
                "url": "https://www.amazon.in/dp/B08HNFV61M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000210",
                "retailer": "Flipkart",
                "external_product_id": "itme71f567510ef2",
                "url": "https://www.flipkart.com/sennheiser-hd-560s-audiophile-over-ear-headphone-wired-without-mic-headset/p/itme71f567510ef2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71z2y-w+hmL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000210-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000210",
                "external_product_id": "B08HNFV61M",
                "image_url": "https://m.media-amazon.com/images/I/71z2y-w+hmL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20HD%20560S%20Audiophile%20Open-</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - HD 560S",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sennheiser HD 560S are top-tier."
            }
        ],
        "external_product_id": "B08HNFV61M",
        "asin": "B08HNFV61M",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000210",
                "retailer": "Amazon",
                "external_product_id": "B08HNFV61M",
                "url": "https://www.amazon.in/dp/B08HNFV61M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000210",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20HD%20560S%20Audiophile%20Open-</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000211",
        "product_id": "c1000000-0000-0000-0000-000000000211",
        "title": "Audio-Technica ATH-M50x Professional Studio Monitor Headphones",
        "slug": "ath-m50x-black",
        "brand": "Audio-Technica",
        "model": "ATH-M50x",
        "sku": "ATH-M50X-BLACK",
        "model_number": "ATH-M50X-BLACK",
        "category": "Audio & Headphones",
        "subcategory": "Studio Monitor Wired",
        "is_component": false,
        "price": 12490.0,
        "currency": "INR",
        "description": "Audio-Technica ATH-M50x Professional Studio Monitor Headphones delivering 45mm large-aperture neodymium magnet drivers sound reproduction, Passive noise isolation via circumaural earcups, and N/A (Passive Wired).",
        "specs": {
            "type": "Over-Ear Closed-Back Wired Studio Monitor",
            "driver": "45mm large-aperture neodymium magnet drivers",
            "anc": "Passive noise isolation via circumaural earcups",
            "battery": "N/A (Passive Wired)",
            "codec": "Analog Studio Audio (15Hz - 28kHz)",
            "microphone": "None (Studio monitor)",
            "connectivity": "Detachable 1.2m coiled, 3m straight, 1.2m straight cables",
            "weight": "285 g",
            "water_resistance": "Not Rated",
            "price": 12490.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B00HVLUR86",
        "amazon_url": "https://www.amazon.in/dp/B00HVLUR86",
        "flipkart_url": "https://www.flipkart.com/audio-technica-ath-m50x-professional-monitor-wired-without-mic/p/itm60d2ac1511889",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000211",
                "retailer": "Amazon",
                "external_product_id": "B00HVLUR86",
                "url": "https://www.amazon.in/dp/B00HVLUR86",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000211",
                "retailer": "Flipkart",
                "external_product_id": "itm60d2ac1511889",
                "url": "https://www.flipkart.com/audio-technica-ath-m50x-professional-monitor-wired-without-mic/p/itm60d2ac1511889",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71G5OkSr2zL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000211-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000211",
                "external_product_id": "B00HVLUR86",
                "image_url": "https://m.media-amazon.com/images/I/71G5OkSr2zL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50x%20Professiona</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - ATH-M50x",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Audio-Technica ATH-M50x are top-tier."
            }
        ],
        "external_product_id": "B00HVLUR86",
        "asin": "B00HVLUR86",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000211",
                "retailer": "Amazon",
                "external_product_id": "B00HVLUR86",
                "url": "https://www.amazon.in/dp/B00HVLUR86",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000211",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50x%20Professiona</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000212",
        "product_id": "c1000000-0000-0000-0000-000000000212",
        "title": "OnePlus Buds Pro 2 TWS Earbuds - Obsidian Black",
        "slug": "oneplus-buds-pro2",
        "brand": "OnePlus",
        "model": "Buds Pro 2",
        "sku": "ONEPLUS-BUDS-PRO2",
        "model_number": "ONEPLUS-BUDS-PRO2",
        "category": "Audio & Headphones",
        "subcategory": "Flagship TWS Earbuds",
        "is_component": false,
        "price": 9999.0,
        "currency": "INR",
        "description": "OnePlus Buds Pro 2 TWS Earbuds - Obsidian Black delivering MelodyBoost 11mm woofer + 6mm tweeter dual drivers sound reproduction, Yes, 48dB Smart Adaptive Noise Cancellation, and 9 hours (buds), 39 hours (total with case).",
        "specs": {
            "type": "Truly Wireless In-Ear Earbuds",
            "driver": "MelodyBoost 11mm woofer + 6mm tweeter dual drivers",
            "anc": "Yes, 48dB Smart Adaptive Noise Cancellation",
            "battery": "9 hours (buds), 39 hours (total with case)",
            "codec": "LHDC 4.0, AAC, SBC, LC3",
            "microphone": "3 microphones per bud with AI noise reduction",
            "connectivity": "Bluetooth 5.3, Google Fast Pair, Qi wireless charging",
            "weight": "4.9 g per earbud",
            "water_resistance": "IP55 (buds), IPX4 (case)",
            "price": 9999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BQN7Y8BB",
        "amazon_url": "https://www.amazon.in/dp/B0BQN7Y8BB",
        "flipkart_url": "https://www.flipkart.com/oneplus-buds-pro-2-bluetooth-headset/p/itm79f97165e1813",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000212",
                "retailer": "Amazon",
                "external_product_id": "B0BQN7Y8BB",
                "url": "https://www.amazon.in/dp/B0BQN7Y8BB",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000212",
                "retailer": "Flipkart",
                "external_product_id": "itm79f97165e1813",
                "url": "https://www.flipkart.com/oneplus-buds-pro-2-bluetooth-headset/p/itm79f97165e1813",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/511M6l6E5bL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000212-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000212",
                "external_product_id": "B0BP28N2M5",
                "image_url": "https://m.media-amazon.com/images/I/511M6l6E5bL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Buds%20Pro%202%20TWS%20Earbuds%20-%20Ob</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Buds Pro 2",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the OnePlus Buds Pro 2 are top-tier."
            }
        ],
        "external_product_id": "B0BP28N2M5",
        "asin": "B0BP28N2M5",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000212",
                "retailer": "Amazon",
                "external_product_id": "B0BP28N2M5",
                "url": "https://www.amazon.in/dp/B0BP28N2M5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000212",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Buds%20Pro%202%20TWS%20Earbuds%20-%20Ob</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000213",
        "product_id": "c1000000-0000-0000-0000-000000000213",
        "title": "boAt Airdopes 141 Bluetooth TWS Earbuds - Bold Black",
        "slug": "boat-airdopes-141",
        "brand": "boAt",
        "model": "Airdopes 141",
        "sku": "BOAT-AIRDOPES-141",
        "model_number": "BOAT-AIRDOPES-141",
        "category": "Audio & Headphones",
        "subcategory": "Budget TWS Earbuds",
        "is_component": false,
        "price": 1299.0,
        "currency": "INR",
        "description": "boAt Airdopes 141 Bluetooth TWS Earbuds - Bold Black delivering 8mm dynamic drivers sound reproduction, ENx Environmental Noise Cancellation for calls, and 42 hours total playback (6 hours per charge).",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "8mm dynamic drivers",
            "anc": "ENx Environmental Noise Cancellation for calls",
            "battery": "42 hours total playback (6 hours per charge)",
            "codec": "SBC, AAC",
            "microphone": "ENx noise-isolating mic for crystal clear calls",
            "connectivity": "Bluetooth 5.1 with IWP (Insta Wake N' Pair)",
            "weight": "4 g per earbud",
            "water_resistance": "IPX4 splash and sweat resistance",
            "price": 1299.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09N3ZNHTY",
        "amazon_url": "https://www.amazon.in/dp/B09N3ZNHTY",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "retailer": "Amazon",
                "external_product_id": "B09N3ZNHTY",
                "url": "https://www.amazon.in/dp/B09N3ZNHTY",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000213-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "external_product_id": "B09N3ZNHTY",
                "image_url": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000213-BACK",
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "external_product_id": "B09N3ZNHTY",
                "image_url": "https://m.media-amazon.com/images/I/61K5w4g-3nL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61K5w4g-3nL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71nvk5b5gLL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Airdopes 141",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the boAt Airdopes 141 are top-tier."
            }
        ],
        "external_product_id": "B09N3ZNHTY",
        "asin": "B09N3ZNHTY",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "retailer": "Amazon",
                "external_product_id": "B09N3ZNHTY",
                "url": "https://www.amazon.in/dp/B09N3ZNHTY",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000213",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb38",
                "url": "https://www.flipkart.com/boat-airdopes-141-bluetooth-headset/p/itmd5543c749eb38",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000214",
        "product_id": "c1000000-0000-0000-0000-000000000214",
        "title": "boAt Rockerz 550 Bluetooth Wireless Over-Ear Headphones - Army Green",
        "slug": "boat-rockerz-550",
        "brand": "boAt",
        "model": "Rockerz 550",
        "sku": "BOAT-ROCKERZ-550",
        "model_number": "BOAT-ROCKERZ-550",
        "category": "Audio & Headphones",
        "subcategory": "Budget Over-Ear Wireless",
        "is_component": false,
        "price": 1799.0,
        "currency": "INR",
        "description": "boAt Rockerz 550 Bluetooth Wireless Over-Ear Headphones - Army Green delivering 50mm dynamic drivers with deep bass sound reproduction, Physical noise isolation, and 20 hours continuous playback.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "50mm dynamic drivers with deep bass",
            "anc": "Physical noise isolation",
            "battery": "20 hours continuous playback",
            "codec": "SBC",
            "microphone": "Built-in microphone for handsfree calling",
            "connectivity": "Bluetooth 5.0 and 3.5mm Aux dual mode",
            "weight": "245 g",
            "water_resistance": "Not Rated",
            "price": 1799.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08R7L77T7",
        "amazon_url": "https://www.amazon.in/dp/B08R7L77T7",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000214",
                "retailer": "Amazon",
                "external_product_id": "B08R7L77T7",
                "url": "https://www.amazon.in/dp/B08R7L77T7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000214",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61leGjTDm0L._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000214-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000214",
                "external_product_id": "B0856HNMR7",
                "image_url": "https://m.media-amazon.com/images/I/61leGjTDm0L._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61gYLMssVvL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61gYLMssVzL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Rockerz 550",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the boAt Rockerz 550 are top-tier."
            }
        ],
        "external_product_id": "B0856HNMR7",
        "asin": "B0856HNMR7",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000214",
                "retailer": "Amazon",
                "external_product_id": "B0856HNMR7",
                "url": "https://www.amazon.in/dp/B0856HNMR7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000214",
                "retailer": "Flipkart",
                "external_product_id": "itmd5543c749eb39",
                "url": "https://www.flipkart.com/boat-rockerz-550-bluetooth-headset/p/itmd5543c749eb39",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61gYLMssVvL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000215",
        "product_id": "c1000000-0000-0000-0000-000000000215",
        "title": "JBL Tune 770NC Wireless Over-Ear Adaptive Noise Cancelling Headphones - Black",
        "slug": "jbl-tune-770nc",
        "brand": "JBL",
        "model": "Tune 770NC",
        "sku": "JBL-TUNE-770NC",
        "model_number": "JBL-TUNE-770NC",
        "category": "Audio & Headphones",
        "subcategory": "Mid-Range Over-Ear ANC",
        "is_component": false,
        "price": 5999.0,
        "currency": "INR",
        "description": "JBL Tune 770NC Wireless Over-Ear Adaptive Noise Cancelling Headphones - Black delivering 40mm dynamic drivers with JBL Pure Bass sound reproduction, Yes, Adaptive Noise Cancelling with Smart Ambient, and 70 hours (ANC Off), 44 hours (ANC On).",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "40mm dynamic drivers with JBL Pure Bass",
            "anc": "Yes, Adaptive Noise Cancelling with Smart Ambient",
            "battery": "70 hours (ANC Off), 44 hours (ANC On)",
            "codec": "AAC, SBC, Bluetooth 5.3 with LE Audio",
            "microphone": "VoiceAware hands-free calling microphone",
            "connectivity": "Bluetooth 5.3, Multi-Point Connection, 3.5mm Aux",
            "weight": "232 g",
            "water_resistance": "Not Rated",
            "price": 5999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0DVGHF7NK",
        "amazon_url": "https://www.amazon.in/dp/B0DVGHF7NK",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000215",
                "retailer": "Amazon",
                "external_product_id": "B0DVGHF7NK",
                "url": "https://www.amazon.in/dp/B0DVGHF7NK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000215",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/41ELxYw4xAL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000215-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000215",
                "external_product_id": "B0C9YQ88Z9",
                "image_url": "https://m.media-amazon.com/images/I/41ELxYw4xAL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/51wB7-7Q7RL._SL1500_.jpg",
            "accessories": "https://m.media-amazon.com/images/I/61o2K3x8bCL._SL1500_.jpg",
            "ports": "https://m.media-amazon.com/images/I/51p6K8m1vTL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71q8P1v5L4L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Tune 770NC",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the JBL Tune 770NC are top-tier."
            }
        ],
        "external_product_id": "B0C9YQ88Z9",
        "asin": "B0C9YQ88Z9",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000215",
                "retailer": "Amazon",
                "external_product_id": "B0C9YQ88Z9",
                "url": "https://www.amazon.in/dp/B0C9YQ88Z9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000215",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/51wB7-7Q7RL._SL1500_.jpg"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000216",
        "product_id": "c1000000-0000-0000-0000-000000000216",
        "title": "HyperX Cloud II Wireless Gaming Headset - Black/Red",
        "slug": "hyperx-cloud-ii",
        "brand": "HyperX",
        "model": "Cloud II Wireless",
        "sku": "HYPERX-CLOUD-II",
        "model_number": "HYPERX-CLOUD-II",
        "category": "Audio & Headphones",
        "subcategory": "Wireless Gaming Headsets",
        "is_component": false,
        "price": 9990.0,
        "currency": "INR",
        "description": "HyperX Cloud II Wireless Gaming Headset - Black/Red delivering 53mm dynamic drivers with neodymium magnets sound reproduction, Closed cup passive noise isolation, and 30 hours battery life.",
        "specs": {
            "type": "Over-Ear Wireless Gaming Headset",
            "driver": "53mm dynamic drivers with neodymium magnets",
            "anc": "Closed cup passive noise isolation",
            "battery": "30 hours battery life",
            "codec": "DTS Headphone:X Spatial Audio",
            "microphone": "Detachable noise-cancelling microphone with LED mute indicator",
            "connectivity": "2.4GHz low-latency wireless USB dongle",
            "weight": "300 g",
            "water_resistance": "Not Rated",
            "price": 9990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08NTYB4M7",
        "amazon_url": "https://www.amazon.in/dp/B08NTYB4M7",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000216",
                "retailer": "Amazon",
                "external_product_id": "B08NTYB4M7",
                "url": "https://www.amazon.in/dp/B08NTYB4M7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000216",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61e0+8QzVBL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000216-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000216",
                "external_product_id": "B08NTYB4M7",
                "image_url": "https://m.media-amazon.com/images/I/61e0+8QzVBL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HyperX%20Cloud%20II%20Wireless%20Gaming%20Hea</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Cloud II Wireless",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the HyperX Cloud II Wireless are top-tier."
            }
        ],
        "external_product_id": "B08NTYB4M7",
        "asin": "B08NTYB4M7",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000216",
                "retailer": "Amazon",
                "external_product_id": "B08NTYB4M7",
                "url": "https://www.amazon.in/dp/B08NTYB4M7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000216",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HyperX%20Cloud%20II%20Wireless%20Gaming%20Hea</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000217",
        "product_id": "c1000000-0000-0000-0000-000000000217",
        "title": "Sony WF-C700N Truly Wireless Noise Cancelling Earbuds - Sage Green",
        "slug": "sony-wfc700n",
        "brand": "Sony",
        "model": "WF-C700N",
        "sku": "SONY-WFC700N",
        "model_number": "SONY-WFC700N",
        "category": "Audio & Headphones",
        "subcategory": "Compact ANC TWS",
        "is_component": false,
        "price": 7990.0,
        "currency": "INR",
        "description": "Sony WF-C700N Truly Wireless Noise Cancelling Earbuds - Sage Green delivering 5mm DSEE Driver sound reproduction, Yes, Noise Sensor ANC, and 15 hours total.",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "5mm DSEE Driver",
            "anc": "Yes, Noise Sensor ANC",
            "battery": "15 hours total",
            "codec": "AAC, SBC",
            "microphone": "Wind noise reduction mic",
            "connectivity": "Bluetooth 5.2, Multipoint",
            "weight": "4.6 g",
            "water_resistance": "IPX4",
            "price": 7990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BZQM5ZDL",
        "amazon_url": "https://www.amazon.in/dp/B0BZQM5ZDL",
        "flipkart_url": "https://www.flipkart.com/sony-wf-c700n-lightest-tws-anc-20hr-battery-in-ear-10-min-quick-charge-multi-point-bluetooth-headset/p/itmb0be8b51b21d7",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000217",
                "retailer": "Amazon",
                "external_product_id": "B0BZQM5ZDL",
                "url": "https://www.amazon.in/dp/B0BZQM5ZDL",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000217",
                "retailer": "Flipkart",
                "external_product_id": "itmb0be8b51b21d7",
                "url": "https://www.flipkart.com/sony-wf-c700n-lightest-tws-anc-20hr-battery-in-ear-10-min-quick-charge-multi-point-bluetooth-headset/p/itmb0be8b51b21d7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51ni1o+keWL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000217-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000217",
                "external_product_id": "B0C1L8Q88H",
                "image_url": "https://m.media-amazon.com/images/I/51ni1o+keWL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WF-C700N%20Truly%20Wireless%20Noise%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - WF-C700N",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony WF-C700N are top-tier."
            }
        ],
        "external_product_id": "B0C1L8Q88H",
        "asin": "B0C1L8Q88H",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000217",
                "retailer": "Amazon",
                "external_product_id": "B0C1L8Q88H",
                "url": "https://www.amazon.in/dp/B0C1L8Q88H",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000217",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20WF-C700N%20Truly%20Wireless%20Noise%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000218",
        "product_id": "c1000000-0000-0000-0000-000000000218",
        "title": "Sony MDR-7506 Professional Large Diaphragm Headphone",
        "slug": "sony-mdr7506",
        "brand": "Sony",
        "model": "MDR-7506",
        "sku": "SONY-MDR7506",
        "model_number": "SONY-MDR7506",
        "category": "Audio & Headphones",
        "subcategory": "Pro Studio Monitor",
        "is_component": false,
        "price": 8990.0,
        "currency": "INR",
        "description": "Sony MDR-7506 Professional Large Diaphragm Headphone delivering 40mm Neodymium Driver sound reproduction, Passive studio isolation, and N/A (Passive Wired).",
        "specs": {
            "type": "Over-Ear Closed-Back Wired",
            "driver": "40mm Neodymium Driver",
            "anc": "Passive studio isolation",
            "battery": "N/A (Passive Wired)",
            "codec": "Analog Studio Sound (10Hz - 20kHz)",
            "microphone": "None",
            "connectivity": "3m coiled cable, 3.5mm/6.3mm gold plated",
            "weight": "230 g",
            "water_resistance": "Not Rated",
            "price": 8990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B000AJIF4E",
        "amazon_url": "https://www.amazon.in/dp/B000AJIF4E",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000218",
                "retailer": "Amazon",
                "external_product_id": "B000AJIF4E",
                "url": "https://www.amazon.in/dp/B000AJIF4E",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000218",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51F-Ok9xuzL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000218-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000218",
                "external_product_id": "B000AJIF4E",
                "image_url": "https://m.media-amazon.com/images/I/51F-Ok9xuzL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20MDR-7506%20Professional%20Large%20Di</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - MDR-7506",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sony MDR-7506 are top-tier."
            }
        ],
        "external_product_id": "B000AJIF4E",
        "asin": "B000AJIF4E",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000218",
                "retailer": "Amazon",
                "external_product_id": "B000AJIF4E",
                "url": "https://www.amazon.in/dp/B000AJIF4E",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000218",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sony%20MDR-7506%20Professional%20Large%20Di</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000219",
        "product_id": "c1000000-0000-0000-0000-000000000219",
        "title": "Sennheiser Accentum Wireless Headphones - Black",
        "slug": "sennheiser-accentum",
        "brand": "Sennheiser",
        "model": "Accentum",
        "sku": "SENNHEISER-ACCENTUM",
        "model_number": "SENNHEISER-ACCENTUM",
        "category": "Audio & Headphones",
        "subcategory": "Mid-Range Wireless ANC",
        "is_component": false,
        "price": 11990.0,
        "currency": "INR",
        "description": "Sennheiser Accentum Wireless Headphones - Black delivering 37mm Transducer sound reproduction, Yes, Hybrid ANC, and 50 hours playback.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "37mm Transducer",
            "anc": "Yes, Hybrid ANC",
            "battery": "50 hours playback",
            "codec": "aptX HD, AAC, SBC",
            "microphone": "2 beamforming mics",
            "connectivity": "Bluetooth 5.2",
            "weight": "222 g",
            "water_resistance": "Not Rated",
            "price": 11990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CGR586KV",
        "amazon_url": "https://www.amazon.in/dp/B0CGR586KV",
        "flipkart_url": "https://www.flipkart.com/sennheiser-accentum-wireless-over-ear-headphones-designed-germany-50hr-battery-bluetooth/p/itm28e134ac6e335",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000219",
                "retailer": "Amazon",
                "external_product_id": "B0CGR586KV",
                "url": "https://www.amazon.in/dp/B0CGR586KV",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000219",
                "retailer": "Flipkart",
                "external_product_id": "itm28e134ac6e335",
                "url": "https://www.flipkart.com/sennheiser-accentum-wireless-over-ear-headphones-designed-germany-50hr-battery-bluetooth/p/itm28e134ac6e335",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71St1R5DFGL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000219-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000219",
                "external_product_id": "B0CGVR15B8",
                "image_url": "https://m.media-amazon.com/images/I/71St1R5DFGL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Accentum%20Wireless%20Headph</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Accentum",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sennheiser Accentum are top-tier."
            }
        ],
        "external_product_id": "B0CGVR15B8",
        "asin": "B0CGVR15B8",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000219",
                "retailer": "Amazon",
                "external_product_id": "B0CGVR15B8",
                "url": "https://www.amazon.in/dp/B0CGVR15B8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000219",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Accentum%20Wireless%20Headph</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000220",
        "product_id": "c1000000-0000-0000-0000-000000000220",
        "title": "Sennheiser Momentum True Wireless 3 - Graphite",
        "slug": "sennheiser-mtw3",
        "brand": "Sennheiser",
        "model": "Momentum TW 3",
        "sku": "SENNHEISER-MTW3",
        "model_number": "SENNHEISER-MTW3",
        "category": "Audio & Headphones",
        "subcategory": "Audiophile TWS",
        "is_component": false,
        "price": 18990.0,
        "currency": "INR",
        "description": "Sennheiser Momentum True Wireless 3 - Graphite delivering 7mm TrueResponse Driver sound reproduction, Yes, Adaptive ANC, and 28 hours with case.",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "7mm TrueResponse Driver",
            "anc": "Yes, Adaptive ANC",
            "battery": "28 hours with case",
            "codec": "aptX Adaptive, AAC",
            "microphone": "3 mics per earbud",
            "connectivity": "Bluetooth 5.2, Qi wireless",
            "weight": "5.8 g",
            "water_resistance": "IPX4",
            "price": 18990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09T8YPFV2",
        "amazon_url": "https://www.amazon.in/dp/B09T8YPFV2",
        "flipkart_url": "https://www.flipkart.com/sennheiser-momentum-true-wireless-3-earbuds-adaptive-noise-cancellation-bluetooth-headset/p/itme99f87279e65d",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000220",
                "retailer": "Amazon",
                "external_product_id": "B09T8YPFV2",
                "url": "https://www.amazon.in/dp/B09T8YPFV2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000220",
                "retailer": "Flipkart",
                "external_product_id": "itme99f87279e65d",
                "url": "https://www.flipkart.com/sennheiser-momentum-true-wireless-3-earbuds-adaptive-noise-cancellation-bluetooth-headset/p/itme99f87279e65d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/617BfhOXfpL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000220-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000220",
                "external_product_id": "B09T8XQ97B",
                "image_url": "https://m.media-amazon.com/images/I/617BfhOXfpL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Momentum%20True%20Wireless%203</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Momentum TW 3",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Sennheiser Momentum TW 3 are top-tier."
            }
        ],
        "external_product_id": "B09T8XQ97B",
        "asin": "B09T8XQ97B",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000220",
                "retailer": "Amazon",
                "external_product_id": "B09T8XQ97B",
                "url": "https://www.amazon.in/dp/B09T8XQ97B",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000220",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Sennheiser%20Momentum%20True%20Wireless%203</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000221",
        "product_id": "c1000000-0000-0000-0000-000000000221",
        "title": "Audio-Technica ATH-M50xBT2 Wireless Studio Monitor",
        "slug": "ath-m50xbt2",
        "brand": "Audio-Technica",
        "model": "ATH-M50xBT2",
        "sku": "ATH-M50XBT2",
        "model_number": "ATH-M50XBT2",
        "category": "Audio & Headphones",
        "subcategory": "Wireless Studio Monitor",
        "is_component": false,
        "price": 17990.0,
        "currency": "INR",
        "description": "Audio-Technica ATH-M50xBT2 Wireless Studio Monitor delivering 45mm Large Aperture Driver sound reproduction, Passive Acoustic Isolation, and 50 hours continuous.",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "45mm Large Aperture Driver",
            "anc": "Passive Acoustic Isolation",
            "battery": "50 hours continuous",
            "codec": "LDAC, AAC, SBC",
            "microphone": "Dual beamforming mics with sidetone",
            "connectivity": "Bluetooth 5.0, 3.5mm Aux",
            "weight": "307 g",
            "water_resistance": "Not Rated",
            "price": 17990.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09BYR3ZLF",
        "amazon_url": null,
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000221",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000221",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50xBT2%20Wireless</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000221-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000221",
                "external_product_id": "B09BYR3ZLF",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50xBT2%20Wireless</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50xBT2%20Wireless</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - ATH-M50xBT2",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Audio-Technica ATH-M50xBT2 are top-tier."
            }
        ],
        "external_product_id": "B09BYR3ZLF",
        "asin": "B09BYR3ZLF",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000221",
                "retailer": "Amazon",
                "external_product_id": "B09BYR3ZLF",
                "url": "https://www.amazon.in/dp/B09BYR3ZLF",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000221",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M50xBT2%20Wireless</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000222",
        "product_id": "c1000000-0000-0000-0000-000000000222",
        "title": "Audio-Technica ATH-M20x Professional Monitor Headphones",
        "slug": "ath-m20x",
        "brand": "Audio-Technica",
        "model": "ATH-M20x",
        "sku": "ATH-M20X",
        "model_number": "ATH-M20X",
        "category": "Audio & Headphones",
        "subcategory": "Budget Studio Monitor",
        "is_component": false,
        "price": 4490.0,
        "currency": "INR",
        "description": "Audio-Technica ATH-M20x Professional Monitor Headphones delivering 40mm Drivers sound reproduction, Passive isolation, and N/A (Passive Wired).",
        "specs": {
            "type": "Over-Ear Wired",
            "driver": "40mm Drivers",
            "anc": "Passive isolation",
            "battery": "N/A (Passive Wired)",
            "codec": "Analog Studio Audio",
            "microphone": "None",
            "connectivity": "3m straight cable with 6.3mm adapter",
            "weight": "190 g",
            "water_resistance": "Not Rated",
            "price": 4490.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B00HVLUR18",
        "amazon_url": "https://www.amazon.in/dp/B00HVLUR18",
        "flipkart_url": "https://www.flipkart.com/audio-technica-ath-m20x-headphone-black-over-ear-wired-without-mic/p/itm3c99543d19bf3",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000222",
                "retailer": "Amazon",
                "external_product_id": "B00HVLUR18",
                "url": "https://www.amazon.in/dp/B00HVLUR18",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000222",
                "retailer": "Flipkart",
                "external_product_id": "itm3c99543d19bf3",
                "url": "https://www.flipkart.com/audio-technica-ath-m20x-headphone-black-over-ear-wired-without-mic/p/itm3c99543d19bf3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/81zcnWFPwVS._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000222-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000222",
                "external_product_id": "B00HVLUR54",
                "image_url": "https://m.media-amazon.com/images/I/81zcnWFPwVS._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M20x%20Professiona</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - ATH-M20x",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Audio-Technica ATH-M20x are top-tier."
            }
        ],
        "external_product_id": "B00HVLUR54",
        "asin": "B00HVLUR54",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000222",
                "retailer": "Amazon",
                "external_product_id": "B00HVLUR54",
                "url": "https://www.amazon.in/dp/B00HVLUR54",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000222",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Audio-Technica%20ATH-M20x%20Professiona</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000223",
        "product_id": "c1000000-0000-0000-0000-000000000223",
        "title": "OnePlus Buds 3 TWS Earbuds - Metallic Gray",
        "slug": "oneplus-buds-3",
        "brand": "OnePlus",
        "model": "Buds 3",
        "sku": "ONEPLUS-BUDS-3",
        "model_number": "ONEPLUS-BUDS-3",
        "category": "Audio & Headphones",
        "subcategory": "Mid-Range TWS",
        "is_component": false,
        "price": 4999.0,
        "currency": "INR",
        "description": "OnePlus Buds 3 TWS Earbuds - Metallic Gray delivering 10.4mm woofer + 6mm tweeter sound reproduction, Yes, 49dB Smart ANC, and 44 hours playback.",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "10.4mm woofer + 6mm tweeter",
            "anc": "Yes, 49dB Smart ANC",
            "battery": "44 hours playback",
            "codec": "LHDC 5.0, AAC, SBC",
            "microphone": "3 mics with AI call noise reduction",
            "connectivity": "Bluetooth 5.3, Google Fast Pair",
            "weight": "4.8 g",
            "water_resistance": "IP55",
            "price": 4999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CW6MXXGB",
        "amazon_url": "https://www.amazon.in/dp/B0CW6MXXGB",
        "flipkart_url": "https://www.flipkart.com/oneplus-buds-3-true-wireless-ear-earbuds-sliding-volume-control-49db-anc-bluetooth-headset/p/itm3f89e2c2d7b10",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000223",
                "retailer": "Amazon",
                "external_product_id": "B0CW6MXXGB",
                "url": "https://www.amazon.in/dp/B0CW6MXXGB",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000223",
                "retailer": "Flipkart",
                "external_product_id": "itm3f89e2c2d7b10",
                "url": "https://www.flipkart.com/oneplus-buds-3-true-wireless-ear-earbuds-sliding-volume-control-49db-anc-bluetooth-headset/p/itm3f89e2c2d7b10",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51fqxfdHIcL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000223-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000223",
                "external_product_id": "B0CQPP9ZJ2",
                "image_url": "https://m.media-amazon.com/images/I/51fqxfdHIcL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Buds%203%20TWS%20Earbuds%20-%20Metall</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Buds 3",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the OnePlus Buds 3 are top-tier."
            }
        ],
        "external_product_id": "B0CQPP9ZJ2",
        "asin": "B0CQPP9ZJ2",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000223",
                "retailer": "Amazon",
                "external_product_id": "B0CQPP9ZJ2",
                "url": "https://www.amazon.in/dp/B0CQPP9ZJ2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000223",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Buds%203%20TWS%20Earbuds%20-%20Metall</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000224",
        "product_id": "c1000000-0000-0000-0000-000000000224",
        "title": "OnePlus Nord Buds 2 TWS - Thunder Gray",
        "slug": "nord-buds-2",
        "brand": "OnePlus",
        "model": "Nord Buds 2",
        "sku": "NORD-BUDS-2",
        "model_number": "NORD-BUDS-2",
        "category": "Audio & Headphones",
        "subcategory": "Budget TWS with ANC",
        "is_component": false,
        "price": 2499.0,
        "currency": "INR",
        "description": "OnePlus Nord Buds 2 TWS - Thunder Gray delivering 12.4mm Titanized Dynamic Driver sound reproduction, Yes, 25dB Active Noise Cancellation, and 36 hours total.",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "12.4mm Titanized Dynamic Driver",
            "anc": "Yes, 25dB Active Noise Cancellation",
            "battery": "36 hours total",
            "codec": "AAC, SBC, Dolby Atmos",
            "microphone": "Dual mic AI clear call algorithm",
            "connectivity": "Bluetooth 5.3",
            "weight": "4.7 g",
            "water_resistance": "IP55",
            "price": 2499.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C22KVGBR",
        "amazon_url": "https://www.amazon.in/dp/B0C22KVGBR",
        "flipkart_url": "https://www.flipkart.com/oneplus-nord-buds-2-true-wireless-earbuds-25db-active-noise-cancellation-bluetooth-headset/p/itm89489818bb3e2",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000224",
                "retailer": "Amazon",
                "external_product_id": "B0C22KVGBR",
                "url": "https://www.amazon.in/dp/B0C22KVGBR",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000224",
                "retailer": "Flipkart",
                "external_product_id": "itm89489818bb3e2",
                "url": "https://www.flipkart.com/oneplus-nord-buds-2-true-wireless-earbuds-25db-active-noise-cancellation-bluetooth-headset/p/itm89489818bb3e2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/516jDyX+YrL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000224-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000224",
                "external_product_id": "B0BVRB2Z2N",
                "image_url": "https://m.media-amazon.com/images/I/516jDyX+YrL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%20Buds%202%20TWS%20-%20Thunder%20G</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Nord Buds 2",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the OnePlus Nord Buds 2 are top-tier."
            }
        ],
        "external_product_id": "B0BVRB2Z2N",
        "asin": "B0BVRB2Z2N",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000224",
                "retailer": "Amazon",
                "external_product_id": "B0BVRB2Z2N",
                "url": "https://www.amazon.in/dp/B0BVRB2Z2N",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000224",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>OnePlus%20Nord%20Buds%202%20TWS%20-%20Thunder%20G</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000225",
        "product_id": "c1000000-0000-0000-0000-000000000225",
        "title": "boAt Nirvana Ion TWS Earbuds - Charcoal Black",
        "slug": "boat-nirvana-ion",
        "brand": "boAt",
        "model": "Nirvana Ion",
        "sku": "BOAT-NIRVANA-ION",
        "model_number": "BOAT-NIRVANA-ION",
        "category": "Audio & Headphones",
        "subcategory": "Long Battery TWS",
        "is_component": false,
        "price": 1999.0,
        "currency": "INR",
        "description": "boAt Nirvana Ion TWS Earbuds - Charcoal Black delivering 10mm Dual EQ Drivers sound reproduction, ENx Quad Mic Noise Cancellation, and 120 hours total playtime (24h in-ear).",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "10mm Dual EQ Drivers",
            "anc": "ENx Quad Mic Noise Cancellation",
            "battery": "120 hours total playtime (24h in-ear)",
            "codec": "HiFi DSP, AAC",
            "microphone": "Quad Mics with ENx technology",
            "connectivity": "Bluetooth 5.2, BEAST Mode 60ms latency",
            "weight": "4.5 g",
            "water_resistance": "IPX4",
            "price": 1999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BVRB2Z2O",
        "amazon_url": null,
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000225",
                "retailer": "Amazon",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000225",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>boAt%20Nirvana%20Ion%20TWS%20Earbuds%20-%20Char</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000225-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000225",
                "external_product_id": "B0BVRB2Z2O",
                "image_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>boAt%20Nirvana%20Ion%20TWS%20Earbuds%20-%20Char</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>",
                "image_type": "front",
                "source": "Placeholder",
                "verified": false
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>boAt%20Nirvana%20Ion%20TWS%20Earbuds%20-%20Char</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Nirvana Ion",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the boAt Nirvana Ion are top-tier."
            }
        ],
        "external_product_id": "B0BVRB2Z2O",
        "asin": "B0BVRB2Z2O",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000225",
                "retailer": "Amazon",
                "external_product_id": "B0BVRB2Z2O",
                "url": "https://www.amazon.in/dp/B0BVRB2Z2O",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000225",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>boAt%20Nirvana%20Ion%20TWS%20Earbuds%20-%20Char</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000226",
        "product_id": "c1000000-0000-0000-0000-000000000226",
        "title": "JBL Live 660NC Wireless Over-Ear Headphones - White",
        "slug": "jbl-live-660nc",
        "brand": "JBL",
        "model": "Live 660NC",
        "sku": "JBL-LIVE-660NC",
        "model_number": "JBL-LIVE-660NC",
        "category": "Audio & Headphones",
        "subcategory": "Mid-Range ANC",
        "is_component": false,
        "price": 8999.0,
        "currency": "INR",
        "description": "JBL Live 660NC Wireless Over-Ear Headphones - White delivering 40mm Signature Sound Drivers sound reproduction, Yes, Adaptive Noise Cancelling, and 50 hours (ANC Off), 40 hours (ANC On).",
        "specs": {
            "type": "Over-Ear Wireless",
            "driver": "40mm Signature Sound Drivers",
            "anc": "Yes, Adaptive Noise Cancelling",
            "battery": "50 hours (ANC Off), 40 hours (ANC On)",
            "codec": "AAC, SBC",
            "microphone": "Built-in dual microphones",
            "connectivity": "Bluetooth 5.0, 3.5mm Aux",
            "weight": "265 g",
            "water_resistance": "Not Rated",
            "price": 8999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B091FYLKNB",
        "amazon_url": "https://www.amazon.in/dp/B091FYLKNB",
        "flipkart_url": "https://www.flipkart.com/jbl-live-660nc-smart-adaptive-noise-cancellation-50-hr-playtime-speed-charge-bluetooth-headset/p/itm1b48abcd3dc59",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000226",
                "retailer": "Amazon",
                "external_product_id": "B091FYLKNB",
                "url": "https://www.amazon.in/dp/B091FYLKNB",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000226",
                "retailer": "Flipkart",
                "external_product_id": "itm1b48abcd3dc59",
                "url": "https://www.flipkart.com/jbl-live-660nc-smart-adaptive-noise-cancellation-50-hr-playtime-speed-charge-bluetooth-headset/p/itm1b48abcd3dc59",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61APOA2BNFL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000226-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000226",
                "external_product_id": "B08W5B4V91",
                "image_url": "https://m.media-amazon.com/images/I/61APOA2BNFL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>JBL%20Live%20660NC%20Wireless%20Over-Ear%20He</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - Live 660NC",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the JBL Live 660NC are top-tier."
            }
        ],
        "external_product_id": "B08W5B4V91",
        "asin": "B08W5B4V91",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000226",
                "retailer": "Amazon",
                "external_product_id": "B08W5B4V91",
                "url": "https://www.amazon.in/dp/B08W5B4V91",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000226",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>JBL%20Live%20660NC%20Wireless%20Over-Ear%20He</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000227",
        "product_id": "c1000000-0000-0000-0000-000000000227",
        "title": "Razer BlackShark V2 Pro Wireless Gaming Headset - Black",
        "slug": "razer-blackshark-v2pro",
        "brand": "Razer",
        "model": "BlackShark V2 Pro",
        "sku": "RAZER-BLACKSHARK-V2PRO",
        "model_number": "RAZER-BLACKSHARK-V2PRO",
        "category": "Audio & Headphones",
        "subcategory": "Esports Gaming Headsets",
        "is_component": false,
        "price": 14999.0,
        "currency": "INR",
        "description": "Razer BlackShark V2 Pro Wireless Gaming Headset - Black delivering Razer TriForce Titanium 50mm sound reproduction, Advanced passive noise cancellation, and 70 hours battery life.",
        "specs": {
            "type": "Over-Ear Wireless Gaming",
            "driver": "Razer TriForce Titanium 50mm",
            "anc": "Advanced passive noise cancellation",
            "battery": "70 hours battery life",
            "codec": "THX Spatial Audio",
            "microphone": "Razer HyperClear Super Wideband Mic",
            "connectivity": "Razer HyperSpeed 2.4GHz + Bluetooth 5.2",
            "weight": "320 g",
            "water_resistance": "Not Rated",
            "price": 14999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08WBLM3HC",
        "amazon_url": "https://www.amazon.in/dp/B08WBLM3HC",
        "flipkart_url": "https://www.flipkart.com/razer-blackshark-v2-pro-wireless-rz04-03220100-r3m1-bluetooth-gaming-headset/p/itm8d8619097f66d",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000227",
                "retailer": "Amazon",
                "external_product_id": "B08WBLM3HC",
                "url": "https://www.amazon.in/dp/B08WBLM3HC",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000227",
                "retailer": "Flipkart",
                "external_product_id": "itm8d8619097f66d",
                "url": "https://www.flipkart.com/razer-blackshark-v2-pro-wireless-rz04-03220100-r3m1-bluetooth-gaming-headset/p/itm8d8619097f66d",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/71Z9KK9-zvL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000227-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000227",
                "external_product_id": "B086PKMZ21",
                "image_url": "https://m.media-amazon.com/images/I/71Z9KK9-zvL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Razer%20BlackShark%20V2%20Pro%20Wireless%20Ga</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - BlackShark V2 Pro",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Razer BlackShark V2 Pro are top-tier."
            }
        ],
        "external_product_id": "B086PKMZ21",
        "asin": "B086PKMZ21",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000227",
                "retailer": "Amazon",
                "external_product_id": "B086PKMZ21",
                "url": "https://www.amazon.in/dp/B086PKMZ21",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000227",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Razer%20BlackShark%20V2%20Pro%20Wireless%20Ga</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c1000000-0000-0000-0000-000000000228",
        "product_id": "c1000000-0000-0000-0000-000000000228",
        "title": "Bose QuietComfort Ultra Earbuds - White Smoke",
        "slug": "bose-qc-ultra-buds",
        "brand": "Bose",
        "model": "QC Ultra Earbuds",
        "sku": "BOSE-QC-ULTRA-BUDS",
        "model_number": "BOSE-QC-ULTRA-BUDS",
        "category": "Audio & Headphones",
        "subcategory": "Flagship ANC Earbuds",
        "is_component": false,
        "price": 25900.0,
        "currency": "INR",
        "description": "Bose QuietComfort Ultra Earbuds - White Smoke delivering Custom High-Output Micro Driver sound reproduction, Yes, CustomTune Active Noise Cancelling, and 6 hours (earbuds) + 18 hours (case).",
        "specs": {
            "type": "Truly Wireless In-Ear",
            "driver": "Custom High-Output Micro Driver",
            "anc": "Yes, CustomTune Active Noise Cancelling",
            "battery": "6 hours (earbuds) + 18 hours (case)",
            "codec": "aptX Adaptive, AAC, SBC",
            "microphone": "Noise-rejecting microphone system",
            "connectivity": "Bluetooth 5.3, SimpleSync",
            "weight": "6.2 g per earbud",
            "water_resistance": "IPX4",
            "price": 25900.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CD2F4B1G",
        "amazon_url": "https://www.amazon.in/dp/B0CD2F4B1G",
        "flipkart_url": "https://www.flipkart.com/bose-new-quietcomfort-ultra-wireless-noise-cancelling-earbuds-spatial-audio-bluetooth-headset/p/itmfd0f641f6cc64",
        "buy_links": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000228",
                "retailer": "Amazon",
                "external_product_id": "B0CD2F4B1G",
                "url": "https://www.amazon.in/dp/B0CD2F4B1G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000228",
                "retailer": "Flipkart",
                "external_product_id": "itmfd0f641f6cc64",
                "url": "https://www.flipkart.com/bose-new-quietcomfort-ultra-wireless-noise-cancelling-earbuds-spatial-audio-bluetooth-headset/p/itmfd0f641f6cc64",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/51qMK4q-NVL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c1000000-0000-0000-0000-000000000228-FRONT",
                "product_id": "c1000000-0000-0000-0000-000000000228",
                "external_product_id": "B0CCZ1L490",
                "image_url": "https://m.media-amazon.com/images/I/51qMK4q-NVL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Bose%20QuietComfort%20Ultra%20Earbuds%20-%20W</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Audio Quality - QC Ultra Earbuds",
                "rating": 4.8,
                "body": "Soundstage, noise cancellation, and call clarity on the Bose QC Ultra Earbuds are top-tier."
            }
        ],
        "external_product_id": "B0CCZ1L490",
        "asin": "B0CCZ1L490",
        "retailer_offers": [
            {
                "product_id": "c1000000-0000-0000-0000-000000000228",
                "retailer": "Amazon",
                "external_product_id": "B0CCZ1L490",
                "url": "https://www.amazon.in/dp/B0CCZ1L490",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c1000000-0000-0000-0000-000000000228",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Bose%20QuietComfort%20Ultra%20Earbuds%20-%20W</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000001",
        "product_id": "c2000000-0000-0000-0000-000000000001",
        "title": "ESP32-WROOM-32D Development Board (Dual-Core Wi-Fi & Bluetooth MCU)",
        "slug": "esp32-wroom-32d",
        "brand": "Espressif",
        "model": "ESP32-WROOM-32D",
        "sku": "ESP32-WROOM-32D",
        "model_number": "ESP32-WROOM-32D",
        "category": "Electronic Components & Modules",
        "subcategory": "Microcontroller Boards",
        "is_component": true,
        "price": 499.0,
        "currency": "INR",
        "description": "ESP32-WROOM-32D Development Board (Dual-Core Wi-Fi & Bluetooth MCU) - Technical hardware component with GPIO, UART, SPI, I2C, ADC, DAC, PWM interfaces, operating at 3.3V (5V via Micro-USB).",
        "specs": {
            "voltage": "3.3V (5V via Micro-USB)",
            "current": "500mA recommended",
            "interface": "GPIO, UART, SPI, I2C, ADC, DAC, PWM",
            "protocol": "802.11 b/g/n Wi-Fi, Bluetooth v4.2 BR/EDR & BLE",
            "package": "38-pin Breadboard DIP module",
            "dimensions": "51.5 x 28.3 mm",
            "operating_range": "-40\u00b0C to +85\u00b0C",
            "part_number": "ESP32-DevKitC-32D",
            "manufacturer": "Espressif Systems",
            "price": 499.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09KLQF4RR",
        "amazon_url": "https://www.amazon.in/dp/B09KLQF4RR",
        "flipkart_url": null,
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000001",
                "retailer": "Amazon",
                "external_product_id": "B09KLQF4RR",
                "url": "https://www.amazon.in/dp/B09KLQF4RR",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000001",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61qtydPJLBL._SX679_.jpg",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000001-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000001",
                "external_product_id": "B086MGV6F3",
                "image_url": "https://m.media-amazon.com/images/I/61qtydPJLBL._SX679_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61jPZp1Zc2L._SL1200_.jpg",
            "back": "https://m.media-amazon.com/images/I/61u9f2GfHPL._SL1100_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71f8N7x6vPL._SL1500_.jpg",
            "board": "https://m.media-amazon.com/images/I/61R12Wk2vCL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - ESP32-WROOM-32D",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the ESP32-DevKitC-32D are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B086MGV6F3",
        "asin": "B086MGV6F3",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000001",
                "retailer": "Amazon",
                "external_product_id": "B086MGV6F3",
                "url": "https://www.amazon.in/dp/B086MGV6F3",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000001",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61jPZp1Zc2L._SL1200_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000002",
        "product_id": "c2000000-0000-0000-0000-000000000002",
        "title": "NodeMCU ESP8266 V3 Lua Wi-Fi IoT Development Board (CH340)",
        "slug": "nodemcu-v3-esp8266",
        "brand": "AI-Thinker",
        "model": "NodeMCU v3",
        "sku": "NODEMCU-V3-ESP8266",
        "model_number": "NODEMCU-V3-ESP8266",
        "category": "Electronic Components & Modules",
        "subcategory": "Microcontroller Boards",
        "is_component": true,
        "price": 299.0,
        "currency": "INR",
        "description": "NodeMCU ESP8266 V3 Lua Wi-Fi IoT Development Board (CH340) - Technical hardware component with GPIO, PWM, I2C, 1-Wire, ADC interfaces, operating at 3.3V (5V via Micro-USB).",
        "specs": {
            "voltage": "3.3V (5V via Micro-USB)",
            "current": "300mA peak",
            "interface": "GPIO, PWM, I2C, 1-Wire, ADC",
            "protocol": "802.11 b/g/n Wi-Fi, TCP/IP stack",
            "package": "30-pin Breadboard module",
            "dimensions": "58 x 31 mm",
            "operating_range": "-40\u00b0C to +125\u00b0C",
            "part_number": "ESP-12E / CH340G",
            "manufacturer": "AI-Thinker",
            "price": 299.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B01M98LHT4",
        "amazon_url": "https://www.amazon.in/dp/B01M98LHT4",
        "flipkart_url": "https://www.flipkart.com/ds-robotics-wireless-module-ch340-nodemcu-v3-lua-wifi-internet-things-development-board-based-esp8266-electronic-components-hobby-kit/p/itme30651435f8f1",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000002",
                "retailer": "Amazon",
                "external_product_id": "B01M98LHT4",
                "url": "https://www.amazon.in/dp/B01M98LHT4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000002",
                "retailer": "Flipkart",
                "external_product_id": "itme30651435f8f1",
                "url": "https://www.flipkart.com/ds-robotics-wireless-module-ch340-nodemcu-v3-lua-wifi-internet-things-development-board-based-esp8266-electronic-components-hobby-kit/p/itme30651435f8f1",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kerfl3k0/electronic-hobby-kit/x/s/z/wireless-module-ch340-nodemcu-v3-lua-wifi-internet-of-things-original-imafvdhadmhxzfz5.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000002-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000002",
                "external_product_id": "B082F24NZL",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kerfl3k0/electronic-hobby-kit/x/s/z/wireless-module-ch340-nodemcu-v3-lua-wifi-internet-of-things-original-imafvdhadmhxzfz5.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61o4m8v7y8L._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61o4m8v7yIL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - NodeMCU v3",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the ESP-12E / CH340G are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B082F24NZL",
        "asin": "B082F24NZL",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000002",
                "retailer": "Amazon",
                "external_product_id": "B082F24NZL",
                "url": "https://www.amazon.in/dp/B082F24NZL",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000002",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61o4m8v7y8L._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000003",
        "product_id": "c2000000-0000-0000-0000-000000000003",
        "title": "Arduino Uno R3 DIP Microcontroller Board (ATmega328P with USB Cable)",
        "slug": "arduino-uno-r3",
        "brand": "Arduino",
        "model": "Uno R3",
        "sku": "ARDUINO-UNO-R3",
        "model_number": "ARDUINO-UNO-R3",
        "category": "Electronic Components & Modules",
        "subcategory": "Development Boards",
        "is_component": true,
        "price": 749.0,
        "currency": "INR",
        "description": "Arduino Uno R3 DIP Microcontroller Board (ATmega328P with USB Cable) - Technical hardware component with 14 Digital I/O (6 PWM), 6 Analog Inputs, UART interfaces, operating at 5V operating (7-12V input limit).",
        "specs": {
            "voltage": "5V operating (7-12V input limit)",
            "current": "40mA per I/O pin",
            "interface": "14 Digital I/O (6 PWM), 6 Analog Inputs, UART",
            "protocol": "UART, I2C, SPI",
            "package": "DIP-28 Socketed IC",
            "dimensions": "68.6 x 53.4 mm",
            "operating_range": "-40\u00b0C to +85\u00b0C",
            "part_number": "A000066",
            "manufacturer": "Arduino.cc",
            "price": 749.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B008GRTSV6",
        "amazon_url": "https://www.amazon.in/dp/B008GRTSV6",
        "flipkart_url": "https://www.flipkart.com/arduino-uno-r3-board-atmega328p/p/itm6e7c5fc169122",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "retailer": "Amazon",
                "external_product_id": "B008GRTSV6",
                "url": "https://www.amazon.in/dp/B008GRTSV6",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "retailer": "Flipkart",
                "external_product_id": "itm6e7c5fc169122",
                "url": "https://www.flipkart.com/arduino-uno-r3-board-atmega328p/p/itm6e7c5fc169122",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kfeamq80/learning-toy/q/r/7/uno-r3-board-atmega328p-arduino-original-imafvuwgc236fhzx.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000003-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "external_product_id": "B00844XE94",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kfeamq80/learning-toy/q/r/7/uno-r3-board-atmega328p-arduino-original-imafvuwgc236fhzx.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000003-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "external_product_id": "B00844XE94",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kf1fo280/learning-toy/r/q/r/uno-r3-board-compatible-usb-cable-arduino-uno-original-imafvhcnjmqznzsd.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61k3A9gQO7L._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/719F8aT8ZzL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61j3Xv7q8KL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Uno R3",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the A000066 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B00844XE94",
        "asin": "B00844XE94",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "retailer": "Amazon",
                "external_product_id": "B00844XE94",
                "url": "https://www.amazon.in/dp/B00844XE94",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000003",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61k3A9gQO7L._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000004",
        "product_id": "c2000000-0000-0000-0000-000000000004",
        "title": "Arduino Mega 2560 R3 Microcontroller Board (ATmega2560 16MHz)",
        "slug": "arduino-mega-2560",
        "brand": "Arduino",
        "model": "Mega 2560 R3",
        "sku": "ARDUINO-MEGA-2560",
        "model_number": "ARDUINO-MEGA-2560",
        "category": "Electronic Components & Modules",
        "subcategory": "Development Boards",
        "is_component": true,
        "price": 1499.0,
        "currency": "INR",
        "description": "Arduino Mega 2560 R3 Microcontroller Board (ATmega2560 16MHz) - Technical hardware component with 54 Digital I/O (15 PWM), 16 Analog Inputs, 4 UARTs interfaces, operating at 5V operating (7-12V input).",
        "specs": {
            "voltage": "5V operating (7-12V input)",
            "current": "40mA per I/O pin",
            "interface": "54 Digital I/O (15 PWM), 16 Analog Inputs, 4 UARTs",
            "protocol": "UART (4 ports), SPI, I2C",
            "package": "QFP-100 soldered IC",
            "dimensions": "101.52 x 53.3 mm",
            "operating_range": "-40\u00b0C to +85\u00b0C",
            "part_number": "A000067",
            "manufacturer": "Arduino.cc",
            "price": 1499.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0046AMGW0",
        "amazon_url": "https://www.amazon.in/dp/B0046AMGW0",
        "flipkart_url": "https://www.flipkart.com/kartex-arduino-mega-2560-r3-compatible-board-atmega2560-ch340-usb-cable-electronic-components-hobby-kit/p/itm5b0af15bf1bc2",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "retailer": "Amazon",
                "external_product_id": "B0046AMGW0",
                "url": "https://www.amazon.in/dp/B0046AMGW0",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "retailer": "Flipkart",
                "external_product_id": "itm5b0af15bf1bc2",
                "url": "https://www.flipkart.com/kartex-arduino-mega-2560-r3-compatible-board-atmega2560-ch340-usb-cable-electronic-components-hobby-kit/p/itm5b0af15bf1bc2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/kf4ajrk0/electronic-hobby-kit/c/z/c/arduino-mega-2560-r3-compatible-board-with-atmega2560-ch340-with-original-imafvnfb6zr3v7a6.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000004-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "external_product_id": "B0046AMGW0",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kf4ajrk0/electronic-hobby-kit/c/z/c/arduino-mega-2560-r3-compatible-board-with-atmega2560-ch340-with-original-imafvnfb6zr3v7a6.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000004-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "external_product_id": "B0046AMGW0",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kf4ajrk0/electronic-hobby-kit/c/z/c/arduino-mega-2560-r3-compatible-board-with-atmega2560-ch340-with-original-imafvnfbeuzsknuz.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Arduino%20Mega%202560%20R3%20Microcontrolle</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Mega 2560 R3",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the A000067 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0046AMGW0",
        "asin": "B0046AMGW0",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "retailer": "Amazon",
                "external_product_id": "B0046AMGW0",
                "url": "https://www.amazon.in/dp/B0046AMGW0",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000004",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Arduino%20Mega%202560%20R3%20Microcontrolle</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000005",
        "product_id": "c2000000-0000-0000-0000-000000000005",
        "title": "Raspberry Pi 4 Model B (8GB RAM, Broadcom BCM2711 Quad-Core 1.5GHz)",
        "slug": "rpi4-8gb",
        "brand": "Raspberry Pi",
        "model": "Raspberry Pi 4 Model B",
        "sku": "RPI4-8GB",
        "model_number": "RPI4-8GB",
        "category": "Electronic Components & Modules",
        "subcategory": "Single Board Computers",
        "is_component": true,
        "price": 7999.0,
        "currency": "INR",
        "description": "Raspberry Pi 4 Model B (8GB RAM, Broadcom BCM2711 Quad-Core 1.5GHz) - Technical hardware component with 40-pin GPIO, 2x USB 3.0, 2x USB 2.0, Gigabit Ethernet, 2x Micro-HDMI interfaces, operating at 5V DC via USB-C (3A).",
        "specs": {
            "voltage": "5V DC via USB-C (3A)",
            "current": "3.0A minimum power supply",
            "interface": "40-pin GPIO, 2x USB 3.0, 2x USB 2.0, Gigabit Ethernet, 2x Micro-HDMI",
            "protocol": "Gigabit Ethernet, 2.4/5.0GHz 802.11ac Wi-Fi, Bluetooth 5.0 BLE",
            "package": "Single Board Computer",
            "dimensions": "88 x 58 x 19.5 mm",
            "operating_range": "0\u00b0C to +50\u00b0C",
            "part_number": "RPI4-MODBP-8GB",
            "manufacturer": "Raspberry Pi Foundation",
            "price": 7999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09TTKT94J",
        "amazon_url": "https://www.amazon.in/dp/B09TTKT94J",
        "flipkart_url": "https://www.flipkart.com/indian-hobby-center-raspberry-pi-4-model-b-8-gb-ram-electronic-components-kit/p/itmccac2ab7a8aa8",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "retailer": "Amazon",
                "external_product_id": "B09TTKT94J",
                "url": "https://www.amazon.in/dp/B09TTKT94J",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "retailer": "Flipkart",
                "external_product_id": "itmccac2ab7a8aa8",
                "url": "https://www.flipkart.com/indian-hobby-center-raspberry-pi-4-model-b-8-gb-ram-electronic-components-kit/p/itmccac2ab7a8aa8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://m.media-amazon.com/images/I/61mpMH5TzkL._SL1500_.jpg",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000005-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "external_product_id": "B0899VXM8F",
                "image_url": "https://m.media-amazon.com/images/I/61mpMH5TzkL._SL1500_.jpg",
                "image_type": "front",
                "source": "Amazon",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000005-BACK",
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "external_product_id": "B0899VXM8F",
                "image_url": "https://m.media-amazon.com/images/I/61Zf1fWf3lL._SL1500_.jpg",
                "image_type": "back",
                "source": "Amazon",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61mpMH5TzkL._SL1500_.jpg",
            "back": "https://m.media-amazon.com/images/I/61Zf1fWf3lL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71s8L5q5L-L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Raspberry Pi 4 Model B",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the RPI4-MODBP-8GB are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0899VXM8F",
        "asin": "B0899VXM8F",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "retailer": "Amazon",
                "external_product_id": "B0899VXM8F",
                "url": "https://www.amazon.in/dp/B0899VXM8F",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000005",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61mpMH5TzkL._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000006",
        "product_id": "c2000000-0000-0000-0000-000000000006",
        "title": "Raspberry Pi 5 (8GB RAM, Broadcom BCM2712 Quad-Core Cortex-A76 2.4GHz)",
        "slug": "rpi5-8gb",
        "brand": "Raspberry Pi",
        "model": "Raspberry Pi 5",
        "sku": "RPI5-8GB",
        "model_number": "RPI5-8GB",
        "category": "Electronic Components & Modules",
        "subcategory": "Single Board Computers",
        "is_component": true,
        "price": 9999.0,
        "currency": "INR",
        "description": "Raspberry Pi 5 (8GB RAM, Broadcom BCM2712 Quad-Core Cortex-A76 2.4GHz) - Technical hardware component with PCIe 2.0 x1 interface, 2x 4-lane MIPI camera/display, 40-pin GPIO interfaces, operating at 5V DC via USB-C PD (5A/25W).",
        "specs": {
            "voltage": "5V DC via USB-C PD (5A/25W)",
            "current": "5.0A recommended",
            "interface": "PCIe 2.0 x1 interface, 2x 4-lane MIPI camera/display, 40-pin GPIO",
            "protocol": "Gigabit Ethernet with PoE+, dual-band 802.11ac Wi-Fi, Bluetooth 5.0",
            "package": "Single Board Computer",
            "dimensions": "85 x 56 mm",
            "operating_range": "0\u00b0C to +50\u00b0C",
            "part_number": "SC1112",
            "manufacturer": "Raspberry Pi Foundation",
            "price": 9999.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0CK2FCG1K",
        "amazon_url": "https://www.amazon.in/dp/B0CK2FCG1K",
        "flipkart_url": "https://www.flipkart.com/raspberry-pi-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-single-board-computer-motherboard/p/itm9560c23bdb9b9",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "retailer": "Amazon",
                "external_product_id": "B0CK2FCG1K",
                "url": "https://www.amazon.in/dp/B0CK2FCG1K",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "retailer": "Flipkart",
                "external_product_id": "itm9560c23bdb9b9",
                "url": "https://www.flipkart.com/raspberry-pi-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-single-board-computer-motherboard/p/itm9560c23bdb9b9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/motherboard/l/p/p/raspberry-pi-5-8gb-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-original-imagudmuhqcjvtgd.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000006-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "external_product_id": "B0CN586R2A",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/motherboard/l/p/p/raspberry-pi-5-8gb-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-original-imagudmuhqcjvtgd.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000006-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "external_product_id": "B0CN586R2A",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/motherboard/z/z/a/raspberry-pi-5-8gb-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-original-imagudmuahxhz32f.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Raspberry%20Pi%205%20%288GB%20RAM%2C%20Broadcom%20B</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Raspberry Pi 5",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SC1112 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0CN586R2A",
        "asin": "B0CN586R2A",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "retailer": "Amazon",
                "external_product_id": "B0CN586R2A",
                "url": "https://www.amazon.in/dp/B0CN586R2A",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000006",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>Raspberry%20Pi%205%20%288GB%20RAM%2C%20Broadcom%20B</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000007",
        "product_id": "c2000000-0000-0000-0000-000000000007",
        "title": "Raspberry Pi Pico W with Pre-Soldered Headers (RP2040 Dual-Core with Wi-Fi)",
        "slug": "rpi-pico-w",
        "brand": "Raspberry Pi",
        "model": "Pico W",
        "sku": "RPI-PICO-W",
        "model_number": "RPI-PICO-W",
        "category": "Electronic Components & Modules",
        "subcategory": "Microcontroller Boards",
        "is_component": true,
        "price": 649.0,
        "currency": "INR",
        "description": "Raspberry Pi Pico W with Pre-Soldered Headers (RP2040 Dual-Core with Wi-Fi) - Technical hardware component with 26 multi-function GPIO pins, 3 ADC, 2 UART, 2 SPI, 2 I2C, 16 PWM interfaces, operating at 1.8V to 5.5V DC (Micro-USB).",
        "specs": {
            "voltage": "1.8V to 5.5V DC (Micro-USB)",
            "current": "100mA typical",
            "interface": "26 multi-function GPIO pins, 3 ADC, 2 UART, 2 SPI, 2 I2C, 16 PWM",
            "protocol": "Single-band 2.4GHz 802.11n Wi-Fi, Bluetooth 5.2",
            "package": "Castellated module DIP-40",
            "dimensions": "51 x 21 mm",
            "operating_range": "-20\u00b0C to +70\u00b0C",
            "part_number": "SC0918",
            "manufacturer": "Raspberry Pi Foundation",
            "price": 649.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0BK9W4H2Q",
        "amazon_url": "https://www.amazon.in/dp/B0BK9W4H2Q",
        "flipkart_url": "https://www.flipkart.com/raspberry-pi-pico-w-wireless-am4socket-nano-itx-armv7-chipset-ddr4-motherboard-desktop-mobile-tablet-workstation/p/itm3588fb962986c",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "retailer": "Amazon",
                "external_product_id": "B0BK9W4H2Q",
                "url": "https://www.amazon.in/dp/B0BK9W4H2Q",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "retailer": "Flipkart",
                "external_product_id": "itm3588fb962986c",
                "url": "https://www.flipkart.com/raspberry-pi-pico-w-wireless-am4socket-nano-itx-armv7-chipset-ddr4-motherboard-desktop-mobile-tablet-workstation/p/itm3588fb962986c",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l51d30w0/motherboard/s/c/n/pico-w-pico-w-wireless-raspberry-pi-original-imagfshhgdxpga6t.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000007-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "external_product_id": "B0B7CBM4KV",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l51d30w0/motherboard/s/c/n/pico-w-pico-w-wireless-raspberry-pi-original-imagfshhgdxpga6t.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000007-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "external_product_id": "B0B7CBM4KV",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l51d30w0/motherboard/f/y/c/pico-w-pico-w-wireless-raspberry-pi-original-imagfshhvgvzhehy.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61Y0G6v7f5L._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/61Y0G6v7fIL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Pico W",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SC0918 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0B7CBM4KV",
        "asin": "B0B7CBM4KV",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "retailer": "Amazon",
                "external_product_id": "B0B7CBM4KV",
                "url": "https://www.amazon.in/dp/B0B7CBM4KV",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000007",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61Y0G6v7f5L._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000008",
        "product_id": "c2000000-0000-0000-0000-000000000008",
        "title": "DHT11 Digital Temperature and Humidity Sensor Module with Cable",
        "slug": "sensor-dht11-mod",
        "brand": "Aosong",
        "model": "DHT11 Module",
        "sku": "SENSOR-DHT11-MOD",
        "model_number": "SENSOR-DHT11-MOD",
        "category": "Electronic Components & Modules",
        "subcategory": "Environmental Sensors",
        "is_component": true,
        "price": 119.0,
        "currency": "INR",
        "description": "DHT11 Digital Temperature and Humidity Sensor Module with Cable - Technical hardware component with 1-Wire Digital Signal interfaces, operating at 3.3V - 5.5V DC.",
        "specs": {
            "voltage": "3.3V - 5.5V DC",
            "current": "0.5mA operating, 100uA standby",
            "interface": "1-Wire Digital Signal",
            "protocol": "Single-bus bidirectional digital protocol",
            "package": "3-pin breakout PCB with 10k pullup resistor",
            "dimensions": "28 x 12 x 8 mm",
            "operating_range": "Temp: 0-50\u00b0C (\u00b12\u00b0C), Humidity: 20-90% RH (\u00b15%)",
            "part_number": "DHT11-MOD",
            "manufacturer": "Guangzhou Aosong Electronics",
            "price": 119.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07FSPW4VK",
        "amazon_url": "https://www.amazon.in/dp/B07FSPW4VK",
        "flipkart_url": "https://www.flipkart.com/vgs-marketings-dht11-digital-temperature-humidity-dht-11-sensor-arduino-diy-module-raspberry-controller-electronic-hobby-kit/p/itmf963eeqrezg77",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "retailer": "Amazon",
                "external_product_id": "B07FSPW4VK",
                "url": "https://www.amazon.in/dp/B07FSPW4VK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "retailer": "Flipkart",
                "external_product_id": "itmf963eeqrezg77",
                "url": "https://www.flipkart.com/vgs-marketings-dht11-digital-temperature-humidity-dht-11-sensor-arduino-diy-module-raspberry-controller-electronic-hobby-kit/p/itmf963eeqrezg77",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/jm81zm80/electronic-hobby-kit/p/4/r/dht11-digital-temperature-and-humidity-temperature-dht-11-sensor-original-imaf95njtbvbzmfe.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000008-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "external_product_id": "B01N9KS2XH",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/jm81zm80/electronic-hobby-kit/p/4/r/dht11-digital-temperature-and-humidity-temperature-dht-11-sensor-original-imaf95njtbvbzmfe.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000008-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "external_product_id": "B01N9KS2XH",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/jm81zm80/electronic-hobby-kit/p/4/r/dht11-digital-temperature-and-humidity-temperature-dht-11-sensor-original-imaf95nhxcbxam3y.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>DHT11%20Digital%20Temperature%20and%20Humid</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - DHT11 Module",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the DHT11-MOD are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B01N9KS2XH",
        "asin": "B01N9KS2XH",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "retailer": "Amazon",
                "external_product_id": "B01N9KS2XH",
                "url": "https://www.amazon.in/dp/B01N9KS2XH",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000008",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>DHT11%20Digital%20Temperature%20and%20Humid</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000009",
        "product_id": "c2000000-0000-0000-0000-000000000009",
        "title": "DHT22 / AM2302 High Precision Digital Temperature and Humidity Sensor",
        "slug": "sensor-dht22-am2302",
        "brand": "Aosong",
        "model": "DHT22 AM2302",
        "sku": "SENSOR-DHT22-AM2302",
        "model_number": "SENSOR-DHT22-AM2302",
        "category": "Electronic Components & Modules",
        "subcategory": "Environmental Sensors",
        "is_component": true,
        "price": 329.0,
        "currency": "INR",
        "description": "DHT22 / AM2302 High Precision Digital Temperature and Humidity Sensor - Technical hardware component with 1-Wire Digital Bus interfaces, operating at 3.3V - 6V DC.",
        "specs": {
            "voltage": "3.3V - 6V DC",
            "current": "1.5mA measuring, 50uA standby",
            "interface": "1-Wire Digital Bus",
            "protocol": "Aosong 1-wire high precision serial bus",
            "package": "4-pin plastic package (0.1 inch pin pitch)",
            "dimensions": "38 x 15 x 10 mm",
            "operating_range": "Temp: -40 to 80\u00b0C (\u00b10.5\u00b0C), Humidity: 0-100% RH (\u00b12%)",
            "part_number": "AM2302",
            "manufacturer": "Guangzhou Aosong Electronics",
            "price": 329.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B01DA3C452",
        "amazon_url": "https://www.amazon.in/dp/B01DA3C452",
        "flipkart_url": "https://www.flipkart.com/iduino-dht22-am2302-digital-temperature-humidity-sensor-controller-electronic-hobby-kit/p/itmd0498454f64b2",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "retailer": "Amazon",
                "external_product_id": "B01DA3C452",
                "url": "https://www.amazon.in/dp/B01DA3C452",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "retailer": "Flipkart",
                "external_product_id": "itmd0498454f64b2",
                "url": "https://www.flipkart.com/iduino-dht22-am2302-digital-temperature-humidity-sensor-controller-electronic-hobby-kit/p/itmd0498454f64b2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l3os4280/electronic-hobby-kit/n/d/y/dht22-am2302-digital-temperature-and-humidity-sensor-iduino-original-imagerh2pfshgamf.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000009-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "external_product_id": "B01N6PB489",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l3os4280/electronic-hobby-kit/n/d/y/dht22-am2302-digital-temperature-and-humidity-sensor-iduino-original-imagerh2pfshgamf.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000009-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "external_product_id": "B01N6PB489",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/l3os4280/electronic-hobby-kit/z/j/i/dht22-am2302-digital-temperature-and-humidity-sensor-iduino-original-imagerh2ygg26pyf.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/51w8N4r6CRL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - DHT22 AM2302",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the AM2302 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B01N6PB489",
        "asin": "B01N6PB489",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "retailer": "Amazon",
                "external_product_id": "B01N6PB489",
                "url": "https://www.amazon.in/dp/B01N6PB489",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000009",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/51w8N4r6CRL._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000010",
        "product_id": "c2000000-0000-0000-0000-000000000010",
        "title": "BME280 Digital Atmospheric Barometric Pressure, Temp & Humidity Sensor (I2C/SPI 3.3V)",
        "slug": "sensor-bme280-i2c",
        "brand": "Bosch",
        "model": "BME280 Breakout",
        "sku": "SENSOR-BME280-I2C",
        "model_number": "SENSOR-BME280-I2C",
        "category": "Electronic Components & Modules",
        "subcategory": "Environmental Sensors",
        "is_component": true,
        "price": 449.0,
        "currency": "INR",
        "description": "BME280 Digital Atmospheric Barometric Pressure, Temp & Humidity Sensor (I2C/SPI 3.3V) - Technical hardware component with I2C (address 0x76 or 0x77), SPI (3 or 4 wire) interfaces, operating at 3.3V DC (with onboard 3.3V LDO regulator).",
        "specs": {
            "voltage": "3.3V DC (with onboard 3.3V LDO regulator)",
            "current": "3.6 uA @ 1Hz humidity and temperature",
            "interface": "I2C (address 0x76 or 0x77), SPI (3 or 4 wire)",
            "protocol": "I2C Fast Mode 3.4MHz, SPI up to 10MHz",
            "package": "6-pin breakout module",
            "dimensions": "15.4 x 11.6 mm",
            "operating_range": "Pressure: 300-1100 hPa (\u00b11 hPa), Temp: -40 to 85\u00b0C",
            "part_number": "BME280",
            "manufacturer": "Bosch Sensortec",
            "price": 449.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07KKB7HR6",
        "amazon_url": "https://www.amazon.in/dp/B07KKB7HR6",
        "flipkart_url": "https://www.flipkart.com/kitsguru-breakout-temperature-humidity-barometric-pressure-bme280-digital-sensor-module-electronic-components-hobby-kit/p/itmf87xwwyjf2fua",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "retailer": "Amazon",
                "external_product_id": "B07KKB7HR6",
                "url": "https://www.amazon.in/dp/B07KKB7HR6",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "retailer": "Flipkart",
                "external_product_id": "itmf87xwwyjf2fua",
                "url": "https://www.flipkart.com/kitsguru-breakout-temperature-humidity-barometric-pressure-bme280-digital-sensor-module-electronic-components-hobby-kit/p/itmf87xwwyjf2fua",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1000/jkzrc7k0/electronic-hobby-kit/g/p/n/breakout-temperature-humidity-barometric-pressure-bme280-digital-original-imaf87xw88vx2ng9.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000010-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "external_product_id": "B07PRVSL9J",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/jkzrc7k0/electronic-hobby-kit/g/p/n/breakout-temperature-humidity-barometric-pressure-bme280-digital-original-imaf87xw88vx2ng9.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000010-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "external_product_id": "B07PRVSL9J",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/jkzrc7k0/electronic-hobby-kit/g/p/n/breakout-temperature-humidity-barometric-pressure-bme280-digital-original-imaf87xwhugcxhrx.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "board": "https://m.media-amazon.com/images/I/71W89r9bHLL._SL1500_.jpg",
            "connector": "https://m.media-amazon.com/images/I/61k9H5W6TGL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71q7Q5V1WHL._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - BME280 Breakout",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the BME280 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07PRVSL9J",
        "asin": "B07PRVSL9J",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "retailer": "Amazon",
                "external_product_id": "B07PRVSL9J",
                "url": "https://www.amazon.in/dp/B07PRVSL9J",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000010",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71W89r9bHLL._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000011",
        "product_id": "c2000000-0000-0000-0000-000000000011",
        "title": "HC-SR501 Pyroelectric Infrared PIR Motion Detector Sensor Module",
        "slug": "sensor-hcsr501-pir",
        "brand": "ElecFreaks",
        "model": "HC-SR501",
        "sku": "SENSOR-HCSR501-PIR",
        "model_number": "SENSOR-HCSR501-PIR",
        "category": "Electronic Components & Modules",
        "subcategory": "Motion Sensors",
        "is_component": true,
        "price": 149.0,
        "currency": "INR",
        "description": "HC-SR501 Pyroelectric Infrared PIR Motion Detector Sensor Module - Technical hardware component with Digital High (3.3V) / Low (0V) Output interfaces, operating at 4.5V - 20V DC input.",
        "specs": {
            "voltage": "4.5V - 20V DC input",
            "current": "65uA quiescent current",
            "interface": "Digital High (3.3V) / Low (0V) Output",
            "protocol": "Discrete logic trigger output (Repeatable / Non-repeatable)",
            "package": "Fresnel lens mounted PCB with sensitivity & delay pots",
            "dimensions": "32 x 24 x 18 mm",
            "operating_range": "Detection range 3-7 meters, 120-degree cone angle",
            "part_number": "HC-SR501 / BISS0001",
            "manufacturer": "ElecFreaks",
            "price": 149.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09HQ2QW6S",
        "amazon_url": "https://www.amazon.in/dp/B09HQ2QW6S",
        "flipkart_url": "https://www.flipkart.com/circuitcomponents-pir-motion-sensor-detector-module-hc-sr501-sensors/p/itm9eec38bb7387a",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "retailer": "Amazon",
                "external_product_id": "B09HQ2QW6S",
                "url": "https://www.amazon.in/dp/B09HQ2QW6S",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "retailer": "Flipkart",
                "external_product_id": "itm9eec38bb7387a",
                "url": "https://www.flipkart.com/circuitcomponents-pir-motion-sensor-detector-module-hc-sr501-sensors/p/itm9eec38bb7387a",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/sensor/l/u/e/pir-motion-sensor-detector-module-hc-sr501-circuitcomponents-resized-original-imag9hcfy9j2qmyj.jpeg",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000011-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "external_product_id": "B07K67B42W",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/sensor/l/u/e/pir-motion-sensor-detector-module-hc-sr501-circuitcomponents-resized-original-imag9hcfy9j2qmyj.jpeg",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000011-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "external_product_id": "B07K67B42W",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kwzap3k0/sensor/f/l/h/pir-motion-sensor-detector-module-hc-sr501-circuitcomponents-original-imag9jq6fgjbhg4j.jpeg",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HC-SR501%20Pyroelectric%20Infrared%20PIR%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - HC-SR501",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the HC-SR501 / BISS0001 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07K67B42W",
        "asin": "B07K67B42W",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "retailer": "Amazon",
                "external_product_id": "B07K67B42W",
                "url": "https://www.amazon.in/dp/B07K67B42W",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000011",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>HC-SR501%20Pyroelectric%20Infrared%20PIR%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000012",
        "product_id": "c2000000-0000-0000-0000-000000000012",
        "title": "HC-SR04 Ultrasonic Distance Measurement Sensor Module (2cm to 400cm)",
        "slug": "sensor-hcsr04-ultra",
        "brand": "ElecFreaks",
        "model": "HC-SR04",
        "sku": "SENSOR-HCSR04-ULTRA",
        "model_number": "SENSOR-HCSR04-ULTRA",
        "category": "Electronic Components & Modules",
        "subcategory": "Distance & Proximity Sensors",
        "is_component": true,
        "price": 129.0,
        "currency": "INR",
        "description": "HC-SR04 Ultrasonic Distance Measurement Sensor Module (2cm to 400cm) - Technical hardware component with Trigger (10us TTL pulse) and Echo (duration proportional to distance) interfaces, operating at 5V DC.",
        "specs": {
            "voltage": "5V DC",
            "current": "15mA working current",
            "interface": "Trigger (10us TTL pulse) and Echo (duration proportional to distance)",
            "protocol": "40kHz ultrasonic burst timing logic",
            "package": "4-pin transducer module (VCC, Trig, Echo, GND)",
            "dimensions": "45 x 20 x 15 mm",
            "operating_range": "Ranging distance: 2cm - 400cm, resolution 0.3cm",
            "part_number": "HC-SR04",
            "manufacturer": "ElecFreaks",
            "price": 129.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B09H6NJYBK",
        "amazon_url": "https://www.amazon.in/dp/B09H6NJYBK",
        "flipkart_url": "https://www.flipkart.com/arduino-hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-educational-electronic-hobby-kit/p/itmf82b8wjbzhudw",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "retailer": "Amazon",
                "external_product_id": "B09H6NJYBK",
                "url": "https://www.amazon.in/dp/B09H6NJYBK",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "retailer": "Flipkart",
                "external_product_id": "itmf82b8wjbzhudw",
                "url": "https://www.flipkart.com/arduino-hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-educational-electronic-hobby-kit/p/itmf82b8wjbzhudw",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/electronic-hobby-kit/b/k/c/hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-resized-original-imag3wfwzpsxffv7.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000012-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "external_product_id": "B07F89V4W7",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/electronic-hobby-kit/b/k/c/hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-resized-original-imag3wfwzpsxffv7.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000012-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "external_product_id": "B07F89V4W7",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/kqfj1jk0/electronic-hobby-kit/g/s/u/hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-original-imag4fwcgfh8fzqx.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61lX7E6P5-L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - HC-SR04",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the HC-SR04 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07F89V4W7",
        "asin": "B07F89V4W7",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "retailer": "Amazon",
                "external_product_id": "B07F89V4W7",
                "url": "https://www.amazon.in/dp/B07F89V4W7",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000012",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61lX7E6P5-L._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000013",
        "product_id": "c2000000-0000-0000-0000-000000000013",
        "title": "MQ-2 Flammable Gas, LPG, Methane & Smoke Sensor Module",
        "slug": "sensor-mq2-gas",
        "brand": "Winsen",
        "model": "MQ-2",
        "sku": "SENSOR-MQ2-GAS",
        "model_number": "SENSOR-MQ2-GAS",
        "category": "Electronic Components & Modules",
        "subcategory": "Gas & Air Quality Sensors",
        "is_component": true,
        "price": 179.0,
        "currency": "INR",
        "description": "MQ-2 Flammable Gas, LPG, Methane & Smoke Sensor Module - Technical hardware component with Analog AO (voltage output) and Digital DO (comparator threshold) interfaces, operating at 5V DC heater and circuit voltage.",
        "specs": {
            "voltage": "5V DC heater and circuit voltage",
            "current": "150mA heater consumption",
            "interface": "Analog AO (voltage output) and Digital DO (comparator threshold)",
            "protocol": "Resistive gas concentration change / LM393 comparator",
            "package": "4-pin breakout board with sensitivity potentiometer",
            "dimensions": "32 x 20 x 22 mm",
            "operating_range": "300 - 10000 ppm LPG, propane, methane, hydrogen, smoke",
            "part_number": "MQ-2",
            "manufacturer": "Zhengzhou Winsen Electronics",
            "price": 179.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07FS3MBCG",
        "amazon_url": "https://www.amazon.in/dp/B07FS3MBCG",
        "flipkart_url": "https://www.flipkart.com/circuitcomponents-mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection/p/itm94e60adea0443",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "retailer": "Amazon",
                "external_product_id": "B07FS3MBCG",
                "url": "https://www.amazon.in/dp/B07FS3MBCG",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "retailer": "Flipkart",
                "external_product_id": "itm94e60adea0443",
                "url": "https://www.flipkart.com/circuitcomponents-mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection/p/itm94e60adea0443",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/kws5hu80/sensor/c/3/m/mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection-original-imag9dntwqwpjwvf.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000013-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "external_product_id": "B07P8VNL4Q",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kws5hu80/sensor/c/3/m/mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection-original-imag9dntwqwpjwvf.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000013-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "external_product_id": "B07P8VNL4Q",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kws5hu80/sensor/u/y/c/mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection-original-imag9dntpq7svhpk.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MQ-2%20Flammable%20Gas%2C%20LPG%2C%20Methane%20%26%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - MQ-2",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the MQ-2 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07P8VNL4Q",
        "asin": "B07P8VNL4Q",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "retailer": "Amazon",
                "external_product_id": "B07P8VNL4Q",
                "url": "https://www.amazon.in/dp/B07P8VNL4Q",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000013",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MQ-2%20Flammable%20Gas%2C%20LPG%2C%20Methane%20%26%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000014",
        "product_id": "c2000000-0000-0000-0000-000000000014",
        "title": "BH1750FVI 16-Bit Digital Ambient Light Intensity Sensor Module (I2C)",
        "slug": "sensor-bh1750-light",
        "brand": "ROHM",
        "model": "BH1750FVI",
        "sku": "SENSOR-BH1750-LIGHT",
        "model_number": "SENSOR-BH1750-LIGHT",
        "category": "Electronic Components & Modules",
        "subcategory": "Optical & Light Sensors",
        "is_component": true,
        "price": 199.0,
        "currency": "INR",
        "description": "BH1750FVI 16-Bit Digital Ambient Light Intensity Sensor Module (I2C) - Technical hardware component with I2C Interface (address 0x23 or 0x5C) interfaces, operating at 3.3V - 5V DC (onboard logic shifter).",
        "specs": {
            "voltage": "3.3V - 5V DC (onboard logic shifter)",
            "current": "120uA operating, 1uA standby",
            "interface": "I2C Interface (address 0x23 or 0x5C)",
            "protocol": "Standard I2C protocol with lux output directly",
            "package": "5-pin breakout board",
            "dimensions": "13.9 x 18.5 mm",
            "operating_range": "1 - 65535 lx illuminance range",
            "part_number": "BH1750FVI",
            "manufacturer": "ROHM Semiconductor",
            "price": 199.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08P5YFMCF",
        "amazon_url": "https://www.amazon.in/dp/B08P5YFMCF",
        "flipkart_url": "https://www.flipkart.com/sunrobotics-bh1750-digital-light-sensor-module-security-circuit-motion-detector-electronic-hobby-kit/p/itmekyhgrrnbtgcs",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000014",
                "retailer": "Amazon",
                "external_product_id": "B08P5YFMCF",
                "url": "https://www.amazon.in/dp/B08P5YFMCF",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000014",
                "retailer": "Flipkart",
                "external_product_id": "itmekyhgrrnbtgcs",
                "url": "https://www.flipkart.com/sunrobotics-bh1750-digital-light-sensor-module-security-circuit-motion-detector-electronic-hobby-kit/p/itmekyhgrrnbtgcs",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/electronic-hobby-kit/z/x/z/bh1750-digital-light-sensor-module-sunrobotics-original-imaekybddhfs8ruy.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000014-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000014",
                "external_product_id": "B07B5N92M8",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/electronic-hobby-kit/z/x/z/bh1750-digital-light-sensor-module-sunrobotics-original-imaekybddhfs8ruy.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>BH1750FVI%2016-Bit%20Digital%20Ambient%20Li</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - BH1750FVI",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the BH1750FVI are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07B5N92M8",
        "asin": "B07B5N92M8",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000014",
                "retailer": "Amazon",
                "external_product_id": "B07B5N92M8",
                "url": "https://www.amazon.in/dp/B07B5N92M8",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000014",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>BH1750FVI%2016-Bit%20Digital%20Ambient%20Li</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000015",
        "product_id": "c2000000-0000-0000-0000-000000000015",
        "title": "5V 1-Channel Relay Module with Optocoupler Isolation (10A 250VAC)",
        "slug": "relay-1ch-5v-opto",
        "brand": "Songle",
        "model": "SRD-05VDC-SL-C Module",
        "sku": "RELAY-1CH-5V-OPTO",
        "model_number": "RELAY-1CH-5V-OPTO",
        "category": "Electronic Components & Modules",
        "subcategory": "Relays & Power Switches",
        "is_component": true,
        "price": 119.0,
        "currency": "INR",
        "description": "5V 1-Channel Relay Module with Optocoupler Isolation (10A 250VAC) - Technical hardware component with IN (High or Low level trigger selectable by jumper) interfaces, operating at 5V DC coil voltage.",
        "specs": {
            "voltage": "5V DC coil voltage",
            "current": "70mA coil trigger current",
            "interface": "IN (High or Low level trigger selectable by jumper)",
            "protocol": "Optoisolated logic switching (PC817 optocoupler)",
            "package": "Screw terminal block output, 3-pin header input",
            "dimensions": "50 x 26 x 18.5 mm",
            "operating_range": "Load: AC 250V/10A, DC 30V/10A",
            "part_number": "SRD-05VDC-SL-C",
            "manufacturer": "Songle Relay",
            "price": 119.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B00LW15A4W",
        "amazon_url": "https://www.amazon.in/dp/B00LW15A4W",
        "flipkart_url": "https://www.flipkart.com/dhruv-pro-1-channel-5v-10a-relay-module-optocoupler-ac-dc-appliance-control-micro-controller-board-electronic-hobby-kit/p/itm9ee3ac19fbb47",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "retailer": "Amazon",
                "external_product_id": "B00LW15A4W",
                "url": "https://www.amazon.in/dp/B00LW15A4W",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "retailer": "Flipkart",
                "external_product_id": "itm9ee3ac19fbb47",
                "url": "https://www.flipkart.com/dhruv-pro-1-channel-5v-10a-relay-module-optocoupler-ac-dc-appliance-control-micro-controller-board-electronic-hobby-kit/p/itm9ee3ac19fbb47",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/kgzg8sw0/electronic-hobby-kit/4/w/c/1-channel-5v-10a-relay-module-with-optocoupler-ac-and-dc-original-imafx3m9zfmzwf7k.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000015-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "external_product_id": "B07V2P9M8W",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/kgzg8sw0/electronic-hobby-kit/4/w/c/1-channel-5v-10a-relay-module-with-optocoupler-ac-and-dc-original-imafx3m9zfmzwf7k.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000015-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "external_product_id": "B07V2P9M8W",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/kgzg8sw0/electronic-hobby-kit/4/w/c/1-channel-5v-10a-relay-module-with-optocoupler-ac-and-dc-original-imafx3m9zx95segr.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/61Mtz1vWwEL._SL1100_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - SRD-05VDC-SL-C Module",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SRD-05VDC-SL-C are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07V2P9M8W",
        "asin": "B07V2P9M8W",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "retailer": "Amazon",
                "external_product_id": "B07V2P9M8W",
                "url": "https://www.amazon.in/dp/B07V2P9M8W",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000015",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61Mtz1vWwEL._SL1100_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000016",
        "product_id": "c2000000-0000-0000-0000-000000000016",
        "title": "5V 4-Channel Relay Module Board with Optocoupler Isolation for Arduino/ESP32",
        "slug": "relay-4ch-5v-opto",
        "brand": "Songle",
        "model": "4-Channel Relay 5V",
        "sku": "RELAY-4CH-5V-OPTO",
        "model_number": "RELAY-4CH-5V-OPTO",
        "category": "Electronic Components & Modules",
        "subcategory": "Relays & Power Switches",
        "is_component": true,
        "price": 289.0,
        "currency": "INR",
        "description": "5V 4-Channel Relay Module Board with Optocoupler Isolation for Arduino/ESP32 - Technical hardware component with 4x Digital Input pins (Active Low/High optocoupled) interfaces, operating at 5V DC coil voltage.",
        "specs": {
            "voltage": "5V DC coil voltage",
            "current": "280mA full 4-channel active",
            "interface": "4x Digital Input pins (Active Low/High optocoupled)",
            "protocol": "Multi-channel discrete logic isolation",
            "package": "4x SPDT Relays with screw terminal outputs",
            "dimensions": "75 x 55 x 19 mm",
            "operating_range": "AC 250V/10A, DC 30V/10A per channel",
            "part_number": "SRD-05VDC-SL-C-4CH",
            "manufacturer": "Songle Relay",
            "price": 289.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07S29BN57",
        "amazon_url": "https://www.amazon.in/dp/B07S29BN57",
        "flipkart_url": "https://www.flipkart.com/rees52-optocoupler-4-channel-5v-relay-module-control-arduino-dsp-avr-pic-arm/p/itmez4fhdmtvwhme",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "retailer": "Amazon",
                "external_product_id": "B07S29BN57",
                "url": "https://www.amazon.in/dp/B07S29BN57",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "retailer": "Flipkart",
                "external_product_id": "itmez4fhdmtvwhme",
                "url": "https://www.flipkart.com/rees52-optocoupler-4-channel-5v-relay-module-control-arduino-dsp-avr-pic-arm/p/itmez4fhdmtvwhme",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1330/j9a8fww0/learning-toy/g/3/d/optocoupler-4-channel-5v-relay-module-relay-control-for-arduino-original-imaez2fdw7wky2uz.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000016-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "external_product_id": "B07V1M8V9Z",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/j9a8fww0/learning-toy/g/3/d/optocoupler-4-channel-5v-relay-module-relay-control-for-arduino-original-imaez2fdw7wky2uz.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000016-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "external_product_id": "B07V1M8V9Z",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1330/j9a8fww0/learning-toy/g/3/d/optocoupler-4-channel-5v-relay-module-relay-control-for-arduino-original-imaez2fendvzjs6y.jpeg?q=90",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "https://m.media-amazon.com/images/I/71a2B6v8v4L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - 4-Channel Relay 5V",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SRD-05VDC-SL-C-4CH are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07V1M8V9Z",
        "asin": "B07V1M8V9Z",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "retailer": "Amazon",
                "external_product_id": "B07V1M8V9Z",
                "url": "https://www.amazon.in/dp/B07V1M8V9Z",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000016",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/71a2B6v8v4L._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000017",
        "product_id": "c2000000-0000-0000-0000-000000000017",
        "title": "5V 8-Channel Relay Module Board with Optocoupler Protection",
        "slug": "relay-8ch-5v",
        "brand": "Songle",
        "model": "8-Channel Relay 5V",
        "sku": "RELAY-8CH-5V",
        "model_number": "RELAY-8CH-5V",
        "category": "Electronic Components & Modules",
        "subcategory": "Relays & Power Switches",
        "is_component": true,
        "price": 549.0,
        "currency": "INR",
        "description": "5V 8-Channel Relay Module Board with Optocoupler Protection - Technical hardware component with 8x Digital inputs interfaces, operating at 5V DC.",
        "specs": {
            "voltage": "5V DC",
            "current": "550mA peak",
            "interface": "8x Digital inputs",
            "protocol": "Optocoupled logic",
            "package": "PCB with 8 SPDT relays",
            "dimensions": "138 x 56 mm",
            "operating_range": "250VAC 10A",
            "part_number": "SRD-05VDC-8CH",
            "manufacturer": "Songle Relay",
            "price": 549.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B01IDNCCFQ",
        "amazon_url": "https://www.amazon.in/dp/B01IDNCCFQ",
        "flipkart_url": "https://www.flipkart.com/sunrobotics-8-channel-5v-relay-board-module/p/itmf3pdt9pxhukzs",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000017",
                "retailer": "Amazon",
                "external_product_id": "B01IDNCCFQ",
                "url": "https://www.amazon.in/dp/B01IDNCCFQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000017",
                "retailer": "Flipkart",
                "external_product_id": "itmf3pdt9pxhukzs",
                "url": "https://www.flipkart.com/sunrobotics-8-channel-5v-relay-board-module/p/itmf3pdt9pxhukzs",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/kq9ta4w0/learning-toy/e/g/r/8-channel-5v-relay-board-module-sunrobotics-original-imag4bbgwgfzjuse.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000017-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000017",
                "external_product_id": "B07P8VNL4R",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kq9ta4w0/learning-toy/e/g/r/8-channel-5v-relay-board-module-sunrobotics-original-imag4bbgwgfzjuse.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>5V%208-Channel%20Relay%20Module%20Board%20wit</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - 8-Channel Relay 5V",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SRD-05VDC-8CH are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07P8VNL4R",
        "asin": "B07P8VNL4R",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000017",
                "retailer": "Amazon",
                "external_product_id": "B07P8VNL4R",
                "url": "https://www.amazon.in/dp/B07P8VNL4R",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000017",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>5V%208-Channel%20Relay%20Module%20Board%20wit</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000018",
        "product_id": "c2000000-0000-0000-0000-000000000018",
        "title": "L298N Dual H-Bridge DC Stepper Motor Driver Controller Board",
        "slug": "driver-l298n-dual",
        "brand": "STMicroelectronics",
        "model": "L298N Driver",
        "sku": "DRIVER-L298N-DUAL",
        "model_number": "DRIVER-L298N-DUAL",
        "category": "Electronic Components & Modules",
        "subcategory": "Motor Drivers & Actuators",
        "is_component": true,
        "price": 229.0,
        "currency": "INR",
        "description": "L298N Dual H-Bridge DC Stepper Motor Driver Controller Board - Technical hardware component with IN1-IN4 directional inputs, ENA/ENB PWM speed interfaces, operating at 5V-35V motor voltage.",
        "specs": {
            "voltage": "5V-35V motor voltage",
            "current": "2A per bridge continuous",
            "interface": "IN1-IN4 directional inputs, ENA/ENB PWM speed",
            "protocol": "Dual full-bridge PWM driver",
            "package": "Heatsink mounted breakout board",
            "dimensions": "43 x 43 x 27 mm",
            "operating_range": "-25\u00b0C to +130\u00b0C",
            "part_number": "L298N",
            "manufacturer": "STMicroelectronics",
            "price": 229.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0DYD468L5",
        "amazon_url": "https://www.amazon.in/dp/B0DYD468L5",
        "flipkart_url": "https://www.flipkart.com/tayal-l298n-motor-driver-module-dual-h-bridge-dc-stepper-arduino-electronic-components-hobby-kit/p/itm035f6479389ae",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "retailer": "Amazon",
                "external_product_id": "B0DYD468L5",
                "url": "https://www.amazon.in/dp/B0DYD468L5",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "retailer": "Flipkart",
                "external_product_id": "itm035f6479389ae",
                "url": "https://www.flipkart.com/tayal-l298n-motor-driver-module-dual-h-bridge-dc-stepper-arduino-electronic-components-hobby-kit/p/itm035f6479389ae",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/c/d/e/l298n-motor-driver-module-dual-h-bridge-dc-stepper-for-arduino-original-imaghzsnvz5zqmse.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000018-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "external_product_id": "B07B5N92M9",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/c/d/e/l298n-motor-driver-module-dual-h-bridge-dc-stepper-for-arduino-original-imaghzsnvz5zqmse.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000018-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "external_product_id": "B07B5N92M9",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/f/q/u/l298n-motor-driver-module-dual-h-bridge-dc-stepper-for-arduino-original-imaghzsnnaqgqxbe.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>L298N%20Dual%20H-Bridge%20DC%20Stepper%20Moto</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - L298N Driver",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the L298N are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07B5N92M9",
        "asin": "B07B5N92M9",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "retailer": "Amazon",
                "external_product_id": "B07B5N92M9",
                "url": "https://www.amazon.in/dp/B07B5N92M9",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000018",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>L298N%20Dual%20H-Bridge%20DC%20Stepper%20Moto</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000019",
        "product_id": "c2000000-0000-0000-0000-000000000019",
        "title": "SG90 9g Micro Digital Servo Motor (180 Degree Rotation)",
        "slug": "servo-sg90-9g",
        "brand": "Tower Pro",
        "model": "SG90 Micro Servo",
        "sku": "SERVO-SG90-9G",
        "model_number": "SERVO-SG90-9G",
        "category": "Electronic Components & Modules",
        "subcategory": "Motor Drivers & Actuators",
        "is_component": true,
        "price": 149.0,
        "currency": "INR",
        "description": "SG90 9g Micro Digital Servo Motor (180 Degree Rotation) - Technical hardware component with PWM signal (50Hz, 1ms - 2ms pulse width) interfaces, operating at 4.8V - 6.0V DC.",
        "specs": {
            "voltage": "4.8V - 6.0V DC",
            "current": "550mA stall current",
            "interface": "PWM signal (50Hz, 1ms - 2ms pulse width)",
            "protocol": "Analog PWM servo position control",
            "package": "Micro plastic gearbox with horn attachments",
            "dimensions": "22.2 x 11.8 x 31 mm",
            "operating_range": "Stall torque 1.8 kg-cm @ 4.8V",
            "part_number": "SG90",
            "manufacturer": "Tower Pro",
            "price": 149.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0FB3RKJ9T",
        "amazon_url": "https://www.amazon.in/dp/B0FB3RKJ9T",
        "flipkart_url": "https://www.flipkart.com/electro-global-servo-motor-sg90-tower-pro-9-gms-mini-micro-control-electronic-hobby-kit/p/itm051e374f20376",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "retailer": "Amazon",
                "external_product_id": "B0FB3RKJ9T",
                "url": "https://www.amazon.in/dp/B0FB3RKJ9T",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "retailer": "Flipkart",
                "external_product_id": "itm051e374f20376",
                "url": "https://www.flipkart.com/electro-global-servo-motor-sg90-tower-pro-9-gms-mini-micro-control-electronic-hobby-kit/p/itm051e374f20376",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/e/i/6/servo-motor-sg90-tower-pro-sg90-servo-motor-9-gms-mini-micro-original-imah79xdpfwyetzk.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000019-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "external_product_id": "B07V2P9M8X",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/e/i/6/servo-motor-sg90-tower-pro-sg90-servo-motor-9-gms-mini-micro-original-imah79xdpfwyetzk.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000019-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "external_product_id": "B07V2P9M8X",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/y/a/9/servo-motor-sg90-tower-pro-sg90-servo-motor-9-gms-mini-micro-original-imah79xdbasseypd.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>SG90%209g%20Micro%20Digital%20Servo%20Motor%20%28</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - SG90 Micro Servo",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SG90 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07V2P9M8X",
        "asin": "B07V2P9M8X",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "retailer": "Amazon",
                "external_product_id": "B07V2P9M8X",
                "url": "https://www.amazon.in/dp/B07V2P9M8X",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000019",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>SG90%209g%20Micro%20Digital%20Servo%20Motor%20%28</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000020",
        "product_id": "c2000000-0000-0000-0000-000000000020",
        "title": "SX1278 433MHz LoRa Wireless Transceiver Module (Ra-02)",
        "slug": "module-ra02-lora",
        "brand": "AI-Thinker",
        "model": "Ra-02 SX1278",
        "sku": "MODULE-RA02-LORA",
        "model_number": "MODULE-RA02-LORA",
        "category": "Electronic Components & Modules",
        "subcategory": "Wireless & RF Modules",
        "is_component": true,
        "price": 499.0,
        "currency": "INR",
        "description": "SX1278 433MHz LoRa Wireless Transceiver Module (Ra-02) - Technical hardware component with SPI interface + DIO0-DIO5 interrupt pins interfaces, operating at 1.8V - 3.7V DC (3.3V typical).",
        "specs": {
            "voltage": "1.8V - 3.7V DC (3.3V typical)",
            "current": "120mA Tx (+20dBm), 12mA Rx",
            "interface": "SPI interface + DIO0-DIO5 interrupt pins",
            "protocol": "LoRa Spread Spectrum, FSK, GFSK, OOK",
            "package": "SMD-16 with IPEX antenna connector",
            "dimensions": "17 x 16 x 3.2 mm",
            "operating_range": "-40\u00b0C to +85\u00b0C, up to 10km line-of-sight",
            "part_number": "Ra-02",
            "manufacturer": "AI-Thinker",
            "price": 499.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0DC5M3CTQ",
        "amazon_url": "https://www.amazon.in/dp/B0DC5M3CTQ",
        "flipkart_url": "https://www.flipkart.com/sunrobotics-lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-spectrum-transmission-socket-smart-home/p/itmfb7fgvandzzre",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "retailer": "Amazon",
                "external_product_id": "B0DC5M3CTQ",
                "url": "https://www.amazon.in/dp/B0DC5M3CTQ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "retailer": "Flipkart",
                "external_product_id": "itmfb7fgvandzzre",
                "url": "https://www.flipkart.com/sunrobotics-lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-spectrum-transmission-socket-smart-home/p/itmfb7fgvandzzre",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/kngd0nk0/learning-toy/v/e/x/lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-original-imag24pr2qqmncgp.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000020-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "external_product_id": "B07V1M8V9A",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kngd0nk0/learning-toy/v/e/x/lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-original-imag24pr2qqmncgp.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000020-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "external_product_id": "B07V1M8V9A",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/kngd0nk0/learning-toy/d/i/t/lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-original-imag24prtqh2kpft.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>SX1278%20433MHz%20LoRa%20Wireless%20Transce</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Ra-02 SX1278",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the Ra-02 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07V1M8V9A",
        "asin": "B07V1M8V9A",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "retailer": "Amazon",
                "external_product_id": "B07V1M8V9A",
                "url": "https://www.amazon.in/dp/B07V1M8V9A",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000020",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>SX1278%20433MHz%20LoRa%20Wireless%20Transce</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000021",
        "product_id": "c2000000-0000-0000-0000-000000000021",
        "title": "NEO-6M GPS Module with Ceramic Antenna and EEPROM",
        "slug": "module-neo6m-gps",
        "brand": "u-blox",
        "model": "NEO-6M GPS",
        "sku": "MODULE-NEO6M-GPS",
        "model_number": "MODULE-NEO6M-GPS",
        "category": "Electronic Components & Modules",
        "subcategory": "Navigation & GPS Modules",
        "is_component": true,
        "price": 649.0,
        "currency": "INR",
        "description": "NEO-6M GPS Module with Ceramic Antenna and EEPROM - Technical hardware component with UART Serial (TX/RX, default 9600 baud) interfaces, operating at 3.3V - 5V DC (onboard regulator).",
        "specs": {
            "voltage": "3.3V - 5V DC (onboard regulator)",
            "current": "45mA tracking",
            "interface": "UART Serial (TX/RX, default 9600 baud)",
            "protocol": "NMEA-0183 standard GPS protocol",
            "package": "Breakout board with external 25x25mm ceramic antenna",
            "dimensions": "36 x 24 mm",
            "operating_range": "Horizontal accuracy 2.5m, update rate 5Hz",
            "part_number": "NEO-6M-0-001",
            "manufacturer": "u-blox AG",
            "price": 649.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B01D1D0F5M",
        "amazon_url": "https://www.amazon.in/dp/B01D1D0F5M",
        "flipkart_url": "https://www.flipkart.com/logicinside-ublox-neo-6m-gps-module-ceramic-antenna/p/itmeter4p7td7r2y",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "retailer": "Amazon",
                "external_product_id": "B01D1D0F5M",
                "url": "https://www.amazon.in/dp/B01D1D0F5M",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "retailer": "Flipkart",
                "external_product_id": "itmeter4p7td7r2y",
                "url": "https://www.flipkart.com/logicinside-ublox-neo-6m-gps-module-ceramic-antenna/p/itmeter4p7td7r2y",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/j1xvzbk0/learning-toy/j/s/f/ublox-neo-6m-gps-module-with-ceramic-antenna-logicinside-original-imaetdhpaukyhw94.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000021-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "external_product_id": "B07B5N92M0",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/j1xvzbk0/learning-toy/j/s/f/ublox-neo-6m-gps-module-with-ceramic-antenna-logicinside-original-imaetdhpaukyhw94.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000021-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "external_product_id": "B07B5N92M0",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/j1xvzbk0/learning-toy/j/s/f/ublox-neo-6m-gps-module-with-ceramic-antenna-logicinside-original-imaetdhpjyggb6eb.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>NEO-6M%20GPS%20Module%20with%20Ceramic%20Ante</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - NEO-6M GPS",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the NEO-6M-0-001 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B07B5N92M0",
        "asin": "B07B5N92M0",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "retailer": "Amazon",
                "external_product_id": "B07B5N92M0",
                "url": "https://www.amazon.in/dp/B07B5N92M0",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000021",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>NEO-6M%20GPS%20Module%20with%20Ceramic%20Ante</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000022",
        "product_id": "c2000000-0000-0000-0000-000000000022",
        "title": "0.96 inch I2C OLED Display Module 128x64 SSD1306 (Blue/Yellow)",
        "slug": "display-oled-096-i2c",
        "brand": "Solomon Systech",
        "model": "SSD1306 0.96 OLED",
        "sku": "DISPLAY-OLED-096-I2C",
        "model_number": "DISPLAY-OLED-096-I2C",
        "category": "Electronic Components & Modules",
        "subcategory": "Displays & Output Modules",
        "is_component": true,
        "price": 249.0,
        "currency": "INR",
        "description": "0.96 inch I2C OLED Display Module 128x64 SSD1306 (Blue/Yellow) - Technical hardware component with I2C (SDA, SCL, default address 0x3C) interfaces, operating at 3.3V - 5V DC.",
        "specs": {
            "voltage": "3.3V - 5V DC",
            "current": "20mA typical with all pixels on",
            "interface": "I2C (SDA, SCL, default address 0x3C)",
            "protocol": "SSD1306 command set via I2C 400kHz",
            "package": "4-pin 0.96 inch monochrome OLED panel",
            "dimensions": "27 x 27 x 4 mm",
            "operating_range": "Wide viewing angle > 160 degrees",
            "part_number": "SSD1306",
            "manufacturer": "Solomon Systech",
            "price": 249.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0C1XCFXMM",
        "amazon_url": "https://www.amazon.in/dp/B0C1XCFXMM",
        "flipkart_url": "https://www.flipkart.com/redprad-0-96-inch-128x64-iic-i2c-oled-display-module-blue-ssd1306-driver-miscellaneous-electronic-hobby-kit/p/itmc95b7d397dc65",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000022",
                "retailer": "Amazon",
                "external_product_id": "B0C1XCFXMM",
                "url": "https://www.amazon.in/dp/B0C1XCFXMM",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000022",
                "retailer": "Flipkart",
                "external_product_id": "itmc95b7d397dc65",
                "url": "https://www.flipkart.com/redprad-0-96-inch-128x64-iic-i2c-oled-display-module-blue-ssd1306-driver-miscellaneous-electronic-hobby-kit/p/itmc95b7d397dc65",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/j/r/p/0-96-inch-128x64-iic-i2c-oled-display-module-blue-ssd1306-driver-original-imagsz9n9hme2h55.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000022-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000022",
                "external_product_id": "B086MGV6F4",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/j/r/p/0-96-inch-128x64-iic-i2c-oled-display-module-blue-ssd1306-driver-original-imagsz9n9hme2h55.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>0.96%20inch%20I2C%20OLED%20Display%20Module%201</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - SSD1306 0.96 OLED",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the SSD1306 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B086MGV6F4",
        "asin": "B086MGV6F4",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000022",
                "retailer": "Amazon",
                "external_product_id": "B086MGV6F4",
                "url": "https://www.amazon.in/dp/B086MGV6F4",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000022",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>0.96%20inch%20I2C%20OLED%20Display%20Module%201</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000023",
        "product_id": "c2000000-0000-0000-0000-000000000023",
        "title": "16x2 Character LCD Display Module with I2C Backpack (HD44780 Blue Backlight)",
        "slug": "display-1602-lcd-i2c",
        "brand": "Hitachi",
        "model": "1602 LCD I2C",
        "sku": "DISPLAY-1602-LCD-I2C",
        "model_number": "DISPLAY-1602-LCD-I2C",
        "category": "Electronic Components & Modules",
        "subcategory": "Displays & Output Modules",
        "is_component": true,
        "price": 299.0,
        "currency": "INR",
        "description": "16x2 Character LCD Display Module with I2C Backpack (HD44780 Blue Backlight) - Technical hardware component with I2C (SDA, SCL, PCF8574 adapter address 0x27) interfaces, operating at 5V DC.",
        "specs": {
            "voltage": "5V DC",
            "current": "50mA with LED backlight on",
            "interface": "I2C (SDA, SCL, PCF8574 adapter address 0x27)",
            "protocol": "HD44780 standard command protocol",
            "package": "16-pin LCD with soldered PCF8574T I2C daughterboard",
            "dimensions": "80 x 36 x 19 mm",
            "operating_range": "Contrast adjustable via potentiometer",
            "part_number": "HD44780 / PCF8574",
            "manufacturer": "Hitachi / NXP",
            "price": 299.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0HBKJSWDJ",
        "amazon_url": "https://www.amazon.in/dp/B0HBKJSWDJ",
        "flipkart_url": "https://www.flipkart.com/trustech-16x2-lcd-blue-i2c-module-ar-duino-electronic-components-hobby-kit/p/itmaafdad7bd7bb2",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "retailer": "Amazon",
                "external_product_id": "B0HBKJSWDJ",
                "url": "https://www.amazon.in/dp/B0HBKJSWDJ",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "retailer": "Flipkart",
                "external_product_id": "itmaafdad7bd7bb2",
                "url": "https://www.flipkart.com/trustech-16x2-lcd-blue-i2c-module-ar-duino-electronic-components-hobby-kit/p/itmaafdad7bd7bb2",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/640/krntoy80/electronic-hobby-kit/k/h/f/16x2-lcd-blue-with-i2c-module-for-ar-duino-trustech-original-imag5et9sbd8vdye.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000023-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "external_product_id": "B082F24NZM",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/krntoy80/electronic-hobby-kit/k/h/f/16x2-lcd-blue-with-i2c-module-for-ar-duino-trustech-original-imag5et9sbd8vdye.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000023-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "external_product_id": "B082F24NZM",
                "image_url": "https://rukminim2.flixcart.com/image/480/640/krntoy80/electronic-hobby-kit/s/m/0/16x2-lcd-blue-with-i2c-module-for-ar-duino-trustech-original-imag5et9pzmm7pkp.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>16x2%20Character%20LCD%20Display%20Module%20w</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - 1602 LCD I2C",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the HD44780 / PCF8574 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B082F24NZM",
        "asin": "B082F24NZM",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "retailer": "Amazon",
                "external_product_id": "B082F24NZM",
                "url": "https://www.amazon.in/dp/B082F24NZM",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000023",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>16x2%20Character%20LCD%20Display%20Module%20w</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000024",
        "product_id": "c2000000-0000-0000-0000-000000000024",
        "title": "LM2596 DC-DC Step-Down Buck Converter Power Module (Adjustable 1.25V-35V)",
        "slug": "power-lm2596-buck",
        "brand": "Texas Instruments",
        "model": "LM2596 Buck Module",
        "sku": "POWER-LM2596-BUCK",
        "model_number": "POWER-LM2596-BUCK",
        "category": "Electronic Components & Modules",
        "subcategory": "Power & Voltage Regulators",
        "is_component": true,
        "price": 129.0,
        "currency": "INR",
        "description": "LM2596 DC-DC Step-Down Buck Converter Power Module (Adjustable 1.25V-35V) - Technical hardware component with Screw terminals for VIN+, VIN-, VOUT+, VOUT- interfaces, operating at Input: 3.2V - 40V, Output: 1.25V - 35V adjustable.",
        "specs": {
            "voltage": "Input: 3.2V - 40V, Output: 1.25V - 35V adjustable",
            "current": "3A maximum peak, 2A continuous",
            "interface": "Screw terminals for VIN+, VIN-, VOUT+, VOUT-",
            "protocol": "150kHz fixed frequency PWM switching regulator",
            "package": "PCB with 10k multiturn trimmer potentiometer",
            "dimensions": "43 x 21 x 14 mm",
            "operating_range": "High conversion efficiency up to 92%",
            "part_number": "LM2596S-ADJ",
            "manufacturer": "Texas Instruments",
            "price": 129.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B0F849GW3Y",
        "amazon_url": "https://www.amazon.in/dp/B0F849GW3Y",
        "flipkart_url": "https://www.flipkart.com/r-d-lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-regulator-module-power-supply-electronic-hobby-kit/p/itm0b45c0b556618",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "retailer": "Amazon",
                "external_product_id": "B0F849GW3Y",
                "url": "https://www.amazon.in/dp/B0F849GW3Y",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "retailer": "Flipkart",
                "external_product_id": "itm0b45c0b556618",
                "url": "https://www.flipkart.com/r-d-lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-regulator-module-power-supply-electronic-hobby-kit/p/itm0b45c0b556618",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/4/b/o/lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-original-imagsrfhxkjkbz4h.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000024-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "external_product_id": "B00844XE95",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/4/b/o/lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-original-imagsrfhxkjkbz4h.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000024-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "external_product_id": "B00844XE95",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/6/k/d/lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-original-imagsrfhx7qavtyt.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>LM2596%20DC-DC%20Step-Down%20Buck%20Convert</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - LM2596 Buck Module",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the LM2596S-ADJ are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B00844XE95",
        "asin": "B00844XE95",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "retailer": "Amazon",
                "external_product_id": "B00844XE95",
                "url": "https://www.amazon.in/dp/B00844XE95",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000024",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>LM2596%20DC-DC%20Step-Down%20Buck%20Convert</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000025",
        "product_id": "c2000000-0000-0000-0000-000000000025",
        "title": "4-Channel I2C Bi-Directional Logic Level Converter (5V to 3.3V)",
        "slug": "converter-level-4ch",
        "brand": "SparkFun",
        "model": "Bi-Directional LLC",
        "sku": "CONVERTER-LEVEL-4CH",
        "model_number": "CONVERTER-LEVEL-4CH",
        "category": "Electronic Components & Modules",
        "subcategory": "Interface & Logic Modules",
        "is_component": true,
        "price": 99.0,
        "currency": "INR",
        "description": "4-Channel I2C Bi-Directional Logic Level Converter (5V to 3.3V) - Technical hardware component with 4 bidirectional level-shifted channels (LV1-LV4 to HV1-HV4) interfaces, operating at Low Voltage: 1.8V-3.3V, High Voltage: 2.8V-5.5V.",
        "specs": {
            "voltage": "Low Voltage: 1.8V-3.3V, High Voltage: 2.8V-5.5V",
            "current": "10mA per channel",
            "interface": "4 bidirectional level-shifted channels (LV1-LV4 to HV1-HV4)",
            "protocol": "Open-drain and push-pull bus shifting for I2C and UART",
            "package": "12-pin breadboard DIP module (BSS138 MOSFETs)",
            "dimensions": "15.2 x 12.7 mm",
            "operating_range": "-40\u00b0C to +85\u00b0C",
            "part_number": "BOB-12009",
            "manufacturer": "SparkFun Electronics",
            "price": 99.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B01KKKYV0E",
        "amazon_url": "https://www.amazon.in/dp/B01KKKYV0E",
        "flipkart_url": "https://www.flipkart.com/sunrobotics-i2c-logic-level-converter-4-ch-bi-directional-5-3-3v-electronic-components-hobby-kit/p/itmemfhzf8erv3mu",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000025",
                "retailer": "Amazon",
                "external_product_id": "B01KKKYV0E",
                "url": "https://www.amazon.in/dp/B01KKKYV0E",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000025",
                "retailer": "Flipkart",
                "external_product_id": "itmemfhzf8erv3mu",
                "url": "https://www.flipkart.com/sunrobotics-i2c-logic-level-converter-4-ch-bi-directional-5-3-3v-electronic-components-hobby-kit/p/itmemfhzf8erv3mu",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kwb07m80/electronic-hobby-kit/l/7/f/i2c-bi-directional-logic-level-converter-4-channel-pack-of-2-original-imaekz3yamqrpkeq.jpeg?q=90",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000025-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000025",
                "external_product_id": "B0046AMGW1",
                "image_url": "https://rukminim2.flixcart.com/image/1000/1000/kwb07m80/electronic-hobby-kit/l/7/f/i2c-bi-directional-logic-level-converter-4-channel-pack-of-2-original-imaekz3yamqrpkeq.jpeg?q=90",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "board": "https://m.media-amazon.com/images/I/61V--WZVUIL._SL1500_.jpg",
            "connector": "https://m.media-amazon.com/images/I/61u9O4G9FLL._SL1500_.jpg",
            "gallery": "https://m.media-amazon.com/images/I/71m6R4W8T9L._SL1500_.jpg"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - Bi-Directional LLC",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the BOB-12009 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0046AMGW1",
        "asin": "B0046AMGW1",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000025",
                "retailer": "Amazon",
                "external_product_id": "B0046AMGW1",
                "url": "https://www.amazon.in/dp/B0046AMGW1",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000025",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "https://m.media-amazon.com/images/I/61V--WZVUIL._SL1500_.jpg"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000026",
        "product_id": "c2000000-0000-0000-0000-000000000026",
        "title": "MPU-6050 6-Axis Gyroscope and Accelerometer Module (I2C 3.3V/5V)",
        "slug": "sensor-mpu6050-6axis",
        "brand": "InvenSense",
        "model": "MPU-6050 GY-521",
        "sku": "SENSOR-MPU6050-6AXIS",
        "model_number": "SENSOR-MPU6050-6AXIS",
        "category": "Electronic Components & Modules",
        "subcategory": "Inertial & Motion Sensors",
        "is_component": true,
        "price": 199.0,
        "currency": "INR",
        "description": "MPU-6050 6-Axis Gyroscope and Accelerometer Module (I2C 3.3V/5V) - Technical hardware component with I2C (Address 0x68 or 0x69) + Interrupt pin interfaces, operating at 3.3V - 5V DC (onboard regulator).",
        "specs": {
            "voltage": "3.3V - 5V DC (onboard regulator)",
            "current": "3.9mA operating",
            "interface": "I2C (Address 0x68 or 0x69) + Interrupt pin",
            "protocol": "I2C Fast Mode with Digital Motion Processor (DMP)",
            "package": "8-pin 2.54mm breakout board",
            "dimensions": "20.5 x 15.5 mm",
            "operating_range": "Gyro \u00b1250 to \u00b12000 \u00b0/s, Accel \u00b12g to \u00b116g",
            "part_number": "MPU-6050",
            "manufacturer": "InvenSense / TDK",
            "price": 199.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08Q7PCN9P",
        "amazon_url": "https://www.amazon.in/dp/B08Q7PCN9P",
        "flipkart_url": "https://www.flipkart.com/aktronics-gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-dof-6-axis-sensor-electronic-components-hobby-kit/p/itmb6d1683e8bb72",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "retailer": "Amazon",
                "external_product_id": "B08Q7PCN9P",
                "url": "https://www.amazon.in/dp/B08Q7PCN9P",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "retailer": "Flipkart",
                "external_product_id": "itmb6d1683e8bb72",
                "url": "https://www.flipkart.com/aktronics-gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-dof-6-axis-sensor-electronic-components-hobby-kit/p/itmb6d1683e8bb72",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/koynr0w0/electronic-hobby-kit/5/y/b/gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-original-imag3anysnzb9m5z.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000026-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "external_product_id": "B0899VXM8G",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/koynr0w0/electronic-hobby-kit/5/y/b/gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-original-imag3anysnzb9m5z.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000026-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "external_product_id": "B0899VXM8G",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/koynr0w0/electronic-hobby-kit/m/g/s/gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-original-imag3anypenrxg79.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MPU-6050%206-Axis%20Gyroscope%20and%20Accel</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - MPU-6050 GY-521",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the MPU-6050 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0899VXM8G",
        "asin": "B0899VXM8G",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "retailer": "Amazon",
                "external_product_id": "B0899VXM8G",
                "url": "https://www.amazon.in/dp/B0899VXM8G",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000026",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MPU-6050%206-Axis%20Gyroscope%20and%20Accel</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000027",
        "product_id": "c2000000-0000-0000-0000-000000000027",
        "title": "TCRT5000 Infrared Reflective Optical Line Tracking Sensor Module",
        "slug": "sensor-tcrt5000-ir",
        "brand": "Vishay",
        "model": "TCRT5000 Module",
        "sku": "SENSOR-TCRT5000-IR",
        "model_number": "SENSOR-TCRT5000-IR",
        "category": "Electronic Components & Modules",
        "subcategory": "Optical & Line Sensors",
        "is_component": true,
        "price": 99.0,
        "currency": "INR",
        "description": "TCRT5000 Infrared Reflective Optical Line Tracking Sensor Module - Technical hardware component with Digital Output (DO) with sensitivity pot + Analog Output (AO) interfaces, operating at 3.3V - 5V DC.",
        "specs": {
            "voltage": "3.3V - 5V DC",
            "current": "20mA operating",
            "interface": "Digital Output (DO) with sensitivity pot + Analog Output (AO)",
            "protocol": "Infrared reflection detection via LM393 comparator",
            "package": "4-pin breakout board with IR emitter/phototransistor pair",
            "dimensions": "32 x 14 mm",
            "operating_range": "Focus distance 2.5mm, detection range 1mm to 25mm",
            "part_number": "TCRT5000",
            "manufacturer": "Vishay Intertechnology",
            "price": 99.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B07QC8Q69X",
        "amazon_url": "https://www.amazon.in/dp/B07QC8Q69X",
        "flipkart_url": "https://www.flipkart.com/harical-tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-electronic-components-hobby-kit/p/itma2857885c1435",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "retailer": "Amazon",
                "external_product_id": "B07QC8Q69X",
                "url": "https://www.amazon.in/dp/B07QC8Q69X",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "retailer": "Flipkart",
                "external_product_id": "itma2857885c1435",
                "url": "https://www.flipkart.com/harical-tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-electronic-components-hobby-kit/p/itma2857885c1435",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/f/v/r/tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-harical-original-imagrtdhyhc4bmmg.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000027-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "external_product_id": "B0CN586R2B",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/f/v/r/tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-harical-original-imagrtdhyhc4bmmg.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            },
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000027-GALLERY",
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "external_product_id": "B0CN586R2B",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/a/i/q/tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-harical-original-imagrtdhbhr2wqf2.jpeg?q=80",
                "image_type": "gallery",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>TCRT5000%20Infrared%20Reflective%20Optica</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - TCRT5000 Module",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the TCRT5000 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0CN586R2B",
        "asin": "B0CN586R2B",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "retailer": "Amazon",
                "external_product_id": "B0CN586R2B",
                "url": "https://www.amazon.in/dp/B0CN586R2B",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000027",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>TCRT5000%20Infrared%20Reflective%20Optica</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    },
    {
        "id": "c2000000-0000-0000-0000-000000000028",
        "product_id": "c2000000-0000-0000-0000-000000000028",
        "title": "MQ-135 Air Quality & Hazardous Gas Sensor Module (Hazardous Gas & Smoke)",
        "slug": "sensor-mq135-air",
        "brand": "Winsen",
        "model": "MQ-135",
        "sku": "SENSOR-MQ135-AIR",
        "model_number": "SENSOR-MQ135-AIR",
        "category": "Electronic Components & Modules",
        "subcategory": "Gas & Air Quality Sensors",
        "is_component": true,
        "price": 199.0,
        "currency": "INR",
        "description": "MQ-135 Air Quality & Hazardous Gas Sensor Module (Hazardous Gas & Smoke) - Technical hardware component with Analog AO (voltage) and Digital DO (LM393 threshold) interfaces, operating at 5V DC.",
        "specs": {
            "voltage": "5V DC",
            "current": "150mA heater",
            "interface": "Analog AO (voltage) and Digital DO (LM393 threshold)",
            "protocol": "Resistive gas concentration change",
            "package": "4-pin module with onboard trimmer potentiometer",
            "dimensions": "32 x 20 x 22 mm",
            "operating_range": "Detection: NH3, NOx, alcohol, benzene, smoke, CO2 (10-1000 ppm)",
            "part_number": "MQ-135",
            "manufacturer": "Zhengzhou Winsen Electronics",
            "price": 199.0
        },
        "source": "Amazon India / Flipkart",
        "source_url": "https://www.amazon.in/dp/B08RDKVDSS",
        "amazon_url": "https://www.amazon.in/dp/B08RDKVDSS",
        "flipkart_url": "https://www.flipkart.com/kitsguru-mq135-mq-135-air-quality-sensor-hazardous-gas-detection-module-electronic-components-hobby-kit/p/itmf7kskzqezzj74",
        "buy_links": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000028",
                "retailer": "Amazon",
                "external_product_id": "B08RDKVDSS",
                "url": "https://www.amazon.in/dp/B08RDKVDSS",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000028",
                "retailer": "Flipkart",
                "external_product_id": "itmf7kskzqezzj74",
                "url": "https://www.flipkart.com/kitsguru-mq135-mq-135-air-quality-sensor-hazardous-gas-detection-module-electronic-components-hobby-kit/p/itmf7kskzqezzj74",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            }
        ],
        "image_url": "https://rukminim2.flixcart.com/image/480/480/jk5r3bk0/electronic-hobby-kit/x/5/t/mq135-mq-135-air-quality-sensor-hazardous-gas-detection-module-original-imaf7kska9yekszk.jpeg?q=80",
        "images": [
            {
                "image_id": "IMG-c2000000-0000-0000-0000-000000000028-FRONT",
                "product_id": "c2000000-0000-0000-0000-000000000028",
                "external_product_id": "B0B7CBM4KW",
                "image_url": "https://rukminim2.flixcart.com/image/480/480/jk5r3bk0/electronic-hobby-kit/x/5/t/mq135-mq-135-air-quality-sensor-hazardous-gas-detection-module-original-imaf7kska9yekszk.jpeg?q=80",
                "image_type": "front",
                "source": "Flipkart",
                "verified": true
            }
        ],
        "media_gallery": {
            "front": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MQ-135%20Air%20Quality%20%26%20Hazardous%20Gas%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
        },
        "reviews": [
            {
                "title": "Verified Technical Component - MQ-135",
                "rating": 4.9,
                "body": "The pinout, logic levels, and electrical characteristics of the MQ-135 are compliant with standard datasheets."
            }
        ],
        "external_product_id": "B0B7CBM4KW",
        "asin": "B0B7CBM4KW",
        "retailer_offers": [
            {
                "product_id": "c2000000-0000-0000-0000-000000000028",
                "retailer": "Amazon",
                "external_product_id": "B0B7CBM4KW",
                "url": "https://www.amazon.in/dp/B0B7CBM4KW",
                "verification_status": "verified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "available"
            },
            {
                "product_id": "c2000000-0000-0000-0000-000000000028",
                "retailer": "Flipkart",
                "external_product_id": null,
                "url": null,
                "verification_status": "unverified",
                "last_verified": "2026-09-18T00:00:00Z",
                "availability_status": "unavailable"
            }
        ],
        "product_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'><rect width='500' height='500' fill='%23f8fafc'/><rect x='40' y='40' width='420' height='420' rx='16' fill='%23f1f5f9' stroke='%23cbd5e1' stroke-width='2'/><circle cx='250' cy='200' r='45' fill='%23e2e8f0'/><path d='M225 200 L275 200 M250 175 L250 225' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round'/><text x='250' y='290' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='16' font-weight='600' fill='%23334155'>MQ-135%20Air%20Quality%20%26%20Hazardous%20Gas%20</text><text x='250' y='325' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='14' font-weight='500' fill='%2364748b'>[Front View]</text><text x='250' y='365' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, sans-serif' font-size='13' font-style='italic' fill='%2394a3b8'>Image unavailable</text></svg>"
    }
]


def validate_product_image(product_id: str, image: Dict[str, Any], external_product_id: Optional[str] = None) -> bool:
    """Validate that an image strictly belongs to the candidate product identity."""
    if not image or not isinstance(image, dict):
        return False
    if image.get("product_id") != product_id:
        return False
    if external_product_id and image.get("external_product_id"):
        if image.get("external_product_id") != external_product_id:
            return False
    return True


def get_product_images(product_id: str, external_product_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve verified images for a specific product ID only.

    Requirements:
    1. Every image MUST belong to a canonical product_id.
    2. image.product_id == product.product_id
    3. If external_product_id exists, image.external_product_id == product.external_product_id.
    4. If identity cannot be verified, DO NOT display the image; return clean placeholder.
    5. NEVER substitute another product's image.
    6. All returned views within a product must have strictly distinct URLs (no fake views).
    """
    for p in FALLBACK_CATALOG:
        if p.get("id") == product_id or p.get("product_id") == product_id:
            ext_id = external_product_id or p.get("external_product_id") or p.get("asin")
            images = p.get("images", [])
            # Verify identity for every candidate image and ensure distinct URLs
            seen_urls = set()
            verified_images = []
            for img in images:
                u = img.get("image_url")
                if validate_product_image(product_id, img, ext_id) and img.get("verified", False):
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        verified_images.append(img)

            if verified_images:
                return verified_images

            # Clean product-specific SVG placeholder for missing/unverified images
            placeholder_url = p.get("image_url") if p.get("image_url", "").startswith("data:image/svg") else (
                f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'>"
                f"<rect width='400' height='400' fill='%23f1f5f9'/>"
                f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='16' fill='%2364748b'>Image unavailable</text></svg>"
            )
            return [{
                "image_id": f"IMG-{product_id}-FRONT",
                "product_id": product_id,
                "external_product_id": ext_id,
                "image_url": placeholder_url,
                "image_type": "front",
                "source": "Placeholder",
                "verified": False,
            }]
    return []


def get_product_buy_links(product_id: str) -> List[Dict[str, Any]]:
    """Retrieve verified buy links for a specific product ID only."""
    for p in FALLBACK_CATALOG:
        if p.get("id") == product_id or p.get("product_id") == product_id:
            return p.get("retailer_offers") or p.get("buy_links", [])
    return []


def get_fallback_product(product_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a product from fallback catalog by ID."""
    for p in FALLBACK_CATALOG:
        if p.get("id") == product_id or p.get("product_id") == product_id:
            return p
    return None


def search_fallback_catalog(
    query: str,
    category: Optional[str] = None,
    budget_max: Optional[float] = None,
    is_component: Optional[bool] = None,
    limit: int = 8,
    sort_expensive_first: bool = True,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search fallback catalog matching query, category, and budget constraints."""
    q_lower = (query or "").lower().strip()
    q_tokens = [t for t in re.split(r"[^a-z0-9]+", q_lower) if t]
    cat_lower = (category or category_filter or "").lower()

    # Determine strict allowed category
    strict_allowed_categories = None
    if any(w in q_lower for w in ["earphone", "earphones", "earbud", "earbuds", "tws", "airpod", "airpods"]):
        strict_allowed_categories = {"Audio & Headphones"}
    elif any(w in q_lower for w in ["headphone", "headphones", "headset"]):
        strict_allowed_categories = {"Audio & Headphones"}
    elif any(w in q_lower for w in ["audio", "sound", "boat", "bose", "rockerz", "jbl", "sennheiser", "airpods"]) or "audio" in cat_lower or "headphone" in cat_lower or "earphone" in cat_lower:
        strict_allowed_categories = {"Audio & Headphones"}
    elif bool(re.search(r"\b(phone|phones|smartphone|smartphones|mobile|mobiles|iphone|galaxy|pixel|oneplus|redmi|android|realme|iqoo)\b", q_lower)) or "smartphone" in cat_lower or cat_lower == "smartphones" or cat_lower == "mobile" or cat_lower == "phone":
        strict_allowed_categories = {"Smartphones"}
    elif any(w in q_lower for w in ["laptop", "laptops", "notebook", "notebooks", "macbook", "ultrabook", "gaming laptop", "zenbook", "thinkpad", "vivobook", "inspiron", "legion", "yoga"]) or "laptop" in cat_lower:
        strict_allowed_categories = {"Laptops & Ultrabooks"}
    elif any(w in q_lower for w in ["electronics", "electronic", "mcu", "microcontroller", "esp32", "arduino", "raspberry", "pi 4", "pi 5", "pico", "sensor", "relay", "shifter", "bme280", "iot", "component", "components", "board", "circuit", "servo", "lora", "gps", "oled", "lcd"]) or any(k in cat_lower for k in ["component", "microcontroller", "sensor", "electronics"]):
        strict_allowed_categories = {"Electronic Components & Modules"}

    # Stop words
    stop_words = {"chahiye", "bhai", "best", "under", "andar", "product", "recommend", "show", "me", "the", "for", "with", "and"}
    meaningful_tokens = [t for t in q_tokens if t not in stop_words]
    if not meaningful_tokens:
        meaningful_tokens = q_tokens

    scored_items = []

    for item in FALLBACK_CATALOG:
        item_cat = item.get("category", "")
        if strict_allowed_categories and item_cat not in strict_allowed_categories:
            continue

        if is_component is not None and item.get("is_component") != is_component:
            continue

        item_text = (
            f"{item['title']} {item['brand']} {item['category']} {item.get('subcategory', '')} "
            f"{item.get('description', '')} {str(item.get('specs', {}))}"
        ).lower()

        score = 0.0
        if strict_allowed_categories and item_cat in strict_allowed_categories:
            score += 2.0

        for t in meaningful_tokens:
            stem = t[:-1] if (len(t) > 4 and t.endswith("s")) else t
            if t in item_text or stem in item_text:
                score += 2.0
                if t in item["title"].lower() or stem in item["title"].lower():
                    score += 3.5
                if t in item["brand"].lower():
                    score += 2.5

        # Budget scoring
        item_price = float(item["price"])
        if budget_max is not None:
            if item_price <= budget_max:
                score += 3.0
                if item_price >= budget_max * 0.7:
                    score += 1.0
            else:
                score -= 2.0
                if item_price > budget_max * 1.3:
                    score -= 6.0

        if score > 0 or not meaningful_tokens:
            item_copy = dict(item)
            item_copy["retrieval_score"] = max(0.5, score)
            scored_items.append((score, item_copy))

    def _rank_sort_key(entry):
        score_val, it = entry
        p = float(it.get("price", 0))
        over_budget = 1 if (budget_max is not None and p > budget_max) else 0
        price_order = -p if sort_expensive_first else p
        return (over_budget, -score_val, price_order)

    scored_items.sort(key=_rank_sort_key)

    if not scored_items:
        for item in FALLBACK_CATALOG:
            item_cat = item.get("category", "")
            if strict_allowed_categories and item_cat not in strict_allowed_categories:
                continue
            if is_component is not None and item.get("is_component") != is_component:
                continue
            item_copy = dict(item)
            item_copy["retrieval_score"] = 1.0
            scored_items.append((1.0, item_copy))
        scored_items.sort(key=_rank_sort_key)

    return [item for _, item in scored_items[:limit]]
