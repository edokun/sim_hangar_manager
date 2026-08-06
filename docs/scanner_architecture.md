# Add-ons / Modules Scanner Architecture

The **Hangar Scanner Subsystem** uses an extensible, plugin-oriented design based on the **Strategy** and **Factory** design patterns. This architecture decouples the directory discovery and parsing logic from the rest of the core application domain.

By relying on explicit abstract interfaces, adding support for new flight simulators (e.g., *X-Plane*, *DCS World*, or *MSFS 2024*) requires zero modifications to existing scanning or database persistence code—adhering strictly to the **Open/Closed Principle**.

---

## 🏗 Architecture Overview

The scanner architecture consists of three core components:

1. **`BaseSimulatorScanner`** (`src/sim_hangar_manager/scanners/base_scanner.py`):
An Abstract Base Class (ABC) serving as the contract interface. Every simulator scanner must implement its methods.
2. **Concrete Scanners** (e.g., `MSFS2020Scanner`):
Simulator-specific classes that inspect folder structures, read proprietary file metadata (such as `manifest.json` or `.lua` definitions), and extract normalized aircraft attributes.
3. **`HangarScannerService`** (`src/sim_hangar_manager/service/scanner_service.py`):
The central orchestrator and registry. It receives a target directory path, identifies which concrete scanner can handle it, executes the scan, and returns normalized data to the application layer.

---

## 🚀 How to Extend the Scanner for a New Simulator

To implement support for a new flight simulator or custom add-on folder layout, follow these steps:

1. **Create a New Scanner Module:**
Create a new Python file inside the `scanners` directory (for example, `xplane_scanner.py` or `dcs_scanner.py`).


2. **Inherit from BaseSimulatorScanner:**
Define a class that extends `BaseSimulatorScanner` and implement all abstract properties and methods.

* **`simulator_name`**: Returns a unique identifier string for the target simulator platform.
* **`can_scan(directory_path)`**: Evaluates whether the given directory matches the target simulator's folder structure (e.g., checking for specific subfolders, manifest formats, or configuration files). Returns a `bool`.
* **`scan_directory(directory_path)`**: Parses the add-on packages and returns a list of normalized dictionary payloads.


3. **Register the New Scanner in ScannerService:**
Add an instance of your new scanner class to the internal registry inside `HangarScannerService.__init__()` or register it dynamically using the `register_scanner()` method.


---

## 💻 Code Example: Implementing a Custom Scanner

Below is an example illustrating how to implement a scanner for **X-Plane**:

```python
# src/sim_hangar_manager/scanners/xplane_scanner.py

from pathlib import Path
from typing import List, Dict, Any
from sim_hangar_manager.scanners.base_scanner import BaseSimulatorScanner

class XPlane12Scanner(BaseSimulatorScanner):

    @property
    def simulator_name(self) -> str:
        return "X-Plane 12"

    def can_scan(self, directory_path: Path) -> bool:
        """
        Inspects the directory for X-Plane indicators (e.g., presence of .acf files).
        """
        if not directory_path.exists() or not directory_path.is_dir():
            return False
        
        # Check if any subfolder contains an X-Plane aircraft configuration file
        acf_files = list(directory_path.glob("*/*.acf"))
        return len(acf_files) > 0

    def scan_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        detected_modules = []

        for folder in directory_path.iterdir():
            if not folder.is_dir():
                continue

            # Look for aircraft configuration files (.acf)
            acf_files = list(folder.glob("*.acf"))
            if acf_files:
                # Normalize metadata into a raw dictionary standard
                raw_data = {
                    "module_name": folder.name,
                    "name": folder.name.replace("_", " ").title(),
                    "developer": "Unknown Developer",
                    "simulator": self.simulator_name,
                    "module_file_location_1": str(folder.absolute()),
                    "notes": f"Scanned automatically from X-Plane directory: {folder.name}"
                }
                detected_modules.append(raw_data)

        return detected_modules

```

---

## ⚙️ Registering the New Scanner

Update `HangarScannerService` to make the orchestrator aware of your new scanner:

```python
# src/sim_hangar_manager/service/scanner_service.py

from sim_hangar_manager.scanners.msfs_scanner import MSFS2020Scanner
from sim_hangar_manager.scanners.xplane_scanner import XPlane12Scanner

class HangarScannerService:
    def __init__(self):
        # Register all available scanner implementations here
        self._scanners: List[BaseSimulatorScanner] = [
            MSFS2020Scanner(),
            XPlane12Scanner(), # <--- New scanner added
        ]

    def register_scanner(self, scanner: BaseSimulatorScanner):
        """Allows dynamic runtime registration of third-party scanners."""
        self._scanners.append(scanner)

```

---

## 🛡 Batch Processing & Robustness Best Practices

When writing a new scanner implementation, adhere to the following operational guidelines:

* **Non-Blocking Parsing Errors:** Always wrap file reading and parsing logic (e.g., `json.load()` or file I/O operations) inside `try...except` blocks. A single corrupted add-on folder or unreadable manifest must **never** break the batch execution for remaining items.
* **Metadata Normalization:** Ensure keys returned by `scan_directory()` align with the payload expected by `ObjectMapper.to_aircraft_model()`. Missing optional fields should default to safe fallbacks or `None`.
* **Path Resolution:** Always use Python’s native `pathlib.Path` objects for cross-platform compatibility across Windows, macOS, and Linux.

---