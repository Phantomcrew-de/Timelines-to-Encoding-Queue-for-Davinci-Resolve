## Timelines to Encoding Queue for Davinci Resolve

This script automaticly adds your timelines of your projects to the encoding queue. Search in names of timelines for choosing which timelines you need to encode.

The main script (search_in_timelines_and_encode.py) runs only in the davinci resolve studio version.
Installation
For Linux (Ubuntu/Zorin, Davinci Resolve Studio):

You need to install python 2.7.18 on your system. Alternatively, install anaconda and create a conda environment with python 2.7 ```chmod +x run_search_and_encode.sh```
Run
#### For Linux (Ubuntu/Zorin, Davinci Resolve Studio):

Run davinci resolve and open your project.
Go to the Deliver page and change the encoding settings to your custom output format
After changing Video and Audio settings you go to File and change Filename use to Timeline name
Open your terminal and run the script with: ```python2 ./search_in_timelines_and_encode_GUI.py``` or ```./run_search_and_encode.sh```
You can run the script several times with multiple project files. You need to activate Show all projects at the three dots in the top right corner of your Encoding Queue

#### For Linux (Ubuntu/Zorin, Davinci Resolve non-Studio):

Open search_in_timelines_and_encode_non_studio.py file with editor.
Modify the string of the variable searchintimelinenamesfor = "_v05" to a string you want to search for.
Copy the text and past it inside Davinci Resolve > Workspace > Console > Python 3
Press enter

#### Example:
[![Watch the video](https://img.youtube.com/vi/iSUb798p8DM/default.jpg)](https://youtu.be/iSUb798p8DM) 

### 🐍 Python Setup

This script requires Python. Depending on your DaVinci Resolve version:

- **DaVinci Resolve Studio** supports **Python 2**.
- **DaVinci Resolve (Free)** supports **Python 3**.

You only need one of them installed on your system. If you're unsure, install **Python 3**.

#### 📅 Install Python
##### Windows

    Download the appropriate version:

        Python 2: https://www.python.org/downloads/release/python-2718/

        Python 3: https://www.python.org/downloads/windows/

        Make sure to check the box "Add Python to PATH" during installation.

##### Linux (Ubuntu/Debian)

    Python 2:

```sudo apt update```
```sudo apt install python2```

Python 3:
    ```sudo apt update```
    ```sudo apt install python3```

🏠 Install Tkinter GUI (required for this script)

##### macOS
Python 3:
```brew install python-tk```

##### Windows
kinter is typically included by default. If you experience issues:
For Python 2: Reinstall from python.org
For Python 3: Use the official installer from python.org, ensuring the tcl/tk and IDLE feature is selected.

##### Linux (Ubuntu/Debian)
Python 2:
```sudo apt install python-tk```

Python 3:
```sudo apt install python3-tk```
