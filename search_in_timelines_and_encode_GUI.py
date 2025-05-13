#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import time
import sys
import imp

# Resolve API laden
DaVinciResolveScript = imp.load_source('DaVinciResolveScript', "/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py")
resolve = DaVinciResolveScript.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()

def run_rendering(settings, selected_timelines):
    project = settings["project"]
    if not project:
        print("Projekt nicht gefunden.")
        return

    print("Lade Projekt:", project.GetName())

    if len(project.GetRenderJobList()) > 0:
        print("Bestehende Renderjobs werden gelöscht.")
        project.DeleteAllRenderJobs()

    print("Füge neue Jobs hinzu ...")
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
            "VideoBitRate": settings.get("bitrate", 20000000)  # Default: 20 Mbit
        }

        if settings["format"]:
            render_settings["Format"] = settings["format"]

        project.SetRenderSettings(render_settings)
        project.AddRenderJob()
        print(" → Timeline hinzugefügt:", timeline.GetName())

    if settings.get("start_render", False):
        print("Starte Rendering ...")
        project.StartRendering(isInteractiveMode=True)
        timer = 0
        animation = "|/-\\"
        while project.IsRenderingInProgress():
            time.sleep(1)
            timer += 1
            sys.stdout.write("Rendering seit %d Sekunden %s\r" % (timer, animation[timer % 4]))
            sys.stdout.flush()
        print("\nRendering abgeschlossen in %d Sekunden." % timer)

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
        self.width.insert(0, "1920")

        tk.Label(master, text="Höhe:").grid(row=3, column=0, sticky='e')
        self.height = tk.Entry(master)
        self.height.grid(row=3, column=1)
        self.height.insert(0, "1080")

        # Framerate
        tk.Label(master, text="Framerate:").grid(row=4, column=0, sticky='e')
        self.framerate = tk.Entry(master)
        self.framerate.grid(row=4, column=1)
        self.framerate.insert(0, "25")

        # Format
        tk.Label(master, text="Format:").grid(row=5, column=0, sticky='e')
        self.format_var = tk.StringVar()
        self.format_menu = tk.OptionMenu(master, self.format_var, "mp4", "mov", "avi", "mxf")
        self.format_var.set("mp4")
        self.format_menu.grid(row=5, column=1, sticky='w')

        # Bitrate
        tk.Label(master, text="Bitrate (Mbit/s):").grid(row=6, column=0, sticky='e')
        self.bitrate = tk.Entry(master)
        self.bitrate.grid(row=6, column=1)
        self.bitrate.insert(0, "20")

        # In/Out Marker
        self.use_in_out = tk.IntVar()
        tk.Checkbutton(master, text="Timeline In/Out Marker verwenden", variable=self.use_in_out).grid(row=6, column=2, sticky='w')

        # Timeline Suchmuster
        tk.Label(master, text="Timeline-Suchmuster:").grid(row=7, column=0, sticky='e')
        self.search_pattern = tk.Entry(master)
        self.search_pattern.grid(row=7, column=1)
        tk.Button(master, text="Timelines nach Muster auswählen", command=self.select_timelines_by_pattern).grid(row=7, column=2)

        # Timeline-Auswahl-Frame
        self.timeline_vars = {}
        self.timeline_frame = tk.LabelFrame(master, text="Timelines auswählen")
        self.timeline_frame.grid(row=8, column=0, columnspan=3, pady=10, sticky='we')

        # Start-Button
        tk.Button(master, text="Rendern starten", command=self.on_start).grid(row=9, column=1, pady=10)

        self.load_projects()

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

        for widget in self.timeline_frame.winfo_children():
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
                cb = tk.Checkbutton(self.timeline_frame, text=name, variable=var)
                cb.pack(anchor='w')

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
            "use_in_out": self.use_in_out.get(),
            "start_render": True,
            "bitrate": int(bitrate_mbit * 1000000),
            "project": self.current_project
        }

        for key in ["output_dir", "width", "height", "framerate"]:
            if not settings[key]:
                tkMessageBox.showerror("Fehler", "Bitte gib %s ein." % key)
                return

        run_rendering(settings, selected_timelines)
        tkMessageBox.showinfo("Info", "Rendering abgeschlossen oder gestartet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenderGUI(root)
    root.mainloop()

