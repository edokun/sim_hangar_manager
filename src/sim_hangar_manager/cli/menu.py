from InquirerPy import prompt
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from sim_hangar_manager.database.connection import SessionLocal
from sim_hangar_manager.database.crud import create_aircraft_model
from sim_hangar_manager.database.models import (
    AircraftCategory, 
    AircraftType, 
    ModuleType, 
    Store, 
    Simulator, 
    SimulatorCompatibility
)

def prompt_add_aircraft_model():
    """
    Displays an interactive terminal wizard to register a new addon/module.
    Includes conditional skipping for optional fields and safe exit handling.
    """
    print("\n=============================================")
    print("      REGISTER NEW AIRCRAFT MODULE / ADDON    ")
    print("  (Press Ctrl+C at any time to cancel & exit) ")
    print("=============================================\n")
    
    try:
        # --- Core Required Fields ---
        name = inquirer.text(
            message="Commercial Aircraft Name (e.g., Piper Comanche 250):",
            validate=EmptyInputValidator("Aircraft name cannot be empty.")
        ).execute()

        module_name = inquirer.text(
            message="Folder/Package Name (e.g., a2a-aircraft-pa24):",
            validate=EmptyInputValidator("Module name is required for folder scanning.")
        ).execute()

        icao_code = inquirer.text(
            message="Designator ICAO Code (4 characters, e.g., PA24):",
            default="UNKN"
        ).execute()

        developer = inquirer.text(
            message="Developer / Publisher Company (e.g., A2A Simulations, PMDG):",
            validate=EmptyInputValidator("Developer name cannot be empty.")
        ).execute()

        # --- Predefined Enum Selections ---
        ac_type = inquirer.select(
            message="Aircraft Type Class:",
            choices=[enum.value for enum in AircraftType]
        ).execute()

        category = inquirer.select(
            message="Engine Plant Category:",
            choices=[enum.value for enum in AircraftCategory]
        ).execute()

        simulator = inquirer.select(
            message="Target Base Simulator Platform:",
            choices=[enum.value for enum in Simulator]
        ).execute()

        simulator_compatibility = inquirer.select(
            message="Simulator Version Compatibility:",
            choices=[enum.value for enum in SimulatorCompatibility]
        ).execute()

        module_type = inquirer.select(
            message="Distribution Framework Strategy:",
            choices=[enum.value for enum in ModuleType]
        ).execute()

        store = inquirer.select(
            message="Acquisition Retail storefront:",
            choices=[enum.value for enum in Store]
        ).execute()

        # --- Dynamic Conditional Skip Trigger ---
        skip_optionals = inquirer.confirm(
            message="Would you like to skip entering all remaining optional details?",
            default=False
        ).execute()

        # Standard defaults dictionary initialization
        answers = {
            "name": name,
            "module_name": module_name,
            "icao_code": icao_code,
            "developer": developer,
            "type": ac_type,
            "category": category,
            "simulator": simulator,
            "simulator_compatibility": simulator_compatibility,
            "module_type": module_type,
            "store": store,
            "version": "1.0.0",
            "rating": 0,
            "developer_url": "",
            "module_file_location_1": "",
            "model_data": "",
            "notes": ""
        }

        # --- Optional Details Fields (Evaluated sequentially based on user selection) ---
        if not skip_optionals:
            answers["version"] = inquirer.text(
                message="Current installation build version layout:",
                default="1.0.0"
            ).execute()

            answers["rating"] = inquirer.number(
                message="Your personal evaluation rating scale (0 to 5 stars):",
                min_allowed=0,
                max_allowed=5,
                default=0
            ).execute()

            answers["developer_url"] = inquirer.text(
                message="Developer Website Reference URL (Optional):",
                default=""
            ).execute()

            answers["module_file_location_1"] = inquirer.text(
                message="Primary local directory path pointer (Optional):",
                default=""
            ).execute()

            answers["model_data"] = inquirer.text(
                message="Performance metadata or limitations specs text (Optional):",
                default=""
            ).execute()

            answers["notes"] = inquirer.text(
                message="Personal cockpit remarks or custom log notes (Optional):",
                default=""
            ).execute()

        # Database session deployment pipeline
        db = SessionLocal()
        try:
            new_model = create_aircraft_model(db, answers)
            print("\n=============================================")
            print(f" SUCCESS: Registered '{new_model.name}'")
            print(f" Generated Database Record Primary ID: {new_model.id}")
            print("=============================================\n")
        except Exception as e:
            print(f"\n[ERROR] Database execution failed to append object context: {e}")
        finally:
            db.close()

    except KeyboardInterrupt:
        # Graceful handling when the user triggers Ctrl+C to cancel operations midway
        print("\n\n[INFO] Operation canceled by the user. Exiting wizard layout without saving data.\n")
        return

if __name__ == "__main__":
    # Allows isolating test routines directly via execution calls
    prompt_add_aircraft_model()