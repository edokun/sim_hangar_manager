from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (DateTime, Float, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# --- Model Objects for the database tables ---

# This table registers the actual aircraft modules/addons
class AircraftModel(Base):
    __tablename__ = "aircraft_models"

    # Basic fields for the aircraft model
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Name of the module like folder name or package name
    module_name: Mapped[str] = mapped_column(String(100))
    # Name of the aircraft model like "bksq_aircraft_baronpro, usually this is taken as aircraft sub folder name"
    name: Mapped[str] = mapped_column(String(100))
    # Variant Name for cases where an aircraft module contains multiple variants
    variant: Mapped[Optional[str]] = mapped_column(String(100))
    # Aircraft name (Correct name like Baron 58, or C172 Skyhawk II)
    aircraft_name: Mapped[Optional[str]] = mapped_column(String(50))
    # ICAO code for the aircraft model
    icao_code: Mapped[str] = mapped_column(String(4), default="UNKN")
    # Aircraft Manufacturer (Piper, Cessna, Beech, Boeing, etc.)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(50)) 
    # ENUM (Aircraft, Helicopter, Glider, etc.)
    type: Mapped[str] = mapped_column(String(20))
    # ENUM Engine Type of the aircraft model (Single Engine, Multi Engine, etc.)
    engine_type: Mapped[str] = mapped_column(String(30))
    # Number of Engines
    engine_count: Mapped[Optional [int]] = mapped_column(Integer, default=0)
    # ENUM Aircraft Category, (GENERAL AVIATION, AIRLINER, etc.)
    aircraft_category: Mapped[Optional[str]] = mapped_column(String(50))
    # ENUM Aircraft Sub-Category, (WARBIRD, VINTAGE, CLASSIC, etc.)
    aircraft_subcategory: Mapped[Optional[str]] = mapped_column(String(50))
    # ENUM simulator, simulator name like "MSFS", "X-Plane", "P3D", etc.
    simulator: Mapped[str] = mapped_column(String(20))
    # Optional field to group modules into a user made group
    group: Mapped[Optional[str]] = mapped_column(String(50))

    # -- Module specific optional fields --
    # additional information like aircraft performance, limitations, etc. (Maybe not needed, delete if not needed)
    model_data: Mapped[Optional[str]] = mapped_column(String(1000))
    # SIM Version compatibility
    simulator_compatibility: Mapped[Optional[str]] = mapped_column(String(50))

    # -- Developer specific fields --
    # Name of the developer or company that created the aircraft model
    developer: Mapped[str] = mapped_column(String(100))
    # ENUM ModuleType
    module_type: Mapped[Optional[str]] = mapped_column(String(100))
    # ENUM Store
    store: Mapped[Optional[str]] = mapped_column(String(100))
    # URL of the developer's website (Maybe not needed, delete if not needed)
    developer_url: Mapped[Optional[str]] = mapped_column(String(100))

    # -- User specific fields --
    # additional notes the user can add about the aircraft model
    notes: Mapped[Optional[str]] = mapped_column(String(500))
    # rating of the aircraft model (1-5 stars)
    rating: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # -- Module/Addon Metadata fields --
    # Module/mod version (Obtained from the aircraft's manifest file)
    version: Mapped[Optional[str]] = mapped_column(String(20))
    # Path to the module's folder or package file
    module_file_location_1: Mapped[Optional[str]] = mapped_column(String(1000)) 
    # Path to the module's folder or package file
    # (For cases where addon has 2 different packages for MSFS 2020 and MSFS 2024, for example) (Maybe not needed, delete if not needed)
    module_file_location_2: Mapped[Optional[str]] = mapped_column(String(1000))
    # additional information of the module/addon (Maybe not needed, delete if not needed)
    model_metadata: Mapped[Optional[str]] = mapped_column(String(1000))
    # Flag to indicate if the aircraft model/module is active (soft delete)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Flag to indicate if the aircraft model/module is installed
    is_installed: Mapped[bool] = mapped_column(default=False)


    # Timestamps passed as callables (lambda) 
    # to evaluate the actual time on row insertion/update
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship: One AircraftModel can have multiple specific Aircraft instances
    aircraft: Mapped[List["Aircraft"]] = relationship(back_populates="model")

    __table_args__ = (
        UniqueConstraint("simulator", "module_name", name="uq_simulator_module_name"),
    )

    def __repr__(self) -> str:
        return f"<AircraftModel(Name={self.name}, Developer={self.developer}, ICAO={self.icao_code}, Type={self.type}, Category={self.category}, Simulator={self.simulator})>"


# Instance of each module/addon
class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Unique tail number for the aircraft
    tail_number: Mapped[str] = mapped_column(String(10), unique=True)
    aircraft_model_id: Mapped[int] = mapped_column(ForeignKey("aircraft_models.id"))
    # Some airplanes have different variants like "Classic", "NG", "X", etc.
    variant: Mapped[Optional[str]] = mapped_column(String(50))
    # Some airplanes have different engine options
    engine_variant: Mapped[Optional[str]] = mapped_column(String(50))
    # ICAO code of the home airport for the aircraft
    home_airport: Mapped[Optional[str]] = mapped_column(String(4))
    # ICAO code of the current location of the aircraft
    current_location: Mapped[Optional[str]] = mapped_column(String(4))
    airframe_hours: Mapped[float] = mapped_column(Float, default=0.0)
    engine_hours: Mapped[float] = mapped_column(Float, default=0.0)
    last_flight_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    # ENUM (CARGO, PASSENGER, MILITARY, etc.)
    type: Mapped[Optional[str]] = mapped_column(String(20))
    # ICAO code of the airline for the aircraft
    airline_icao: Mapped[Optional[str]] = mapped_column(String(4))
    # Name of the airline for the aircraft
    airline_name: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped["AircraftModel"] = relationship(back_populates="aircraft")
    flights: Mapped[List["Flight"]] = relationship(back_populates="aircraft")

    def __repr__(self) -> str:
        return f"<Aircraft(TailNumber={self.tail_number}, ModelID={self.aircraft_model_id}, Type={self.type}, AirlineICAO={self.airline_icao}, AirlineName={self.airline_name})>"


class Flight(Base):
    __tablename__ = "flight_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aircraft_id: Mapped[int] = mapped_column(ForeignKey("aircraft.id"))
    flight_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))  # Date and time of the flight
    origin_airport: Mapped[str] = mapped_column(String(4))
    destination_airport: Mapped[str] = mapped_column(String(4))
    # Duration of the flight in minutes
    duration: Mapped[int] = mapped_column(Integer, default=0)
    aircraft: Mapped["Aircraft"] = relationship(back_populates="flights")

    def __repr__(self) -> str:
        return f"<Flight(ID={self.id}, AircraftID={self.aircraft_id}, From={self.origin_airport} To={self.destination_airport})>"