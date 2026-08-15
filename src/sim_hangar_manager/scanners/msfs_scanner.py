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

    MANIFEST_FILE =  "manifest.json"
    AIRPLANES_SUBDIR = "SimObjects/Airplanes"


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
        '''
        Scans the root directory where all MSFS addons/module are located, 
        like community folder or a custom folder
        '''
        detected_modules = []

        for package_folder in directory_path.iterdir():
            # Each of the folder here should be the addon folder

            if not self._is_valid_aircraft_package(package_folder):
                continue

            simobjects_airplanes_folder = package_folder / self.AIRPLANES_SUBDIR
            
            for aircraft_subfolder in simobjects_airplanes_folder.iterdir():
                if not aircraft_subfolder.is_dir():
                    continue

                # get aircraft variants paths
                variants_paths = self._get_variants_folders(aircraft_subfolder)
                for variant_path in variants_paths:
                    raw_data = self._extract_variant_data(package_folder, variant_path)
                    if "error" not in raw_data:
                        detected_modules.append(raw_data)

        return detected_modules


    def _is_valid_aircraft_package(self, package_dir: Path) -> bool:
        """
        Validates if folder is a valid module / aircraft object:
        1. Has the file manifest.json
        2. Contains correct file structure of MSFS addons: 
            - SimObjects/Airplanes/*/model*
            - SimObjects/Airplanes/*/*/model* (support for common/ and nested folders)
        """

        if not package_dir.exists() or not package_dir.is_dir():
            return False

        manifest_path = package_dir / self.MANIFEST_FILE
        if not manifest_path.exists():
            return False

        airplanes_dir = package_dir / self.AIRPLANES_SUBDIR
        if not airplanes_dir.exists() or not airplanes_dir.is_dir():
            return False

        patterns = ("*/model*", "*/*/model*")

        return any(
            path.is_dir()
            for pattern in patterns
            for path in airplanes_dir.glob(pattern)
        )

    def _get_variants_folders(self, aircraft_subfolder: Path) -> List[Path]:
        """
        Finds and returns the variant folder paths inside an aircraft subfolder.
        Handles standard, nested (e.g., wbsim c152), and 'common' folder structures.
        """

        if not aircraft_subfolder.exists() or not aircraft_subfolder.is_dir():
            return []

        variant_folders: List[Path] = []

        # Search for model* folders directly inside or 1 level deeper
        model_dirs = [
            p for p in list(aircraft_subfolder.glob("model*")) + list(aircraft_subfolder.glob("*/model*"))
            if p.is_dir()
        ]

        for model_path in model_dirs:
            parent = model_path.parent

            if parent == aircraft_subfolder:
                target_folder = aircraft_subfolder
            elif parent.name.lower() == "common":
                target_folder = parent.parent
            else:
                target_folder = parent

            # Add avoiding duplicates while preserving order
            if target_folder not in variant_folders:
                variant_folders.append(target_folder)

        return variant_folders


    def _extract_variant_data(self, package_folder: Path, aircraft_variant_folder: Path) -> Dict[str, Any]:


        manifest_path = package_folder / self.MANIFEST_FILE

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            content_type = manifest_data.get("content_type", "").upper()
            if content_type != "AIRCRAFT":
                return {"error": f"Invalid content_type: {content_type}"}

            # Format variant name
            variant_folder_name = aircraft_variant_folder.name
            clean_variant_name = variant_folder_name.replace("_", " ").replace("-", " ").title()

            return {
                # Unique ID  package name + variant name based on sub folder for variant
                "module_name": f"{package_folder.name}::{variant_folder_name}",
                "name": f"{manifest_data.get('title', package_folder.name)} - {clean_variant_name}",
                "developer": manifest_data.get("creator", "Unknown Developer"),
                "version": manifest_data.get("package_version", "1.0.0"),
                "simulator": self.simulator_name,
                "module_file_location_1": str(aircraft_variant_folder.absolute()),
                "icao_code": "UNKN",
                "type": "UNKNOWN",
                "category": "UNKNOWN",
                "notes": f"Scanned from bundle {package_folder.name} (Variant: {variant_folder_name})",
            }

        except (json.JSONDecodeError, OSError) as e:
            return {"error": f"Failed to parse manifest: {str(e)}"}