import pytest
from sim_hangar_manager.database import enums
from sim_hangar_manager.exceptions.exceptions import AircraftModuleAlreadyExistsError

def test_register_aircraft_module_success(aircraft_service):

    payload = {
        "name": "F/A-18C Hornet",
        "icao_code": "F18",
        "developer": "Eagle Dynamics",
        "module_name": "FA-18C_hornet",
        "simulator": "DCS",
        "notes": "Carrier capable multirole fighter",
        "type": "AIRCRAFT",
        "engine_type": "MULTI_JET"
    }

    created = aircraft_service.register_aircraft_model(payload)

    assert created.id is not None
    assert created.name == "F/A-18C Hornet"
    assert created.developer == "Eagle Dynamics"


def test_list_active_hangar_modules_returns_all(aircraft_service):

    payload1 = {
        "name": "Baron 58 Professional",
        "icao_code": "BE58",
        "developer": "BlackSquare",
        "module_name": "bksq-b58",
        "simulator": "MSFS",
        "type": "AIRCRAFT",
        "engine_type": "MULTI_PISTON_ENGINE"
    }
    payload2 = {
        "name": "Bonanza A36 Professional",
        "icao_code": "BE36",
        "developer": "BlackSquare",
        "module_name": "bksq-a36",
        "simulator": "MSFS",
        "type": "AIRCRAFT",
        "engine_type": "SINGLE_PISTON_ENGINE"
    }

    aircraft_service.register_aircraft_model(payload1)
    aircraft_service.register_aircraft_model(payload2)

    active_modules = aircraft_service.get_all_aircraft_models()
    assert len(active_modules) == 2
    assert active_modules[0].developer == "BlackSquare"


def test_register_duplicate_aircraft_module_raises_exception(aircraft_service):
    payload = {
        "name": "PMDG 737-700",
        "module_name": "pmdg-aircraft-737",
        "simulator": "MSFS",
        "icao_code": "B737",
        "developer": "PMDG",
        "type": "AIRCRAFT",
        "engine_type": "MULTI_JET",
        "aircraft_category": "AIRLINER"
    }

    # First Save successful
    aircraft_service.register_aircraft_model(payload)

    # Second attempt should throw exception
    with pytest.raises(AircraftModuleAlreadyExistsError) as exc_info:
        aircraft_service.register_aircraft_model(payload)

    assert "pmdg-aircraft-737" in str(exc_info.value)