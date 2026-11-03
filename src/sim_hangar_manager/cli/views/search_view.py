from typing import Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console

from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService


class SearchAircraftView:

    def __init__(self, aircraft_model_service: AircraftModelService, stdout_console: Console):
        self.aircraft_model_service=aircraft_model_service
        self.console=stdout_console

    def run(self) -> Optional[AircraftModel]:
        self.console.clear()
        self.console.rule("[bold cyan]Search for Modules/Addons[/bold cyan]\n")

        aircraft_modules = self.aircraft_model_service.get_all_aircraft_models(include_inactive=True)

        try:
            if not aircraft_modules:
                self.console.print("[yellow]No Modules Addons registered.[/yellow]\n")
                inquirer.text(message="Press Enter to go back...").execute()
                return None

            # Prepare Options to be visible for search
            choices = [
                Choice(
                    value=ac,
                    name=f"{ac.name} | ICAO: {ac.icao_code or 'N/A'} | Dev: {ac.developer} | Sim: {ac.simulator}",
                )
                for ac in aircraft_modules
            ]

            # InquirerPy Fuzzy for real time dynamic search
            selected_aircraft: AircraftModel = inquirer.fuzzy(
                message="Type to filter (Name, ICAO, Developer, Simulator):",
                choices=choices,
                match_exact=False,
                transformer=lambda result: f"Selected: {result}" if result else "",
            ).execute()

        except(KeyboardInterrupt):
            self.console.clear()
            return

        return selected_aircraft