from pathlib import Path
from typing import List, Dict, Any
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sim_hangar_manager.service.scanner_service import HangarScannerService
from sim_hangar_manager.service.aircraft_model_service import AircraftModelService
from sim_hangar_manager.exceptions.exceptions import AircraftModuleAlreadyExistsError

console = Console()


class ScanAndImportView:

    def __init__(
        self,
        scanner_service: HangarScannerService,
        aircraft_service: AircraftModelService,
    ):
        self.scanner_service = scanner_service
        self.aircraft_service = aircraft_service

    def run(self):
        console.clear()

        console.rule("[bold cyan]Aircraft module scanner[/bold cyan]")

        # 1. Request Path to scan
        target_path_str = inquirer.text(
            message="Addons/Community folder path to scan (ej. path to  MSFS Community folder):",
            validate=lambda result: Path(result).exists() and Path(result).is_dir(),
            invalid_message="Path is not valid or does not exist.",
        ).execute()

        target_path = Path(target_path_str)

        # 2. Start scanning process with Rich's Spinner component
        detected_modules: List[Dict[str, Any]] = []
        with console.status(
            "[bold cyan]Analyzing folders looking for Aircraft addons...[/bold cyan]",
            spinner="dots",
        ):
            detected_modules = self.scanner_service.scan_path(target_path)

        if not detected_modules:
            console.print(
                Panel(
                    "[bold yellow]No Aircraft modules found on specified folder.[/bold yellow]\n"
                    "[dim]Make sure the folder contains the modules in correct structure.[/dim]",
                    title="Scan complete",
                    style="yellow",
                )
            )
            return

        # 3. Select modules to be registered, using Checkbox of InquirePy
        choices = [
            {
                "name": f"{mod['name']} ({mod['developer']}) — [Folder: {mod['module_name']}]",
                "value": mod,
                "enabled": False,  # Not selected All by default
            }
            for mod in detected_modules
        ]

        console.print(
            f"\n[bold green]✓ Found {len(detected_modules)} valid addons/modules.[/bold green]\n"
        )

        selected_modules = inquirer.checkbox(
            message="Select the modules/addons to be imported to the database (Space to select, Enter/Return to confirm):",
            choices=choices,
            transformer=lambda result: f"{len(result)} modules selected"
        ).execute()

        if not selected_modules:
            console.print("[yellow]Import canceled by the user.[/yellow]")
            return

        # 4. Import modules to DB
        imported_count = 0
        skipped_count = 0

        with console.status(
            "[bold cyan]Saving modules into database...[/bold cyan]",
            spinner="dots",
        ):
            for raw_data in selected_modules:
                try:
                    self.aircraft_service.register_aircraft_model(raw_data)
                    imported_count += 1
                except AircraftModuleAlreadyExistsError:
                    # Duplicate module exists, skipping
                    skipped_count += 1
                except Exception as e:
                    # IF error happens when saving the module
                    skipped_count += 1

        # 5. Render summary table
        self._render_summary_table(imported_count, skipped_count, len(selected_modules))

    def _render_summary_table(self, imported: int, skipped: int, total: int):
        table = Table(title="Import summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Amount", justify="right", style="green")

        table.add_row("Selected for import", str(total))
        table.add_row("Imported successfully", f"[bold green]{imported}[/bold green]")
        if skipped > 0:
            table.add_row("Skipped / Already Registered", f"[bold yellow]{skipped}[/bold yellow]")

        console.print()
        console.print(table)
        console.print("\n[bold green]Process completed successfully![/bold green]\n")
        input("Press Enter to return to the main menu...")