from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.database import enums


def test_create_and_get_aircraft_model(aircraft_repo):

    new_aircraft = AircraftModel(
        name="PMDG 737-700",
        icao_code="B737",
        developer="PMDG",
        module_name="pmdg-aircraft-737",
        simulator="MSFS",
        type=enums.AircraftType.AIRCRAFT,
        category=enums.AircraftCategory.MULTI_JET
    )

    saved_aircraft = aircraft_repo.create(new_aircraft)
    
    assert saved_aircraft.id is not None

    retrieved = aircraft_repo.get_by_id(saved_aircraft.id)
    assert retrieved is not None
    assert retrieved.name == "PMDG 737-700"
    assert retrieved.developer == "PMDG"


def test_list_active_modules_filters_soft_deleted(aircraft_repo):

    ac1 = AircraftModel(
        name="A2A Comanche 250",
        icao_code="PA24",
        developer="A2A",
        module_name="a2a-comanche",
        simulator="MSFS",
        type=enums.AircraftType.AIRCRAFT,
        category=enums.AircraftCategory.SINGLE_PISTON_ENGINE
    )
    ac2 = AircraftModel(
        name="IniBuilds A300-600",
        icao_code="A306",
        developer="IniBuilds",
        module_name="inibuilds-a300",
        simulator="MSFS",
        type=enums.AircraftType.AIRCRAFT,
        category=enums.AircraftCategory.MULTI_JET
    )

    aircraft_repo.create(ac1)
    aircraft_repo.create(ac2)

    modules = aircraft_repo.get()
    assert len(modules) == 2