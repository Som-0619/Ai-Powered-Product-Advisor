#!/usr/bin/env python3
"""Database snapshot and backup script for canonical electronics catalog."""

import os
import sys
import json
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def backup_database():
    db_url = os.environ.get("LOCAL_POSTGRES_URL") or "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor"
    engine = create_async_engine(db_url, echo=False)
    
    backup_data = {}
    tables = [
        "products",
        "product_variants",
        "product_images",
        "product_reviews",
        "retailer_offers",
        "product_sources",
    ]
    
    async with engine.connect() as conn:
        for t in tables:
            res = await conn.execute(text(f"SELECT * FROM {t};"))
            columns = list(res.keys())
            rows = []
            for r in res.fetchall():
                row_dict = {}
                for col, val in zip(columns, r):
                    if hasattr(val, "isoformat"):
                        row_dict[col] = val.isoformat()
                    elif hasattr(val, "hex"): # UUID
                        row_dict[col] = str(val)
                    else:
                        row_dict[col] = val
                rows.append(row_dict)
            backup_data[t] = rows
            print(f"Backed up table '{t}': {len(rows)} records")
            
    out_dir = Path("/Users/soumyajithazra/.gemini/antigravity-ide/brain/925bfe50-ae41-4b79-ad7e-de39b1a12198/scratch")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "database_backup_pre_stage2.json"
    with open(out_file, "w") as f:
        json.dump(backup_data, f, indent=2)
    print(f"\nSuccessfully created pre-import database snapshot at: {out_file}")
    return 0

if __name__ == "__main__":
    asyncio.run(backup_database())
