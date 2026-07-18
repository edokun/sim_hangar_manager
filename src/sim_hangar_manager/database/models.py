from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# --- ENUMs  ---
class AircraftCategory(str, Enum):
    SINGLE_PISTON_ENGINE = "SINGLE PISTON ENGINE"
    MULTI_PISTON_ENGINE = "MULTI PISTON ENGINE"
    SINGLE_JET = "SINGLE_JET"
    MULTI_JET = "MULTI_JET"
    SINGLE_TURBOPROP = "SINGLE_TURBOPROP"
    MULTI_TURBOPROP = "MULTI_TURBOPROP"
    HELICOPTER = "HELICOPTER"
    OTHER = "OTHER"

class AircraftType(str, Enum):
    AIRCRAFT = "AIRCRAFT"
    HELICOPTER = "HELICOPTER"
    GLIDER = "GLIDER"
    OTHER = "OTHER"

class AircraftOrigin(str, Enum):
    FREEWARE = "FREEWARE"
    PAYWARE = "PAYWARE"
    DEFAULT = "DEFAULT"

class OriginStore(str, Enum):
    MARKETPLACE = "MARKETPLACE"
    JUST_FLIGHT = "JUST_FLIGHT"
    SIMMARKET = "SIMMARKET"
    ORBX = "ORBX"
    CONTRAIL = "CONTRAIL"
    INIBUILDS = "INIBUILDS"
    DEVELOPER_SITE = "DEVELOPER_SITE"
    OTHER = "OTHER"

class FlightType(str, Enum):
    CARGO = "CARGO"
    PASSENGER = "PASSENGER"
    MILITARY = "MILITARY"

class Simulator(str, Enum):
    MSFS = "MSFS"
    XP = "X-PLANE"
    P3D = "PREPAR3D"
    OTHER = "OTHER"

# This is the table that maps the actual aircraft modules, (freeware, paid, default, etc.)
class AircraftModel(Base):
    __tablename__ = "aircraft_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_name: Mapped[str] = mapped_column(String(100)) # Name of the module like folder name or package name
    name: Mapped[str] = mapped_column(String(100)) # Name of the aircraft model like "Cessna 172 Skyhawk" or "Boeing 747-8"
    icao_code: Mapped[str] = mapped_column(String(4), default="UNKN") # ICAO code for the aircraft model
    developer: Mapped[Optional[str]] = mapped_column(String(100)) # Name of the developer or company that created the aircraft model
    
    category: Mapped[Optional[str]] = mapped_column(String(20)) # ENUM Category of the aircraft model (Single Engine, Multi Engine, Jet, etc.)
    type: Mapped[Optional[str]] = mapped_column(String(20)) # ENUM (Aircraft, Helicopter, Glider, etc.)
    origin: Mapped[Optional[str]] = mapped_column(String(100)) # ENUM (freeware, payware, default)
    origin_store: Mapped[Optional[str]] = mapped_column(String(100)) # name of the store, ENUM of known stores
    
    developer_url: Mapped[Optional[str]] = mapped_column(String(100)) # URL of the developer's website
    version: Mapped[Optional[str]] = mapped_column(String(20)) # Module/mod version (Obtained from the aircraft's manifest file)
    
    model_metadata: Mapped[Optional[str]] = mapped_column(String(1000)) # additional information like aircraft performance, limitations, etc.
    notes: Mapped[Optional[str]] = mapped_column(String(500)) # additional notes the user can add about the aircraft model
    rating: Mapped[Optional[int]] = mapped_column(Integer, default=0) # rating of the aircraft model (1-5 stars)
    simulator: Mapped[Optional[str]] = mapped_column(String(20)) # simulator name like "MSFS", "X-Plane", "Prepar3D", etc.


    aircrafts: Mapped[List["Aircraft"]] = relationship(back_populates="model")

    def __repr__(self) -> str:
        return f"<AircraftModel(Nombre={self.name}, Desarrollador={self.developer})>"

# There can be multiple instances of the same aircraft model, each with its own unique tail number and flight hours.
class Aircraft(Base):
    __tablename__ = "aircrafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tail_number: Mapped[str] = mapped_column(String(10), unique=True) # Unique tail number for the aircraft
    aircraft_model_id: Mapped[int] = mapped_column(ForeignKey("aircraft_models.id"))
    variant: Mapped[Optional[str]] = mapped_column(String(50)) # Some airplanes have different variants like "Classic", "NG", "X", etc.
    enginevariant: Mapped[Optional[str]] = mapped_column(String(50)) # Some airplanes have different engine options
    home_airport: Mapped[Optional[str]] = mapped_column(String(4)) # ICAO code of the home airport for the aircraft
    current_location: Mapped[Optional[str]] = mapped_column(String(4)) # ICAO code of the current location of the aircraft
    airframe_hours: Mapped[float] = mapped_column(Float, default=0.0)
    engine_hours: Mapped[float] = mapped_column(Float, default=0.0)
    last_flight_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    type: Mapped[Optional[str]] = mapped_column(String(20)) # ENUM (CARGO, PASSENGER, MILITARY, etc.)
    airline_icao: Mapped[Optional[str]] = mapped_column(String(4)) # ICAO code of the airline for the aircraft
    airline_name: Mapped[Optional[str]] = mapped_column(String(100)) # Name of the airline for the aircraft

    model: Mapped["AircraftModel"] = relationship(back_populates="aircrafts")
    flights: Mapped[List["Flight"]] = relationship(back_populates="aircraft")

    def __repr__(self) -> str:
        return f"<Aircraft(TailNumber={self.tail_number}, ModelID={self.aircraft_model_id}, Type={self.type}, AirlineICAO={self.airline_icao}, AirlineName={self.airline_name})>"


class Flight(Base):
    __tablename__ = "flight_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aircraft_id: Mapped[int] = mapped_column(ForeignKey("aircrafts.id"))
    flight_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) # Date and time of the flight
    origin_airport: Mapped[str] = mapped_column(String(4))
    destination_airport: Mapped[str] = mapped_column(String(4))
    duration: Mapped[int] = mapped_column(Integer, default=0) # Duration of the flight in minutes

    aircraft: Mapped["Aircraft"] = relationship(back_populates="flights")

    def __repr__(self) -> str:
        return f"<Flight(ID={self.id}, AircraftID={self.aircraft_id}, From={self.origin_airport} To={self.destination_airport})>"