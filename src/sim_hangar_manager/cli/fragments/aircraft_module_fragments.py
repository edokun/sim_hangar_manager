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
        # 1. Header Table
        id_table = Table(
            show_header=False,
            box=None,
            padding=(0,0,1,0),
            expand=True,
        )

        id_table.add_column("Value1", style="bold yellow", justify="left")
        id_table.add_column("Value2", style="white", justify="left")

        column_text = f"[bold cyan] {aircraft.name.upper()} [/bold cyan]"
        id_table.add_row(f"[bold yellow] {str(aircraft.id)} [/bold yellow]", column_text)

        # 2. Aircraft Data Table
        aircraft_data_table = Table(show_header=False, box=None, padding=(0, 1))
        aircraft_data_table.add_column("Field", style="bold yellow", width=20)
        aircraft_data_table.add_column("Value", style="white", overflow="fold", width=25)

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

        left_column = Group(
            Text.from_markup("[bold cyan]✈️ Aircraft Information[/bold cyan]"),
            aircraft_data_table,
        )

        # 3. Module Version, Rating and Developer Information
        rating_stars = "⭐" * (aircraft.rating or 0) if aircraft.rating else "[dim]-[/dim]"

        developer_info_table = Table(show_header=False, box=None, padding=(0, 1))
        developer_info_table.add_column("Field", style="bold yellow", width=15)
        developer_info_table.add_column("Value", style="white", width=30, overflow="fold")

        developer_info_table.add_row("Mod Version:", aircraft.version or "1.0.0")
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
            Text.from_markup("[bold cyan]⚙️ Developer and Module Data[/bold cyan]"),
            developer_info_table,
        )

        two_column_section = Columns([left_column, right_column], expand=False)

        # 4. Module Metadata
        module_metadata_table = Table(show_header=False, box=None, padding=(0, 2))
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

        bottom_table = Table(
            show_header=False,
            box=None,
            padding=(1,1,0,0),
            expand=True,
        )

        #bottom_table.add_column("Value1", style="bold yellow", justify="left")
        bottom_table.add_column("Value2", style="white", justify="left")

        active_text = "Active: ✅" if (aircraft.is_active) else "Active: ❌"
        installed_text = "Installed: ✅" if (aircraft.is_installed) else "Installed: ❌"
        column_text = f"[bold magenta]{aircraft.simulator}[/bold magenta] - {active_text} {installed_text}"
                        
        bottom_table.add_row(column_text)


        # 5. Group
        content_group = Group(
            id_table,
            two_column_section,
            Text.from_markup("\n[bold cyan]📝 Additional Data[/bold cyan]"),
            module_metadata_table,
            bottom_table
        )
        
        # Retro Styled Panel
        panel = Panel(
            content_group,
            title="[bold white on blue] MODULE DETAILS [/bold white on blue]",
            box=DOUBLE,
            border_style="blue",
            padding=(1, 2),
        )

        self.console.print(panel)