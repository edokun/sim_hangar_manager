from unittest.mock import MagicMock

import pytest

from sim_hangar_manager.database import enums
from sim_hangar_manager.exceptions.exceptions import \
    AircraftModuleAlreadyExistsError
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService


def _payload(**overrides):
    """Builds a valid registration payload, allowing individual fields to be overridden."""
    defaults = {
        "name": "A36 Bonanza",
        "icao_code": "BE36",
        "developer": "Black Square",
        "module_name": "Bonanza Professional",
        "simulator": "MSFS",
        "notes": "Analog classic Bonanza",
        "type": "AIRCRAFT",
        "engine_type": "PISTON",
    }
    defaults.update(overrides)
    return defaults


def test_register_aircraft_module_success(aircraft_service):

    payload = {
        "name": "A36 Bonanza",
        "icao_code": "BE36",
        "developer": "Black Square",
        "module_name": "Bonanza Professional",
        "simulator": "MSFS",
        "notes": "Analog classic Bonanza",
        "type": "AIRCRAFT",
        "engine_type": "PISTON",
    }

    created = aircraft_service.register_aircraft_model(payload)

    assert created.id is not None
    assert created.name == "A36 Bonanza"
    assert created.developer == "Black Square"


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


def test_register_aircraft_module_with_overwrite_updates_existing(aircraft_service):
    original = aircraft_service.register_aircraft_model(
        _payload(name="Original Name", module_name="pmdg-aircraft-737")
    )

    updated = aircraft_service.register_aircraft_model(
        _payload(
            name="Changed Name",
            module_name="pmdg-aircraft-737",
            developer="PMDG",
            version="2.0",
            is_active=False,
            is_installed=True,
            module_file_location_1="C:/MSFS/Community/pmdg-737",
        ),
        overwrite=True,
    )

    assert updated.id == original.id
    # Fields not part of the override data are left untouched
    assert updated.name == "Original Name"
    assert updated.developer == "PMDG"
    assert updated.version == "2.0"
    assert updated.is_active is False
    assert updated.is_installed is True
    assert updated.module_file_location_1 == "C:/MSFS/Community/pmdg-737"
    assert len(aircraft_service.get_all_aircraft_models(include_inactive=True)) == 1


def test_register_aircraft_module_allows_same_module_for_different_simulator(aircraft_service):
    aircraft_service.register_aircraft_model(_payload(simulator="MSFS"))
    aircraft_service.register_aircraft_model(_payload(simulator="X-PLANE"))

    assert len(aircraft_service.get_all_aircraft_models()) == 2


def test_debug_logs_messages_when_console_is_provided(aircraft_repo):
    console = MagicMock()
    service = AircraftModelService(aircraft_repo, log_console=console)

    service.register_aircraft_model(_payload())

    console.print.assert_called()
    messages = " ".join(str(call.args[0]) for call in console.print.call_args_list)
    assert "[AircraftModuleService]" in messages
    assert "Saving new module" in messages


def test_get_by_id_returns_model(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    retrieved = aircraft_service.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


def test_get_by_id_returns_none_for_missing_model(aircraft_service):
    assert aircraft_service.get_by_id(9999) is None


def test_get_all_aircraft_models_respects_pagination_and_inactive_filter(aircraft_service):
    first = aircraft_service.register_aircraft_model(
        _payload(module_name="module-1")
    )
    aircraft_service.register_aircraft_model(_payload(module_name="module-2"))
    aircraft_service.disable_aircraft_model(first.id)

    active = aircraft_service.get_all_aircraft_models()
    assert len(active) == 1
    assert active[0].id != first.id

    all_models = aircraft_service.get_all_aircraft_models(include_inactive=True)
    assert len(all_models) == 2

    assert len(aircraft_service.get_all_aircraft_models(include_inactive=True, limit=1)) == 1
    assert len(aircraft_service.get_all_aircraft_models(include_inactive=True, skip=1)) == 1


def test_update_aircraft_model_changes_fields(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    updated = aircraft_service.update_aircraft_model(
        created.id, {"name": "Updated Hornet", "notes": "Updated notes"}
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.name == "Updated Hornet"
    assert updated.notes == "Updated notes"


def test_update_aircraft_model_returns_none_for_missing_model(aircraft_service):
    assert aircraft_service.update_aircraft_model(9999, {"name": "Nope"}) is None


def test_disable_and_enable_aircraft_model_toggles_active_flag(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    assert aircraft_service.disable_aircraft_model(created.id) is None
    assert aircraft_service.get_by_id(created.id).is_active is False

    assert aircraft_service.enable_aircraft_model(created.id) is None
    assert aircraft_service.get_by_id(created.id).is_active is True


def test_update_aircraft_model_notes(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    updated = aircraft_service.update_aircraft_model_notes(created.id, "New notes")

    assert updated is not None
    assert updated.notes == "New notes"


def test_update_aircraft_model_notes_returns_none_for_missing_model(aircraft_service):
    assert aircraft_service.update_aircraft_model_notes(9999, "New notes") is None


def test_update_aircraft_model_rating(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    updated = aircraft_service.update_aircraft_model_rating(created.id, 4)

    assert updated is not None
    assert updated.rating == 4


def test_update_aircraft_model_rating_returns_none_for_missing_model(aircraft_service):
    assert aircraft_service.update_aircraft_model_rating(9999, 4) is None


def test_delete_aircraft_model_removes_it(aircraft_service):
    created = aircraft_service.register_aircraft_model(_payload())

    assert aircraft_service.delete(created.id) is None
    assert aircraft_service.get_by_id(created.id) is None