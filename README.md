# Timelines to Encoding Queue – Render Manager for DaVinci Resolve

This tool acts as a Timeline Render Manager for DaVinci Resolve, allowing you to automatically add multiple timelines to the encoding queue.
You can filter timelines by name and either use presets or define custom encoder settings like bitrate, format, or resolution.

> 🖥 Supports **DaVinci Resolve Studio**
> 
> ✅ GUI for both **Windows, macOS (Python 3)** and **Linux (Python 2.7)** included

---

## 🔧 Features

- Filter timelines by name (e.g., `_v01`, `Final`, `cut1`)
- Add multiple timelines to the render queue with one click
- GUI for selecting projects, timelines, render presets, and output settings
- Custom resolution, bitrate, codec & format possible
- Logging status
- Saves previous settings

---

## 📁 Folder Structure

- `release/`
  - `linux/` → Python 2 scripts for Linux (GUI & shell start scripts)
  - `mac/` → Python 3 scripts for macOS (GUI & shell start scripts)
  - `win/` → Python 3 scripts for Windows (stable versions with GUI)
  - `win/nightly/` → Python 3 scripts for Windows (nightly versions with GUI)
- `Screenshots/` → GUI screenshots for documentation
- `alternativ/` → Experimental alternative GUI versions for Linux
- Root contains quick launchers & legacy scripts.

---

## 💻 Installation

### Windows (Python 3.x, DaVinci Resolve)

1. **Install Python 3.x**: https://www.python.org/downloads/
2. Install `tkinter` via:

    ```bash
    pip install tk
    ```

3. Go to `release/win/` and use e.g.:
    - `nightly/search_in_timelines_and_encode_GUI_py3_win_nightly_02b_EN.py` (English) for more feature GUI
    - Optional: Use `Encodingmanager_EN.py` for stable GUI

4. Run the script **inside DaVinci Resolve** via Console:
    - Menu: `Workspace > Console > Python 3`
    - Paste the content of the .py script and press Enter

---

### Mac OS X (Python 3.x, DaVinci Resolve Studio)


* `run_encoding_manager_mac_a.sh` – Launcher for version A
* `search_in_timelines_and_encode_GUI_mac_a.py` – Main Python GUI for version A
* `run_encoding_manager_mac_b.sh` – Launcher for version B
* `search_in_timelines_and_encode_GUI_mac_b.py` – Main Python GUI for version B

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
---
### Linux (Python 2.7, DaVinci Resolve Studio)

1. Install dependencies:

    ```bash
    sudo apt install python2 python-tk
    ```

2. Navigate to `release/linux/` and run:

```bash
./run_encoding_manager_a.sh
```

This calls `search_in_timelines_and_encode_GUI.py`, the full GUI version.
Alternatively, run manually:

```bash
python2 search_in_timelines_and_encode_GUI_alternativ_d.py
```

If you use Anaconda:

```bash
conda create -n drencode python=2.7
conda activate drencode
python search_in_timelines_and_encode_GUI_alternativ_d.py
```

---

## ▶ How to Use

1. Open **DaVinci Resolve Studio** and load your project.
2. Go to the **Deliver** page.
3. Set render settings (format, codec, etc.)
4. Set filename option to **Timeline name**
5. Run the script (GUI appears)
6. Choose project, output folder, render preset or custom config
7. Enter search term (e.g., `_v05`) → Click **Filter**
8. Select timelines → Click **Add to Queue**
9. Click **Start Rendering**

---


## 🧩 Dependencies

| Platform | Version | Required | Notes |
|---------|---------|----------|-------|
| Python 3 | Windows | ✅ | Required for Windows GUIs |
| Python 2.7 | Linux | ✅ | Needed for older DaVinci scripting |
| tkinter | All | ✅ | Install with Python or OS package manager |

---

## 📁 Project Variants

| Script | Platform | Language | UI | Path |
|--------|----------|----------|----|------|
| `search_in_timelines_and_encode_GUI_py3_win_nightly_02b_EN.py` | Windows | EN | ✅ | `release/win/nightly/` |
| `Encodingmanager_EN.py` | Windows | EN | ✅ | `release/win/nightly/` |
| `search_in_timelines_and_encode_GUI_mac_a.py` | macOS | DE | ✅ | `release/mac/` |
| `search_in_timelines_and_encode_GUI_mac_b.py` | macOS | DE | ✅ | `release/mac/` |
| `search_in_timelines_and_encode_GUI_alternativ_d.py` | Linux | DE | ✅ | `release/linux/` |
| `search_in_timelines_and_encode_non_studio.py` | Linux | EN | ❌ | root (legacy) |

---

## 📺 Demo

[![YouTube Demo](http://img.youtube.com/vi/iSUb798p8DM/0.jpg)](http://www.youtube.com/watch?v=iSUb798p8DM)

---
## 📷 Screenshots

<table>
  <tr>
    <td align="center" width="25%">
      <img src="Screenshots/search_in_timelines_and_encode_GUI_py3_win_nightly_02b_EN.PNG" width="250px"><br>
      <strong>GUI (Windows, EN)</strong>
    </td>
    <td align="center" width="25%">
      <img src="Screenshots/search_in_timelines_and_encode_GUI_mac_a.png" width="250px"><br>
      <strong>GUI (macOS)</strong>
    </td>
    <td align="center" width="25%">
      <img src="Screenshots/search_in_timelines_and_encode_GUI_d_screenshot.png" width="250px"><br>
      <strong>GUI (Linux)</strong>
    </td>
    <td align="center" width="25%">
      <img src="Screenshots/Encodingmanager_py3_win_release_EN_2025_05_03.PNG" width="250px"><br>
      <strong>DaVinci Resolve Console</strong>
    </td>
  </tr>
</table>



---

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).  
You are free to use, modify, and distribute it — as long as you share your changes under the same license.

---

## 🤝 Author

Made with ❤️ by Julius – [phantomcrew.de](https://phantomcrew.de/)

For issues or suggestions, open a GitHub issue or visit [phantomcrew.de](https://phantomcrew.de)
