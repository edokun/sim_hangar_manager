from sqlalchemy import text

from sim_hangar_manager.cli.interactive_cli import main_menu

#from sim_hangar_manager.database.connection import SessionLocal


def init_app():
    """
    Verify APP startup, if fresh install create DB and other initial checks.
    """
    # TODO: Add code to call Alembic to create DB if not exist
    #db = SessionLocal()
    #try:
    #    db.execute(text("SELECT 1"))
    #finally:
    #    db.close()


def main():
    #with console.status("[bold cyan]Loading Sim Hangar Manager...[/bold cyan]",
    #                    spinner="dots"):
    #    init_app()
    main_menu()


if __name__ == "__main__":
    main()