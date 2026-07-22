from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sim_hangar_manager.database.models import AircraftModel

console = Console()

def show_aircraft_model_details(model: AircraftModel):
    """
    Show detailed information of an Aircraft Model
    """
    console.print(f"\n")
    console.print(Panel.fit(f"[bold cyan]Aircraft Module Details:[/bold cyan] {model.name} [{model.icao_code}]", border_style="cyan"))
    
    # --- Tabla 1: Información Core ---
    table_core = Table(show_header=False, box=None, padding=(0, 2))
    table_core.add_column("Property", style="bold green", justify="right")
    table_core.add_column("Value", style="white")

    table_core.add_row("Module ID:", str(model.id))
    table_core.add_row("Aircraft Name:", model.name)
    table_core.add_row("ICAO Code:", model.icao_code)
    table_core.add_row("Developer:", model.developer)
    table_core.add_row("Module Folder:", model.module_name)
    
    # --- Tabla 2: Clasificación y Plataforma ---
    table_specs = Table(show_header=False, box=None, padding=(0, 2))
    table_specs.add_column("Property", style="bold yellow", justify="right")
    table_specs.add_column("Value", style="white")
    
    table_specs.add_row("Type Class:", model.type.value if hasattr(model.type, 'value') else str(model.type))
    table_specs.add_row("Engine Category:", model.category.value if hasattr(model.category, 'value') else str(model.category))
    table_specs.add_row("Simulator:", model.simulator.value if hasattr(model.simulator, 'value') else str(model.simulator))
    table_specs.add_row("Compatibility:", model.simulator_compatibility.value if hasattr(model.simulator_compatibility, 'value') else str(model.simulator_compatibility))
    
    # --- Tabla 3: Instalación y Notas ---
    table_local = Table(show_header=False, box=None, padding=(0, 2))
    table_local.add_column("Property", style="bold magenta", justify="right")
    table_local.add_column("Value", style="white")

    # Convert numeric rating into star icons for visual flare
    stars = "★" * model.rating if model.rating > 0 else "-"

    table_core.add_row("Rating:", f"[bold gold1]{stars}[/bold gold1]")
    table_local.add_row("Acquired Store:", model.store.value if hasattr(model.store, 'value') else str(model.store))
    table_local.add_row("Distribution:", model.module_type.value if hasattr(model.module_type, 'value') else str(model.module_type))
    if model.module_file_location_1:
        table_local.add_row("Path 1:", model.module_file_location_1)
    if model.notes:
        table_local.add_row("Notes:", f"[italic]{model.notes}[/italic]")

    # Renderizamos las tablas en pantalla de forma ordenada
    console.print("\n[bold]⚙️ Core Identifiers[/bold]")
    console.print(table_core)
    console.print("\n[bold]📊 Specifications[/bold]")
    console.print(table_specs)
    console.print("\n[bold]💾 System & Local Data[/bold]")
    console.print(table_local)
    console.print("\n" + "="*50 + "\n")