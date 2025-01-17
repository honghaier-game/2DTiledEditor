
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import json
import os

class MapCanvas(tk.Canvas):
    def __init__(self, parent, rows=10, cols=10, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.original_grid_width = 32
        self.original_grid_height = 32
        self.grid_width = self.original_grid_width
        self.grid_height = self.original_grid_height
        self.zoom_level = 1.0
        self.show_grid = True
        self.layers = []
        self.current_layer = None
        self.selected_image = None
        self.image_cache = {}
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.rows = rows
        self.cols = cols
        self.background_music = None
        self.init_ui()
        self.bind_events()
        self.drag_selection = {"start": None, "end": None, "active": False}
        self.previous_selection_data = []
        self.drag_offset = {"x": 0, "y": 0}
        self.drag_begin_x = 0
        self.drag_beign_y = 0
        self.highlighted_grid = None

    def init_ui(self):
        self.configure(bg="#2F4F4F")  # 设置背景颜色为深灰蓝色
        self.scroll_x = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.xview)
        self.scroll_y = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.yview)
        self.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.draw_grid()
        self.bind("<Configure>", self.on_resize)

    def center_map(self):
        self.update_idletasks()
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        x_offset = (canvas_width - self.grid_width * self.cols) // 2
        y_offset = (canvas_height - self.grid_height * self.rows) // 2
        self.drag_offset["x"] = x_offset
        self.drag_offset["y"] = y_offset
        self.xview_moveto(0)
        self.yview_moveto(0)
        self.scan_dragto(x_offset, y_offset, gain=1)

    def bind_events(self):
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<ButtonRelease-1>", self.on_left_release)
        self.bind("<B1-Motion>", self.on_left_drag)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<ButtonPress-2>", self.on_middle_press)
        self.bind("<ButtonRelease-2>", self.on_middle_release)
        self.bind("<B2-Motion>", self.on_middle_drag)

    def on_mouse_move(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        grid_x, grid_y = self.get_grid_position(x, y)
        if self.is_within_map(grid_x, grid_y):
            if self.highlighted_grid:
                self.delete(self.highlighted_grid)
            x1 = grid_x * self.grid_width
            y1 = grid_y * self.grid_height
            x2 = x1 + self.grid_width
            y2 = y1 + self.grid_height
            self.highlighted_grid = self.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2, tags="highlight")

    def on_middle_press(self, event):
        self.scan_mark(event.x, event.y)        
        self.drag_begin_x = event.x
        self.drag_beign_y = event.y

    def on_middle_release(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def on_middle_drag(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
        self.drag_offset["x"] += event.x - self.drag_begin_x
        self.drag_offset["y"] += event.y - self.drag_beign_y
        self.drag_begin_x = event.x
        self.drag_beign_y = event.y

    def get_drag_offset(self):
        """返回鼠标拖动地图的偏移位置"""
        return self.drag_offset["x"], self.drag_offset["y"]

    def draw_grid(self):
        self.delete("grid")
        self.delete("gray_area")
        if self.show_grid:
            width = self.cols * self.grid_width
            height = self.rows * self.grid_height
            if self.grid_width > 0 and self.grid_height > 0:
                for x in range(0, width, self.grid_width):
                    self.create_line(x, 0, x, height, tags="grid", fill="gray")
                self.create_line(width, 0, width, height, tags="grid", fill="gray")
                for y in range(0, height, self.grid_height):
                    self.create_line(0, y, width, y, tags="grid", fill="gray")
                self.create_line(0, height, width, height, tags="grid", fill="gray")

    def on_resize(self, event):
        self.draw_grid()
        self.center_map()

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.draw_grid()

    def add_layer(self, layer_name):
        grid_data = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.layers.append({"name": layer_name, "elements": [], "visible": True, "grid_data": grid_data, "image_ids": {}})
        if not self.current_layer:
            self.current_layer = layer_name

    def delete_layer(self, layer_name):
        for layer in self.layers:
            if layer["name"] == layer_name:
                for grid_y in range(self.rows):
                    for grid_x in range(self.cols):
                        if layer["grid_data"][grid_y][grid_x] is not None:
                            image_id = layer["image_ids"].get((grid_x, grid_y))
                            if image_id:
                                self.delete(image_id)
                                layer["elements"].remove(image_id)
                                layer["grid_data"][grid_y][grid_x] = None
                                del layer["image_ids"][(grid_x, grid_y)]
                self.layers.remove(layer)
                if self.current_layer == layer_name:
                    self.current_layer = self.layers[0]["name"] if self.layers else None
                break

    def set_current_layer(self, layer_name):
        self.current_layer = layer_name

    def is_within_map(self, grid_x, grid_y):
        return 0 <= grid_x < self.cols and 0 <= grid_y < self.rows

    def on_left_click(self, event):
        if self.selected_image:
            x, y = self.canvasx(event.x), self.canvasy(event.y)
            grid_x = int(x // self.grid_width)
            grid_y = int(y // self.grid_height)
            if self.is_within_map(grid_x, grid_y) and self.current_layer:
                self.drag_selection["start"] = (grid_x, grid_y)
                self.drag_selection["active"] = True
                self.previous_selection_data = []

    def on_left_drag(self, event):
        if self.drag_selection["active"]:
            x, y = self.canvasx(event.x), self.canvasy(event.y)
            grid_x = int(x // self.grid_width)
            grid_y = int(y // self.grid_height)
            if self.is_within_map(grid_x, grid_y):
                self.drag_selection["end"] = (grid_x, grid_y)
                self.draw_selection_rect()
                self.temporarily_apply_selection()

    def on_left_release(self, event):
        if self.drag_selection["active"]:
            x, y = self.canvasx(event.x), self.canvasy(event.y)
            grid_x = int(x // self.grid_width)
            grid_y = int(y // self.grid_height)
            if self.is_within_map(grid_x, grid_y):
                self.drag_selection["end"] = (grid_x, grid_y)
                self.reset_previous_selection()
                self.apply_selection()
                self.drag_selection["start"] = None
                self.drag_selection["end"] = None
                self.drag_selection["active"] = False
                self.delete("selection_rect")

    def draw_selection_rect(self):
        self.delete("selection_rect")
        if self.drag_selection["start"] and self.drag_selection["end"]:
            start_x, start_y = self.drag_selection["start"]
            end_x, end_y = self.drag_selection["end"]
            x1 = min(start_x, end_x) * self.grid_width
            y1 = min(start_y, end_y) * self.grid_height
            x2 = (max(start_x, end_x) + 1) * self.grid_width
            y2 = (max(start_y, end_y) + 1) * self.grid_height
            self.create_rectangle(x1, y1, x2, y2, outline="red", tags="selection_rect")

    def temporarily_apply_selection(self):
        if self.drag_selection["start"] and self.drag_selection["end"]:
            start_x, start_y = self.drag_selection["start"]
            end_x, end_y = self.drag_selection["end"]
            min_x = min(start_x, end_x)
            max_x = max(start_x, end_x)
            min_y = min(start_y, end_y)
            max_y = max(start_y, end_y)
            for grid_x in range(min_x, max_x + 1):
                for grid_y in range(min_y, max_y + 1):
                    if self.is_within_map(grid_x, grid_y) and self.current_layer:
                        for layer in self.layers:
                            if layer["name"] == self.current_layer:
                                if layer["grid_data"][grid_y][grid_x] is not None:
                                    image_id = layer["image_ids"].get((grid_x, grid_y))
                                    if image_id:
                                        self.previous_selection_data.append((grid_x, grid_y, layer["grid_data"][grid_y][grid_x], image_id))
                                        self.delete(image_id)
                                        layer["elements"].remove(image_id)
                                        layer["grid_data"][grid_y][grid_x] = None
                                        del layer["image_ids"][(grid_x, grid_y)]
                                if self.selected_image not in self.image_cache:
                                    image = Image.open(f"Resources/{self.selected_image}")
                                    image = image.resize((self.grid_width, self.grid_height))
                                    photo = ImageTk.PhotoImage(image)
                                    self.image_cache[self.selected_image] = [image, photo]
                                else:
                                    photo = self.image_cache[self.selected_image][1]
                                image_id = self.create_image(grid_x * self.grid_width, grid_y * self.grid_height, image=photo, anchor=tk.NW, tags=(str("%s(%d,%d)" % (self.current_layer, grid_x, grid_y))))
                                layer["elements"].append(image_id)
                                layer["grid_data"][grid_y][grid_x] = self.selected_image
                                layer["image_ids"][(grid_x, grid_y)] = image_id

    def reset_previous_selection(self):
        for data in self.previous_selection_data:
            grid_x, grid_y, image_name, image_id = data
            for layer in self.layers:
                if layer["name"] == self.current_layer:
                    if layer["grid_data"][grid_y][grid_x] is not None:
                        self.delete(layer["image_ids"].get((grid_x, grid_y)))
                        layer["elements"].remove(layer["image_ids"].get((grid_x, grid_y)))
                        layer["grid_data"][grid_y][grid_x] = None
                        del layer["image_ids"][(grid_x, grid_y)]
                    if image_name:
                        if image_name not in self.image_cache:
                            image = Image.open(f"Resources/{image_name}")
                            image = image.resize((self.grid_width, self.grid_height))
                            photo = ImageTk.PhotoImage(image)
                            self.image_cache[image_name] = [image, photo]
                        else:
                            photo = self.image_cache[image_name][1]
                        new_image_id = self.create_image(grid_x * self.grid_width, grid_y * self.grid_height, image=photo, anchor=tk.NW, tags=(str("%s(%d,%d)" % (self.current_layer, grid_x, grid_y))))
                        layer["elements"].append(new_image_id)
                        layer["grid_data"][grid_y][grid_x] = image_name
                        layer["image_ids"][(grid_x, grid_y)] = new_image_id

    def apply_selection(self):
        if self.drag_selection["start"] and self.drag_selection["end"]:
            start_x, start_y = self.drag_selection["start"]
            end_x, end_y = self.drag_selection["end"]
            min_x = min(start_x, end_x)
            max_x = max(start_x, end_x)
            min_y = min(start_y, end_y)
            max_y = max(start_y, end_y)
            for grid_x in range(min_x, max_x + 1):
                for grid_y in range(min_y, max_y + 1):
                    if self.is_within_map(grid_x, grid_y) and self.current_layer:
                        for layer in self.layers:
                            if layer["name"] == self.current_layer:
                                if layer["grid_data"][grid_y][grid_x] is not None:
                                    image_id = layer["image_ids"].get((grid_x, grid_y))
                                    if image_id:
                                        self.delete(image_id)
                                        layer["elements"].remove(image_id)
                                        layer["grid_data"][grid_y][grid_x] = None
                                        del layer["image_ids"][(grid_x, grid_y)]
                                if self.selected_image not in self.image_cache:
                                    image = Image.open(f"Resources/{self.selected_image}")
                                    image = image.resize((self.grid_width, self.grid_height))
                                    photo = ImageTk.PhotoImage(image)
                                    self.image_cache[self.selected_image] = [image, photo]
                                else:
                                    photo = self.image_cache[self.selected_image][1]
                                image_id = self.create_image(grid_x * self.grid_width, grid_y * self.grid_height, image=photo, anchor=tk.NW, tags=(str("%s(%d,%d)" % (self.current_layer, grid_x, grid_y))))
                                layer["elements"].append(image_id)
                                layer["grid_data"][grid_y][grid_x] = self.selected_image
                                layer["image_ids"][(grid_x, grid_y)] = image_id

    def on_right_click(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        grid_x = int(x // self.grid_width)
        grid_y = int(y // self.grid_height)
        if self.is_within_map(grid_x, grid_y) and self.current_layer:
            for layer in self.layers:
                if layer["name"] == self.current_layer:
                    if layer["grid_data"][grid_y][grid_x] is not None:
                        image_id = layer["image_ids"].get((grid_x, grid_y))
                        if image_id:
                            self.delete(image_id)
                            layer["elements"].remove(image_id)
                            layer["grid_data"][grid_y][grid_x] = None
                            del layer["image_ids"][(grid_x, grid_y)]

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_level += 0.1
        else:
            self.zoom_level -= 0.1
        self.grid_width = int(self.original_grid_width * self.zoom_level)
        self.grid_height = int(self.original_grid_height * self.zoom_level)
        self.scale("all", 0, 0, self.zoom_level, self.zoom_level)
        self.draw_grid()
        self.resize_images()
        self.parent.update()
        self.on_mouse_move(event)

    def resize_images(self):
        for image_name in self.image_cache.keys():
            image = self.image_cache[image_name][0]
            image_resize = image.resize((self.grid_width, self.grid_height))
            photo = ImageTk.PhotoImage(image_resize)
            self.image_cache[image_name] = [image, photo]

        for layer in self.layers:
            for (grid_x, grid_y), image_id in layer["image_ids"].items():
                image_name = layer["grid_data"][grid_y][grid_x]
                if image_name:
                    photo = self.image_cache[image_name][1]
                    self.itemconfig(image_id, image=photo)
                    self.coords(image_id, grid_x * self.grid_width, grid_y * self.grid_height)

    def update_grid(self):
        self.draw_grid()

    def refresh_map(self):
        self.delete("all")
        for layer in self.layers:
            layer["elements"].clear()
            for (grid_x, grid_y), image_id in layer["image_ids"].items():
                image_name = layer["grid_data"][grid_y][grid_x]
                if image_name:
                    photo = self.image_cache[image_name][1]
                    image_id = self.create_image(grid_x * self.grid_width, grid_y * self.grid_height, image=photo, anchor=tk.NW, tags=(str("%s(%d,%d)" % (layer["name"], grid_x, grid_y))))
                    layer["elements"].append(image_id)
                    layer["image_ids"][(grid_x, grid_y)] = image_id
        for layer in self.layers:
            if layer["visible"]:
                for element_id in layer["elements"]:
                    self.itemconfig(element_id, state=tk.NORMAL)
            else:
                for element_id in layer["elements"]:
                    self.itemconfig(element_id, state=tk.HIDDEN)
        self.draw_grid()

    def save_map(self, file_path):
        if file_path:
            map_data = {
                "grid_width": self.original_grid_width,
                "grid_height": self.original_grid_height,
                "zoom_level": self.zoom_level,
                "show_grid": self.show_grid,
                "rows": self.rows,
                "cols": self.cols,
                "background_music": self.background_music,
                "layers": [],
                "image_cache": {image_name: image_name for image_name in self.image_cache.keys()}
            }
            for layer in self.layers:
                layer_data = {
                    "name": layer["name"],
                    "visible": layer["visible"],
                    "grid_data": layer["grid_data"]
                }
                map_data["layers"].append(layer_data)
            with open(file_path, "w") as f:
                json.dump(map_data, f, indent=4)

    def new_map(self, rows=10, cols=10, grid_width=32, grid_height=32):
        """重设格子的宽高、行列数，并清空各个图层及图像元素"""
        self.rows = rows
        self.cols = cols
        self.original_grid_width = grid_width
        self.original_grid_height = grid_height
        self.grid_width = int(self.original_grid_width * self.zoom_level)
        self.grid_height = int(self.original_grid_height * self.zoom_level)
        self.layers = []
        self.current_layer = None
        self.selected_image = None
        self.image_cache = {}
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.background_music = None
        self.refresh_map()
        
    def load_map(self, file_path):
        if file_path:
            with open(file_path, "r") as f:
                map_data = json.load(f)
            self.original_grid_width = map_data["grid_width"]
            self.original_grid_height = map_data["grid_height"]
            self.zoom_level = map_data["zoom_level"]
            self.grid_width = int(self.original_grid_width * self.zoom_level)
            self.grid_height = int(self.original_grid_height * self.zoom_level)
            self.show_grid = map_data["show_grid"]
            self.rows = map_data.get("rows", 10)
            self.cols = map_data.get("cols", 10)
            self.background_music = map_data.get("background_music")
            self.layers = []
            self.image_cache = {}
            for image_name in map_data["image_cache"]:
                image = Image.open(f"Resources/{image_name}")
                image = image.resize((self.grid_width, self.grid_height))
                photo = ImageTk.PhotoImage(image)
                self.image_cache[image_name] = [image, photo]

            layer_counter = 1
            for layer_data in map_data["layers"]:
                self.add_layer(layer_data["name"])
                layer = self.layers[-1]
                layer["name"] = f"图层_{layer_counter}"
                layer_counter = layer_counter + 1
                layer["visible"] = layer_data["visible"]
                layer["grid_data"] = layer_data["grid_data"]
                for y, row in enumerate(layer["grid_data"]):
                    for x, image_name in enumerate(row):
                        if image_name:
                            photo = self.image_cache[image_name][1]
                            image_id = self.create_image(x * self.grid_width, y * self.grid_height, image=photo, anchor=tk.NW, tags=(str("%s(%d,%d)" % (layer["name"], x, y))))
                            layer["elements"].append(image_id)
                            layer["image_ids"][(x, y)] = image_id
            self.refresh_map()
    def get_grid_position(self, x, y):
        """获取指定像素位置对应的格子行列数"""
        grid_x = int(x // self.grid_width)
        grid_y = int(y // self.grid_height)
        return grid_x, grid_y
