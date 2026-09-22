"""Curated Authentic Canonical Electronics Products Dataset aggregator.

Combines all authentic dataset modules into ALL_NEW_CANONICAL_PRODUCTS.
"""

from typing import List, Dict, Any

from app.ingestion.data.laptops import LAPTOPS_DATASET
from app.ingestion.data.smartphones import SMARTPHONES_DATASET
from app.ingestion.data.audio import AUDIO_DATASET
from app.ingestion.data.tablets import TABLETS_DATASET
from app.ingestion.data.smartwatches import SMARTWATCHES_DATASET
from app.ingestion.data.monitors import MONITORS_DATASET
from app.ingestion.data.peripherals import PERIPHERALS_DATASET
from app.ingestion.data.cameras_networking import CAMERAS_NETWORKING_DATASET
from app.ingestion.data.iot_smarthome import IOT_SMARTHOME_DATASET
from app.ingestion.data.components_devboards import COMPONENTS_DEVBOARDS_DATASET

ALL_NEW_CANONICAL_PRODUCTS: List[Dict[str, Any]] = (
    LAPTOPS_DATASET
    + SMARTPHONES_DATASET
    + AUDIO_DATASET
    + TABLETS_DATASET
    + SMARTWATCHES_DATASET
    + MONITORS_DATASET
    + PERIPHERALS_DATASET
    + CAMERAS_NETWORKING_DATASET
    + IOT_SMARTHOME_DATASET
    + COMPONENTS_DEVBOARDS_DATASET
)
