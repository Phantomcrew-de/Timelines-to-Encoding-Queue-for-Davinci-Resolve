==============================
INSTALLING ENCODINGMANAGER MANUALLY IN DAVINCI RESOLVE
==============================

Copy *.py files to "/Users/$USER/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit" 

If the script does not appear in the "Workspace > Scripts" menu,
you can run it manually using the DaVinci Resolve Console.

Follow these steps:

------------------------------
1. OPEN THE CONSOLE
------------------------------
- Launch DaVinci Resolve
- Go to the top menu:
  Workspace > Console

A small console window will appear, usually at the bottom of your screen.

------------------------------
2. SWITCH TO PYTHON 3
------------------------------
- py3
------------------------------
3. COPY THE SCRIPT CONTENT
------------------------------
- Open the file `Encodingmanager_XX.py` in a text editor like Notepad
  (replace `XX` with your language code: DE, EN, IT, ES, FR, CS, PL, NL)

- Select all contents (Ctrl+A) and copy it (Ctrl+C)

- Paste the entire script into the Console (Ctrl+V)

- Press ENTER

The script will now execute.

------------------------------
SUPPORTED LANGUAGES
------------------------------
1 - German (DE)
2 - English (EN)
3 - Italian (IT)
4 - Spanish (ES)
5 - French (FR)
6 - Czech (CS)
7 - Polish (PL)
8 - Dutch (NL)

------------------------------
TROUBLESHOOTING
------------------------------
- If nothing happens, make sure you've typed `py3 or python` first.
- Make sure you copied the **entire** content of the `.py` file.
- The script must be compatible with Python 3 and contain valid syntax.
- No restart of DaVinci Resolve is required using this method.

------------------------------
Enjoy!
