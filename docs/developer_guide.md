## Notes for developer

### Setup and Installation

```bash
# Install Python 3 and Poetry

# Install Poetry en Windows:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# See Poetry installed version
poetry --version

# Install project dependencies (from root folder, where pyproject.toml is)
poetry install
```

### Usage of Poetry shell
```python
# Enter to Poetry virtual env
poetry shell

# Exit Poetry virtual env
exit

# To run command inside Poetry shell no need to add poetry first

# Execute a command without enter Poetry shell
poetry run <comando>

# Examples:
poetry run python --version
poetry run pytest
```

### DB Migrations using Alembic
```python
# Initialize Alembic (Only once at first step), this generates files init files
poetry run alembic init migrations

# Create a new migration based on the models
poetry run alembic revision --autogenerate -m "migration message"

# Apply all pending migrations (updates DB schema to the latest changes)
poetry run alembic upgrade head

# Revert changes to previous version (Specifing concrete revision ID)
poetry run alembic downgrade <revision_id>

# See migration history
poetry run alembic history

# See current applied DB version
poetry run alembic current
```

### DB Operations during development

To recreate the DB first delete the DB file kakeibo.db, then run
```Python
# Recreate clean DB from migrations (or on a fresh install)
poetry run alembic upgrade head
```

### Execute scripts, Launch application
```Python
# Execute a script alone (example)
poetry run python tests/manual_create_db.py

# Execute a module of the application (Like a cli app)
poetry run python -m kakeibo.cli
```
