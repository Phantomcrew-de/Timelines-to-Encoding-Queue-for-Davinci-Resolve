#!/usr/bin/env python2
#Timelines to Encoding Queue Version 1.0.3 runs on Linux (Ubuntu/Zorin OS 16.1) Python 2.7.18 Davinci Resolve Studio 18.0.2
from ast import IsNot
import imp
from operator import is_not
DaVinciResolveScript = imp.load_source('DaVinciResolveScript', "/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py")
RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting/"
RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
import sys
import time
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")



project_manager = resolve.GetProjectManager()
print("\033[0;37;40m \n************************************************************************")
print("* Advanced Encoding Queue for DaVinci Resolve Studio by Phantomcrew.de *")
print("************************************************************************\n\n")
print("Choose a Project(copy & paste):\n\033[1;37;40m")
print ("\n".join(project_manager.GetProjectListInCurrentFolder()))
ProjectName = raw_input("\033[0;37;40m\nEnter projectname or press Enter: ")
if ProjectName is "":
    project = project_manager.GetCurrentProject()
else:
    project = project_manager.LoadProject(ProjectName)
print ("\033[1;32;40m\n --> " + project.GetName() + " is open\n\033[0;37;40m")
n = project.GetTimelineCount()
i = 1
enci = 0
Table = project.GetRenderJobList()
for colum in Table:
    enci = enci + 1
deletequeue = "n"
if enci > 0:
    deletequeue = raw_input("\033[1;37;40m !!! "+str(enci) + " jobs \033[1;33;40mare left in the render queue.\033[1;37;40m Do you want to delete them? (y/n)\033[0;37;40m")
enci = 0
#print (project.GetPresetList())
advancedsettings = raw_input(" Advanced Settings? (y/n): ")
if advancedsettings is "y":
    targetdir = raw_input(" Output directory: ")
    videowidth = input(" Resolution width (e.g. 1920 or 3840): ")
    videohight = input(" Resolution hight (e.g. 1080 or 2160): ")
    framerate = input(" Framerate  (e.g. 23.976, 24, 25, 30): ")
    useinandout = raw_input(" Use Timeline in and out marker (y/n): ")
timelineindex = 1
timelinesearch = raw_input(" Enter a custom searchterm for timelines (e.g. _v002) or press Enter: ")
startrendering = raw_input(" Do you want to render all after adding timelines (y/n)")
#timelinesearch = str(timelinesearch)
print ("Deleting jobs in queue")
if deletequeue is "y":
    project.DeleteAllRenderJobs()
print ("Adding new jobs to queue")
time.sleep(0.1)
while i <= n:
    time.sleep(0.1)
    timelineindex = project.GetTimelineByIndex(i)
    project.SetCurrentTimeline(timelineindex)
    timeline = project.GetCurrentTimeline()
    if timeline.GetName() != None and timelinesearch in timeline.GetName():
        time.sleep(0.1)
        if advancedsettings is "y":
            if useinandout is "y":
                project.SetRenderSettings({
                    "SelectAllFrames": False,
                    "TargetDir" : targetdir,
                    "FormatWidth": videowidth,
                    "FormatHeight": videohight,
                    "FrameRate": framerate,
                    })
            else:
                project.SetRenderSettings({
                    "SelectAllFrames": True,
                    "TargetDir" : targetdir,
                    "FormatWidth": videowidth,
                    "FormatHeight": videohight,
                    "FrameRate": framerate,
                    })
        else:
            project.SetRenderSettings({
                "SelectAllFrames": True,
                })
        pid = project.AddRenderJob()
        print ("\033[1;32;40m  add:  Timeline " + "%02d" % (i,) + " of " + "%02d" % (n,) + " -> " + timeline.GetName())
        time.sleep(0.2)
        i = i + 1
    else:
        print("\033[1;35;40m  skip: Timeline " + "%02d" % (i,) + " of " + "%02d" % (n,) + " -> " + timeline.GetName())
        i = i + 1    
Table = project.GetRenderJobList()

for colum in Table:
    enci = enci + 1
print("\033[0;37;40m\n --> " + str(enci) + " of " + str(i-1) + " timelines are added to the render queue \n\n")
if startrendering is "y":
    print ("Start Rendering")
    project.StartRendering(isInteractiveMode = True)
    timer = 0    
    waitanimation = "|/-\\"
    while project.IsRenderingInProgress() is True:
        time.sleep(1)
        timer = timer + 1
        if str(timer/60) is "0":
            print("Rendering in progress for "  + str(timer) + " sec " + waitanimation[timer % len(waitanimation)] + "\r")          
        else:
            print("Rendering in progress for "  + str(timer/60) + " min " + waitanimation[timer % len(waitanimation)] + "   \r" )
        sys.stdout.write("\033[F")
    
    if str(timer/60) is "0":
        print("Rendering was done in " + str(timer) + " seconds       ")          
    else:
        print("Rendering was done in " + str(timer/60) + " minutes       ")
       
    
