from sqlalchemy.orm import Session
from sim_hangar_manager.database.models import AircraftModel

def create_aircraft_model(db: Session, aircraft_model_data: dict) -> AircraftModel:
    """
    Receives a dictionary with the form data and creates a new AircraftModel in the database.
    """
    db_model = AircraftModel(
        module_name=aircraft_model_data["module_name"],
        name=aircraft_model_data["name"],
        icao_code=aircraft_model_data["icao_code"].upper(),
        developer=aircraft_model_data["developer"],
        type=aircraft_model_data["type"],
        category=aircraft_model_data["category"],
        simulator=aircraft_model_data["simulator"],
        
        # Optional fields mapped safely using dict.get()
        model_data=aircraft_model_data.get("model_data"),
        simulator_compatibility=aircraft_model_data.get("simulator_compatibility"),
        module_type=aircraft_model_data.get("module_type"),
        store=aircraft_model_data.get("store"),
        developer_url=aircraft_model_data.get("developer_url"),
        notes=aircraft_model_data.get("notes"),
        rating=int(aircraft_model_data.get("rating", 0)),
        
        # Metadata file path locations
        module_file_location_1=aircraft_model_data.get("module_file_location_1"),
        module_file_location_2=aircraft_model_data.get("module_file_location_2"),
        model_metadata=aircraft_model_data.get("model_metadata"),
        is_active=aircraft_model_data.get("is_active", True)
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model) # Refreshes to populate the autoincremented ID
    return db_model