from enum import StrEnum


# --- ENUM Objects for the database tables ---
# -- ENUMS for aircraft_models table --
class AircraftCategory(StrEnum):
    SINGLE_PISTON_ENGINE = "SINGLE_PISTON_ENGINE"
    MULTI_PISTON_ENGINE = "MULTI_PISTON_ENGINE"
    SINGLE_JET = "SINGLE_JET"
    MULTI_JET = "MULTI JET"
    SINGLE_TURBOPROP = "SINGLE_TURBOPROP"
    MULTI_TURBOPROP = "MULTI_TURBOPROP"
    HELICOPTER = "HELICOPTER"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class AircraftType(StrEnum):
    AIRCRAFT = "AIRCRAFT"
    HELICOPTER = "HELICOPTER"
    GLIDER = "GLIDER"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class ModuleType(StrEnum):
    FREEWARE = "FREEWARE"
    PAYWARE = "PAYWARE"
    DEFAULT = "DEFAULT"


class Store(StrEnum):
    AEROSOFT = "AEROSOFT"
    MARKETPLACE = "MARKETPLACE"
    JUST_FLIGHT = "JUST_FLIGHT"
    SIMMARKET = "SIMMARKET"
    ORBX = "ORBX"
    CONTRAIL = "CONTRAIL"
    INIBUILDS = "INIBUILDS"
    DEVELOPER_SITE = "DEVELOPER_SITE"
    FLIGHTSIM_TO = "FLIGHTSIM_TO"
    FBW = "FBW"  # Fly By Wire Installer
    HEADWIND = "HEADWIND"  # Headwind Simulations (Installer)
    OTHER = "OTHER"


# The Enum is listing one record only as currently this app only supports MSFS
class Simulator(StrEnum):
    MSFS = "MSFS"


class SimulatorCompatibility(StrEnum):
    MSFS_2020 = "MSFS_2020"
    MSFS_2024_COMPATIBLE = "MSFS_2024_COMPATIBLE"
    MSFS_2024_NATIVE = "MSFS_2024_NATIVE"
    # The developer has 2 different installer/packages for each MSFS version
    MSFS_DUAL_VERSIONS = "MSFS_DUAL_VERSIONS"


# -- ENUMS for aircrafts table --
class FlightType(StrEnum):
    CARGO = "CARGO"
    PASSENGER = "PASSENGER"
    MILITARY = "MILITARY"
