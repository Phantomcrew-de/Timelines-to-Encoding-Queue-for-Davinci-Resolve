#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import ttk
import time
import sys
import imp
import json
import os
from datetime import datetime

DaVinciResolveScript = imp.load_source('DaVinciResolveScript', "/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py")
resolve = DaVinciResolveScript.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()

PRESET_FILE = "last_preset.json"

settings_keys = [
    "ExportVideo", "VideoCodec", "Format", "VideoBitRate", "ResolutionWidth",
    "ResolutionHeight", "FrameRate", "QualityEnable", "QualitySetting",
    "ExportAudio", "AudioCodec", "AudioBitRate", "AudioSampleRate",
    "AudioBitDepth", "AudioChannel", "AudioFormat"
]

def run_rendering(settings, selected_timelines, log_callback, update_status_callback):
    project = settings["project"]
    if not project:
        log_callback("❌ Projekt nicht gefunden.\n")
        return

    log_callback("\n📁 Lade Projekt: %s\n" % project.GetName())

    if len(project.GetRenderJobList()) > 0:
        log_callback("🧹 Bestehende Renderjobs werden gelöscht.\n")
        project.DeleteAllRenderJobs()

    if settings.get("use_preset"):
        preset_name = settings.get("preset")
        project.LoadRenderPreset(preset_name)
        log_callback("🎛 Preset geladen: %s\n" % preset_name)
        for key in settings_keys:
            val = project.GetSetting(key)
            log_callback("    %s: %s\n" % (key, val))
    else:
        log_callback("🎞 Format: %s, Codec: %s\n" % (settings["format"], settings["codec"]))
        project.SetCurrentRenderFormatAndCodec(settings["format"], settings["codec"])

    log_callback("\n➕ Neue Renderjobs werden hinzugefügt:\n")
    total = len(selected_timelines)
    for idx, i in enumerate(selected_timelines):
        timeline = project.GetTimelineByIndex(i)
        if not timeline:
            continue
        project.SetCurrentTimeline(timeline)

        render_settings = {
            "SelectAllFrames": not bool(int(settings["use_in_out"])),
            "TargetDir": settings["output_dir"],
            "CustomName": timeline.GetName()
        }

        if not settings.get("use_preset"):
            render_settings.update({
                "FormatWidth": int(settings["width"]),
                "FormatHeight": int(settings["height"]),
                "FrameRate": float(settings["framerate"]),
                "VideoBitRate": settings.get("bitrate", 20000000)
            })

        project.SetRenderSettings(render_settings)
        project.AddRenderJob()
        log_callback(" → %s hinzugefügt\n" % timeline.GetName())
        update_status_callback(idx, "Vorbereitet")

    if settings.get("start_render", False):
        log_callback("\n🚀 Rendering wird gestartet...\n")
        start_time = time.time()
        project.StartRendering(isInteractiveMode=True)

        while project.IsRenderingInProgress():
            time.sleep(1)

        end_time = time.time()
        elapsed = int(end_time - start_time)
        log_callback("✅ Rendering abgeschlossen.\n")
        log_callback("🕒 Dauer: %d Sekunden\n" % elapsed)
        log_callback("⏱ Start: %s\n" % datetime.fromtimestamp(start_time).strftime("%H:%M:%S"))
        log_callback("⏱ Ende: %s\n" % datetime.fromtimestamp(end_time).strftime("%H:%M:%S"))
        for idx in range(total):
            update_status_callback(idx, "Fertig")

class RenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Render-Einstellungen")

        self.current_project = project
        self.render_presets = project.GetRenderPresetList() if project else []

        tk.Label(master, text="Render-Preset:").grid(row=0, column=0, sticky='e')
        self.preset_var = tk.StringVar()
        self.preset_menu = tk.OptionMenu(master, self.preset_var, *self.render_presets)
        self.preset_menu.grid(row=0, column=1, columnspan=2, sticky='w')

        tk.Label(master, text="Timeline-Suchmuster:").grid(row=1, column=0, sticky='e')
        self.search_pattern = tk.Entry(master)
        self.search_pattern.grid(row=1, column=1)
        tk.Button(master, text="Timelines filtern", command=self.select_timelines_by_pattern).grid(row=1, column=2)

        self.timeline_vars = {}
        self.status_labels = []
        self.timeline_frame = tk.LabelFrame(master, text="Timelines")
        self.timeline_frame.grid(row=2, column=0, columnspan=3, pady=10)
        self.timeline_canvas = tk.Canvas(self.timeline_frame, height=200, width=500)
        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.timeline_frame, orient="vertical", command=self.timeline_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.inner_frame = tk.Frame(self.timeline_canvas)
        self.inner_frame.bind("<Configure>", lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all")))
        self.timeline_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.load_timelines()

        tk.Label(master, text="Speicherort:").grid(row=3, column=0, sticky='e')
        self.output_dir = tk.Entry(master, width=40)
        self.output_dir.grid(row=3, column=1)
        tk.Button(master, text="Durchsuchen", command=self.browse_dir).grid(row=3, column=2)

        self.use_in_out = tk.IntVar()
        tk.Checkbutton(master, text="Timeline In/Out Marker verwenden", variable=self.use_in_out).grid(row=4, column=0, columnspan=2)

        self.progress = ttk.Progressbar(master, orient="horizontal", mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="we", padx=5)

        tk.Button(master, text="Rendern starten", command=self.on_start).grid(row=6, column=1, pady=10)

        self.log_output = tk.Text(master, height=10, width=80)
        self.log_output.grid(row=7, column=0, columnspan=3)
        self.log_output.config(state="disabled")

    def log(self, message):
        self.log_output.config(state="normal")
        self.log_output.insert(tk.END, message)
        self.log_output.see(tk.END)
        self.log_output.config(state="disabled")

    def browse_dir(self):
        directory = tkFileDialog.askdirectory()
        if directory:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, directory)

    def load_timelines(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.timeline_vars = {}
        self.status_labels = []
        self.current_timelines = {}
        if not self.current_project:
            return
        timeline_count = self.current_project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            tl = self.current_project.GetTimelineByIndex(i)
            if tl:
                name = tl.GetName()
                var = tk.IntVar()
                row = tk.Frame(self.inner_frame)
                cb = tk.Checkbutton(row, text=name, variable=var, width=60, anchor="w")
                cb.pack(side="left")
                status = tk.Label(row, text="Warte", width=10)
                status.pack(side="right")
                row.pack(fill="x")
                self.timeline_vars[i] = var
                self.current_timelines[i] = name
                self.status_labels.append(status)

    def select_timelines_by_pattern(self):
        pattern = self.search_pattern.get().lower()
        for i, name in self.current_timelines.items():
            if pattern in name.lower():
                self.timeline_vars[i].set(1)

    def update_status(self, index, status_text):
        if 0 <= index < len(self.status_labels):
            self.status_labels[index].config(text=status_text)
        self.progress['value'] = (index + 1) * 100.0 / len(self.status_labels)

    def on_start(self):
        selected_timelines = [i for i, var in self.timeline_vars.items() if var.get() == 1]
        if not selected_timelines:
            tkMessageBox.showwarning("Warnung", "Bitte mindestens eine Timeline auswählen.")
            return
        if not self.output_dir.get():
            tkMessageBox.showerror("Fehler", "Bitte Speicherort angeben.")
            return

        settings = {
            "output_dir": self.output_dir.get(),
            "use_in_out": self.use_in_out.get(),
            "start_render": True,
            "use_preset": bool(self.preset_var.get()),
            "preset": self.preset_var.get(),
            "project": self.current_project
        }

        run_rendering(settings, selected_timelines, self.log, self.update_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = RenderGUI(root)
    root.mainloop()

