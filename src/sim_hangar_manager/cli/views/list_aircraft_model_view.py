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

    def show_aircraft_models(self):
        models = self.service.get_all_aircraft_models()
        self.display_aircraft_models_table(models)


    def display_aircraft_models_table(self, models: List[AircraftModel]) -> None:
        """
        Renders a stylized Rich table displaying all active aircraft models.
        """
        self.console.clear()

        if not models:
            self.console.print("\n[bold yellow]No aircraft modules registered in your hangar yet.[/bold yellow]\n")
            inquirer.text(message="Press Enter to Return to main menu...").execute()
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

        inquirer.text(message="Press Enter to Return to main menu...").execute()