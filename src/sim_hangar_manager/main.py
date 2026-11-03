from pathlib import Path

from rich.console import Console

from sim_hangar_manager.cli.interactive_cli import InteractiveCLI
from sim_hangar_manager.cli.views.add_aircraft_model_view import \
    AddAircraftModelView
from sim_hangar_manager.cli.views.list_aircraft_model_view import \
    ListAircraftModelView
from sim_hangar_manager.cli.views.scan_view import ScanView
from sim_hangar_manager.cli.views.search_view import SearchAircraftView
from sim_hangar_manager.cli.views.show_aircraft_model_view import \
    AircraftModelDetailView
from sim_hangar_manager.database.connection import get_db_session, init_db
from sim_hangar_manager.database.repository.aircraft_model_repository import \
    AircraftModelRepository
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService
from sim_hangar_manager.service.scanner_service import ScannerService


def bootstrap_application() -> InteractiveCLI:
    """Composition Root: Wires all dependencies for interactive cli."""

    # 1. Main output console (terminal)
    stdout_console = Console()

    # Optional: Make sure DB exists
    # init_db()
    
    # 2. Infra / DB
    session = get_db_session()
    
    # 3. Repositories
    aircraft_model_repo = AircraftModelRepository(session=session)
    
    # 4. Auxiliary components
    
    # 5. Services
    aircraft_model_service = AircraftModelService(repository=aircraft_model_repo)
    scanner_service = ScannerService()
    
    # 6. Views
    search_aircraft_view = SearchAircraftView(
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console)
    
    aircraft_model_detail_view = AircraftModelDetailView(
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console)

    add_aircraft_model_view = AddAircraftModelView(
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console)

    list_aircraft_model_view = ListAircraftModelView(
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console)
    
    # 7. Menú Principal / REPL CLI (Inyectando las vistas armadas)
    interactive_cli = InteractiveCLI(
        aircraft_model_service=aircraft_model_service,
        search_aircraft_view=search_aircraft_view,
        aircraft_model_detail_view=aircraft_model_detail_view,
        add_aircraft_model_view=add_aircraft_model_view,
        list_aircraft_model_view=list_aircraft_model_view,
        stdout_console=stdout_console
    )
    
    return interactive_cli


def bootstrap_add_aircraft_model_view() -> AddAircraftModelView:
    # 1. Main output console (terminal)
    stdout_console = Console()
    
    # 2. Infra / DB
    session = get_db_session()
    
    # 3. Repositories
    aircraft_model_repo = AircraftModelRepository(session=session)
        
    # 4. Services
    aircraft_model_service = AircraftModelService(repository=aircraft_model_repo)
    
    # 5. Views
    add_aircraft_model_view = AddAircraftModelView(
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console
    )
    
    return add_aircraft_model_view


def bootstrap_list_aircraft_model_view() -> ListAircraftModelView:
    # 1. Main output console (terminal)
    stdout_console = Console()
    
    # 2. Infra / DB
    session = get_db_session()
    
    # 3. Repositories
    aircraft_model_repo = AircraftModelRepository(session=session)
        
    # 4. Services
    aircraft_model_service = AircraftModelService(repository=aircraft_model_repo)
    
    # 5. Views
    list_aircraft_model_view = ListAircraftModelView(
            aircraft_model_service=aircraft_model_service,
            stdout_console=stdout_console)
    
    return list_aircraft_model_view


def bootstrap_scan_context(log_path: Path | None = None):
    '''
    Method used for CLI scan command, this method wires all the dependencies
    '''
    # 1. Main output console (terminal)
    stdout_console = Console()
    
    # 2. File output for log
    log_file_handle = None
    log_console = None

    if log_path:
        log_file_handle = open(log_path, "a", encoding="utf-8")
        log_console = Console(file=log_file_handle, width=140)

    # 3. DB / Repository
    session = get_db_session()
    aircraft_repo = AircraftModelRepository(session=session)

    # 4. Services
    aircraft_model_service = AircraftModelService(
        repository=aircraft_repo, 
        log_console=log_console
    )
        
    scanner_service = ScannerService(
        log_console=log_console
    )

    # 5. Views
    scan_view = ScanView(
        scanner_service=scanner_service,
        aircraft_model_service=aircraft_model_service,
        stdout_console=stdout_console,
        log_console=log_console
    )

    return scan_view, log_file_handle


def main():
    app = bootstrap_application()
    app.run()


if __name__ == "__main__":
    main()