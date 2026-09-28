from sim_hangar_manager.database.models import AircraftModel


class ObjectMapper:

    @staticmethod
    def to_aircraft_model(aircraft_model_data: dict) -> AircraftModel:
        """
        Receives a dictionary with the form data and creates a new AircraftModel object.
        """
        aircraftModel = AircraftModel()

        if "id" in aircraft_model_data:
            aircraftModel.id = aircraft_model_data["id"]
        if "module_name" in aircraft_model_data:
            aircraftModel.module_name = aircraft_model_data["module_name"]
        if "name" in aircraft_model_data:
            aircraftModel.name = aircraft_model_data["name"]
        if "aircraft_name" in aircraft_model_data:
            aircraftModel.aircraft_name = aircraft_model_data["aircraft_name"]
        if "icao_code" in aircraft_model_data:
            aircraftModel.icao_code = aircraft_model_data["icao_code"].upper()
        if "developer" in aircraft_model_data:
            aircraftModel.developer = aircraft_model_data["developer"]
        if "type" in aircraft_model_data:
            aircraftModel.type = aircraft_model_data["type"]
        if "engine_type" in aircraft_model_data:
            aircraftModel.engine_type = aircraft_model_data["engine_type"]
        if "aircraft_category" in aircraft_model_data:
            aircraftModel.aircraft_category = aircraft_model_data["aircraft_category"]
        if "aircraft_subcategory" in aircraft_model_data:
            aircraftModel.aircraft_subcategory = aircraft_model_data["aircraft_subcategory"]
        if "simulator" in aircraft_model_data:
            aircraftModel.simulator = aircraft_model_data["simulator"]

        # Fields that do not need to check for None
        aircraftModel.model_data = aircraft_model_data.get("model_data")
        aircraftModel.simulator_compatibility = aircraft_model_data.get("simulator_compatibility")
        aircraftModel.module_type = aircraft_model_data.get("module_type")
        aircraftModel.store = aircraft_model_data.get("store")
        aircraftModel.developer_url = aircraft_model_data.get("developer_url")
        aircraftModel.notes = aircraft_model_data.get("notes")
        aircraftModel.rating = int(aircraft_model_data.get("rating", 0))
        aircraftModel.module_file_location_1 = aircraft_model_data.get("module_file_location_1")
        aircraftModel.module_file_location_2 = aircraft_model_data.get("module_file_location_2")
        aircraftModel.model_metadata = aircraft_model_data.get("model_metadata")
        aircraftModel.is_active = aircraft_model_data.get("is_active", True)
        aircraftModel.is_installed = aircraft_model_data.get("is_installed", False)
        
        return aircraftModel