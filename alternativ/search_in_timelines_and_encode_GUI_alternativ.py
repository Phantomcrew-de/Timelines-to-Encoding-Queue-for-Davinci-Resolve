#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import os
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import ttk
import imp
import sys

# Davinci Resolve API laden
try:
    DaVinciResolveScript = imp.load_source('DaVinciResolveScript', '/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py')
    resolve = DaVinciResolveScript.scriptapp("Resolve")
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
except Exception as e:
    print("Fehler beim Laden des Resolve-Skripting-Moduls:", e)
    sys.exit(1)


project = project_manager.GetCurrentProject()

if not project:
    tkMessageBox.showerror("Fehler", "Kein Projekt geöffnet.")
    sys.exit(1)

timelines = [project.GetTimelineByIndex(i+1).GetName() for i in range(project.GetTimelineCount())]
render_presets = project.GetRenderPresetList()

# Bekannte Render-Settings Keys zur Anzeige
settings_keys = [
    "ExportVideo", "VideoCodec", "Format", "VideoBitRate", "ResolutionWidth",
    "ResolutionHeight", "FrameRate", "QualityEnable", "QualitySetting",
    "ExportAudio", "AudioCodec", "AudioBitRate", "AudioSampleRate",
    "AudioBitDepth", "AudioChannel", "AudioFormat"
]

class BatchRenderGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Resolve Batch Render Tool")
        self.geometry("750x700")

        self.timeline_vars = {}
        self.build_gui()

    def build_gui(self):
        # Preset-Auswahl
        tk.Label(self, text="Render Preset:").pack(anchor="w")
        self.preset_var = tk.StringVar()
        self.preset_menu = ttk.Combobox(self, textvariable=self.preset_var, values=render_presets)
        self.preset_menu.pack(fill="x")
        self.preset_menu.bind("<<ComboboxSelected>>", self.show_preset_settings)

        # Preset-Einstellungen Anzeige
        self.settings_frame = tk.LabelFrame(self, text="Preset-Einstellungen")
        self.settings_frame.pack(fill="x", padx=5, pady=5)
        self.settings_text = tk.Text(self.settings_frame, height=10, state="disabled")
        self.settings_text.pack(fill="both", padx=5, pady=5)

        # Timeline-Filter
        tk.Label(self, text="Timeline-Filter:").pack(anchor="w")
        self.filter_entry = tk.Entry(self)
        self.filter_entry.pack(fill="x")
        self.filter_entry.bind("<KeyRelease>", self.update_timeline_list)

        # Timeline-Scroll-Box
        self.timeline_frame = tk.Frame(self)
        self.timeline_frame.pack(fill="both", expand=True)
        self.timeline_canvas = tk.Canvas(self.timeline_frame)
        self.scrollbar = tk.Scrollbar(self.timeline_frame, orient="vertical", command=self.timeline_canvas.yview)
        self.scroll_frame = tk.Frame(self.timeline_canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all")))
        self.timeline_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.populate_timelines()

        # Speicherort
        tk.Label(self, text="Speicherort:").pack(anchor="w")
        self.dir_var = tk.StringVar()
        tk.Entry(self, textvariable=self.dir_var).pack(fill="x")
        tk.Button(self, text="Durchsuchen...", command=self.select_directory).pack(anchor="e")

        # Dateiname
        tk.Label(self, text="Dateiname:").pack(anchor="w")
        self.name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.name_var).pack(fill="x")

        # Checkbox: SelectAllFrames
        self.allframes_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Alle Frames (kein In/Out)", variable=self.allframes_var).pack(anchor="w")

        # Render Button
        tk.Button(self, text="Render starten", command=self.start_render).pack(pady=10)

        # Logbox
        self.log = tk.Text(self, height=10, state="disabled")
        self.log.pack(fill="both", padx=5, pady=5)

    def populate_timelines(self, filter_text=""):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.timeline_vars = {}
        for i, name in enumerate(timelines):
            if filter_text.lower() in name.lower():
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.scroll_frame, text=name, variable=var)
                chk.pack(anchor="w")
                self.timeline_vars[name] = var

    def update_timeline_list(self, event=None):
        filter_text = self.filter_entry.get()
        self.populate_timelines(filter_text)

    def select_directory(self):
        directory = tkFileDialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def log_msg(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def show_preset_settings(self, event=None):
        preset = self.preset_var.get()
        if not preset:
            return

        project.LoadRenderPreset(preset)
        self.settings_text.config(state="normal")
        self.settings_text.delete("1.0", "end")
        self.settings_text.insert("end", "Einstellungen für Preset: {}\n\n".format(preset))

        for key in settings_keys:
            val = project.GetSetting(key)
            self.settings_text.insert("end", "{}: {}\n".format(key, val))

        self.settings_text.config(state="disabled")

    def start_render(self):
        selected_timelines = [name for name, var in self.timeline_vars.items() if var.get()]
        if not selected_timelines:
            self.log_msg("Keine Timeline ausgewählt.")
            return

        target_dir = self.dir_var.get()
        custom_name = self.name_var.get()
        preset = self.preset_var.get()
        select_all = self.allframes_var.get()

        if not target_dir or not os.path.isdir(target_dir):
            self.log_msg("Ungültiger Speicherort.")
            return

        if not preset:
            self.log_msg("Kein Render-Preset ausgewählt.")
            return

        project.LoadRenderPreset(preset)

        for name in selected_timelines:
            for i in range(project.GetTimelineCount()):
                tl = project.GetTimelineByIndex(i+1)
                if tl.GetName() == name:
                    project.SetCurrentTimeline(tl)
                    self.log_msg("Rendering: " + name)

                    project.DeleteAllRenderJobs()
                    settings = {
                        "TargetDir": target_dir,
                        "CustomName": custom_name + "_" + name
                    }
                    if select_all:
                        settings["SelectAllFrames"] = True

                    project.SetRenderSettings(settings)
                    project.AddRenderJob()
                    project.StartRendering(False)
                    self.log_msg("Fertig: " + name)

app = BatchRenderGUI()
app.mainloop()

