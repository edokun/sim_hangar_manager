from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from sim_hangar_manager.scanners.base_scanner import BaseSimulatorScanner
from sim_hangar_manager.scanners.msfs_scanner import MSFSScanner


class ScannerService:

    def __init__(self, log_console: Console | None = None):
        self.log_console= log_console

        # Register all active scanners here.
        # In the future, someone can append XPlaneScanner(), DCSWorldScanner(), etc.
        self._scanners: List[BaseSimulatorScanner] = [
            MSFSScanner(self.log_console),
        ]

    def register_scanner(self, scanner: BaseSimulatorScanner):
        """Allows dynamic registration of custom third-party scanners."""
        self._scanners.append(scanner)


    def scan_path(self, target_path: str, skip_validation: bool = False) -> List[Dict[str, Any]]:
        path = self._validate_path(target_path)

        for scanner in self._scanners:
            if scanner.can_scan(path):
                return scanner.scan_directory(path, skip_validation)

        # If no scanner recognized the folder structure
        return []


    def _validate_path(self, target_path: str) -> Path:
        path = Path(target_path)           
        
        if not path.exists():
            error_str = f"The path '{target_path}' does not exist."
            self._debug(error_str)
            raise FileNotFoundError(error_str)

        return path


    def _debug(self, message: str):
        if self.log_console:
            self.log_console.print(f"[ScannerService] {message}")