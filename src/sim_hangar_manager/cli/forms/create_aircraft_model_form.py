from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from sim_hangar_manager.database.enums import (
    AircraftCategory, 
    AircraftType, 
    ModuleType, 
    Store, 
    Simulator, 
    SimulatorCompatibility
)

def prompt_add_aircraft_model() -> getattr:
    """
    Displays an interactive terminal wizard to gather raw aircraft configuration inputs.
    Does not interact with database engines or sessions directly.
    """
    print("\n=============================================")
    print("      REGISTER NEW AIRCRAFT MODULE / ADDON    ")
    print("  (Press Ctrl+C at any time to cancel & exit) ")
    print("=============================================\n")
    
    try:
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
            message="Acquisition Store:",
            choices=[enum.value for enum in Store]
        ).execute()

        skip_optionals = inquirer.confirm(
            message="Would you like to skip entering all remaining optional details?",
            default=False
        ).execute()

        # Initialize dictionary payload
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

        if not skip_optionals:
            answers["version"] = inquirer.text(message="Current installation build version layout:", default="1.0.0").execute()
            answers["rating"] = inquirer.number(message="Your personal evaluation rating scale (0 to 5 stars):", min_allowed=0, max_allowed=5, default=0).execute()
            answers["developer_url"] = inquirer.text(message="Developer Website Reference URL (Optional):", default="").execute()
            answers["module_file_location_1"] = inquirer.text(message="Primary local directory path pointer (Optional):", default="").execute()
            answers["module_file_location_2"] = inquirer.text(message="Secondary local directory path pointer (Optional):", default="").execute()
            answers["model_data"] = inquirer.text(message="Performance metadata or limitations specs text (Optional):", default="").execute()
            answers["notes"] = inquirer.text(message="Personal notes on the module (Optional):", default="").execute()

        return answers

    except KeyboardInterrupt:
        print("\n\n[INFO] Operation canceled by the user.\n")
        return None