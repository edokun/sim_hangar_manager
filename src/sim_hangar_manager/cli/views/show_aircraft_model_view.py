from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sim_hangar_manager.cli.fragments.aircraft_module_fragments import \
    AircraftModelFragments
from sim_hangar_manager.cli.util.utils import aircraft_manufacturers
from sim_hangar_manager.database.enums import (AircraftCategory,
                                               AircraftSubCategory,
                                               AircraftType, EngineType,
                                               ModuleType,
                                               SimulatorCompatibility, Store)
from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService

console = Console()

class AircraftModelDetailView:

    _inquirer_keybindings = {
        "answer":    [{"key": "enter"}],
        "skip":      [{"key": "c-c"}],
        "interrupt": [{"key": "escape"},{"key": "c-d"}],
    }

    _default_help_message = "(Type ? for help)"

    def __init__(self, aircraft_model_service: AircraftModelService):
        self.aircraft_model_service = aircraft_model_service

    def run(self, aircraft: AircraftModel):        
        # Commands for user input and autocomplete
        commands = ['rate', 'notes', 'help', 'back', 'edit', 'disable', 'enable', 'uninstall', 'exit' ]
        completer = WordCompleter(commands, ignore_case=True)

        feedback_message = f" {self._default_help_message}"

        toolbar_style = Style.from_dict({
            "bottom-toolbar": "#ffffff bg:#333333 noreverse",
        })

        while True:
            try:
                console.clear()
                self._render_aircraft_card(aircraft)

                bottom_toolbar = [("class:bottom-toolbar", f"{feedback_message}")]
                user_input = prompt(f"> ", completer=completer, bottom_toolbar=bottom_toolbar, style=toolbar_style, cursor=CursorShape.BLINKING_BLOCK).strip()

                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                match cmd:
                    case "rate":
                        result = self._update_rating(aircraft, args) 
                        feedback_message = f" {self._default_help_message} | {result}"
                    case "notes":
                        result = self._edit_notes(aircraft, args)
                        feedback_message = f" {self._default_help_message} | {result}"
                    case "edit":
                        choice = inquirer.select(
                            message="Select an option:",
                            choices=[
                                Choice(value="1", name="1. ✈️ Edit Aircraft Information"),
                                Choice(value="2", name="2. ⚙️ Edit Developer and Module Data"),
                            ],
                            keybindings=self._inquirer_keybindings,
                        ).execute()

                        result = ""
                        if choice.startswith("1"):
                            result = self._edit_aircraft_information(aircraft)
                        elif choice.startswith("2"):
                            result = self._edit_developer_information(aircraft)

                        feedback_message = f" {self._default_help_message} | {result}"

                    case "disable":
                        result = self._disable(aircraft)
                        feedback_message = f" {self._default_help_message} | {result}"
                    case "enable":
                        result = self._enable(aircraft)
                        feedback_message = f" {self._default_help_message} | {result}"
                    case "uninstall":
                        result = self._uninstall(aircraft)
                        feedback_message = f" {self._default_help_message} | {result}"
                    case "help" | "?":
                        self._show_command_list()
                        feedback_message = " Available commands: back, disable, edit, enable, exit, help, notes, rate, uninstall"
                    case "back" | "exit" | "q":
                        break
                    case _:
                        feedback_message = f" Unknown command: '{cmd}'. Type 'help' or '?' for options."

            except KeyboardInterrupt as e:
                console.clear()
                continue
           
            
    def _render_aircraft_card(self, aircraft: AircraftModel):
        AircraftModelFragments.show_detailed_fragment(aircraft)


    def _show_command_list(self): 
        command_table = Table(show_header=False, box=None)
        command_table.add_column("command", style="yellow")
        command_table.add_column("description", style="white", overflow="fold")

        command_table.add_row("back | exit | q", "Exits this screen and return to menu.")
        command_table.add_row("delete", "Delete the Module/Addon from Database.")
        command_table.add_row("disable", "Disables the Aircraft Module, preventing registering new Aircraft.")
        command_table.add_row("edit", "Edit the Module Data, launches a select prompt for more options.")
        command_table.add_row("enable", "Enable the Aircraft Module.")
        command_table.add_row("help | ?", "Shows this list.")
        command_table.add_row("notes <text>", "Add/Overwrites additional brief note on the module. if just the command is inputted can clear existing notes")
        command_table.add_row("rate <0-5>", "Score the Module/Addon from 0 to 5")
        command_table.add_row("uninstall", "Marks the Addon/Module as not installed, this action does not remove the module from the disk, just updates the record in the database.")

        panel = Panel(command_table,title="Commands:")
        console.print(panel)


    def _edit_aircraft_information(self, aircraft: AircraftModel) -> str | None:
        console.clear()
        self._render_aircraft_card(aircraft)
        
        new_icao = self._ask(
            aircraft, 
            inquirer.text(
                message="ICAO Code (4 characters):",
                default=aircraft.icao_code or "UNKN",
                validate=lambda new_icao: len(new_icao) == 4,
                invalid_message="ICAO code must be 4 characters."
            )
        )

        new_manufacturer = self._ask(
            aircraft,
            inquirer.text(
                message="Aircraft Manufacturer:",
                completer=aircraft_manufacturers,
                multicolumn_complete=True,
                default=aircraft.manufacturer or "",
                filter=lambda val: val.strip() if val and val.strip() else None
            )
        )

        new_aircraft_name = self._ask(
            aircraft,
            inquirer.text(
                message="Aircraft Name:",
                default=aircraft.aircraft_name or "",
                filter=lambda val: val.strip() if val and val.strip() else None
            )
        )

        new_type = self._ask(
            aircraft,
            inquirer.select(
                message="Aircraft Type:",
                choices=[enum.value for enum in AircraftType],
                default=aircraft.type,
            )
        )

        new_engine_type = self._ask(
            aircraft,
            inquirer.select(
                message="Engine Type:",
                choices=[enum.value for enum in EngineType],
                default=aircraft.engine_type,
            )
        )

        new_aircraft_category = self._ask(
            aircraft,
            inquirer.select(
                message="Aircraft Category:",
                choices=[enum.value for enum in AircraftCategory],
                default=aircraft.aircraft_category,
            )
        )

        aircraft_sub_categories_choices = [
            Choice(value=None, name="None / Clear"),
            *[Choice(value=e.value, name=e.value) for e in AircraftSubCategory]
        ]

        new_aircraft_sub_category = self._ask(
            aircraft,
            inquirer.select(
                message="Aircraft Sub-Category:",
                choices=aircraft_sub_categories_choices,
                default=aircraft.aircraft_subcategory,
            )
        )

        updated_data = {
            "icao_code" : new_icao.upper(),
            "manufacturer" : new_manufacturer.upper() if new_manufacturer else None,
            "aircraft_name" : new_aircraft_name,
            "type" : new_type,
            "engine_type" : new_engine_type,
            "aircraft_category" : new_aircraft_category,
            "aircraft_subcategory" : new_aircraft_sub_category,
        }
        
        updated_aircraft = self.aircraft_model_service.update_aircraft_model(
            aircraft.id,
            updated_data
        )
        
        aircraft.icao_code = updated_aircraft.icao_code
        aircraft.manufacturer = updated_aircraft.manufacturer
        aircraft.aircraft_name = updated_aircraft.aircraft_name
        aircraft.type = updated_aircraft.type
        aircraft.engine_type = updated_aircraft.engine_type
        aircraft.aircraft_category = updated_aircraft.aircraft_category
        aircraft.aircraft_subcategory = updated_aircraft.aircraft_subcategory
        return " Aircraft Data Updated."


    def _edit_developer_information(self, aircraft: AircraftModel) -> str | None:
        console.clear()
        self._render_aircraft_card(aircraft)

        mod_version = self._ask(
            aircraft,
            inquirer.text(
                message="Module Version:",
                default=aircraft.version or "1.0.0",
                filter=lambda val: val.strip() if val and val.strip() else None
            )
        )

        developer = self._ask(
            aircraft,
            inquirer.text(
                message="Developer:",
                default=aircraft.developer or "N/A",
                filter=lambda val: val.strip() if val and val.strip() else None
            )
        )
        
        module_type = self._ask(
            aircraft,
            inquirer.select(
                message="Module Type:",
                choices=[enum.value for enum in ModuleType],
                default=aircraft.module_type,
            )
        )

        store = self._ask(
            aircraft,
            inquirer.select(
                message="Store:",
                choices=[enum.value for enum in Store],
                default=aircraft.store,
            )
        )

        simulator_compatibility = self._ask(
            aircraft,
            inquirer.select(
                message="Simulator Compatibility:",
                choices=[enum.value for enum in SimulatorCompatibility],
                default=aircraft.simulator_compatibility,
            )
        )

        updated_data = {
            "version" : mod_version,
            "developer" : developer,
            "module_type" : module_type,
            "store" : store,
            "simulator_compatibility" : simulator_compatibility,
        }
        
        updated_aircraft = self.aircraft_model_service.update_aircraft_model(
            aircraft.id,
            updated_data
        )
        
        aircraft.version = updated_aircraft.version
        aircraft.developer = updated_aircraft.developer
        aircraft.module_type = updated_aircraft.module_type
        aircraft.store = updated_aircraft.store
        aircraft.simulator_compatibility = updated_aircraft.simulator_compatibility
        return " Developer Data Updated."


    def _edit_notes(self, aircraft: AircraftModel, notes: str) -> str | None:
        new_notes = notes if notes else None

        if not notes:
            confirm = prompt('Clear existing notes [y/n]?: ').strip().lower()
            if confirm != "y":
                return None

        updated = self.aircraft_model_service.update_aircraft_model_notes(aircraft.id, new_notes)
        aircraft.notes = updated.notes
        return "Notes Updated."


    def _update_rating(self, aircraft: AircraftModel, rating: str) -> str | None:
        if rating.isdigit() and 0 <= int(rating) <= 5:
            new_rating = int(rating)
            updated = self.aircraft_model_service.update_aircraft_model_rating(
                    aircraft.id,
                    new_rating=new_rating,
            )

            aircraft.rating = updated.rating

            rating_stars = "⭐" * (new_rating)
            return (f"Rating updated to {rating_stars}.")
        
        else:
            return ("Invalid command usage: rate <0-5>.")


    def _disable(self, aircraft: AircraftModel) -> str | None:
        confirm = inquirer.confirm(
            message= "Disable Module?:",
            default=False,
            qmark="",
            long_instruction="Prevents registering new aircraft for this module."
        ).execute()
        
        if not confirm:
            return ""

        self.aircraft_model_service.disable_aircraft_model(aircraft.id)
        aircraft.is_active = False
        return " Aircraft Module Disabled."


    def _enable(self, aircraft: AircraftModel) -> str | None:
        self.aircraft_model_service.enable_aircraft_model(aircraft.id)
        aircraft.is_active = True
        return "Aircraft Module Enabled."


    def _uninstall(self, aircraft: AircraftModel) -> str | None:
        confirm = inquirer.confirm(
            message= "Mark Module as not installed?:",
            default=False,
            qmark="",
            long_instruction="Prevents registering aircraft for this module. You will need to scan for modules again to reinstall"
        ).execute()
        
        if not confirm:
            return ""

        update_data  = {
            "is_active" : False,
            "is_installed" : False,
            "module_file_location_1" : None,
            "module_file_location_2" : None,
        }

        self.aircraft_model_service.update_aircraft_model(aircraft.id, update_data)
        aircraft.is_active = False
        aircraft.is_installed = False
        aircraft.module_file_location_1 = None
        aircraft.module_file_location_2 = None
        return "Aircraft Module Marked as not installed."


    def _ask(self, aircraft: AircraftModel, prompt_builder):
        console.clear()
        self._render_aircraft_card(aircraft)
        return prompt_builder.execute()