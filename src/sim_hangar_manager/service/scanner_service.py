from pathlib import Path
from typing import List, Dict, Any
from sim_hangar_manager.scanners.base_scanner import BaseSimulatorScanner
from sim_hangar_manager.scanners.msfs_scanner import MSFSScanner

class HangarScannerService:
    def __init__(self):
        # Register all active scanners here.
        # In the future, someone can append XPlaneScanner(), DCSWorldScanner(), etc.
        self._scanners: List[BaseSimulatorScanner] = [
            MSFSScanner(),
        ]

    def register_scanner(self, scanner: BaseSimulatorScanner):
        """Allows dynamic registration of custom third-party scanners."""
        self._scanners.append(scanner)

    def scan_path(self, target_path: str) -> List[Dict[str, Any]]:
        path = Path(target_path)
        
        if not path.exists():
            raise FileNotFoundError(f"The path '{target_path}' does not exist.")

        for scanner in self._scanners:
            if scanner.can_scan(path):
                return scanner.scan_directory(path)

        # If no scanner recognized the folder structure
        return []