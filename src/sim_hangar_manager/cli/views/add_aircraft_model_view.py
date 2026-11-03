from InquirerPy import get_style, inquirer
from InquirerPy.validator import EmptyInputValidator
from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from sim_hangar_manager.cli.fragments.aircraft_module_fragments import \
    AircraftModelFragments
from sim_hangar_manager.cli.util.utils import aircraft_manufacturers
from sim_hangar_manager.database.enums import (AircraftCategory,
                                               AircraftSubCategory,
                                               AircraftType, EngineType,
                                               ModuleType, Simulator,
                                               SimulatorCompatibility, Store)
from sim_hangar_manager.exceptions.exceptions import \
    AircraftModuleAlreadyExistsError
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService


class AddAircraftModelView():

    def __init__(
        self,
        aircraft_model_service: AircraftModelService,
        stdout_console: Console, 
    ):
        self.aircraft_model_service = aircraft_model_service
        self.console = stdout_console

    def run(self, confirm_data_saved: bool = False):
        '''
        Launches an interactive form to register an Aircraft Model
        '''
        try:
            self.console.clear()
            self._show_header()
            captured_data = self._capture_form()
            saved_aircraft_model = self.aircraft_model_service.register_aircraft_model(captured_data)
            self.console.print(f"[green]Aircraft module saved successfully.[/green]")
            aircraft_model_detail_view = AircraftModelFragments(self.console)
            aircraft_model_detail_view.show_detailed_fragment(saved_aircraft_model)

            if confirm_data_saved:
                inquirer.text(
                    message="Press any key to go back to menu...",
                    qmark="",
                    amark=""
                ).execute()
                
        except(AircraftModuleAlreadyExistsError):
            self.console.print(f"A model/module with provided data already exists, make sure to specify variant.")
        except(KeyboardInterrupt):
            self.console.clear()
            self.console.print(f"[red]Process cancelled by the user.[/red]")


    def _show_header(self):
        panel = Panel(
            Text("If the Aircraft Module is already installed, it is recommended to use the scan option.", justify="center"),
            title="[bold white on blue] ADD Aircraft Module [/bold white on blue]",
            box=DOUBLE,
            border_style="blue",
            padding=(1, 1),
        )
        
        self.console.print(panel)


    def _capture_form(self) -> Dict[Any,Any]:
        style = get_style(
            {
                "questionmark": "#ff9d00 bold",
                "answermark": "#84e57b bold",
            }, 
            style_override=False
        )

        # --- General Aircraft Data
        self.console.rule("[bold cyan]General Aircraft Data[/bold cyan]")

        aircraft_type = inquirer.select(
            message="Aircraft Type Class:",
            qmark="*",
            amark="🗸",
            style=style,
            choices=[enum.value for enum in AircraftType],
            long_instruction="Press CTRL + C to cancel."
        ).execute()
        
        aircraft_name = inquirer.text(
            message="Aircraft Module name (e.g., 172SP, Baron 58):",
            qmark="*",
            amark="🗸",
            style=style,
            validate=EmptyInputValidator("Aircraft Module name cannot be empty."),
            long_instruction="Name of the Aircraft. Manufacturer field comes next.",
        ).execute()

        manufacturer = inquirer.text(
            message="Aircraft Manufacturer (e.g., Piper, Cessna):",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Type name of the Manufacturer, press tab to select auto complete suggestion.",
            completer=aircraft_manufacturers,
            multicolumn_complete=True,
            default="",
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()

        icao_code = inquirer.text(
            message="Designator ICAO Code (4 characters, e.g., PA24):",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Aircraft ICAO unique designator code. Press enter to skip...",
        ).execute()

        variant = inquirer.text(
            message="Variant (e.g., Bush wheels, Wheel Pants, Cargo cabin):",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Some Models have multiple variants. Press enter to skip...",
        ).execute()

        engine_type = inquirer.select(
            message="Engine Type Category:",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
            choices=[enum.value for enum in EngineType]
        ).execute()

        engine_count = inquirer.number(
            message="Number of Engines:",
            qmark="*",
            amark="🗸",
            style=style,
            default=0,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
        ).execute()

        aircraft_category = inquirer.select(
            message="Aircraft Category:",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
            choices=[enum.value for enum in AircraftCategory]
        ).execute()

        aircraft_subcategory = inquirer.select(
            message="Aircraft Sub-Category:",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
            choices=[enum.value for enum in AircraftSubCategory]
        ).execute()

        # --- Aircraft Model Data
        self.console.rule("[bold cyan]Aircraft Model Data[/bold cyan]")

        simulator = inquirer.select(
            message="Target Simulator:",
            qmark="*",
            amark="🗸",
            style=style,
            choices=[enum.value for enum in Simulator]
        ).execute()

        simulator_compatibility = inquirer.select(
            message="Simulator Version Compatibility:",
            qmark="*",
            amark="🗸",
            style=style,
            choices=[enum.value for enum in SimulatorCompatibility]
        ).execute()

        # --- Data used only for installed module
        is_installed = inquirer.confirm(
            message="Is the Aircraft Model/Module installed?",
            qmark="*",
            amark="🗸",
            style=style,
            long_instruction="MSFS 2024 streams packages, so they can't be read normally",
            default=False,
        ).execute()
        
        folder_location = None
        is_active = False

        name = manufacturer + "_" + aircraft_name
        name = name.replace(" ","_").lower()
        module_name = name + "::" + variant
        version = "1.0.0"
        folder_location = None

        if is_installed:
            module_name = inquirer.text(
                message="Folder/Package Name (e.g., a2a-aircraft-pa24):",
                qmark="*",
                amark="🗸",
                style=style,
                long_instruction="Name of the Folder of the module.",
                validate=EmptyInputValidator("Module name cannot be empty.")
            ).execute()

            name = inquirer.text(
                message="Name of the Aircraft Model (e.g., Piper Comanche 250):",
                qmark="*",
                amark="🗸",
                style=style,
                long_instruction="Usually this is the title field in the manifest.json file.",
                validate=EmptyInputValidator("Name cannot be empty.")
            ).execute()

            version = inquirer.text(
                message="Version of the model:",
                qmark="*",
                amark="🗸",
                style=style,
                default="1.0.0",
                instruction="(Optional)",
                long_instruction="Press enter to skip...",
            ).execute()

            folder_location = inquirer.text(
                message="Local directory path:", 
                qmark="*",
                amark="🗸",
                style=style,
                instruction="(Optional)",
                long_instruction="Press enter to skip...",
            ).execute()


        is_active = inquirer.confirm(
            message="Model is active?",
            qmark="*",
            amark="🗸",
            style=style,
            default=False,
            long_instruction="Active Models can be used to register an Aircraft of given Model/Module",
        ).execute()

        # --- Developer Data
        self.console.rule("[bold cyan]Developer Data[/bold cyan]")

        developer = inquirer.text(
            message="Developer (e.g., A2A Simulations):",
            qmark="*",
            amark="🗸",
            style=style,
            validate=EmptyInputValidator("Developer name cannot be empty.")
        ).execute()

        module_type = inquirer.select(
            message="Type of Module:",
            qmark="*",
            amark="🗸",
            style=style,
            long_instruction="DEFAULT Modules comes with the simulator.",
            default=ModuleType.DEFAULT,
            choices=[enum.value for enum in ModuleType]
        ).execute()

        store = Store.MARKETPLACE
        if module_type != ModuleType.DEFAULT:
            store = inquirer.select(
                message="Store:",
                qmark="*",
                amark="🗸",
                style=style,
                choices=[enum.value for enum in Store]
            ).execute()

        # --- Additional Data
        self.console.rule("[bold cyan]Additional Data[/bold cyan]")

        rating = inquirer.number(
            message="Your personal evaluation rating scale (0 to 5 stars):",
            qmark="*",
            amark="🗸",
            style=style,
            min_allowed=0, 
            max_allowed=5, 
            default=0,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
        ).execute()

        notes = inquirer.text(
            message="Personal notes on the module:",
            qmark="*",
            amark="🗸",
            style=style,
            instruction="(Optional)",
            long_instruction="Press enter to skip...",
        ).execute()

        # Initialize dictionary payload
        answers = {
            "name": name,
            "module_name": module_name,
            "icao_code": icao_code,
            "developer": developer,
            "type": aircraft_type,
            "manufacturer": manufacturer,
            "engine_type": engine_type,
            "aircraft_category": aircraft_category,
            "aircraft_subcategory": aircraft_subcategory,
            "simulator": simulator,
            "simulator_compatibility": simulator_compatibility,
            "module_type": module_type,
            "store": store,
            "variant": variant,
            "aircraft_name": aircraft_name,
            "engine_count": engine_count,
            "version": version,
            "rating": rating,
            "developer_url": None,
            "module_file_location_1": folder_location,
            "model_data": None,
            "notes": notes,
            "is_installed": is_installed,
            "is_active": is_active
        }

        return answers
