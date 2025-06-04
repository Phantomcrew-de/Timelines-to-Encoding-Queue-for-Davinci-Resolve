#!/bin/bash

# Verzeichnis des Skripts ermitteln
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve-Scripting-Modulpfad setzen
export PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules:$PYTHONPATH"

# Python-Skript relativ zum Skriptverzeichnis ausführen
python3 "$SCRIPT_DIR/search_in_timelines_and_encode_GUI_mac_a.py"
