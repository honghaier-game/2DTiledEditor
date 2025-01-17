
import tkinter as tk
from tkinter import ttk

class LayerPanel(tk.Frame):
    def __init__(self, parent, map_canvas=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.map_canvas = map_canvas
        self.layers = []
        self.layer_counter = 1  # 新增计数器
        self.init_ui()

    def init_ui(self):
        self.configure(width=200, bg="lightgray")
        self.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.layer_list = ttk.Treeview(self, columns=("visible", "name"), show="headings")
        self.layer_list.heading("visible", text="显示")
        self.layer_list.heading("name", text="图层名称")
        self.layer_list.column("visible", width=50, anchor="center")
        self.layer_list.column("name", width=150, anchor="w")
        self.layer_list.pack(fill=tk.BOTH, expand=True)

        self.add_button = tk.Button(self, text="添加图层", command=self.add_layer)
        self.add_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.remove_button = tk.Button(self, text="删除图层", command=self.remove_layer)
        self.remove_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.move_up_button = tk.Button(self, text="上移", command=self.move_layer_up)
        self.move_up_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.move_down_button = tk.Button(self, text="下移", command=self.move_layer_down)
        self.move_down_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.layer_list.bind("<Button-1>", self.toggle_visibility)
        self.layer_list.bind("<<TreeviewSelect>>", self.set_current_layer)

    def add_layer(self):
        layer_name = f"图层_{self.layer_counter}"  # 使用计数器生成唯一图层名称
        self.layer_counter += 1  # 计数器自增
        self.layers.append({"name": layer_name, "visible": True})
        self.layer_list.insert("", "end", values=("✓", layer_name))
        if self.map_canvas:
            self.map_canvas.add_layer(layer_name)
            self.map_canvas.refresh_map()

    def remove_layer(self):
        selected_item = self.layer_list.selection()
        if selected_item:
            layer_name = self.layer_list.item(selected_item, "values")[1]
            self.layer_list.delete(selected_item)
            self.layers = [layer for layer in self.layers if layer["name"] != layer_name]
            if self.map_canvas:
                self.map_canvas.delete_layer(layer_name)

    def toggle_visibility(self, event):
        item = self.layer_list.identify_row(event.y)
        if item:
            column = self.layer_list.identify_column(event.x)
            if column == "#1":
                current_value = self.layer_list.item(item, "values")[0]
                new_value = " " if current_value == "✓" else "✓"
                self.layer_list.item(item, values=(new_value, self.layer_list.item(item, "values")[1]))
                layer_name = self.layer_list.item(item, "values")[1]
                self.layers = [layer if layer["name"] != layer_name else {"name": layer_name, "visible": new_value == "✓"} for layer in self.layers]
                if self.map_canvas:
                    for layer in self.map_canvas.layers:
                        if layer["name"] == layer_name:
                            layer["visible"] = True if new_value == "✓" else False
                    self.map_canvas.refresh_map()

    def move_layer_up(self):
        selected_item = self.layer_list.selection()
        if selected_item:
            index = self.layer_list.index(selected_item)
            if index > 0:
                self.layer_list.move(selected_item, "", index - 1)
                self.layers[index], self.layers[index - 1] = self.layers[index - 1], self.layers[index]
                if self.map_canvas:
                    self.map_canvas.layers[index], self.map_canvas.layers[index - 1] = self.map_canvas.layers[index - 1], self.map_canvas.layers[index]
                    self.map_canvas.refresh_map()

    def move_layer_down(self):
        selected_item = self.layer_list.selection()
        if selected_item:
            index = self.layer_list.index(selected_item)
            if index < len(self.layers) - 1:
                self.layer_list.move(selected_item, "", index + 1)
                self.layers[index], self.layers[index + 1] = self.layers[index + 1], self.layers[index]
                if self.map_canvas:
                    self.map_canvas.layers[index], self.map_canvas.layers[index + 1] = self.map_canvas.layers[index + 1], self.map_canvas.layers[index]
                    self.map_canvas.refresh_map()

    def set_current_layer(self, event):
        selected_item = self.layer_list.selection()
        if selected_item:
            layer_name = self.layer_list.item(selected_item, "values")[1]
            if self.map_canvas:
                self.map_canvas.current_layer = layer_name

    def serialize(self):
        return self.layers

    def deserialize(self, layers_data):
        self.layers = layers_data
        self.layer_list.delete(*self.layer_list.get_children())
        for layer in self.layers:
            self.layer_list.insert("", "end", values=("✓" if layer["visible"] else " ", layer["name"]))
