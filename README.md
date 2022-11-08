# Timelines to Encoding Queue for Davinci Resolve
This script automaticly adds your timelines of your projects to the encoding queue. 
Search in the names of the timelines for choosing which timelines you need to encode.

The main script (search_in_timelines_and_encode.py) runs only in the davinci resolve studio version.
## Installation
### For Linux (Ubuntu/Zorin):
You need to install python 2.7.18 on your system. Alternatively, install anaconda and create a conda environment with python 2.7 

## Run
### For Linux (Ubuntu/Zorin):
1. Run davinci resolve and open your project. 
2. Go to the **Deliver** page and change the encoding settings to your custom output format
3. After changing **Video** and **Audio** settings you go to **File** and change **Filename use** to **Timeline name**
4. Open your terminal and run the script with: **python ./search_in_timelines_and_encode.py**
5. You can run the script several times with multiple project files. You need to activate **Show all projects** at the three dots in the top right corner of your **Encoding Queue**
