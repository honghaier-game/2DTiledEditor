import tkinter as tk
from tkinter import ttk

class MiniMap(tk.Canvas):
    def __init__(self, parent, main_canvas, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.main_canvas = main_canvas
        self.init_ui()
        self.bind_events()

    def init_ui(self):
        self.configure(width=200, height=150, bg="lightgray")
        self.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.update_minimap()

    def bind_events(self):
        self.bind("<Button-1>", self.on_click)

    def update_minimap(self):
        self.delete("all")
        main_width = self.main_canvas.winfo_width()
        main_height = self.main_canvas.winfo_height()
        scale_x = 200 / main_width
        scale_y = 150 / main_height

        for item in self.main_canvas.find_all():
            coords = self.main_canvas.coords(item)
            scaled_coords = [coord * scale_x if idx % 2 == 0 else coord * scale_y for idx, coord in enumerate(coords)]
            self.create_rectangle(*scaled_coords, fill="blue", tags="element")

        view_x0 = self.main_canvas.canvasx(0) * scale_x
        view_y0 = self.main_canvas.canvasy(0) * scale_y
        view_x1 = self.main_canvas.canvasx(self.main_canvas.winfo_width()) * scale_x
        view_y1 = self.main_canvas.canvasy(self.main_canvas.winfo_height()) * scale_y
        self.create_rectangle(view_x0, view_y0, view_x1, view_y1, outline="red", tags="view_area")

    def on_click(self, event):
        scale_x = self.main_canvas.winfo_width() / 200
        scale_y = self.main_canvas.winfo_height() / 150
        x = event.x * scale_x
        y = event.y * scale_y
        self.main_canvas.xview_moveto((x - self.main_canvas.winfo_width() / 2) / self.main_canvas.winfo_width())
        self.main_canvas.yview_moveto((y - self.main_canvas.winfo_height() / 2) / self.main_canvas.winfo_height())
        self.update_minimap()
