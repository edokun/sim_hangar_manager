from enum import StrEnum


# --- ENUM Objects for the database tables ---
# -- ENUMS for aircraft_models table --
class AircraftCategory(StrEnum):
    AIRLINER = "AIRLINER"
    BUSINESS_JET = "BUSINESS JET"
    CARGO_UTILITY = "CARGO UTILITY"
    EXPERIMENTAL = "EXPERIMENTAL"
    GENERAL_AVIATION = "GENERAL AVIATION"
    MILITARY_BOMBER = "MILITARY BOMBER"
    MILITARY_CARGO = "MILITARY CARGO"
    MILITARY_FIGHTER = "MILITARY FIGHTER"
    MILITARY_TRAINER = "MILITARY TRAINER"
    MILITARY_UTILITY = "MILITARY UTILITY"
    OTHER = "OTHER"
    SPORT_LIGHT_AIRCRAFT = "SPORT LIGHT AIRCRAFT"
    ULTRA_LIGHT_AIRCRAFT = "ULTRA LIGHT AIRCRAFT"
    UNKNOWN = "UNKNOWN"

class AircraftSubCategory(StrEnum):
    CLASSIC_AIRCRAFT = "CLASSIC"
    HEAVY = "HEAVY"
    NONE = "NONE"
    MULTI_ROLE = "MULTI-ROLE"
    OTHER = "OTHER"
    VINTAGE_AIRCRAFT = "VINTAGE"
    WARBIRD = "WARBIRD"
    
    

class EngineType(StrEnum):
    PISTON = "PISTON"
    JET = "JET"
    TURBOPROP_TURBOSHAFT = "TURBOPROP/TURBOSHAFT"
    UNKNOWN = "UNKNOWN"


class AircraftType(StrEnum):
    AIRPLANE = "AIRPLANE"
    HELICOPTER = "HELICOPTER"
    GLIDER = "GLIDER"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class ModuleType(StrEnum):
    FREEWARE = "FREEWARE"
    PAYWARE = "PAYWARE"
    DEFAULT = "DEFAULT" # Comes by default with the simulator


class Store(StrEnum):
    AEROSOFT = "AEROSOFT"
    MARKETPLACE = "MARKETPLACE"
    JUST_FLIGHT = "JUST FLIGHT"
    SIMMARKET = "SIMMARKET"
    ORBX = "ORBX"
    CONTRAIL = "CONTRAIL"
    INIBUILDS = "INIBUILDS"
    DEVELOPER_SITE = "DEVELOPER SITE"
    FLIGHTSIM_TO = "FLIGHTSIM.TO"
    FBW = "FBW"  # Fly By Wire Installer
    HEADWIND = "HEADWIND"  # Headwind Simulations (Installer)
    HANGAR_ADDONS = "HANGAR ADDONS"
    OTHER = "OTHER"


# The Enum is listing one record only as currently this app only supports MSFS
class Simulator(StrEnum):
    MSFS = "MSFS"


class SimulatorCompatibility(StrEnum):
    MSFS_2020 = "MSFS 2020"
    MSFS_2024_COMPATIBLE = "MSFS 2024 COMPATIBLE"
    MSFS_2024 = "MSFS 2024"
    # The developer has 2 different installer/packages for each MSFS version
    MSFS_DUAL_VERSIONS = "MSFS 2020 & 2024"


# -- ENUMS for aircraft table --
class FlightType(StrEnum):
    CARGO = "CARGO"
    PASSENGER = "PASSENGER"
    MILITARY = "MILITARY"
