#!/usr/bin/env python
#Julius Video 2023
#Runs inside Davinci Resolve -> Workspace -> Console -> Python 3
#Modify the variable in nextline ("v05") to a string you want to search for. Then Copy and paste all text to console.

searchintimelinenamesfor = "_v05"

import time
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
print (project.GetName())
print ("Adding Timelines to Queue:")
n = project.GetTimelineCount()
s = 0
i = 1
timelineindex = 1
time.sleep(0.1)
project.DeleteAllRenderJobs()
while i <= n:
    time.sleep(0.1)
    timelineindex = project.GetTimelineByIndex(i)
    project.SetCurrentTimeline(timelineindex)
    timeline = project.GetCurrentTimeline()
    if timeline.GetName() != None and searchintimelinenamesfor in timeline.GetName():
        time.sleep(0.1)
        project.SetRenderSettings({
		    "SelectAllFrames": True,
		    "FormatWidth": 1920,
		    "FormatHeight": 1080,
        })
        pid = project.AddRenderJob()
        print ("Add:  Timeline " + str(i) + " of " + str(n) + " -> " + timeline.GetName())
        time.sleep(0.2)
        i = i + 1
    else:
        print("Skip: Timeline " + str(i) + " of " + str(n) + " -> " + timeline.GetName())
        i = i + 1    
print("All Timelines Added")
project.StartRendering(isInteractiveMode = True)
print("Rendering in Progress...")
       
    
