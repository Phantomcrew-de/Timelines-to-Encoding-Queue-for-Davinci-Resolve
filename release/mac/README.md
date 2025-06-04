**Render Manager for DaVinci Resolve – macOS Setup Instructions**

This directory contains two GUI-based render manager applications for DaVinci Resolve. You can launch them on macOS using the provided shell scripts.

### 📁 Files Included

* `run_encoding_manager_mac_a.sh` – Launcher for version A
* `search_in_timelines_and_encode_GUI_mac_a.py` – Main Python GUI for version A
* `run_encoding_manager_mac_b.sh` – Launcher for version B
* `search_in_timelines_and_encode_GUI_mac_b.py` – Main Python GUI for version B

### 🛠️ Installation & Setup

1. **Ensure All Files Are in the Same Folder**
   Each `.sh` file must be in the same folder as its corresponding `.py` file:

   * `run_encoding_manager_mac_a.sh` ⇨ `search_in_timelines_and_encode_GUI_mac_a.py`
   * `run_encoding_manager_mac_b.sh` ⇨ `search_in_timelines_and_encode_GUI_mac_b.py`

2. **Make the Shell Scripts Executable**
   Open a Terminal in the folder where the files are located and run:

   ```bash
   chmod +x run_encoding_manager_mac_a.sh
   chmod +x run_encoding_manager_mac_b.sh
   ```

3. **Run the Application**
   In the same Terminal window, launch one of the GUIs by running:

   ```bash
   ./run_encoding_manager_mac_a.sh
   ```

   or

   ```bash
   ./run_encoding_manager_mac_b.sh
   ```

   This will start the corresponding Python-based GUI interface using the DaVinci Resolve scripting API.

### 🧩 Requirements

* DaVinci Resolve (Studio version recommended)
* Python 3 installed and accessible via `python3`
* DaVinci Resolve Scripting API (automatically referenced in the script)

### ℹ️ Notes

* The GUIs allow you to select timelines, set rendering options, and start batch render jobs.
* Version B supports loading and using custom render presets from DaVinci Resolve.

