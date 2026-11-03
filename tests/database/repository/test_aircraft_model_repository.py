from sim_hangar_manager.database import enums
from sim_hangar_manager.database.models import AircraftModel


def _make_aircraft_model(**overrides):
    """Builds a valid AircraftModel, allowing individual fields to be overridden."""
    defaults = {
        "name": "Test Aircraft",
        "icao_code": "TST",
        "developer": "Test Developer",
        "module_name": "test-aircraft",
        "simulator": "MSFS",
        "manufacturer": "Test Manufacturer",
        "type": enums.AircraftType.AIRPLANE,
        "engine_type": enums.EngineType.PISTON,
        "aircraft_category": enums.AircraftCategory.GENERAL_AVIATION,
    }
    defaults.update(overrides)
    return AircraftModel(**defaults)


def test_create_and_get_aircraft_model(aircraft_repo):

    new_aircraft = AircraftModel(
        name="737-700 NG",
        icao_code="B737",
        developer="PMDG",
        module_name="pmdg-aircraft-737",
        simulator="MSFS",
        manufacturer="Boeing",
        type=enums.AircraftType.AIRPLANE,
        engine_type=enums.EngineType.JET,
        aircraft_category=enums.AircraftCategory.AIRLINER
    )

    saved_aircraft = aircraft_repo.create(new_aircraft)
    
    assert saved_aircraft.id is not None

    retrieved = aircraft_repo.get_by_id(saved_aircraft.id)
    assert retrieved is not None
    assert retrieved.name == "737-700 NG"
    assert retrieved.developer == "PMDG"


def test_list_active_modules_filters_soft_deleted(aircraft_repo):

    ac1 = AircraftModel(
        name="A2A Comanche 250",
        icao_code="PA24",
        developer="A2A",
        module_name="a2a-comanche",
        simulator="MSFS",
        manufacturer="Piper",
        type=enums.AircraftType.AIRPLANE,
        engine_type=enums.EngineType.PISTON,
        aircraft_category=enums.AircraftCategory.GENERAL_AVIATION
    )
    ac2 = AircraftModel(
        name="IniBuilds A300-600",
        icao_code="A306",
        developer="IniBuilds",
        module_name="inibuilds-a300",
        manufacturer="Airbus",
        simulator="MSFS",
        type=enums.AircraftType.AIRPLANE,
        engine_type=enums.EngineType.JET,
        aircraft_category=enums.AircraftCategory.AIRLINER,
        aircraft_subcategory=enums.AircraftSubCategory.HEAVY
    )

    aircraft_repo.create(ac1)
    aircraft_repo.create(ac2)

    modules = aircraft_repo.get()
    assert len(modules) == 2


def test_get_by_module_and_simulator_returns_matching_model(aircraft_repo):
    saved = aircraft_repo.create(
        _make_aircraft_model(module_name="pmdg-aircraft-737", simulator="MSFS")
    )

    retrieved = aircraft_repo.get_by_module_and_simulator("pmdg-aircraft-737", "MSFS")

    assert retrieved is not None
    assert retrieved.id == saved.id


def test_get_by_module_and_simulator_returns_none_when_not_found(aircraft_repo):
    aircraft_repo.create(
        _make_aircraft_model(module_name="pmdg-aircraft-737", simulator="MSFS")
    )

    assert aircraft_repo.get_by_module_and_simulator("unknown-module", "MSFS") is None
    assert aircraft_repo.get_by_module_and_simulator("pmdg-aircraft-737", "X-PLANE") is None


def test_get_paginates_results(aircraft_repo):
    for index in range(3):
        aircraft_repo.create(
            _make_aircraft_model(name=f"Aircraft {index}", module_name=f"module-{index}")
        )

    first_page = aircraft_repo.get(skip=0, limit=2)
    second_page = aircraft_repo.get(skip=2, limit=2)

    assert len(first_page) == 2
    assert len(second_page) == 1
    assert {model.name for model in first_page + second_page} == {
        "Aircraft 0",
        "Aircraft 1",
        "Aircraft 2",
    }


def test_get_includes_inactive_models_when_requested(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())
    aircraft_repo.disable(saved.id)

    assert aircraft_repo.get() == []
    inactive = aircraft_repo.get(include_inactive=True)
    assert len(inactive) == 1
    assert inactive[0].id == saved.id
    assert inactive[0].is_active is False


def test_update_changes_provided_fields(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    updated = aircraft_repo.update(
        saved.id,
        {"name": "Updated Aircraft", "developer": "New Developer", "notes": "Updated notes"},
    )

    assert updated is not None
    assert updated.id == saved.id
    assert updated.name == "Updated Aircraft"
    assert updated.developer == "New Developer"
    assert updated.notes == "Updated notes"


def test_update_ignores_id_and_unknown_fields(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    updated = aircraft_repo.update(
        saved.id,
        {"id": saved.id + 100, "not_a_real_field": "ignored", "name": "Renamed"},
    )

    assert updated is not None
    assert updated.id == saved.id
    assert updated.name == "Renamed"
    assert not hasattr(updated, "not_a_real_field")


def test_update_returns_none_for_missing_model(aircraft_repo):
    assert aircraft_repo.update(9999, {"name": "Does Not Exist"}) is None


def test_update_notes_updates_notes(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    updated = aircraft_repo.update_notes(saved.id, "Needs a repaint")

    assert updated is not None
    assert updated.notes == "Needs a repaint"


def test_update_notes_returns_none_for_missing_model(aircraft_repo):
    assert aircraft_repo.update_notes(9999, "Notes") is None


def test_update_rating_updates_rating(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    updated = aircraft_repo.update_rating(saved.id, 5)

    assert updated is not None
    assert updated.rating == 5


def test_update_rating_returns_none_for_missing_model(aircraft_repo):
    assert aircraft_repo.update_rating(9999, 5) is None


def test_disable_marks_model_inactive(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    assert aircraft_repo.disable(saved.id) is True

    retrieved = aircraft_repo.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.is_active is False


def test_disable_returns_false_for_missing_model(aircraft_repo):
    assert aircraft_repo.disable(9999) is False


def test_enable_marks_model_active(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())
    aircraft_repo.disable(saved.id)

    assert aircraft_repo.enable(saved.id) is True

    retrieved = aircraft_repo.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.is_active is True


def test_enable_returns_false_for_missing_model(aircraft_repo):
    assert aircraft_repo.enable(9999) is False


def test_delete_removes_model(aircraft_repo):
    saved = aircraft_repo.create(_make_aircraft_model())

    assert aircraft_repo.delete(saved.id) is True
    assert aircraft_repo.get_by_id(saved.id) is None


def test_delete_returns_false_for_missing_model(aircraft_repo):
    assert aircraft_repo.delete(9999) is False