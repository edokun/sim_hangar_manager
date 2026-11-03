from pathlib import Path
from typing import Any, Dict, List

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sim_hangar_manager.exceptions.exceptions import \
    AircraftModuleAlreadyExistsError
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService
from sim_hangar_manager.service.scanner_service import ScannerService


class ImportResults:
    def __init__(self, total_imported: int, total_skipped: int) -> None:
        self.total_imported = total_imported
        self.total_skipped = total_skipped


class ScanView:

    def __init__(
        self,
        scanner_service: ScannerService,
        aircraft_model_service: AircraftModelService,
        stdout_console: Console, 
        log_console: Console | None = None
    ):

        self.scanner_service = scanner_service
        self.aircraft_model_service = aircraft_model_service
        self.console = stdout_console
        self.log_console = log_console


    def scan_modules(self):
        '''
        This method is to be used interactively, will contain many prompts to confirm steps
        '''
        self.console.clear()

        self.console.rule("[bold cyan]Aircraft Module Scanner[/bold cyan]")

        try:
            # 1. Request Path to scan
            target_path = inquirer.text(
                message="Path:",
                qmark="",
                amark="",
                long_instruction="Path to directory where models/modules are installed e.g. MSFS Community folder path. Press CTRL + C to return.",
                validate=lambda result: Path(result).exists() and Path(result).is_dir(),
                invalid_message="Path is not valid or does not exist.",
            ).execute()

            if not target_path:
                self.console.print("[yellow]No Path entered.[/yellow]")
                return

            scan_path = Path(target_path)

            # ask to confirm to skip validation
            skip_validation = False
            skip_validation = inquirer.confirm(
                message="Skip strict aircraft module validation?", 
                qmark="",
                amark="",
                long_instruction="Some aircraft packages are not standard and might not be detected, enabling skip validation, will allow to be scanned.",
                default=False).execute()

            # 2. Start scanning process with Rich's Spinner component
            detected_modules = self._scan_for_modules(scan_path,skip_validation=skip_validation)

            # 3. Select modules to be registered, using Checkbox of InquirePy
            selected_modules = self._select_modules_to_add(detected_modules)

            if not selected_modules:
                self.console.print("[yellow]No Modules registered.[/yellow]")
                return


            # ask to confirm to overwrite
            dry_run = inquirer.confirm(
                message="Do you want to skip saving data?", 
                amark="",
                qmark="",
                default=False).execute()

            
            import_results = None
            if not dry_run:
                # ask to confirm to overwrite
                overwrite = inquirer.confirm(
                    message="Do you want to overwrite existing records?", 
                    amark="",
                    qmark="",
                    default=False).execute()

                # 4. Import modules to DB
                import_results = self._save_modules(selected_modules, overwrite)

            else:
                import_results = ImportResults(total_imported=0, total_skipped=len(selected_modules))

        except(KeyboardInterrupt):
            self.console.clear()
            return

        # 5. Render summary table
        self._render_summary_table(import_results, len(detected_modules), len(selected_modules), True)


    def scan_modules_cli(self, 
                         scan_directory: Path, 
                         ask_confirmation: bool = False,
                         skip_validation: bool = False,
                         overwrite_aircraft_module: bool = False,
                         dry_run: bool = False):

        self.console.clear()
        
        if not scan_directory:
            self.console.print("[yellow]No Path entered.[/yellow]")
            return

        self.console.print(f"[cyan]Scanning Path:[/cyan] {scan_directory}")
        self._debug(f"Scanning Path: {scan_directory}")

        # 1. Start scanning process with Rich's Spinner component
        detected_modules = self._scan_for_modules(scan_directory, skip_validation)

        if not detected_modules:
            self.console.print("[yellow]No Modules Found.[/yellow]")
            return

        selected_modules = detected_modules
        # 2. Select modules to be registered, using Checkbox of InquirePy
        if ask_confirmation:
            selected_modules = self._select_modules_to_add(detected_modules,True)

        if not selected_modules:
            self.console.print("[yellow]No Modules Selected.[/yellow]")
            return

        import_results = None
        if not dry_run:
            # 3. Import modules to DB
            import_results = self._save_modules(selected_modules, overwrite_module=overwrite_aircraft_module)

        else:
            self._debug(f"Skipping saving modules to DB because dry run flag was provided")
            import_results = ImportResults(total_imported=0, total_skipped=len(selected_modules))
        
        # 4. Render summary table
        self._render_summary_table(import_results, 
                                   len(detected_modules), 
                                   len(selected_modules), 
                                   False)


    def _scan_for_modules(self, scan_directory: Path, skip_validation: bool = False) -> List[Dict[str, Any]]:
        if not self._is_valid_path(scan_directory):
            self.console.print("[yellow]Path not valid or does not exist.[/yellow]")
            return
                
        detected_modules: List[Dict[str, Any]] = []
        with self.console.status(
            "[bold cyan]Analyzing folders looking for Aircraft addons...[/bold cyan]",
            spinner="dots",
        ):
            detected_modules = self.scanner_service.scan_path(scan_directory, skip_validation)

        if not detected_modules:
            self.console.print(
                Panel(
                    "[bold yellow]No Aircraft modules found on specified folder.[/bold yellow]\n"
                    "[dim]Make sure the folder contains the modules in correct structure.[/dim]",
                    style="yellow",
                )
            )
            return

        return detected_modules


    def _select_modules_to_add(self, detected_modules: List[Dict[str, Any]], all_selected: bool = False) -> List[Dict[str, Any]]:
        choices = [
            {
                "name": f"{mod['name']} {mod['variant']} ({mod['developer']}) — [Folder: {mod['module_name']}]",
                "value": mod,
                "enabled": all_selected,
            }
            for mod in detected_modules
        ]
        
        self.console.print(
            f"\n[bold green]✓ Found {len(detected_modules)} Modules.[/bold green]\n"
        )

        selected_modules = inquirer.checkbox(
            message="Select the modules to be imported:",
            long_instruction="Space to select, Enter/Return to confirm, CTRL + R to select/deselect all",
            qmark="",
            amark="",
            show_cursor=False,
            border=True,
            choices=choices,
            transformer=lambda result: f"{len(result)} modules selected"
        ).execute()

        return selected_modules


    def _save_modules(self, aircraft_modules: List[Dict[str, Any]], overwrite_module: bool = False) -> ImportResults:
        imported_count = 0
        skipped_count = 0

        with self.console.status(
            "[bold cyan]Saving modules into database...[/bold cyan]",
            spinner="dots",
        ):
            for raw_data in aircraft_modules:
                try:
                    self.aircraft_model_service.register_aircraft_model(raw_data, overwrite_module)
                    imported_count += 1
                except (AircraftModuleAlreadyExistsError) as e:
                    # Duplicate module exists, or other error, skipping
                    skipped_count += 1

        return ImportResults(total_imported = imported_count, total_skipped = skipped_count)


    def _render_summary_table(self, importedResults: ImportResults, total: int, selected: int, askForConfirm: bool = True):
        table = Table(title="[bold cyan]Import summary[/bold cyan]", show_header=False, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Amount", justify="right", style="green")

        table.add_row("Modules found for import", f"[green]{str(total)}[/green]")
        table.add_row("Selected to import", f"[green]{str(selected)}[/green]")
        table.add_row("Imported successfully", f"[green]{importedResults.total_imported}[/green]")
        table.add_row("Skipped/Already Registered", f"[yellow]{importedResults.total_skipped}[/yellow]")

        self.console.print()
        self.console.print(table)
        self.console.print("\n[bold green]Process completed.[/bold green]\n")

        self._debug(f"Totals:")
        self._debug(f"Modules To be imported: {str(total)}")
        self._debug(f"Modules Imported: {str(importedResults.total_imported)}")
        self._debug(f"Modules Skipped: {str(importedResults.total_skipped)}")
        
        if askForConfirm:
            input("Press Enter to return.")


    def _debug(self, message: str):
        if self.log_console:
            self.log_console.print(f"[ScanView] {message}")


    def _is_valid_path(self, target_path: Path) -> bool: 
        if not target_path.exists():
            error_str = f"The path '{target_path}' does not exist."
            self._debug(error_str)
            return False

        return True