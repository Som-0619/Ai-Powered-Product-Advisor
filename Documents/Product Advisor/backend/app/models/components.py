"""Electronic Component models: Component and ComponentSpecification."""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Component(Base, UUIDMixin, TimestampMixin):
    """Electronic component physical and package details."""
    __tablename__ = "components"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    part_number: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    package_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, index=True) # e.g. "DIP-8", "SOIC-8", "TO-220", "SMD-0805"
    pin_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mounting_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)             # "Through Hole", "Surface Mount"
    lifecycle_status: Mapped[str] = mapped_column(String(40), default="active", nullable=False) # "Active", "NRND", "Obsolete"
    datasheet_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="component_profile")
    specification: Mapped[Optional["ComponentSpecification"]] = relationship(
        "ComponentSpecification", back_populates="component", uselist=False, cascade="all, delete-orphan"
    )


class ComponentSpecification(Base, UUIDMixin, TimestampMixin):
    """Detailed electrical and environmental specifications for components."""
    __tablename__ = "component_specifications"

    component_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Voltage parameters
    voltage_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    voltage_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    voltage_unit: Mapped[str] = mapped_column(String(10), default="V", nullable=False)

    # Current parameters
    current_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_unit: Mapped[str] = mapped_column(String(10), default="A", nullable=False)

    # Passive parameters
    resistance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resistance_unit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # "Ohm", "kOhm", "MOhm"

    capacitance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    capacitance_unit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # "pF", "nF", "uF"

    power: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    power_unit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)       # "W", "mW"

    tolerance: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)        # "±1%", "±5%", "±10%"
    interface: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)        # "I2C, SPI, UART"
    package: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)          # Package alias e.g. "0805", "DIP-8"

    frequency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    frequency_unit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)   # "MHz", "GHz"

    temperature_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperature_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    extra_specs: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="specification")

    __table_args__ = (
        Index("ix_comp_spec_voltage", "voltage_min", "voltage_max"),
        Index("ix_comp_spec_temp", "temperature_min", "temperature_max"),
    )
