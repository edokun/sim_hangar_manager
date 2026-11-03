from rich.box import DOUBLE
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sim_hangar_manager.database.models import AircraftModel


class AircraftModelFragments:

    def __init__(self,stdout_console: Console):
        self.console = stdout_console

    def show_detailed_fragment(self, aircraft: AircraftModel):

        # Padding 4 values tuple means:
        # top, right, bottom, and left

        # 1. Header Table
        id_table = Table(
            show_header=False,
            box=None,
            padding=(0,2,1,0),
            expand=False,
        )

        id_table.add_column("module_id", style="bold yellow", justify="left", width=6)
        id_table.add_column("module_name", style="white", justify="left", width=43)
        id_table.add_column("module_status", style="white", justify="right")

        id_column = f"[bold cyan]ID[/bold cyan][bold] {str(aircraft.id)} [/bold]"
        column_model_name = f"[bold cyan]{aircraft.name.upper()}[/bold cyan]"

        active_text = "Active:✅" if (aircraft.is_active) else "Active:❌"
        installed_text = "Installed:✅" if (aircraft.is_installed) else "Installed:❌"
        status_text = f"[bold magenta]{aircraft.simulator}[/bold magenta] - {active_text} {installed_text}"

        id_table.add_row(id_column, column_model_name, status_text)

        # 2. Aircraft Data Table
        aircraft_data_table = Table(show_header=False, box=None)
        aircraft_data_table.add_column("Field", style="bold yellow", width=18)
        aircraft_data_table.add_column("Value", style="white", overflow="fold", width=30)

        aircraft_data_table.add_row("ICAO Code:", aircraft.icao_code or "[red]UNKN[/red]")
        aircraft_data_table.add_row("Manufacturer:", aircraft.manufacturer or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Aircraft name:", aircraft.aircraft_name or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Type:", aircraft.type or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Engine Type:", aircraft.engine_type or f"[dim]N/A[/dim]")
        aircraft_data_table.add_row("Engine Count:", str(aircraft.engine_count) or f"[dim]0[/dim]")
        aircraft_data_table.add_row("Aircraft Category:", aircraft.aircraft_category or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.aircraft_subcategory:
            aircraft_data_table.add_row("Sub-Category:", aircraft.aircraft_subcategory)

        aircraft_data_table.add_row("Variant:", aircraft.variant or f"[dim]N/A[/dim]")
            
        left_column = Group(
            Text.from_markup("[bold cyan]AIRCRAFT INFORMATION[/bold cyan]"),
            aircraft_data_table,
        )

        # 3. Module Version, Rating and Developer Information
        rating_stars = "⭐" * (aircraft.rating or 0) if aircraft.rating else "[dim]-[/dim]"

        developer_info_table = Table(show_header=False, box=None)
        developer_info_table.add_column("Field", style="bold yellow", width=15)
        developer_info_table.add_column("Value", style="white", width=30, overflow="fold")

        developer_info_table.add_row("Mod Version:", aircraft.version or f"[dim]N/A[/dim]")
        developer_info_table.add_row("Developer:", aircraft.developer)
        developer_info_table.add_row("Module Type:", aircraft.module_type or f"[dim]N/A[/dim]")
        developer_info_table.add_row("Store:", aircraft.store or f"[dim]N/A[/dim]")
        # DO NOT RENDER IF None
        if aircraft.developer_url:
            developer_info_table.add_row("developer_url:", aircraft.developer_url)


        developer_info_table.add_row("Compatibility:", aircraft.simulator_compatibility or f"[dim]N/A[/dim]")
        developer_info_table.add_row("Rating:", rating_stars)

        # DO NOT RENDER IF None
        if aircraft.notes:
            developer_info_table.add_row("Notes:", aircraft.notes or f"[dim]N/A[/dim]")

        right_column = Group(
            Text.from_markup("[bold cyan]DEVELOPER & MODEL DATA[/bold cyan]"),
            developer_info_table,
        )

        two_column_section = Columns([left_column, right_column], expand=False)

        # 4. Module Metadata
        module_metadata_table = Table(show_header=False, box=None)
        module_metadata_table.add_column("Field", style="bold yellow")
        module_metadata_table.add_column("Value", style="white")

        #module_metadata_table.add_row("Addon name:", aircraft.name)
        module_metadata_table.add_row("Folder name:", f"[dim]{aircraft.module_name}[/dim]")
        # DO NOT RENDER IF None
        if aircraft.module_file_location_1:
            long_path1 = aircraft.module_file_location_1 or f"[dim]N/A[/dim]"
            module_metadata_table.add_row("Disk Location:", Text(long_path1, style="dim white", overflow="fold"))
        # DO NOT RENDER IF None
        if aircraft.module_file_location_2:
            long_path2 = aircraft.module_file_location_2 or f"[dim]N/A[/dim]"
            module_metadata_table.add_row("Disk Location:", Text(long_path2, style="white", overflow="fold"))
        # DO NOT RENDER IF None
        if aircraft.model_metadata:
            long_metadata = aircraft.model_metadata or f"[dim]N/A[/dim]"
            module_metadata_table.add_row("Module Metadata:", Text(long_metadata, style="white", overflow="fold"))


        # 5. Group
        content_group = Group(
            id_table,
            two_column_section,
            Text.from_markup("[bold cyan]\nADDITIONAL DATA[/bold cyan]"),
            module_metadata_table
        )
        
        # Retro Styled Panel
        panel = Panel(
            content_group,
            title="[bold white on blue] AIRCRAFT MODEL DETAILS [/bold white on blue]",
            box=DOUBLE,
            border_style="blue",
            padding=(1, 1),
        )

        self.console.print(panel)