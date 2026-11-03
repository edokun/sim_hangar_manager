from typing import List

from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table

from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService


class ListAircraftModelView():

    def __init__(self, 
                 aircraft_model_service: AircraftModelService,
                 stdout_console: Console ):
        self.service = aircraft_model_service
        self.console = stdout_console

    def list_aircraft_models_interactive(self):
        '''
        This method is to be called from interactive cli, 
        it asks for confirmation to return to menu.
        '''
        models = self.service.get_all_aircraft_models()
        self.console.clear()
        self._display_aircraft_models_table(models)


    def list_aircraft_models(self):
        models = self.service.get_all_aircraft_models()
        self._render_results_table(models)


    def _render_results_table(self, models: List[AircraftModel]) -> None:
        '''
        Renders a simple table with data
        '''
        if not models or len(models) == 0:
            self.console.print("[bold yellow]No aircraft modules registered.[/bold yellow]")
            return

        table = Table(
                    show_header=True,
                    header_style="bold",
                    border_style="dim"
                )
        
        # Define layout table headers
        table.add_column("ID", style="bold white", width=4, no_wrap=True)
        table.add_column("Manufacturer", style="bold white")
        table.add_column("Name", style="bold white")
        table.add_column("ICAO", justify="center", style="bold white")
        table.add_column("Variant", style="bold white")
        table.add_column("Developer", style="bold white")
        table.add_column("Type", style="bold white")
        table.add_column("Simulator", style="bold white")
        table.add_column("Rating", justify="center", width=7)

        for model in models:
            # Convert numeric rating into star icons for visual flare
            stars = "★" * model.rating if model.rating > 0 else "-"
            
            table.add_row(
                str(model.id),
                model.manufacturer if model.manufacturer else "-",
                model.aircraft_name if model.aircraft_name else model.name,
                model.icao_code,
                model.variant,
                model.developer,
                model.type,
                model.simulator,
                f"[bold]{stars}[/bold]"
            )

        self.console.print(table)
        self.console.print(f"Total registered Aircraft models: {len(models)}\n")


    def _display_aircraft_models_table(self, models: List[AircraftModel]) -> None:
        """
        Renders a stylized Rich table displaying aircraft models.
        """
        if not models or len(models) == 0:
            self.console.print("[bold yellow]No aircraft modules registered.[/bold yellow]")
            inquirer.text(message="Press Enter to return to main menu...", qmark="", amark="").execute()
            return

        table = Table(
            title="[bold cyan]REGISTERED AIRCRAFT MODULES[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="dim"
        )

        # Define layout table headers
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Name", style="bold white")
        table.add_column("ICAO", justify="center", style="yellow")
        table.add_column("Developer", style="green")
        table.add_column("Type", style="dim")
        table.add_column("Simulator", style="blue")
        table.add_column("Rating", justify="center")

        for model in models:
            # Convert numeric rating into star icons for visual flare
            stars = "★" * model.rating if model.rating > 0 else "-"
            
            table.add_row(
                str(model.id),
                model.name,
                model.icao_code,
                model.developer,
                model.type,
                model.simulator,
                f"[bold gold1]{stars}[/bold gold1]"
            )

        self.console.print("\n")
        self.console.print(table)
        self.console.print(f"[dim]Total registered modules: {len(models)}[/dim]\n")

        inquirer.text(message="Press Enter to return to main menu...", qmark="", amark="").execute()

        