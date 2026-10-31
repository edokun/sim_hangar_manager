from typing import List, Optional

from sqlalchemy.orm import Session

from sim_hangar_manager.database.models import AircraftModel


class AircraftModelRepository:
    def __init__(self, session: Session):
        self.db = session

    def create(self, aircraft_model: AircraftModel) -> AircraftModel:
        """
        Receives an AircraftModel instance and creates a new record in the database.
        """
        self.db.add(aircraft_model)
        self.db.commit()
        self.db.refresh(aircraft_model)  # Refreshes to populate the auto-incremented ID
        return aircraft_model

    def get(
        self, skip: int = 0, limit: int = 100, include_inactive: bool = False
    ) -> List[AircraftModel]:
        """
        Retrieves a list of aircraft modules from the database.
        By default, it filters out inactive modules unless include_inactive is set to True.
        """
        query = self.db.query(AircraftModel)

        # Apply filter only if we don't want to include inactive records
        if not include_inactive:
            query = query.filter(AircraftModel.is_active == True)

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, model_id: int) -> Optional[AircraftModel]:
        """
        Fetches a specific aircraft model using its primary key ID identifier.
        Returns None if the record context does not exist.
        """
        return self.db.query(AircraftModel).filter(AircraftModel.id == model_id).first()

    def get_by_module_and_simulator(self, module_name: str, simulator: str) -> Optional[AircraftModel]:
        return (
            self.db.query(AircraftModel)
            .filter(
                AircraftModel.module_name == module_name,
                AircraftModel.simulator == simulator
            )
            .first()
        )

    def update(self, model_id: int, updated_data: dict) -> Optional[AircraftModel]:
        """
        Performs a dynamic full or partial update on an existing AircraftModel.
        It updates all provided keys in the dictionary matching the model fields.
        """
        db_model = self.get_by_id(model_id)
        if not db_model:
            return None

        # Dynamically loop over dictionary fields and set attributes on the model object
        for key, value in updated_data.items():
            # Safety check: prevent overriding internal primary key fields accidentally
            if hasattr(db_model, key) and key != "id":
                setattr(db_model, key, value)

        self.db.commit()
        self.db.refresh(db_model)
        return db_model

    def update_notes(self, model_id: int, new_notes: str) -> Optional[AircraftModel]:
        """
        Updates the personal remarks or notes of a specific aircraft module.
        Useful for quick operational reminders.
        """
        db_model = self.get_by_id(model_id)
        if db_model:
            db_model.notes = new_notes
            self.db.commit()
            self.db.refresh(db_model)
        return db_model

    def update_rating(self, model_id: int, new_rating: int) -> Optional[AircraftModel]:
        """
        Updates the rating of a specific aircraft module.
        Useful for user-generated reviews or feedback.
        """
        db_model = self.get_by_id(model_id)
        if db_model:
            db_model.rating = new_rating
            self.db.commit()
            self.db.refresh(db_model)
        return db_model

    def disable(self, model_id: int) -> bool:
        """
        Disable an aircraft model by turning off the is_active flag.
        This preserves underlying historical flight log relations.
        """
        db_model = self.get_by_id(model_id)
        if db_model:
            db_model.is_active = False
            self.db.commit()
            return True
        return False

    def enable(self, model_id: int) -> bool:
        """
        Enable an aircraft model by turning on the is_active flag.
        This preserves underlying historical flight log relations.
        """
        db_model = self.get_by_id(model_id)
        if db_model:
            db_model.is_active = True
            self.db.commit()
            return True
        return False
