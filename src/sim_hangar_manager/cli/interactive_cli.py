import sys

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from sim_hangar_manager.cli.forms.create_aircraft_model_form import \
    prompt_add_aircraft_model
from sim_hangar_manager.cli.views.add_aircraft_model_view import \
    AddAircraftModelView
from sim_hangar_manager.cli.views.list_aircraft_model_view import \
    ListAircraftModelView
from sim_hangar_manager.cli.views.scan_view import ScanView
from sim_hangar_manager.cli.views.search_view import SearchAircraftView
from sim_hangar_manager.cli.views.show_aircraft_model_view import \
    AircraftModelDetailView
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService
from sim_hangar_manager.version import APP_VERSION


class InteractiveCLI():

    def __init__(self, 
                 aircraft_model_service: AircraftModelService,
                 scan_view: ScanView,
                 search_aircraft_view: SearchAircraftView,
                 aircraft_model_detail_view: AircraftModelDetailView,
                 add_aircraft_model_view: AddAircraftModelView,
                 list_aircraft_model_view: ListAircraftModelView,
                 stdout_console: Console):
        self.aircraft_model_service=aircraft_model_service
        self.scan_view=scan_view
        self.search_aircraft_view=search_aircraft_view
        self.aircraft_model_detail_view=aircraft_model_detail_view
        self.add_aircraft_model_view=add_aircraft_model_view
        self.list_aircraft_model_view=list_aircraft_model_view
        self.console=stdout_console

    
    def _handle_create_model(self):
        """
        Flow for collecting raw data and inserting a new aircraft module.
        """
        raw_data = prompt_add_aircraft_model()
        if not raw_data:
            return

        try:
            saved_model = self.aircraft_model_service.register_aircraft_model(raw_data)
            self.console.print(
                f"\n[bold green]✔ Successfully registered '{saved_model.name}' (ID: {saved_model.id})[/bold green]\n"
            )
        except Exception as e:
            self.console.print(f"\n[bold red]✖ Failed to save record: {e}[/bold red]\n")


    def _handle_list_models(self):
        """
        Flow for fetching and displaying registered aircraft modules.
        """
        try:
            models = self.aircraft_model_service.get_all_aircraft_models()
            self.list_aircraft_model_view.display_aircraft_models_table(models)
        except Exception as e:
            self.console.print(f"\n[bold red]✖ Error reading Aircraft modules: {e}[/bold red]\n")


    def _handle_module_scan_option(self):
        try:
            self.scan_view.scan_modules()
        except Exception as e:
                print(f"\n[ERROR] Failed to scan modules: {e}\n")

    def _handle_module_search_option(self):
        try:
            selected = self.search_aircraft_view.run()
            if selected:
                self.aircraft_model_detail_view.run(selected)

        except Exception as e:
                print(f"\n[ERROR] {e}\n")

    
    def run(self):
        """
        Main interactive loop for the CLI application.
        """
        while True:
            self.console.clear()

            title = Text("SIM HANGAR MANAGER - CLI", style="bold white", justify="center")
            version = f"v{APP_VERSION}"
            version_text = Text(version, style="dim white", justify="right")
            instructions = Text.from_markup("[bold cyan]Use the arrows [yellow](↑/↓)[/yellow] and press [yellow]Enter[/yellow] to select:[/bold cyan]", justify="left")

            instructions_panel_content = Columns([instructions, version_text], expand=True)

            header_panel = Panel(
                title, 
                box = box.DOUBLE, 
                border_style="bold white", 
                style="on blue",
                padding=(1, 2)
            )

            self.console.print(header_panel)

            self.console.print(Panel(instructions_panel_content, border_style="blue"))

            try:
                custom_style = get_style({
                    "questionmark": "#000000",
                    "pointer": "#00aaff bold",
                    "highlighted": "#ffffff bold",
                    "selected": "#00ff00",
                    "separator": "#cc5500",
                    "instruction": "#888888",
                }, style_override=True)

                choice = inquirer.select(
                    message="",
                    qmark="",
                    amark="",
                    choices=[
                        Choice(value="1", name="1. Add New Aircraft Module"),
                        Choice(value="2", name="2. Scan folder for Aircraft Modules"),
                        Choice(value="3", name="3. List All Aircraft Modules"),
                        Choice(value="4", name="4. Search/Filter Aircraft Modules"),
                        Choice(value=None, name="5. Exit"),
                    ],
                    pointer="❯ ",
                    style=custom_style,
                ).execute()

                if not choice:
                    self.console.clear()
                    self.console.print("\n[bold blue]Closing SIM HANGAR MANAGER... Bye![/bold blue]\n")
                    sys.exit(0)

                if choice.startswith("1"):
                    self._handle_create_model()
                elif choice.startswith("2"):
                    self._handle_module_scan_option()
                elif choice.startswith("3"):
                    self._handle_list_models()
                elif choice.startswith("4"):
                    self._handle_module_search_option()

            except KeyboardInterrupt:
                self.console.print("\n[bold blue]Closing SIM HANGAR MANAGER... Bye![/bold blue]\n")
                sys.exit(0)
