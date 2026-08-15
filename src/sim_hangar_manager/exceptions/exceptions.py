class AircraftModuleAlreadyExistsError(Exception):
    """
    To be thrown when attempting to insert an existing module to the database
    """
    def __init__(self, module_name: str, simulator: str):
        self.module_name = module_name
        self.simulator = simulator
        super().__init__(f"Module '{module_name}' already exists in DB for {simulator}.")