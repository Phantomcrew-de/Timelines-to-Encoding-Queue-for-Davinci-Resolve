#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from tkinter import ttk
import time
import sys
import importlib.util
import json
import os
from datetime import datetime

spec = importlib.util.spec_from_file_location("DaVinciResolveScript", "C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules/DaVinciResolveScript.py")
DaVinciResolveScript = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DaVinciResolveScript)
import DaVinciResolveScript as bmd
resolve = bmd.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()

settings_keys = [
    "ExportVideo", "VideoCodec", "Format", "VideoBitRate", "ResolutionWidth",
    "ResolutionHeight", "FrameRate", "QualityEnable", "QualitySetting",
    "ExportAudio", "AudioCodec", "AudioBitRate", "AudioSampleRate",
    "AudioBitDepth", "AudioChannel", "AudioFormat"
]

def add_render_jobs(settings, selected_timelines, log_callback, update_status_callback):
    project = settings["project"]
    if not project:
        log_callback("\u274c Projekt nicht gefunden.\n")
        return

    log_callback("\n\ud83d\udcc1 Lade Projekt: %s\n" % project.GetName())

    if settings.get("clear_existing", True) and project.GetRenderJobList():
        log_callback("\ud83e\ude79 Bestehende Renderjobs werden gel\u00f6scht.\n")
        project.DeleteAllRenderJobs()

    if settings.get("use_preset"):
        preset_name = settings.get("preset")
        project.LoadRenderPreset(preset_name)
        log_callback("\ud83c\udf1b Preset geladen: %s\n" % preset_name)
    else:
        project.SetCurrentRenderFormatAndCodec(settings["format"], settings["codec"])

    log_callback("\n\u2795 Neue Renderjobs werden hinzugef\u00fcgt:\n")
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
        log_callback(" \u2192 %s hinzugef\u00fcgt\n" % timeline.GetName())
        update_status_callback(idx, "Vorbereitet")

def start_rendering(project, log_callback, update_status_callback, total_jobs):
    log_callback("\n\ud83d\ude80 Rendering wird gestartet...\n")
    start_time = time.time()
    project.StartRendering(isInteractiveMode=True)
    while project.IsRenderingInProgress():
        time.sleep(1)
    end_time = time.time()
    elapsed = int(end_time - start_time)
    log_callback("\u2705 Rendering abgeschlossen.\n")
    log_callback("\ud83d\udd52 Dauer: %d Sekunden\n" % elapsed)
    log_callback("\u23f1 Start: %s\n" % datetime.fromtimestamp(start_time).strftime("%H:%M:%S"))
    log_callback("\u23f1 Ende: %s\n" % datetime.fromtimestamp(end_time).strftime("%H:%M:%S"))
    for idx in range(total_jobs):
        update_status_callback(idx, "Fertig")

class RenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Render Settings")

        self.current_project = project

        tk.Label(master, text="Projekt:").grid(row=0, column=0, sticky='e')
        self.project_var = tk.StringVar()
        self.project_menu = tk.OptionMenu(master, self.project_var, "")
        self.project_menu.grid(row=0, column=1, sticky='w')
        self.project_var.trace("w", lambda *args: self.on_project_change())
        self.render_presets = project.GetRenderPresetList() if project else []

        tk.Label(master, text="Render Preset:").grid(row=0, column=0, sticky='e')
        self.preset_var = tk.StringVar()
        if self.render_presets:
            self.preset_var.set(self.render_presets[0])
        self.preset_menu = tk.OptionMenu(master, self.preset_var, *self.render_presets)
        self.preset_menu.grid(row=0, column=1, columnspan=2, sticky='w')

        tk.Label(master, text="Timeline Search Pattern:").grid(row=1, column=0, sticky='e')
        self.search_pattern = tk.Entry(master)
        self.search_pattern.grid(row=1, column=1)
        tk.Button(master, text="Filter Timelines", command=self.select_timelines_by_pattern).grid(row=1, column=2)

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

        tk.Label(master, text="Output Directory:").grid(row=3, column=0, sticky='e')
        self.output_dir = tk.Entry(master, width=40)
        self.output_dir.grid(row=3, column=1)
        tk.Button(master, text="Browse", command=self.browse_dir).grid(row=3, column=2)

        self.use_in_out = tk.IntVar()
        tk.Checkbutton(master, text="Use Timeline In/Out Markers", variable=self.use_in_out).grid(row=4, column=0, columnspan=2)

        self.progress = ttk.Progressbar(master, orient="horizontal", mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="we", padx=5)

        tk.Button(master, text="\u2795 Zur Warteschlange hinzuf\u00fcgen", command=self.on_add_jobs).grid(row=6, column=0, pady=10)
        tk.Button(master, text="\ud83d\ude80 Jetzt rendern", command=self.on_start_rendering).grid(row=6, column=2, pady=10)

        self.log_output = tk.Text(master, height=10, width=80)
        self.log_output.grid(row=7, column=0, columnspan=3)
        self.log_output.config(state="disabled")
        self.load_projects()

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
                status = tk.Label(row, text="Waiting", width=10)
                status.pack(side="right")
                row.pack(fill="x")
                self.timeline_vars[i] = var
                self.current_timelines[i] = name
                self.status_labels.append(status)

    def select_timelines_by_pattern(self):
        pattern = self.search_pattern.get().lower()
        for i, name in list(self.current_timelines.items()):
            if pattern in name.lower():
                self.timeline_vars[i].set(1)

    def update_status(self, index, status_text):
        if 0 <= index < len(self.status_labels):
            self.status_labels[index].config(text=status_text)
        self.progress['value'] = (index + 1) * 100.0 / len(self.status_labels)

    def get_selected_timelines(self):
        return [i for i, var in self.timeline_vars.items() if var.get() == 1]

    def get_settings(self):
        return {
            "output_dir": self.output_dir.get(),
            "use_in_out": self.use_in_out.get(),
            "use_preset": bool(self.preset_var.get()),
            "preset": self.preset_var.get(),
            "project": self.current_project
        }

    def on_add_jobs(self):
        selected_timelines = self.get_selected_timelines()
        if not selected_timelines:
            tkMessageBox.showwarning("Warning", "Please select at least one timeline.")
            return
        if not self.output_dir.get():
            tkMessageBox.showerror("Error", "Please specify an output directory.")
            return
        settings = self.get_settings()
        add_render_jobs(settings, selected_timelines, self.log, self.update_status)

    def on_start_rendering(self):
        if not self.current_project or not self.current_project.GetRenderJobList():
            tkMessageBox.showwarning("Warning", "Es sind keine Renderjobs in der Warteschlange.")
            return
        total = len(self.timeline_vars)
        start_rendering(self.current_project, self.log, self.update_status, total)

    def load_projects(self):
        self.projects = project_manager.GetProjectListInCurrentFolder()
        menu = self.project_menu["menu"]
        menu.delete(0, "end")
        for name in self.projects:
            menu.add_command(label=name, command=tk._setit(self.project_var, name))
        if self.projects:
            self.project_var.set(self.projects[0])
            self.on_project_change()

    def on_project_change(self):
        project_name = self.project_var.get()
        project_manager.LoadProject(project_name)
        self.current_project = project_manager.GetCurrentProject()
        project = self.current_project
        if not project:
            return
        self.render_presets = project.GetRenderPresetList()
        self.preset_var.set(self.render_presets[0] if self.render_presets else "")
        menu = self.preset_menu["menu"]
        menu.delete(0, "end")
        for preset in self.render_presets:
            menu.add_command(label=preset, command=lambda p=preset: self.preset_var.set(p))
        self.load_timelines()
        self.log(f"\n\ud83d\udcc1 Projekt gewechselt zu: {project_name}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenderGUI(root)
    root.mainloop()
