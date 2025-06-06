#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
DaVinci Resolve Studio 20+ batch timeline renderer with UI.

Place this file in:
  Windows: C:\Users\%USERNAME%\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit

Run from: DaVinci Resolve menu > Workspace > Scripts > Edit > Encodingmanager_EN.py

This script WILL NOT work from the command line or VSCode!
"""

import sys
import os
import time
from datetime import datetime

# --- Robust DaVinci Resolve API Boot ---
try:
    import DaVinciResolveScript as bmd
except ImportError:
    print("ERROR: Run this script from inside DaVinci Resolve (Scripts menu, not command line).")
    sys.exit(1)

resolve = bmd.scriptapp("Resolve")
if not resolve:
    print("ERROR: Could not get Resolve scripting instance. Are you running from Scripts menu?")
    sys.exit(1)

fu = getattr(resolve, "Fusion", None)
if not callable(fu):
    print("ERROR: 'Fusion' property is missing or not callable. UI scripting requires Fusion to be enabled.")
    sys.exit(1)
fu = fu()
if fu is None:
    print("ERROR: Could not get Fusion object from Resolve scripting API.")
    sys.exit(1)

ui = getattr(fu, "UIManager", None)
if ui is None:
    print("ERROR: Could not get UIManager from Fusion. Your Resolve installation may be missing Fusion scripting support.")
    sys.exit(1)

try:
    disp = bmd.UIDispatcher(ui)
except Exception as e:
    print("ERROR: Could not create UIDispatcher:", str(e))
    sys.exit(1)

project_manager = resolve.GetProjectManager()
if not project_manager:
    print("ERROR: Could not get Project Manager from Resolve.")
    sys.exit(1)

project = project_manager.GetCurrentProject()
if not project:
    print("ERROR: No project is currently open in DaVinci Resolve.")
    sys.exit(1)

# --- Settings ---
settings_keys = [
    "ExportVideo", "VideoCodec", "Format", "VideoBitRate", "ResolutionWidth",
    "ResolutionHeight", "FrameRate", "QualityEnable", "QualitySetting",
    "ExportAudio", "AudioCodec", "AudioBitRate", "AudioSampleRate",
    "AudioBitDepth", "AudioChannel", "AudioFormat"
]

def ensure_ui_callable(obj, name):
    if not hasattr(obj, name):
        print(f"ERROR: ui has no attribute '{name}'. This DaVinci Resolve version may not support it.")
        sys.exit(1)
    fn = getattr(obj, name)
    if not callable(fn):
        print(f"ERROR: ui.{name} is not callable (it's {fn}).")
        sys.exit(1)
    return fn

def run_rendering(settings, selected_timelines, log_callback, update_status_callback):
    project = settings["project"]
    if not project:
        log_callback("❌ Project not found.\n")
        return

    log_callback("\n📁 Project: %s\n" % project.GetName())

    render_jobs = project.GetRenderJobList()
    if render_jobs and len(render_jobs) > 0:
        log_callback("🧹 Deleting existing render jobs.\n")
        project.DeleteAllRenderJobs()

    if settings.get("use_preset"):
        preset_name = settings.get("preset")
        if preset_name:
            project.LoadRenderPreset(preset_name)
            log_callback("🎛 Preset loaded: %s\n" % preset_name)
            for key in settings_keys:
                val = project.GetSetting(key)
                log_callback("    %s: %s\n" % (key, val))
    else:
        log_callback("🎞 Format: %s, Codec: %s\n" % (settings.get("format"), settings.get("codec")))
        project.SetCurrentRenderFormatAndCodec(settings.get("format"), settings.get("codec"))

    log_callback("\n➕ Adding render jobs:\n")
    total = len(selected_timelines)
    for idx, i in enumerate(selected_timelines):
        timeline = project.GetTimelineByIndex(i)
        if not timeline:
            continue
        project.SetCurrentTimeline(timeline)

        render_settings = {
            "SelectAllFrames": not bool(int(settings.get("use_in_out", 0))),
            "TargetDir": settings["output_dir"],
            "CustomName": timeline.GetName()
        }

        if not settings.get("use_preset"):
            render_settings.update({
                "FormatWidth": int(settings.get("width", 1920)),
                "FormatHeight": int(settings.get("height", 1080)),
                "FrameRate": float(settings.get("framerate", 25)),
                "VideoBitRate": settings.get("bitrate", 20000000)
            })

        project.SetRenderSettings(render_settings)
        project.AddRenderJob()
        log_callback(" → %s added\n" % timeline.GetName())
        update_status_callback(idx, "Prepared")

    if settings.get("start_render", False):
        log_callback("\n🚀 Starting rendering...\n")
        start_time = time.time()
        project.StartRendering(isInteractiveMode=True)
        while project.IsRenderingInProgress():
            time.sleep(1)
        end_time = time.time()
        elapsed = int(end_time - start_time)
        log_callback("✅ Rendering complete.\n")
        log_callback("🕒 Duration: %d seconds\n" % elapsed)
        log_callback("⏱ Start: %s\n" % datetime.fromtimestamp(start_time).strftime("%H:%M:%S"))
        log_callback("⏱ End: %s\n" % datetime.fromtimestamp(end_time).strftime("%H:%M:%S"))
        for idx in range(total):
            update_status_callback(idx, "Done")

def main():
    timeline_count = project.GetTimelineCount()
    timelines = []
    for i in range(1, timeline_count + 1):
        tl = project.GetTimelineByIndex(i)
        if tl:
            timelines.append((i, tl.GetName()))

    timeline_checkboxes = []
    status_labels = []
    timeline_vgroup = []
    for idx, name in timelines:
        cb = ensure_ui_callable(ui, "CheckBox")({"ID": f"tl_{idx}", "Text": name, "Checked": False, "Weight": 0})
        timeline_checkboxes.append(cb)
        status_lbl = ensure_ui_callable(ui, "Label")({"ID": f"status_{idx}", "Text": "Waiting", "Weight": 0})
        status_labels.append(status_lbl)
        timeline_vgroup.append(ensure_ui_callable(ui, "HGroup")([cb, status_lbl]))

    render_presets = project.GetRenderPresetList()

    window_layout = ensure_ui_callable(ui, "VGroup")([
        ensure_ui_callable(ui, "Label")({"Text": "Encoding Manager (Resolve Native UI)", "Alignment": {"AlignHCenter": True}, "Weight": 0}),
        ensure_ui_callable(ui, "HGroup")([
            ensure_ui_callable(ui, "Label")({"Text": "Render Preset:"}),
            ensure_ui_callable(ui, "ComboBox")({"ID": "preset_combo", "Editable": False, "Weight": 1, "CurrentIndex": 0,
                         "Items": render_presets}),
        ], {"Weight": 0}),
        ensure_ui_callable(ui, "HGroup")([
            ensure_ui_callable(ui, "Label")({"Text": "Output Directory:"}),
            ensure_ui_callable(ui, "LineEdit")({"ID": "output_dir", "PlaceholderText": "Select output directory...", "Weight": 2}),
            ensure_ui_callable(ui, "Button")({"ID": "browse_btn", "Text": "Browse", "Weight": 0}),
        ], {"Weight": 0}),
        ensure_ui_callable(ui, "CheckBox")({"ID": "use_io", "Text": "Use Timeline In/Out Markers", "Checked": False, "Weight": 0}),
        ensure_ui_callable(ui, "Label")({"Text": "Select Timelines to Render:"}),
        ensure_ui_callable(ui, "VGroup")(timeline_vgroup, {"ID": "timeline_vgroup", "Weight": 1, "Spacing": 2}),
        # ProgressBar replaced with Label for compatibility!
        ensure_ui_callable(ui, "Label")({"ID": "progress_label", "Text": "Progress: 0 / %d" % max(len(timelines), 1), "Weight": 0}),
        ensure_ui_callable(ui, "TextEdit")({"ID": "log", "ReadOnly": True, "Weight": 0, "MinimumHeight": 120}),
        ensure_ui_callable(ui, "HGroup")([
            ensure_ui_callable(ui, "Button")({"ID": "start_btn", "Text": "Start Rendering", "Weight": 0}),
            ensure_ui_callable(ui, "Button")({"ID": "quit_btn", "Text": "Quit", "Weight": 0}),
        ], {"Weight": 0}),
    ], {"Spacing": 8, "Weight": 1})

    dlg = disp.AddWindow({
        "WindowTitle": "Encoding Manager",
        "ID": "EncodingManagerWin",
        "Geometry": [100, 300, 600, 600],
        "WindowFlags": {"Window": True}
    }, window_layout)

    items = dlg.GetItems()
    log_widget = items["log"]
    progress_label = items["progress_label"]

    def log_message(msg):
        log_widget.Text = log_widget.Text + msg

    def update_status(idx, text):
        if idx < len(timeline_checkboxes):
            status = status_labels[idx]
            status.Text = text
            progress_label.Text = "Progress: %d / %d" % (idx + 1, max(len(timeline_checkboxes), 1))

    def browse_dir(ev):
        try:
            import PySide2
            from PySide2.QtWidgets import QFileDialog
            path = QFileDialog.getExistingDirectory(None, "Select Output Directory", os.path.expanduser("~"))
            if path:
                items["output_dir"].Text = path
        except Exception:
            log_message("📁 Cannot open OS file dialog in this environment.\n")

    def on_start(ev):
        selected = []
        for idx, cb in enumerate(timeline_checkboxes):
            if items[cb.ID].Checked:
                selected.append(timelines[idx][0])
        if not selected:
            log_message("Please select at least one timeline.\n")
            return
        output_dir = items["output_dir"].Text.strip()
        if not output_dir:
            log_message("Please specify an output directory.\n")
            return
        preset_idx = items["preset_combo"].CurrentIndex
        preset = render_presets[preset_idx] if 0 <= preset_idx < len(render_presets) else ""
        settings = {
            "output_dir": output_dir,
            "use_in_out": 1 if items["use_io"].Checked else 0,
            "start_render": True,
            "use_preset": bool(preset),
            "preset": preset,
            "project": project
        }
        for lbl in status_labels:
            lbl.Text = "Waiting"
        progress_label.Text = "Progress: 0 / %d" % max(len(timeline_checkboxes), 1)
        log_widget.Text = ""
        run_rendering(settings, selected, log_message, update_status)

    def on_close(ev):
        disp.ExitLoop()

    def on_quit(ev):
        dlg.Hide()
        disp.ExitLoop()

    # Bind events
    items["browse_btn"].Clicked = browse_dir
    items["start_btn"].Clicked = on_start
    dlg.On.Close = on_close
    items["quit_btn"].Clicked = on_quit

    dlg.Show()
    disp.RunLoop()
    dlg.Hide()

if __name__ == "__main__":
    main()