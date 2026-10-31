import json
from pathlib import Path

from sim_hangar_manager.scanners.msfs_scanner import MSFSScanner


def test_can_scan_returns_false_for_empty_or_non_existent_directory(tmp_path: Path):

    scanner = MSFSScanner()

    # Case 1: Non-Existent Path
    non_existent_path = tmp_path / "does_not_exist"
    assert scanner.can_scan(non_existent_path) is False

    # Case 2: Empty Path
    empty_dir = tmp_path / "empty_folder"
    empty_dir.mkdir()
    assert scanner.can_scan(empty_dir) is False


def test_valid_aircraft_package_detection(tmp_path: Path):

    scanner = MSFSScanner()

    # 1. Create correct folder structure to simulate a module folder (e.g. A2A Comanche)
    addon_dir = tmp_path / "a2a-comanche"
    model_dir = addon_dir / "SimObjects" / "Airplanes" / "a2a_pa24" / "model"
    model_dir.mkdir(parents=True)

    # 2. Create manifest.json file
    manifest_data = {
        "title": "Piper PA-24 Comanche 250",
        "creator": "A2A Simulations",
        "package_version": "1.2.0",
        "content_type": "AIRCRAFT",
    }
    manifest_file = addon_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # 3. Validations
    assert scanner.can_scan(tmp_path) is True

    # Test
    results = scanner.scan_directory(tmp_path)
    assert len(results) == 1
    assert results[0]["name"] == "Piper PA-24 Comanche 250 - A2A Pa24"
    assert results[0]["developer"] == "A2A Simulations"
    assert results[0]["simulator"] == "MSFS"


def test_livery_is_ignored_by_scanner(tmp_path: Path):

    scanner = MSFSScanner()

    # Create a livery path without model folder
    livery_dir = tmp_path / "livery-737-aeromexico"
    texture_dir = (
        livery_dir / "SimObjects" / "Airplanes" / "pmdg737_AM" / "texture"
    )
    texture_dir.mkdir(parents=True)

    manifest_data = {
        "title": "PMDG 737 Aeromexico Livery",
        "creator": "Community Painter",
        "content_type": "AIRCRAFT",
    }
    (livery_dir / "manifest.json").write_text(
        json.dumps(manifest_data), encoding="utf-8"
    )

    # Should not be scanned
    assert scanner.can_scan(tmp_path) is False
    results = scanner.scan_directory(tmp_path)
    assert len(results) == 0

def test_valid_aircraft_package_detection_real_dir():

    scanner = MSFSScanner()

    directory_path = "D:/MSFS_ADDONS/2024/AIRCRAFTS/bksq-aircraft-bonanzapro"
    target_path = Path(directory_path)

    # Test
    results = scanner.scan_directory(target_path)
    assert len(results) == 2
    assert results[0]["module_name"] == "bksq-aircraft-bonanzapro::bksq-aircraft-bonanzapro"
    assert results[0]["developer"] == "Black Square"
    assert results[0]["icao_code"] == "BE36"
    assert results[0]["manufacturer"] == "BEECHCRAFT"
    assert results[0]["type"] == "AIRPLANE"
    assert results[0]["aircraft_name"] == "A36 Bonanza"
    assert results[0]["engine_count"] == 1
    assert results[0]["engine_type"] == "PISTON"
    assert results[1]["module_name"] == "bksq-aircraft-bonanzapro::bksq-aircraft-bonanzaproturbine"
    assert results[1]["developer"] == "Black Square"
    assert results[1]["icao_code"] == "B36T"
    assert results[1]["manufacturer"] == "BEECHCRAFT"
    assert results[1]["type"] == "AIRPLANE"
    assert results[1]["aircraft_name"] == "B36TP Bonanza"
    assert results[1]["engine_count"] == 1
    assert results[1]["engine_type"] == "PISTON"


def test_variant_scan_real_dir():

    scanner = MSFSScanner()

    directory_path = "D:/MSFS_ADDONS/2024/AIRCRAFTS/bksq-aircraft-bonanzapro"
    target_path = Path(directory_path)

    # Test
    results = scanner.scan_directory(target_path, True)
    assert len(results) == 3
    assert results[0]["module_name"] == "bksq-aircraft-bonanzapro::bksq-aircraft-bonanzapro"
    assert results[0]["developer"] == "Black Square"
    assert results[0]["icao_code"] == "BE36"
    assert results[0]["manufacturer"] == "BEECHCRAFT"
    assert results[0]["type"] == "AIRPLANE"
    assert results[0]["aircraft_name"] == "A36 Bonanza"
    assert results[0]["engine_count"] == 1
    assert results[0]["engine_type"] == "PISTON"
    assert results[1]["module_name"] == "bksq-aircraft-bonanzapro::bksq-aircraft-bonanzaproturbine"
    assert results[1]["developer"] == "Black Square"
    assert results[1]["icao_code"] == "B36T"
    assert results[1]["manufacturer"] == "BEECHCRAFT"
    assert results[1]["type"] == "AIRPLANE"
    assert results[1]["aircraft_name"] == "B36TP Bonanza"
    assert results[1]["engine_count"] == 1
    assert results[1]["engine_type"] == "PISTON"
    assert results[2]["module_name"] == "bksq-aircraft-bonanzapro::bksq-aircraft-bonanzaproturbo"
    assert results[2]["developer"] == "Black Square"
    assert results[2]["icao_code"] == "BT36"
    assert results[2]["manufacturer"] == "BEECHCRAFT"
    assert results[2]["type"] == "AIRPLANE"
    assert results[2]["aircraft_name"] == "A36TC Bonanza"
    assert results[2]["engine_count"] == 1
    assert results[2]["engine_type"] == "PISTON"