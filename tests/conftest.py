import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sim_hangar_manager.database.models import Base
from sim_hangar_manager.database.repository.aircraft_model_repository import AircraftModelRepository
from sim_hangar_manager.service.aircraft_model_service import AircraftModelService


@pytest.fixture(scope="function")
def db_session():

    # 1. In Memory DB
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # 2. Create Schema
    Base.metadata.create_all(bind=engine)

    # 3. Create test session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Cleanup
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def aircraft_repo(db_session):
    """Provides a repository instance with an In-Memory DB Session."""
    return AircraftModelRepository(db_session)


@pytest.fixture(scope="function")
def aircraft_service(aircraft_repo):
    """Provides a service instance with an In-Memory DB Session."""
    return AircraftModelService(aircraft_repo)