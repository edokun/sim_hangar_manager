import json
from pathlib import Path
from sim_hangar_manager.scanners.msfs_scanner import MSFSScanner


def test_can_scan_returns_false_for_empty_or_non_existent_directory(tmp_path: Path):

    scanner = MSFSScanner()

    # Case 1: Non-Existent Path
    non_existent_path = tmp_path / "does_not_exist"
    assert scanner.can_scan(non_existent_path) is False

    # Case 2: Emppty Path
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
    assert results[0]["name"] == "Piper PA-24 Comanche 250"
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