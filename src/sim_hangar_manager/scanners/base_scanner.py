from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class BaseSimulatorScanner(ABC):
    """
    Abstract Base Class (Interface) that all simulator scanners must implement.
    """

    @property
    @abstractmethod
    def simulator_name(self) -> str:
        """Returns the identifier string of the simulator (e.g., 'MSFS2020', 'X-Plane')."""
        pass

    @abstractmethod
    def can_scan(self, directory_path: Path) -> bool:
        """
        Inspects the target directory to determine if it belongs to this simulator structure.
        E.g., checks for manifest.json, layout.json, or specific folder hierarchies.
        """
        pass

    @abstractmethod
    def scan_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """
        Scans the directory and returns a normalized list of raw dictionaries 
        containing the detected aircraft module metadata.
        """
        pass