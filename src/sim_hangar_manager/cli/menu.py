from sim_hangar_manager.database.connection import SessionLocal
from sim_hangar_manager.database.repository.aircraft_model_repository import AircraftModelRepository
from sim_hangar_manager.cli.forms.create_aircraft_model_form import prompt_add_aircraft_model
from sim_hangar_manager.service.aircraft_model_service import AircraftModelService

def run_create_aircraft_model_flow():
    """
    Orchestrates the creation flow process by linking the UI form, 
    the object mapper framework, and the repository session context.
    """
    # 1. Fetch input dictionary straight from the visual form module
    raw_data = prompt_add_aircraft_model()
    
    if not raw_data:
        return  # Form was aborted or canceled by the user
        
    # 2. Open context database engine session loop
    db = SessionLocal()
    try:
        # 3. DI
        repository = AircraftModelRepository(db)
        service = AircraftModelService(repository)

        # 4. Call Service layer to handle the creation of the aircraft model  
        saved_model = service.create_aircraft_model(raw_data)
        
        print("\n=============================================")
        print(f" SUCCESS: Registered '{saved_model.name}'")
        print(f" Generated Database Record Primary ID: {saved_model.id}")
        print("=============================================\n")
        
    except Exception as e:
        print(f"\n[ERROR] Core execution failed to commit transaction model: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Test execution route mapping directly
    run_create_aircraft_model_flow()