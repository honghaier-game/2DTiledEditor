
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ResourceTree(ttk.Treeview):
    def __init__(self, parent, on_select_callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.resources_dir = "Resources"
        self.image_cache = {}
        self.icon_cache = {}
        self.init_ui()
        self.scan_resources()

    def init_ui(self):
        self.heading('#0', text='Resources图片列表', anchor=tk.W)
        self.bind("<<TreeviewSelect>>", self.on_item_select)

    def scan_resources(self):
        for filename in os.listdir(self.resources_dir):
            if filename.lower().endswith(".png"):
                file_path = os.path.join(self.resources_dir, filename)
                image = Image.open(file_path)
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)
                self.image_cache[filename] = photo

                # Create icon
                icon_image = image.copy()
                icon_image.thumbnail((16, 16))
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.icon_cache[filename] = icon_photo

                self.insert("", "end", text="  " + filename, image=icon_photo)

    def on_item_select(self, event):
        selected_item = self.selection()
        if selected_item:
            filename = self.item(selected_item, "text").strip()
            if self.on_select_callback:
                self.on_select_callback(filename)
