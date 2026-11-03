from InquirerPy import get_style, inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.styles import Style
from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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


class AircraftModelDetailView:

    _inquirer_keybindings = {
        "answer":    [{"key": "enter"}],
        "skip":      [{"key": "c-c"}],
        "interrupt": [{"key": "escape"},{"key": "c-d"}],
    }

    _default_help_message = "Type ? for list of commands"

    def __init__(self, 
                 aircraft_model_service: AircraftModelService,
                 stdout_console: Console):
        self.aircraft_model_service = aircraft_model_service
        self.console = stdout_console

        self.form_style = get_style(
            {
                "questionmark": "#ff9d00 bold",
                "answermark": "#84e57b bold",
            }, 
            style_override=False
        )

    def run(self, aircraft: AircraftModel):        
        # Commands for user input and autocomplete
        commands = ['rate', 'notes', 'help', 'edit', 'disable', 'enable', 'uninstall', 'exit', 'delete' ]
        completer = WordCompleter(commands, ignore_case=True)

        feedback_message = f" {self._default_help_message}"

        toolbar_style = Style.from_dict({
            "bottom-toolbar": "#ffffff bg:#333333 noreverse",
        })

        self.console.clear()
        self._render_aircraft_card(aircraft)

        while True:
            try:
                bottom_toolbar = [("class:bottom-toolbar", f"{feedback_message}")]
                user_input = prompt(f"command -> ", completer=completer, bottom_toolbar=bottom_toolbar, style=toolbar_style, cursor=CursorShape.BLINKING_BLOCK).strip()

                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                match cmd:
                    case "rate":
                        result = self._update_rating(aircraft, args) 
                        feedback_message = f" {result}"
                    case "notes":
                        result = self._edit_notes(aircraft, args)
                        feedback_message = f" {result}"
                    case "edit":
                        choice = inquirer.select(
                            message="Select an option:",
                            choices=[
                                Choice(value="1", name="1. Edit Aircraft Information"),
                                Choice(value="2", name="2. Edit Developer and Module Data"),
                                Choice(value="3", name="3. Change Module Name"),
                            ],
                            qmark="",
                            amark="",
                            keybindings=self._inquirer_keybindings,
                        ).execute()

                        result = ""
                        if choice.startswith("1"):
                            result = self._edit_aircraft_information(aircraft)
                        elif choice.startswith("2"):
                            result = self._edit_developer_information(aircraft)
                        elif choice.startswith("3"):
                            result = self._edit_module_name(aircraft)

                        feedback_message = f" {result}"

                    case "delete":
                        result = self._delete(aircraft)
                        if result == "deleted":
                            break
                        self.console.clear()
                        self._render_aircraft_card(aircraft)
                    case "disable":
                        result = self._disable(aircraft)
                        feedback_message = f" {result}"
                    case "enable":
                        result = self._enable(aircraft)
                        feedback_message = f" {result}"
                    case "uninstall":
                        result = self._uninstall(aircraft)
                        feedback_message = f" {result}"
                    case "help" | "?":
                        self._show_command_list()
                        feedback_message = " Available commands: delete, disable, edit, enable, exit, help, notes, rate, uninstall"
                    case "exit":
                        break
                    case _:
                        feedback_message = f" Unknown command: '{cmd}'. Type 'help' or '?' for options."

            except KeyboardInterrupt as e:
                self.console.clear()
                self._render_aircraft_card(aircraft)
                #return
           
            
    def _render_aircraft_card(self, aircraft: AircraftModel):
        show_aircraft_model_card = AircraftModelFragments(stdout_console=self.console)
        show_aircraft_model_card.show_detailed_fragment(aircraft)


    def _show_command_list(self): 
        command_table = Table(show_header=False, box=None)
        command_table.add_column("command", style="yellow")
        command_table.add_column("description", style="white", overflow="fold")

        command_table.add_row("delete", "Delete the Aircraft Model from Database.")
        command_table.add_row("disable", "Disables the Aircraft Model, preventing registering new Aircraft.")
        command_table.add_row("edit", "Edit the Aircraft Model Data.")
        command_table.add_row("enable", "Enables the Aircraft Model.")
        command_table.add_row("exit", "Exits this screen and return to menu.")
        command_table.add_row("help | ?", "Shows this list.")
        command_table.add_row("notes <text>", "Overwrites brief notes on the Aircraft Model. if just the command is typed, it can clear existing notes")
        command_table.add_row("rate <0-5>", "Score the Aircraft Model from 0 to 5")
        command_table.add_row("uninstall", "Marks the Aircraft Model as not installed, this action does not remove the module from the disk, just updates the record in the database.")

        panel = Panel(command_table,title="Commands:")
        self.console.print(panel)


    def _edit_aircraft_information(self, aircraft: AircraftModel) -> str | None:
        new_icao = inquirer.text(
            message="ICAO Code (3 to 4 characters):",
            default=aircraft.icao_code or "UNKN",
            style=self.form_style,
            qmark="*",
            amark="🗸",
            validate=lambda new_icao: len(new_icao) >= 3 and len(new_icao) <= 4,
            invalid_message="ICAO code must be 3 or 4 characters."
        ).execute()

        new_manufacturer = inquirer.text(
            message="Aircraft Manufacturer:",
            completer=aircraft_manufacturers,
            multicolumn_complete=True,
            default=aircraft.manufacturer or "",
            style=self.form_style,
            qmark="*",
            amark="🗸",
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()

        new_aircraft_name = inquirer.text(
            message="Aircraft Name:",
            default=aircraft.aircraft_name or "",
            style=self.form_style,
            qmark="*",
            amark="🗸",
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()

        new_type = inquirer.select(
            message="Aircraft Type:",
            choices=[enum.value for enum in AircraftType],
            default=aircraft.type,
            qmark="*",
            amark="🗸",
            style=self.form_style,
        ).execute()

        new_engine_type = inquirer.select(
            message="Engine Type:",
            choices=[enum.value for enum in EngineType],
            default=aircraft.engine_type,
            qmark="*",
            amark="🗸",
            style=self.form_style,
        ).execute()

        new_engine_count = inquirer.number(
            message="Number of Engines:",
            qmark="*",
            amark="🗸",
            style=self.form_style,
            default=aircraft.engine_count or 0,
        ).execute()

        new_aircraft_category = inquirer.select(
            message="Aircraft Category:",
            choices=[enum.value for enum in AircraftCategory],
            default=aircraft.aircraft_category,
            style=self.form_style,
            qmark="*",
            amark="🗸",
        ).execute()

        aircraft_sub_categories_choices = [
            Choice(value=None, name="None / Clear"),
            *[Choice(value=e.value, name=e.value) for e in AircraftSubCategory]
        ]

        new_aircraft_sub_category = inquirer.select(
            message="Aircraft Sub-Category:",
            choices=aircraft_sub_categories_choices,
            default=aircraft.aircraft_subcategory,
            style=self.form_style,
            qmark="*",
            amark="🗸",
        ).execute()

        new_variant = inquirer.text(
            message="Variant:",
            default=aircraft.variant or "",
            style=self.form_style,
            qmark="*",
            amark="🗸",
            long_instruction="Specify Model variant e.g., Bush wheels, Wheel Pants, Cargo cabin, etc.",
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()

        updated_data = {
            "icao_code" : new_icao.upper(),
            "manufacturer" : new_manufacturer.upper() if new_manufacturer else None,
            "aircraft_name" : new_aircraft_name,
            "type" : new_type,
            "engine_type" : new_engine_type,
            "aircraft_category" : new_aircraft_category,
            "aircraft_subcategory" : new_aircraft_sub_category,
            "engine_count": new_engine_count,
            "variant": new_variant if new_variant else None
        }
        
        updated_aircraft = self.aircraft_model_service.update_aircraft_model(
            aircraft.id,
            updated_data
        )
        
        self.console.clear()
        self._render_aircraft_card(updated_aircraft)

        return " Aircraft Data Updated."


    def _edit_developer_information(self, aircraft: AircraftModel) -> str | None:
        #self.console.clear()
        #self._render_aircraft_card(aircraft)

        mod_version = inquirer.text(
            message="Module Version:",
            default=aircraft.version or "1.0.0",
            qmark="*",
            amark="🗸",
            style=self.form_style,
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()

        developer = inquirer.text(
            message="Developer:",
            default=aircraft.developer or "N/A",
            qmark="*",
            amark="🗸",
            style=self.form_style,
            filter=lambda val: val.strip() if val and val.strip() else None
        ).execute()
        
        module_type = inquirer.select(
            message="Module Type:",
            choices=[enum.value for enum in ModuleType],
            default=aircraft.module_type,
            qmark="*",
            amark="🗸",
            style=self.form_style,
        ).execute()

        store = inquirer.select(
            message="Store:",
            choices=[enum.value for enum in Store],
            default=aircraft.store,
            qmark="*",
            amark="🗸",
            style=self.form_style,
        ).execute()

        simulator_compatibility = inquirer.select(
            message="Simulator Compatibility:",
            choices=[enum.value for enum in SimulatorCompatibility],
            default=aircraft.simulator_compatibility,
            qmark="*",
            amark="🗸",
            style=self.form_style,
        ).execute()

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
        
        #aircraft.version = updated_aircraft.version
        #aircraft.developer = updated_aircraft.developer
        #aircraft.module_type = updated_aircraft.module_type
        #aircraft.store = updated_aircraft.store
        #aircraft.simulator_compatibility = updated_aircraft.simulator_compatibility

        self.console.clear()
        self._render_aircraft_card(updated_aircraft)

        return " Developer Data Updated."


    def _edit_module_name(self, aircraft: AircraftModel) -> str | None:
            self.console.clear()
            self._show_header(message="Module name should be unique.")

            try:
                name = inquirer.text(
                    message="Name of the Aircraft Model (e.g., Piper Comanche 250):",
                    qmark="*",
                    amark="🗸",
                    default=aircraft.name,
                    style=self.form_style,
                    long_instruction="Usually this is the title field in the manifest.json file.",
                    validate=EmptyInputValidator("Name cannot be empty.")
                ).execute()
    
                updated_data = {
                    "name" : name,
                }
            
                updated_aircraft = self.aircraft_model_service.update_aircraft_model(
                    aircraft.id,
                    updated_data
                )
            
                self.console.clear()
                self._render_aircraft_card(updated_aircraft)
                return " Model Name updated."

            except(KeyboardInterrupt):
                self.console.clear()
                self._render_aircraft_card(aircraft)
                return "Operation cancelled."


    def _edit_notes(self, aircraft: AircraftModel, notes: str) -> str | None:
        new_notes = notes if notes else None

        if not notes:
            confirm = prompt('Clear existing notes [y/n]?: ').strip().lower()
            if confirm != "y":
                return None

        updated_aircraft = self.aircraft_model_service.update_aircraft_model_notes(aircraft.id, new_notes)
        #aircraft.notes = updated_aircraft.notes

        self.console.clear()
        self._render_aircraft_card(updated_aircraft)

        return " Notes Updated."


    def _update_rating(self, aircraft: AircraftModel, rating: str) -> str | None:
        if rating.isdigit() and 0 <= int(rating) <= 5:
            new_rating = int(rating)
            updated_aircraft = self.aircraft_model_service.update_aircraft_model_rating(
                    aircraft.id,
                    new_rating=new_rating,
            )

            self.console.clear()
            self._render_aircraft_card(updated_aircraft)

            return " Rating updated."
        
        else:
            return " Invalid command usage: rate <0-5>."


    def _disable(self, aircraft: AircraftModel) -> str | None:
        confirm = inquirer.confirm(
            message= "Disable Module?:",
            default=False,
            style=self.form_style,
            qmark="*",
            amark="🗸",
            long_instruction="Prevents registering new aircraft for this module."
        ).execute()
        
        if not confirm:
            return ""

        self.aircraft_model_service.disable_aircraft_model(aircraft.id)
        aircraft.is_active = False
        self.console.clear()
        self._render_aircraft_card(aircraft)

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
        }

        self.aircraft_model_service.update_aircraft_model(aircraft.id, update_data)
        aircraft.is_active = False
        aircraft.is_installed = False
        aircraft.module_file_location_1 = None
        return "Aircraft Module Marked as not installed."


    def _delete(self, aircraft: AircraftModel) -> str | None:
        self.console.clear()
        self._render_aircraft_card(aircraft)
        self._show_header(message="This WILL REMOVE the record from the database and will delete all Aircraft associated with this record.")
        
        confirm = inquirer.confirm(
            message= f"Delete Model {aircraft.id} - {aircraft.name}?",
            default=False,
            style=self.form_style,
            qmark="*",
            amark="🗸",
            long_instruction="This operation cannot be undone."
        ).execute()
                
        if not confirm:
            return "cancel"

        self.aircraft_model_service.delete(aircraft.id)
        self.console.clear()
        return "deleted"


    def _show_header(self, message: str):
        panel = Panel(
            Text(message, justify="center"),
            box=DOUBLE,
            border_style="blue",
            padding=(1, 1),
        )
        
        self.console.print(panel)