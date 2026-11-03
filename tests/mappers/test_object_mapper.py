from sim_hangar_manager.database import enums
from sim_hangar_manager.mappers.object_mapper import ObjectMapper


def test_to_aircraft_model_maps_all_provided_fields():
    data = {
        "id": 7,
        "module_name": "pmdg-aircraft-737",
        "name": "pmdg-aircraft-737",
        "aircraft_name": "Boeing 737-700",
        "icao_code": "b737",
        "developer": "PMDG",
        "type": enums.AircraftType.AIRPLANE,
        "engine_type": enums.EngineType.JET,
        "aircraft_category": enums.AircraftCategory.AIRLINER,
        "aircraft_subcategory": enums.AircraftSubCategory.HEAVY,
        "simulator": "MSFS",
        "model_data": "Some model data",
        "simulator_compatibility": "MSFS 2020",
        "module_type": enums.ModuleType.PAYWARE,
        "store": enums.Store.MARKETPLACE,
        "developer_url": "https://pmdg.com",
        "notes": "Favorite airliner",
        "rating": "5",
        "module_file_location_1": "C:/MSFS/Community/pmdg-737",
        "module_file_location_2": "C:/MSFS/Community/pmdg-737-2",
        "model_metadata": {"version": "3.0"},
        "is_active": False,
        "is_installed": True,
        "version": "3.0.1",
        "manufacturer": "Boeing",
        "engine_count": 2,
        "variant": "700",
        "group": "Airliners",
    }

    model = ObjectMapper.to_aircraft_model(data)

    assert model.id == 7
    assert model.module_name == "pmdg-aircraft-737"
    assert model.name == "pmdg-aircraft-737"
    assert model.aircraft_name == "Boeing 737-700"
    # ICAO codes are normalised to upper case
    assert model.icao_code == "B737"
    assert model.developer == "PMDG"
    assert model.type == enums.AircraftType.AIRPLANE
    assert model.engine_type == enums.EngineType.JET
    assert model.aircraft_category == enums.AircraftCategory.AIRLINER
    assert model.aircraft_subcategory == enums.AircraftSubCategory.HEAVY
    assert model.simulator == "MSFS"
    assert model.model_data == "Some model data"
    assert model.simulator_compatibility == "MSFS 2020"
    assert model.module_type == enums.ModuleType.PAYWARE
    assert model.store == enums.Store.MARKETPLACE
    assert model.developer_url == "https://pmdg.com"
    assert model.notes == "Favorite airliner"
    # Rating strings are converted to integers
    assert model.rating == 5
    assert model.module_file_location_1 == "C:/MSFS/Community/pmdg-737"
    assert model.module_file_location_2 == "C:/MSFS/Community/pmdg-737-2"
    assert model.model_metadata == {"version": "3.0"}
    assert model.is_active is False
    assert model.is_installed is True
    assert model.version == "3.0.1"
    assert model.manufacturer == "Boeing"
    assert model.engine_count == 2
    assert model.variant == "700"
    assert model.group == "Airliners"


def test_to_aircraft_model_applies_defaults_when_fields_are_missing():
    model = ObjectMapper.to_aircraft_model({})

    assert model.id is None
    assert model.module_name is None
    assert model.name is None
    assert model.aircraft_name is None
    assert model.icao_code is None
    assert model.developer is None
    assert model.type is None
    assert model.engine_type is None
    assert model.aircraft_category is None
    assert model.aircraft_subcategory is None
    assert model.simulator is None
    assert model.model_data is None
    assert model.simulator_compatibility is None
    assert model.module_type is None
    assert model.store is None
    assert model.developer_url is None
    assert model.notes is None
    assert model.rating == 0
    assert model.module_file_location_1 is None
    assert model.module_file_location_2 is None
    assert model.model_metadata is None
    assert model.is_active is True
    assert model.is_installed is False
    assert model.version is None
    assert model.manufacturer is None
    assert model.engine_count is None
    assert model.variant is None
    assert model.group is None


def test_to_aircraft_model_only_maps_provided_fields():
    model = ObjectMapper.to_aircraft_model(
        {
            "module_name": "a2a-comanche",
            "name": "A2A Comanche 250",
            "icao_code": "pa24",
        }
    )

    assert model.module_name == "a2a-comanche"
    assert model.name == "A2A Comanche 250"
    assert model.icao_code == "PA24"
    assert model.developer is None
    assert model.simulator is None
    assert model.rating == 0
    assert model.is_active is True
    assert model.is_installed is False
