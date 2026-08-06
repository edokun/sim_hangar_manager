import pytest
from sim_hangar_manager.database import enums

def test_register_aircraft_module_success(aircraft_service):

    payload = {
        "name": "F/A-18C Hornet",
        "icao_code": "F18",
        "developer": "Eagle Dynamics",
        "module_name": "FA-18C_hornet",
        "simulator": "DCS",
        "notes": "Carrier capable multirole fighter",
        "type": "AIRCRAFT",
        "category": "MULTI_JET"
    }

    created = aircraft_service.create_aircraft_model(payload)

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
        "category": "MULTI_PISTON_ENGINE"
    }
    payload2 = {
        "name": "Bonanza A36 Professional",
        "icao_code": "BE36",
        "developer": "BlackSquare",
        "module_name": "bksq-a36",
        "simulator": "MSFS",
        "type": "AIRCRAFT",
        "category": "SINGLE_PISTON_ENGINE"
    }

    aircraft_service.create_aircraft_model(payload1)
    aircraft_service.create_aircraft_model(payload2)

    active_modules = aircraft_service.get_all_aircraft_models()
    assert len(active_modules) == 2
    assert active_modules[0].developer == "BlackSquare"