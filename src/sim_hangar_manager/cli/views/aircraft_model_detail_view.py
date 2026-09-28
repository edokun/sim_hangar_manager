from InquirerPy import inquirer
#from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
from rich.box import DOUBLE
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService

console = Console()


class AircraftModelDetailView:

    def __init__(self, aircraft_service: AircraftModelService):
        self.aircraft_service = aircraft_service

    def run(self, aircraft: AircraftModel):
        """Shows Aircraft Model information and actions menu."""
        while True:
            console.clear()
            self._render_aircraft_card(aircraft)


            custom_style = get_style({
                "questionmark": "#000000",
                "pointer": "#00aaff bold",
                "highlighted": "#ffffff bold",
                "selected": "#00ff00",
                "separator": "#cc5500",
                "instruction": "#888888",
            }, style_override=True)

            action = inquirer.select(
                message="Select an action:",
                qmark="",
                amark="",
                choices=[
                    {"name": "✏️  Edit Aircraft Model Details", "value": "edit"},
                    {"name": "📝  Edit Notes and Rating/Score", "value": "notes"},
                    {"name": "❌  Disable Aircraft Module", "value": "disable"},
                    {"name": "✏️  Mark Aircraft Module as Not installed", "value": "uninstall"},
                    {"name": "📝  Duplicate Module", "value": "duplicate"},
                    {"name": "🗑️  Delete Aircraft Module", "value": "delete"},
                    {"name": "⬅️  Return to Menu", "value": "back"},
                ],
                pointer="❯ ",
                style=custom_style,
            ).execute()

            if action == "edit":
                aircraft = self._edit_technical_data(aircraft)
            elif action == "notes":
                aircraft = self._edit_notes_and_rating(aircraft)
            elif action == "disable":
                self._show_file_paths(aircraft)
            elif action == "uninstall":
                aircraft = self._edit_notes_and_rating(aircraft)
            elif action == "duplicate":
                aircraft = self._edit_notes_and_rating(aircraft)
            elif action == "delete":
                aircraft = self._edit_notes_and_rating(aircraft)
            elif action == "back":
                break        

    def _render_aircraft_card(self, aircraft: AircraftModel):
        """Renders a technical card retro styled."""
        console.rule(f"[bold cyan] ✈️  Module/Addon: {aircraft.name.upper()} [/bold cyan]\n")

        # 1. Header Table (Only Id and flags)
        id_table = Table(
            show_header=False,
            box=None,
            padding=(0,2,1,2),
            expand=True,
        )

        id_table.add_column("Value1", style="bold yellow", justify="left", width=15)
        id_table.add_column("Value2", style="white", justify="right")
        id_table.add_column("Value3", style="white", justify="right")
        id_table.add_column("Value4", style="white", justify="right")

        id_table.add_row(f"ID: {str(aircraft.id)}", 
                         "Active: ✅" if (aircraft.is_active) else "Active: ❌",
                         "Installed: ✅" if (aircraft.is_installed) else "Installed: ❌",
                         f"Simulator: [magenta]{aircraft.simulator}[/magenta]"
                        )

        # 2. Aircraft Data Table
        aircraft_data_table = Table(show_header=False, box=None, padding=(0, 2))
        aircraft_data_table.add_column("Field", style="bold yellow")
        aircraft_data_table.add_column("Value", style="white")

        aircraft_data_table.add_row("ICAO Code:", aircraft.icao_code or "[red]UNKN[/red]")
        aircraft_data_table.add_row("Manufacturer:", aircraft.manufacturer or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Aircraft name:", aircraft.aircraft_name or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Type:", aircraft.type or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Engine Type:", aircraft.engine_type or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Aircraft Category:", aircraft.aircraft_category or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.aircraft_subcategory:
            aircraft_data_table.add_row("Aircraft Sub-Category:", aircraft.aircraft_subcategory)
        # DO NOT RENDER IF None
        if aircraft.model_data:
            aircraft_data_table.add_row("Model Data:", aircraft.model_data)

        # 3. Module Version, Rating and Developer Information
        rating_stars = "⭐" * (aircraft.rating or 0) if aircraft.rating else "[dim]-[/dim]"

        developer_info_table = Table(show_header=False, box=None, padding=(0, 2))
        developer_info_table.add_column("Field", style="bold yellow")
        developer_info_table.add_column("Value", style="white")

        developer_info_table.add_row("Mod Version:", aircraft.version or "1.0.0")
        developer_info_table.add_row("Simulator Compatibility", aircraft.simulator_compatibility or f"[dim]N/A[/dim]")
        developer_info_table.add_row("Developer:", aircraft.developer)
        developer_info_table.add_row("Module Type:", aircraft.module_type or f"[dim]N/A[/dim]")
        developer_info_table.add_row("Store:", aircraft.store or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.developer_url:
            developer_info_table.add_row("developer_url:", aircraft.developer_url)

        developer_info_table.add_row("Rating/Score:", rating_stars)

        # DO NOT RENDER IF None
        if aircraft.notes:
            developer_info_table.add_row("Notes:", aircraft.notes or f"[dim]N/A[/dim]")

        # 4. Module Metadata
        module_metadata_table = Table(show_header=False, box=None, padding=(0, 2))
        module_metadata_table.add_column("Field", style="bold yellow")
        module_metadata_table.add_column("Value", style="white")

        module_metadata_table.add_row("Folder name/Module name:", f"[dim]{aircraft.module_name}[/dim]")
        module_metadata_table.add_row("Addon name:", aircraft.name)
        # DO NOT RENDER IF None
        if aircraft.module_file_location_1:
            module_metadata_table.add_row("Module Disk Location 1:", aircraft.module_file_location_1 or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.module_file_location_2:
            module_metadata_table.add_row("Module Disk Location 2:", aircraft.module_file_location_2 or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.model_metadata:
            module_metadata_table.add_row("Module Metadata:", aircraft.model_metadata or f"[dim]N/A[/dim]")
        
        # 5. Group
        content_group = Group(
            id_table,
            Text.from_markup("[bold cyan]✈️ Aircraft Information[/bold cyan]"),
            aircraft_data_table,
            Text.from_markup("\n[bold cyan]⚙️ Developer and Module Data[/bold cyan]"),
            developer_info_table,
            Text.from_markup("\n[bold cyan]📝 Additional Notes[/bold cyan]"),
            module_metadata_table,
        )
        
        # Retro Styled Panel
        panel = Panel(
            content_group,
            title="[bold white on blue] MODULE DETAILS [/bold white on blue]",
            box=DOUBLE,
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)
        console.print()

'''
    def _edit_technical_data(self, aircraft: AircraftModel) -> AircraftModel:
        """Interactive Form to edit Module data."""
        console.print("\n[bold yellow]--- Edit Form ---[/bold yellow]")
        console.print("[dim](Press Enter to keep current value)[/dim]\n")

        new_name = inquirer.text(
            message="Module Name:",
            default=aircraft.name,
        ).execute()

        new_icao = inquirer.text(
            message="ICAO Code (4 characters):",
            default=aircraft.icao_code or "UNKN",
        ).execute()

        new_developer = inquirer.text(
            message="Developer:",
            default=aircraft.developer,
        ).execute()

        new_type = inquirer.select(
            message="Aircraft Type:",
            choices=["Airliner", "General Aviation", "Helicopter", "Military", "Glider", "Other"],
            default=aircraft.type if aircraft.type in ["Airliner", "General Aviation", "Helicopter", "Military", "Glider", "Other"] else "General Aviation",
        ).execute()

        new_category = inquirer.select(
            message="Categoría de Motorización:",
            choices=["Single Engine Piston", "Multi Engine Piston", "Turboprop", "Jet", "Turboshaft", "Other"],
            default=aircraft.category if aircraft.category in ["Single Engine Piston", "Multi Engine Piston", "Turboprop", "Jet", "Turboshaft", "Other"] else "Single Engine Piston",
        ).execute()

        # Guardar en la base de datos a través del servicio
        updated_aircraft = self.aircraft_service.update_aircraft(
            aircraft.id,
            name=new_name.strip(),
            icao_code=new_icao.strip().upper(),
            developer=new_developer.strip(),
            type=new_type,
            category=new_category,
        )

        console.print("\n[bold green]✓ ¡Ficha técnica actualizada correctamente![/bold green]")
        inquirer.text(message="Presiona Enter para continuar...").execute()
        
        return updated_aircraft or aircraft

    def _edit_notes_and_rating(self, aircraft: AircraftModel) -> AircraftModel:
        """Formulario para editar notas y rating."""
        console.print("\n[bold yellow]--- Notas y Calificación ---[/bold yellow]\n")

        new_notes = inquirer.text(
            message="Notas del usuario:",
            default=aircraft.notes or "",
        ).execute()

        new_rating = inquirer.select(
            message="Calificación (1 a 5 estrellas):",
            choices=[
                {"name": "⭐ (1)", "value": 1},
                {"name": "⭐⭐ (2)", "value": 2},
                {"name": "⭐⭐⭐ (3)", "value": 3},
                {"name": "⭐⭐⭐⭐ (4)", "value": 4},
                {"name": "⭐⭐⭐⭐⭐ (5)", "value": 5},
            ],
            default=aircraft.rating or 3,
        ).execute()

        updated_aircraft = self.aircraft_service.update_aircraft(
            aircraft.id,
            notes=new_notes.strip(),
            rating=int(new_rating),
        )

        console.print("\n[bold green]✓ ¡Notas y calificación actualizadas![/bold green]")
        inquirer.text(message="Presiona Enter para continuar...").execute()

        return updated_aircraft or aircraft

    def _show_file_paths(self, aircraft: AircraftModel):
        """Muestra las rutas físicas registradas del módulo."""
        console.clear()
        console.rule(f"[bold cyan] Ubicación de Archivos: {aircraft.name} [/bold cyan]\n")

        console.print(f"[bold yellow]Ubicación Principal (MSFS/Sim):[/bold yellow]")
        console.print(f"  {aircraft.module_file_location_1 or '[dim]No registrada[/dim]'}\n")

        if aircraft.module_file_location_2:
            console.print(f"[bold yellow]Ubicación Secundaria:[/bold yellow]")
            console.print(f"  {aircraft.module_file_location_2}\n")

        inquirer.text(message="Presiona Enter para regresar...").execute()
'''