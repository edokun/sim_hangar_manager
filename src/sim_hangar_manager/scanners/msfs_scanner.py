import configparser
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from sim_hangar_manager.database import enums
from sim_hangar_manager.scanners.base_scanner import BaseSimulatorScanner

logger = logging.getLogger(__name__)

class MSFSScanner(BaseSimulatorScanner):
    """
    Scanner for MSFS (2020 and 2024)
    """

    MANIFEST_FILE =  "manifest.json"
    AIRPLANES_SUBDIR = "SimObjects/Airplanes"
    WELL_KNOWN_NOT_AIRCRAFT_MODULES = ["fsltl-traffic-base"]


    @property
    def simulator_name(self) -> str:
        return "MSFS"


    def __init__(self, log_console: Console | None = None):
        self.log_console = log_console


    def can_scan(self, directory_path: Path) -> bool:

        if not directory_path.exists() or not directory_path.is_dir():
            return False

        # Check if given path is already the root folder of the module, if false continue to iteration
        is_valid_package, _ = self._is_valid_aircraft_package(directory_path)
        if directory_path.is_dir() and is_valid_package:
            return True
        else:
            for subfolder in directory_path.iterdir():
                if subfolder.is_dir() and self._is_valid_aircraft_package(subfolder):
                    return True

        return False


    def scan_directory(self, directory_path: Path, skip_validations: bool = False) -> List[Dict[str, Any]]:
        '''
        Scans the root directory where all MSFS addons/module are located, 
        like community folder or a custom folder, also allows to scan the exact module folder
        '''
        detected_modules = None

        if not directory_path.exists() or not directory_path.is_dir():
            return detected_modules

        detected_modules = self._scan_module_root_folder(directory_path, skip_validations)

        if detected_modules is not None:
            return detected_modules

        detected_modules = []
        # If given directory is not the module root directory then iterate
        for package_folder in directory_path.iterdir():
            '''
            Iteration assumes the given directory is a folder where all 
            the modules are installed like community folder, 
            or a external folder if using Addon-Linker
            '''
            modules = self._scan_module_root_folder(package_folder, skip_validations)

            if modules is not None:
               detected_modules.extend(modules) 

        return detected_modules


    def _scan_module_root_folder(self, module_root_path: Path, skip_variant_check: bool = False) -> List[Dict[str, Any]]:
        '''
        The flag skip_variant_check if True will skip validation for valid variant,
        this is useful when providing a concrete module folder to ensure 
        all variants are added.
        '''
        variants = []

        if not module_root_path.is_dir():
            return None

        # Skip known non-aircraft modules (e.g. FSLTL folders)
        if module_root_path.name in self.WELL_KNOWN_NOT_AIRCRAFT_MODULES:
            return None

        is_valid_package, manifest_data = self._is_valid_aircraft_package(module_root_path)

        if not is_valid_package:
            return None

        simObjects_airplanes_folder = module_root_path / self.AIRPLANES_SUBDIR
        
        for aircraft_variant_subfolder in simObjects_airplanes_folder.iterdir():
            if not aircraft_variant_subfolder.is_dir():
                return None

            self._debug(f"Scanning: {simObjects_airplanes_folder}")

            if not skip_variant_check:
                # Add another check to discard liveries (some liveries use AIRCRAFT in the manifest)
                if not self._is_valid_variant(aircraft_variant_subfolder):
                    continue

            # get inside aircraft_variant_subfolder and extract raw data
            raw_data = self._extract_variant_data(module_root_path, aircraft_variant_subfolder, manifest_data)
            if "error" not in raw_data:
                variants.append(raw_data)

        return variants
        

    def _is_valid_aircraft_package(self, package_dir: Path) -> tuple[bool, Dict[str, str] | None]:
        '''
        Validates if folder is a valid module / aircraft object:
        1. Has the file manifest.json
        2. Manifest file is for Aircraft
        3. Contains correct file structure of MSFS addons: 
            - SimObjects/Airplanes/*/
        '''
        if not package_dir.exists() or not package_dir.is_dir():
            return (False, None)

        manifest_path = package_dir / self.MANIFEST_FILE
        if not manifest_path.exists():
            return (False, None)

        airplanes_dir = package_dir / self.AIRPLANES_SUBDIR
        if not airplanes_dir.exists() or not airplanes_dir.is_dir():
            return (False, None)

        # Read the Manifest file here to discard non AIRCRAFT type packages
        manifest_data = self._extract_manifest_data(manifest_path)
        if manifest_data is None or "error" in manifest_data:
            return (False, None)

        return (True, manifest_data)

    
    def _extract_manifest_data(self, manifest_path: Path) -> Dict[str, Any]:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            content_type = manifest_data.get("content_type", "").upper()
            if content_type != "AIRCRAFT":
                return None

            manufacturer = manifest_data.get("manufacturer")

            return {
                "content_type": manifest_data.get('content_type',"AIRCRAFT"),
                "title": manifest_data.get('title',""),
                "creator": manifest_data.get("creator", "Unknown Developer"),
                "manufacturer": manufacturer.upper() if manufacturer else None,
                "package_version": manifest_data.get("package_version", "1.0.0"),
            }

        except (json.JSONDecodeError, OSError) as e:
            return {"error": f"Failed to parse manifest: {str(e)}"}


    def _extract_variant_data(self, package_folder: Path, aircraft_variant_folder: Path, manifest_data: Dict) -> Dict[str, Any]:
        # Format variant name
        variant_folder_name = aircraft_variant_folder.name
        clean_variant_name = variant_folder_name.replace("_", " ").replace("-", " ").title()

        manufacturer= manifest_data.get("manufacturer")

        self._debug(f"Extracting module: {clean_variant_name}")

        variant_data = {
            # Unique ID  package name + variant name based on sub folder for variant
            "module_name": f"{package_folder.name}::{variant_folder_name}",
            "name": f"{manifest_data.get('title', package_folder.name)}",
            "developer": manifest_data.get("creator", "Unknown Developer"),
            "manufacturer": manufacturer.upper() if manufacturer else None,
            "version": manifest_data.get("package_version"),
            "simulator": self.simulator_name,
            "module_file_location_1": str(package_folder.absolute()),
            "icao_code": "UNKN",
            "type": enums.AircraftType.UNKNOWN ,
            "engine_type": enums.EngineType.UNKNOWN,
            "aircraft_category": enums.AircraftCategory.UNKNOWN,
            "is_installed": True,
            "is_active": True,
            "variant" : clean_variant_name,
        }

        # Attempt to read aircraft.cfg return none if not able to read or file not found 
        # (aircraft addons from official marketplace do not have the file accesible)
        config_file_path = self._get_aircraft_cfg_path(aircraft_variant_folder)
        if config_file_path:
            config_file_data = self._read_aircraft_cfg(config_file_path)
            if config_file_data:
                # overwrite few data
                variant_data["icao_code"] = config_file_data["icao_code"]
                variant_data["manufacturer"] = config_file_data["manufacturer"]
                variant_data["type"] = config_file_data["category"]
                variant_data["aircraft_name"] = config_file_data["model"]
                variant_data["engine_count"] = config_file_data["engine_count"]
                engine_type = config_file_data["engine_type"]
                variant_data["engine_type"] = engine_type if engine_type else enums.EngineType.UNKNOWN
                variant_data["variant"] = config_file_data["model"]

        return variant_data


    def _is_valid_variant(self, aircraft_variant_folder: Path) -> bool:
        '''
        Usually the aircraft module package folder should contain a model folder or common folder,
        but in some cases variants reuses folders from adjacent variants, this method will not pick
        such cases.
        '''
        if not aircraft_variant_folder.exists() or not aircraft_variant_folder.is_dir():
            return False

        # Check if the given aircraft_variant_folder has any of these sub-folders: 'model', 'model.*', 'common'
        for subfolder in aircraft_variant_folder.iterdir():
            if not subfolder.is_dir():
                continue

            subfolder_name = subfolder.name.lower()
            if subfolder_name == "common" or subfolder_name == "model" or subfolder_name.startswith("model."):
                return True

        return False

    def _get_aircraft_cfg_path(self, variant_path: Path) -> Path:
        '''
        Usually the aircraft.cfg file is located under the variant folder 
        or inside common/config
        '''
        config_file_path =  variant_path / "aircraft.cfg"
        if config_file_path.exists():
            self._debug(f"Found config file in: {config_file_path}")
            return config_file_path
            
        config_file_path =  variant_path / "common/config/aircraft.cfg"
        if config_file_path.exists():
            self._debug(f"Found config file in: {config_file_path}")
            return config_file_path

        return None


    def _read_aircraft_cfg(self, aircraft_cfg_file_path: Path) -> Dict[str, Any]:
        '''
        The method tries to read the config file, if cannot read None is returned
        '''
        config = configparser.ConfigParser()
        config.read(aircraft_cfg_file_path)
        if not config:
            return None
        
        try:
            self._debug(f"Reading aircraft.cfg")
            return {
                "icao_code": config.get('GENERAL', 'icao_type_designator').upper().replace('"','')[0:4] if config.get('GENERAL', 'icao_type_designator') else None,
                "category": config.get('GENERAL', 'Category').upper().replace('"','') if config.get('GENERAL', 'Category') else None,
                "model": config.get('GENERAL', 'icao_model').replace('"','') if config.get('GENERAL', 'icao_model') else None,
                "engine_type": config.get('GENERAL', 'icao_engine_type').upper().replace('"','') if config.get('GENERAL', 'icao_engine_type') else None,
                "engine_count": int(config.get('GENERAL', 'icao_engine_count')) if config.get('GENERAL', 'icao_engine_count') else None,
                "manufacturer": config.get('GENERAL', 'icao_manufacturer').upper().replace('"','') if config.get('GENERAL', 'icao_manufacturer') else None,
            }

        except (configparser.Error, configparser.NoSectionError) as e:
            return None


    def _debug(self, message: str):
        if self.log_console:
            self.log_console.print(f"[MSFSScanner] {message}")