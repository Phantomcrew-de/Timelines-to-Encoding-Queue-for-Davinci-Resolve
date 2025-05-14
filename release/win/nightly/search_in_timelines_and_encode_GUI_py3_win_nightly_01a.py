#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox
import time
import sys
import importlib.util
import json
import os
from datetime import datetime

# Resolve API laden (robust für Windows)
try:
    import DaVinciResolveScript as bmd
except ImportError:
    import importlib.util
    import sys
    import os

    script_path = os.path.join(os.getenv('PROGRAMDATA'), 'Blackmagic Design', 'DaVinci Resolve', 'Support', 'Developer', 'Scripting', 'Modules')
    script_file = os.path.join(script_path, 'DaVinciResolveScript.py')

    spec = importlib.util.spec_from_file_location("DaVinciResolveScript", script_file)
    bmd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bmd)

resolve = bmd.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()

PRESET_FILE = "last_preset.json"

def run_rendering(settings, selected_timelines, log_callback):
    project = settings["project"]
    if not project:
        log_callback("❌ Projekt nicht gefunden.\n")
        return

    log_callback("📁 Lade Projekt: %s\n" % project.GetName())

    if len(project.GetRenderJobList()) > 0:
        log_callback("🧹 Bestehende Renderjobs werden gelöscht.\n")
        project.DeleteAllRenderJobs()

    log_callback("🎞 Format: %s, Codec: %s\n" % (settings["format"], settings["codec"]))
    project.SetCurrentRenderFormatAndCodec(settings["format"], settings["codec"])

    log_callback("➕ Neue Renderjobs werden hinzugefügt:\n")
    for i in selected_timelines:
        timeline = project.GetTimelineByIndex(i)
        if not timeline:
            continue
        project.SetCurrentTimeline(timeline)

        render_settings = {
            "SelectAllFrames": not bool(int(settings["use_in_out"])),
            "TargetDir": settings["output_dir"],
            "FormatWidth": int(settings["width"]),
            "FormatHeight": int(settings["height"]),
            "FrameRate": float(settings["framerate"]),
            "VideoBitRate": settings.get("bitrate", 20000000)
        }

        project.SetRenderSettings(render_settings)
        project.AddRenderJob()
        log_callback(" → %s\n" % timeline.GetName())

    if settings.get("start_render", False):
        log_callback("🚀 Rendering wird gestartet...\n")
        start_time = time.time()
        project.StartRendering(isInteractiveMode=True)

        animation = "|/-\\"
        anim_index = 0

        while project.IsRenderingInProgress():
            time.sleep(1)
            sys.stdout.write("Rendering... %s\r" % animation[anim_index % 4])
            sys.stdout.flush()
            anim_index += 1

        end_time = time.time()
        elapsed = int(end_time - start_time)
        log_callback("✅ Rendering abgeschlossen.\n")
        log_callback("🕒 Dauer: %d Sekunden\n" % elapsed)
        log_callback("⏱ Start: %s\n" % datetime.fromtimestamp(start_time).strftime("%H:%M:%S"))
        log_callback("⏱ Ende: %s\n" % datetime.fromtimestamp(end_time).strftime("%H:%M:%S"))

class RenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Render-Einstellungen")

        self.current_project = None

        # Projekt-Auswahl
        tk.Label(master, text="Projekt:").grid(row=0, column=0, sticky='e')
        self.project_var = tk.StringVar()
        self.project_menu = tk.OptionMenu(master, self.project_var, "")
        self.project_menu.grid(row=0, column=1, sticky='w')
        self.project_var.trace("w", lambda *args: self.on_project_change())

        # Speicherort
        tk.Label(master, text="Speicherort:").grid(row=1, column=0, sticky='e')
        self.output_dir = tk.Entry(master, width=40)
        self.output_dir.grid(row=1, column=1)
        tk.Button(master, text="Durchsuchen", command=self.browse_dir).grid(row=1, column=2)

        # Auflösung
        tk.Label(master, text="Breite:").grid(row=2, column=0, sticky='e')
        self.width = tk.Entry(master)
        self.width.grid(row=2, column=1)

        tk.Label(master, text="Höhe:").grid(row=3, column=0, sticky='e')
        self.height = tk.Entry(master)
        self.height.grid(row=3, column=1)

        # Framerate
        tk.Label(master, text="Framerate:").grid(row=4, column=0, sticky='e')
        self.framerate = tk.Entry(master)
        self.framerate.grid(row=4, column=1)

        # Format
        tk.Label(master, text="Format:").grid(row=5, column=0, sticky='e')
        self.format_var = tk.StringVar()
        self.format_menu = tk.OptionMenu(master, self.format_var, "")
        self.format_menu.grid(row=5, column=1, sticky='w')
        self.format_var.trace("w", lambda *args: self.update_codecs_for_format())

        # Codec
        tk.Label(master, text="Codec:").grid(row=5, column=2, sticky='e')
        self.codec_var = tk.StringVar()
        self.codec_menu = tk.OptionMenu(master, self.codec_var, "")
        self.codec_menu.grid(row=5, column=3, sticky='w')

        # Bitrate
        tk.Label(master, text="Bitrate (Mbit/s):").grid(row=6, column=0, sticky='e')
        self.bitrate = tk.Entry(master)
        self.bitrate.grid(row=6, column=1)

        # In/Out Marker
        self.use_in_out = tk.IntVar()
        tk.Checkbutton(master, text="Timeline In/Out Marker verwenden", variable=self.use_in_out).grid(row=6, column=2, sticky='w')

        # Timeline-Suchmuster
        tk.Label(master, text="Timeline-Suchmuster:").grid(row=7, column=0, sticky='e')
        self.search_pattern = tk.Entry(master)
        self.search_pattern.grid(row=7, column=1)
        tk.Button(master, text="Timelines nach Muster auswählen", command=self.select_timelines_by_pattern).grid(row=7, column=2)

        # Scrollbarer Timeline-Auswahl-Frame
        self.timeline_vars = {}

        self.timeline_frame = tk.LabelFrame(master, text="Timelines auswählen")
        self.timeline_frame.grid(row=8, column=0, columnspan=4, pady=10, sticky='nsew')

        self.timeline_canvas = tk.Canvas(self.timeline_frame, height=150)
        self.timeline_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.timeline_frame, orient="vertical", command=self.timeline_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.inner_timeline_frame = tk.Frame(self.timeline_canvas)
        self.inner_timeline_frame.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all"))
        )

        self.timeline_canvas.create_window((0, 0), window=self.inner_timeline_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Start-Button
        tk.Button(master, text="Rendern starten", command=self.on_start).grid(row=9, column=1, pady=10)

        # Log-Ausgabe
        self.log_output = tk.Text(master, height=10, width=80)
        self.log_output.grid(row=10, column=0, columnspan=4)
        self.log_output.config(state="disabled")

        self.load_projects()
        self.load_last_preset()

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

        self.update_formats()

        for widget in self.inner_timeline_frame.winfo_children():
            widget.destroy()

        self.timeline_vars = {}
        self.current_timelines = {}

        timeline_count = project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            timeline = project.GetTimelineByIndex(i)
            if timeline:
                name = timeline.GetName()
                var = tk.IntVar()
                self.timeline_vars[i] = var
                self.current_timelines[i] = name
                cb = tk.Checkbutton(self.inner_timeline_frame, text=name, variable=var)
                cb.pack(anchor='w')

    def update_formats(self):
        if not self.current_project:
            return
        formats = self.current_project.GetRenderFormats()
        menu = self.format_menu["menu"]
        menu.delete(0, "end")
        for fmt in formats.keys():
            menu.add_command(label=fmt, command=tk._setit(self.format_var, fmt))
        if formats:
            self.format_var.set(next(iter(formats.keys())))

    def update_codecs_for_format(self):
        if not self.current_project:
            return
        fmt = self.format_var.get()
        codecs = self.current_project.GetRenderCodecs(fmt)
        menu = self.codec_menu["menu"]
        menu.delete(0, "end")
        for desc, codec in codecs.items():
            menu.add_command(label=desc, command=tk._setit(self.codec_var, codec))
        if codecs:
            self.codec_var.set(next(iter(codecs.values())))

    def select_timelines_by_pattern(self):
        pattern = self.search_pattern.get().lower()
        if not pattern:
            tkMessageBox.showwarning("Hinweis", "Bitte ein Suchmuster eingeben.")
            return
        for i, name in self.current_timelines.items():
            if pattern in name.lower():
                self.timeline_vars[i].set(1)

    def on_start(self):
        selected_timelines = [i for i, var in self.timeline_vars.items() if var.get() == 1]
        if not selected_timelines:
            tkMessageBox.showwarning("Warnung", "Bitte mindestens eine Timeline auswählen.")
            return

        try:
            bitrate_mbit = float(self.bitrate.get())
        except ValueError:
            tkMessageBox.showerror("Fehler", "Bitte eine gültige Bitrate eingeben.")
            return

        settings = {
            "output_dir": self.output_dir.get(),
            "width": self.width.get(),
            "height": self.height.get(),
            "framerate": self.framerate.get(),
            "format": self.format_var.get(),
            "codec": self.codec_var.get(),
            "use_in_out": self.use_in_out.get(),
            "start_render": True,
            "bitrate": int(bitrate_mbit * 1000000),
            "project": self.current_project
        }

        for key in ["output_dir", "width", "height", "framerate", "format", "codec"]:
            if not settings[key]:
                tkMessageBox.showerror("Fehler", "Bitte gib %s ein." % key)
                return

        self.save_last_preset(settings)
        run_rendering(settings, selected_timelines, self.log)

    def save_last_preset(self, settings):
        try:
            preset = {
                "output_dir": settings["output_dir"],
                "width": settings["width"],
                "height": settings["height"],
                "framerate": settings["framerate"],
                "format": settings["format"],
                "codec": settings["codec"],
                "bitrate": settings["bitrate"] // 1000000,
                "use_in_out": settings["use_in_out"]
            }
            with open(PRESET_FILE, "w") as f:
                json.dump(preset, f)
        except Exception as e:
            self.log("⚠ Fehler beim Speichern des Presets: %s\n" % str(e))

    def load_last_preset(self):
        if not os.path.exists(PRESET_FILE):
            return
        try:
            with open(PRESET_FILE, "r") as f:
                preset = json.load(f)
                self.output_dir.insert(0, preset.get("output_dir", ""))
                self.width.insert(0, preset.get("width", "1920"))
                self.height.insert(0, preset.get("height", "1080"))
                self.framerate.insert(0, preset.get("framerate", "25"))
                self.bitrate.insert(0, preset.get("bitrate", "20"))
                self.format_var.set(preset.get("format", "mp4"))
                self.codec_var.set(preset.get("codec", ""))
                self.use_in_out.set(preset.get("use_in_out", 0))
        except Exception as e:
            self.log("⚠ Fehler beim Laden des Presets: %s\n" % str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = RenderGUI(root)
    root.mainloop()

