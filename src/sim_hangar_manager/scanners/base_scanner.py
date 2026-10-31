from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseSimulatorScanner(ABC):
    """
    Abstract Base Class (Interface) that all simulator scanners must implement.
    """

    @property
    @abstractmethod
    def simulator_name(self) -> str:
        """Returns the identifier string of the simulator (e.g., 'MSFS', 'X-Plane')."""
        pass

    @abstractmethod
    def can_scan(self, directory_path: Path) -> bool:
        """
        Inspects the target directory to determine if it belongs to this simulator structure.
        E.g., checks for manifest.json, layout.json, or specific folder hierarchies.
        """
        pass

    @abstractmethod
    def scan_directory(self, directory_path: Path, skip_validations: bool = False) -> List[Dict[str, Any]]:
        """
        Scans the directory and returns a normalized list of raw dictionaries 
        containing the detected aircraft module data.
        The flag skip_validations is used to force detection if the module structure is not standard, disabled by default.
        """
        pass