#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import sys
import importlib.util
import json
import os
from datetime import datetime

# Resolve API laden
try:
    import DaVinciResolveScript as bmd
except ImportError:
    script_path = os.path.join(os.getenv('PROGRAMDATA'), 'Blackmagic Design', 'DaVinci Resolve', 'Support', 'Developer', 'Scripting', 'Modules')
    script_file = os.path.join(script_path, 'DaVinciResolveScript.py')
    spec = importlib.util.spec_from_file_location("DaVinciResolveScript", script_file)
    bmd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bmd)

resolve = bmd.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
PRESET_FILE = "last_preset.json"

class RenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Interfaccia di rendering con selezione progetto")

        self.current_project = None

        # Projektwahl
        tk.Label(master, text="Progetto:").grid(row=0, column=0, sticky='e')
        self.project_var = tk.StringVar()
        self.project_menu = tk.OptionMenu(master, self.project_var, "")
        self.project_menu.grid(row=0, column=1, sticky='w')
        self.project_var.trace("w", lambda *args: self.on_project_change())

        # Render Preset
        tk.Label(master, text="Preset di rendering:").grid(row=0, column=2, sticky='e')
        self.preset_var = tk.StringVar()
        self.preset_menu = tk.OptionMenu(master, self.preset_var, "")
        self.preset_menu.grid(row=0, column=3, sticky='w')

        # Speicherort
        tk.Label(master, text="Cartella di destinazione:").grid(row=1, column=0, sticky='e')
        self.output_dir = tk.Entry(master, width=40)
        self.output_dir.grid(row=1, column=1)
        tk.Button(master, text="Sfoglia", command=self.browse_dir).grid(row=1, column=2)

        # Auflösung / Framerate / Bitrate
        tk.Label(master, text="Larghezza:").grid(row=2, column=0, sticky='e')
        self.width = tk.Entry(master)
        self.width.grid(row=2, column=1)

        tk.Label(master, text="Altezza:").grid(row=2, column=2, sticky='e')
        self.height = tk.Entry(master)
        self.height.grid(row=2, column=3)

        tk.Label(master, text="Frequenza fotogrammi:").grid(row=3, column=0, sticky='e')
        self.framerate = tk.Entry(master)
        self.framerate.grid(row=3, column=1)

        tk.Label(master, text="Bitrate (Mbps):").grid(row=3, column=2, sticky='e')
        self.bitrate = tk.Entry(master)
        self.bitrate.grid(row=3, column=3)

        # Format / Codec
        tk.Label(master, text="Formato:").grid(row=4, column=0, sticky='e')
        self.format_var = tk.StringVar()
        self.format_menu = tk.OptionMenu(master, self.format_var, "")
        self.format_menu.grid(row=4, column=1, sticky='w')
        self.format_var.trace("w", lambda *args: self.update_codecs_for_format())

        tk.Label(master, text="Codec:").grid(row=4, column=2, sticky='e')
        self.codec_var = tk.StringVar()
        self.codec_menu = tk.OptionMenu(master, self.codec_var, "")
        self.codec_menu.grid(row=4, column=3, sticky='w')

        # In/Out
        self.use_in_out = tk.IntVar()
        tk.Checkbutton(master, text="Usa marcatori In/Out della timeline", variable=self.use_in_out).grid(row=5, column=0, columnspan=2, sticky='w')

        # Timeline-Suchmuster
        tk.Label(master, text="Filtro timeline:").grid(row=6, column=0, sticky='e')
        self.search_pattern = tk.Entry(master)
        self.search_pattern.grid(row=6, column=1)
        tk.Button(master, text="Filtra", command=self.select_timelines_by_pattern).grid(row=6, column=2)

        # Timeline-Auswahl
        self.timeline_vars = {}
        self.timeline_frame = tk.LabelFrame(master, text="Seleziona timeline")
        self.timeline_frame.grid(row=7, column=0, columnspan=4, pady=10, sticky='nsew')
        self.timeline_canvas = tk.Canvas(self.timeline_frame, height=150)
        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.timeline_frame, orient="vertical", command=self.timeline_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.inner_frame = tk.Frame(self.timeline_canvas)
        self.timeline_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame.bind("<Configure>", lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all")))

        # Buttons und Log
        tk.Button(master, text="Aggiungi alla coda", command=self.add_to_queue).grid(row=8, column=0, pady=10)
        tk.Button(master, text="Svuota coda", command=self.clear_queue).grid(row=8, column=1, pady=10)
        tk.Button(master, text="Avvia rendering", command=self.start_rendering).grid(row=8, column=2, pady=10)
        self.log_output = tk.Text(master, height=10, width=80)
        self.log_output.grid(row=9, column=0, columnspan=4)
        self.log_output.config(state="disabled")

        self.load_projects()
        self.load_last_preset()

    def log(self, message):
        self.log_output.config(state="normal")
        self.log_output.insert(tk.END, message)
        self.log_output.see(tk.END)
        self.log_output.config(state="disabled")

    def browse_dir(self):
        directory = filedialog.askdirectory()
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
        if not project_manager.LoadProject(project_name):
            self.log(f"⚠ Impossibile caricare il progetto: {project_name}\n")
            return
        self.current_project = project_manager.GetCurrentProject()
        self.update_formats()
        self.update_presets()
        self.load_timelines()
        self.log(f"📁 Progetto cambiato in: {project_name}\n")

    def update_presets(self):
        def update_custom_state():
            preset = self.preset_var.get()
            state = 'normal' if preset == 'Custom' else 'disabled'
            for widget in [
                self.width, self.height, self.framerate,
                self.bitrate, self.format_menu, self.codec_menu
            ]:
                widget.config(state=state)
        
        presets = self.current_project.GetRenderPresetList() if self.current_project else []
        presets.append('Custom')  # Append Custom manually if not included
        menu = self.preset_menu["menu"]
        menu.delete(0, "end")
        for preset in presets:
            menu.add_command(label=preset, command=lambda p=preset: self.preset_var.set(p))
        if presets:
            self.preset_var.set(presets[0])
        update_custom_state()
        self.preset_var.trace("w", lambda *args: update_custom_state())

    def update_formats(self):
        if not self.current_project:
            return
        formats = self.current_project.GetRenderFormats()
        menu = self.format_menu["menu"]
        menu.delete(0, "end")
        for fmt in formats:
            menu.add_command(label=fmt, command=tk._setit(self.format_var, fmt))
        if formats:
            self.format_var.set(next(iter(formats)))

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

    def load_timelines(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.timeline_vars = {}
        self.current_timelines = {}
        if not self.current_project:
            return
        timeline_count = self.current_project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            timeline = self.current_project.GetTimelineByIndex(i)
            if timeline:
                name = timeline.GetName()
                var = tk.IntVar()
                cb = tk.Checkbutton(self.inner_frame, text=name, variable=var)
                cb.pack(anchor='w')
                self.timeline_vars[i] = var
                self.current_timelines[i] = name

    def select_timelines_by_pattern(self):
        pattern = self.search_pattern.get().lower()
        for i, name in self.current_timelines.items():
            if pattern in name.lower():
                self.timeline_vars[i].set(1)

    
    def add_to_queue(self):
        if not self.current_project:
            messagebox.showerror("Errore", "Nessun progetto caricato.")
            return
        selected_timelines = [i for i, var in self.timeline_vars.items() if var.get() == 1]
        if not selected_timelines:
            messagebox.showwarning("Nota", "Seleziona almeno una timeline.")
            return

        settings = {
            "output_dir": self.output_dir.get(),
            "use_in_out": self.use_in_out.get(),
            "project": self.current_project,
            "selected_timelines": selected_timelines
        }

        if self.preset_var.get() == "Custom":
            try:
                bitrate_mbit = float(self.bitrate.get())
            except ValueErrore:
                messagebox.showerror("Errore", "Inserisci un bitrate valido.")
                return
            settings.update({
                "width": self.width.get(),
                "height": self.height.get(),
                "framerate": self.framerate.get(),
                "bitrate": int(bitrate_mbit * 1000000),
                "format": self.format_var.get(),
                "codec": self.codec_var.get(),
            })

        self.save_last_preset(settings)
        self.enqueue_timelines(settings)


    
    def enqueue_timelines(self, settings):
        project = settings["project"]
        if not project:
            self.log("❌ Nessun progetto.")
            return

        is_custom = self.preset_var.get() == "Custom"

        for i in settings["selected_timelines"]:
            tl = project.GetTimelineByIndex(i)
            if not tl:
                continue
            project.SetCurrentTimeline(tl)

            if is_custom:
                project.SetCurrentRenderFormatAndCodec(settings["format"], settings["codec"])
                render_settings = {
                    "SelectAllFrames": not bool(settings["use_in_out"]),
                    "TargetDir": settings["output_dir"],
                    "FormatWidth": int(settings["width"]),
                    "FormatHeight": int(settings["height"]),
                    "FrameRate": float(settings["framerate"]),
                    "VideoBitRate": settings["bitrate"],
                    "CustomName": tl.GetName()
                }
            else:
                project.LoadRenderPreset(self.preset_var.get())
                render_settings = {
                    "SelectAllFrames": not bool(settings["use_in_out"]),
                    "TargetDir": settings["output_dir"],
                    "CustomName": tl.GetName()
                }

            project.SetRenderSettings(render_settings)
            project.AddRenderJob()
            self.log(f"➕ {tl.GetName()} aggiunto alla coda\n")


    def clear_queue(self):
        if self.current_project:
            self.current_project.DeleteAllRenderJobs()
            self.log("🗑️ Coda svuotata\n")

    def start_rendering(self):
        if not self.current_project:
            self.log("❌ Nessun progetto caricato.")
            return
        start_dt = datetime.now()
        self.log(f"🚀 Avvio rendering alle {start_dt.strftime('%H:%M:%S')}...\n")
        start_time = time.time()
        self.current_project.StartRendering()
        while self.current_project.IsRenderingInProgress():
            time.sleep(1)
        end_time = time.time()
        end_dt = datetime.now()
        elapsed = end_time - start_time
        minutes, seconds = divmod(int(elapsed), 60)
        self.log(f"✅ Rendering completato alle {end_dt.strftime('%H:%M:%S')}.\n")
        self.log(f"⏱ Durata: {minutes} minuti {seconds} secondi\n")


    def save_last_preset(self, settings):
        try:
            preset = settings.copy()
            preset["bitrate"] = preset["bitrate"] // 1000000
            with open(PRESET_FILE, "w") as f:
                json.dump(preset, f)
        except Exception as e:
            self.log(f"⚠ salvataggio degli errori: {e}\n")

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
            self.log(f"⚠ Errore beim Laden des Presets: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenderGUI(root)
    root.mainloop()
