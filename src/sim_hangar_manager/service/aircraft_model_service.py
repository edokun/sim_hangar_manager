from sim_hangar_manager.database.repository import AircraftModelRepository
from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.mappers.object_mapper import ObjectMapper


class AircraftModelService:
    """
    Service class for managing aircraft models.
    """
    def __init__(self, repository: AircraftModelRepository):
        self.repository = repository

    def create_aircraft_model(self, raw_data: dict) -> AircraftModel:
        """
        Create a new aircraft model.
        """
        aircraft_entity = ObjectMapper.to_aircraft_model(raw_data)
        return self.repository.create(aircraft_entity)
    
    def get_all_aircraft_models(self, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> list[AircraftModel]:
        """
        Retrieve all aircraft models with optional pagination and filtering for inactive models.
        """
        return self.repository.get(skip=skip, limit=limit, include_inactive=include_inactive)
    
    def get_aircraft_model_by_id(self, model_id: int) -> AircraftModel:
        """
        Retrieve an aircraft model by its ID.
        """
        return self.repository.get_by_id(model_id)

    def update_aircraft_model(self, model_id: int, updated_data: dict) -> AircraftModel:
        """
        Update an existing aircraft model.
        """
        return self.repository.update(model_id, updated_data)
    
    def disable_aircraft_model(self, model_id: int) -> None:
        """
        Disable an aircraft model by its ID.
        """
        self.repository.disable(model_id)

    def enable_aircraft_model(self, model_id: int) -> None:
        """
        Enable an aircraft model by its ID.
        """
        self.repository.enable(model_id)
    
    def update_aircraft_model_notes(self, model_id: int, new_notes: str) -> AircraftModel:
        """
        Update the notes of a specific aircraft model.
        """
        return self.repository.update_notes(model_id, new_notes)
    
    def update_aircraft_model_rating(self, model_id: int, new_rating: int) -> AircraftModel:
        """
        Update the rating of a specific aircraft model.
        """
        return self.repository.update_rating(model_id, new_rating)