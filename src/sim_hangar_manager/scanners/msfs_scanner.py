import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from sim_hangar_manager.scanners.base_scanner import BaseSimulatorScanner

logger = logging.getLogger(__name__)

class MSFSScanner(BaseSimulatorScanner):
    """
    Scanner for MSFS (2020 and 2024)
    """

    @property
    def simulator_name(self) -> str:
        return "MSFS"


    def can_scan(self, directory_path: Path) -> bool:

        if not directory_path.exists() or not directory_path.is_dir():
            return False

        for subfolder in directory_path.iterdir():
            if subfolder.is_dir() and self._is_valid_aircraft_package(subfolder):
                return True

        return False


    def scan_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        detected_modules = []

        for folder in directory_path.iterdir():
            if not folder.is_dir() or not self._is_valid_aircraft_package(folder):
                continue

            raw_data = self._extract_raw_data(folder)
            if "error" not in raw_data:
                detected_modules.append(raw_data)

        return detected_modules


    def _is_valid_aircraft_package(self, package_dir: Path) -> bool:
        """
        Validates if folder has a module / aircraft object:
        1. Has the file manifest.json
        2. Contains correct file structure of MSFS addons: SimObjects/Airplanes/*/model
        """
        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            return False

        simobjects_dir = package_dir / "SimObjects" / "Airplanes"
        if not simobjects_dir.exists() or not simobjects_dir.is_dir():
            return False

        # Search for the folder 'model' inside SimObjects/Airplanes/{any_folder}
        # Use glob to find sub folders (e.g. SimObjects/Airplanes/pmdg737/model)
        model_directories = list(simobjects_dir.glob("*/model"))
        return len(model_directories) > 0


    def _extract_raw_data(self, module_folder: Path) -> Dict[str, Any]:
        """
        Helper method to extract and normalize metadata from manifest.json
        """
        manifest_path = module_folder / "manifest.json"

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract & normalize metadata to fit the model domain
            content_type = data.get("content_type", "").upper()

            # We can filter only AIRCRAFT type modules
            if content_type == "AIRCRAFT":
                return {
                    "module_name": module_folder.name,
                    "name": data.get("title", module_folder.name),
                    "manufacturer": data.get("manufacturer", "Unknown"),
                    "developer": data.get("creator", "Unknown Developer"),
                    "version": data.get("package_version", "1.0.0"),
                    "simulator": "MSFS",
                    "module_file_location_1": str(module_folder.absolute()),
                    "notes": f"Scanned automatically from {module_folder.name}",
                    "icao_code": "UNKN",
                    "type": "UNKNOWN",
                    "category": "UNKNOWN",
                }
            logger.warning(f"Skipping {module_folder.name}: content_type '{content_type}' is not AIRCRAFT.")
            return {"error": f"Invalid content_type: {content_type}"}
        
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading manifest.json in {module_folder}: {e}")
            return {"error": f"Failed to parse manifest.json: {str(e)}"}