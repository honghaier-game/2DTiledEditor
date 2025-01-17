
import ttkbootstrap as ttk
from tkinter import Menu, messagebox, simpledialog, filedialog
from editor.map_canvas import MapCanvas
from editor.layer_panel import LayerPanel
from editor.resource_tree import ResourceTree
from utils.config import ConfigManager
import os.path
import json

class MainWindow(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("格子地图编辑器")
        self.geometry("800x600")
        self.resizable(True, True)
        self.config_manager = ConfigManager()
        self.current_map_file = None
        self.language = self.config_manager.get_language()
        self.load_language()
        self.init_menu()
        self.init_layout()
        self.load_last_map()
        self.bind("<Control-s>", self.save_map_shortcut)
        self.bind("<Control-g>", self.toggle_grid_shortcut)

    def load_language(self):
        lang_file = f"resources/{self.language}.json"
        with open(lang_file, 'r', encoding='utf-8') as f:
            self.lang_data = json.load(f)

    def init_menu(self):
        menubar = Menu(self)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.lang_data["menu"]["file"]["new_map"], command=self.new_map)
        file_menu.add_command(label=self.lang_data["menu"]["file"]["open_map"], command=self.open_map)
        file_menu.add_command(label=self.lang_data["menu"]["file"]["save_map"], command=self.save_map)
        file_menu.add_separator()
        file_menu.add_command(label=self.lang_data["menu"]["file"]["exit"], command=self.quit)
        menubar.add_cascade(label=self.lang_data["menu"]["file"]["label"], menu=file_menu)

        # 编辑菜单
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label=self.lang_data["menu"]["edit"]["undo"], command=self.undo)
        edit_menu.add_command(label=self.lang_data["menu"]["edit"]["redo"], command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label=self.lang_data["menu"]["edit"]["toggle_grid"], command=self.toggle_grid)
        menubar.add_cascade(label=self.lang_data["menu"]["edit"]["label"], menu=edit_menu)

        # 语言菜单
        language_menu = Menu(menubar, tearoff=0)
        language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        language_menu.add_command(label="中文", command=lambda: self.change_language("zh"))
        menubar.add_cascade(label="Language", menu=language_menu)

        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.lang_data["menu"]["help"]["about"], command=self.show_about)
        menubar.add_cascade(label=self.lang_data["menu"]["help"]["label"], menu=help_menu)

        self.config(menu=menubar)

    def change_language(self, language):
        self.config_manager.set_language(language)
        self.language = language
        self.load_language()
        self.init_menu()
        self.update_ui_text()
        self.update_window_title()

    def update_ui_text(self):
        self.map_info_label.config(text=f"{self.lang_data['ui']['tiles']}:{self.map_canvas.rows} x {self.map_canvas.cols}  {self.lang_data['ui']['tilesize']}:{self.map_canvas.original_grid_width}x{self.map_canvas.original_grid_height}")
        self.layer_panel.add_button.config(text=self.lang_data["ui"]["add_layer"])
        self.layer_panel.remove_button.config(text=self.lang_data["ui"]["remove_layer"])
        self.layer_panel.move_up_button.config(text=self.lang_data["ui"]["move_up"])
        self.layer_panel.move_down_button.config(text=self.lang_data["ui"]["move_down"])
        self.layer_panel.layer_list.heading("visible", text=self.lang_data["ui"]["layer_visibility"])
        self.layer_panel.layer_list.heading("name", text=self.lang_data["ui"]["layer_name"])

    def init_layout(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=ttk.BOTH, expand=True)

        # 左侧面板 - 地图画布
        left_panel = ttk.Frame(main_frame, style="darkly.TFrame")
        left_panel.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)

        self.map_canvas = MapCanvas(left_panel)
        self.map_canvas.pack(fill=ttk.BOTH, expand=True)

        # 右侧面板 - 编辑面板
        right_panel = ttk.Frame(main_frame, width=300, style="darkly.TFrame")
        right_panel.pack(side=ttk.RIGHT, fill=ttk.Y)

        # 地图信息显示
        self.map_info_label = ttk.Label(right_panel, text=f"{self.lang_data['ui']['tiles']}:{self.map_canvas.rows} x {self.map_canvas.cols}  {self.lang_data['ui']['tilesize']}:{self.map_canvas.original_grid_width}x{self.map_canvas.original_grid_height}")
        self.map_info_label.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)

        self.layer_panel = LayerPanel(right_panel, self.map_canvas)
        self.layer_panel.pack(side=ttk.TOP,fill=ttk.X, expand=False)

        self.resource_tree = ResourceTree(right_panel, on_select_callback=self.on_image_select)
        self.resource_tree.pack(fill=ttk.BOTH, expand=True)

        # 底部信息栏
        self.info_canvas = ttk.Canvas(self, height=20)
        self.info_canvas.pack(side=ttk.BOTTOM, fill=ttk.X)
        self.info_text = self.info_canvas.create_text(10, 5, anchor=ttk.NW, text=f"{self.lang_data['ui']['mouse_position']} (0, 0) {self.lang_data['ui']['offset']} (0, 0)", fill="white")

        # 绑定鼠标移动事件
        self.map_canvas.bind("<Motion>", self.update_mouse_position)
        self.map_canvas.bind("<B2-Motion>", self.update_mouse_position,add=True)
        self.map_canvas.bind("<MouseWheel>", self.update_mouse_position,add=True)

    def update_mouse_position(self, event):
        offset_x,offset_y = self.map_canvas.get_drag_offset()
        x = event.x - offset_x
        y = event.y - offset_y
        grid_x = x // self.map_canvas.grid_width
        grid_y = y // self.map_canvas.grid_height
        grid_x = max(0, min(grid_x, self.map_canvas.cols - 1))
        grid_y = max(0, min(grid_y, self.map_canvas.rows - 1))
        zoom = int(self.map_canvas.zoom_level * 100)
        self.info_canvas.itemconfig(self.info_text, text=f"{self.lang_data['ui']['mouse_position']} ({grid_x}, {grid_y}) {self.lang_data['ui']['offset']} ({offset_x}, {offset_y})  {self.lang_data['ui']['zoom']} ({zoom}%)")
        self.map_canvas.on_mouse_move(event)

    def load_last_map(self):
        last_map_file = self.config_manager.get_last_map_file()
        if last_map_file:
            if os.path.exists(last_map_file) == True:
                self.map_canvas.load_map(last_map_file)
                self.current_map_file = last_map_file
                self.update_window_title()
                self.update_layer_list()
                self.map_canvas.center_map()
                self.update_map_info()

    def new_map(self):
        dialog = ttk.Toplevel(self)
        dialog.title(self.lang_data["ui"]["new_map_dialog"]["title"])
        dialog.geometry("400x180")
        dialog.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 180) // 2
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text=self.lang_data["ui"]["new_map_dialog"]["grid_width"]).place(x=10, y=10)
        width_entry = ttk.Entry(dialog, width=6)
        width_entry.insert(0, "32")
        width_entry.place(x=80, y=10)

        ttk.Label(dialog, text=self.lang_data["ui"]["new_map_dialog"]["grid_height"]).place(x=180, y=10)
        height_entry = ttk.Entry(dialog, width=6)
        height_entry.insert(0, "32")
        height_entry.place(x=280, y=10)

        ttk.Label(dialog, text=self.lang_data["ui"]["new_map_dialog"]["rows"]).place(x=10, y=50)
        row_entry = ttk.Entry(dialog, width=6)
        row_entry.insert(0, "10")
        row_entry.place(x=80, y=50)

        ttk.Label(dialog, text=self.lang_data["ui"]["new_map_dialog"]["cols"]).place(x=180, y=50)
        col_entry = ttk.Entry(dialog, width=6)
        col_entry.insert(0, "10")
        col_entry.place(x=280, y=50)

        ttk.Label(dialog, text=self.lang_data["ui"]["new_map_dialog"]["bg_music"]).place(x=10, y=90)
        bg_music_entry = ttk.Entry(dialog)
        bg_music_entry.place(x=80, y=90, width=200)

        def browse_music():
            file_path = filedialog.askopenfilename(filetypes=[(f"{self.lang_data["ui"]["musicfile"]}", "*.mp3 *.wav")])
            if file_path:
                bg_music_entry.delete(0, ttk.END)
                bg_music_entry.insert(0, file_path)

        browse_button = ttk.Button(dialog, text=self.lang_data["ui"]["new_map_dialog"]["browse"], command=browse_music)
        browse_button.place(x=290, y=90)

        def on_ok():
            width = width_entry.get()
            height = height_entry.get()
            rows = row_entry.get()
            cols = col_entry.get()
            bg_music = bg_music_entry.get()
            if width and height and rows and cols:
                self.map_canvas.delete("all")
                self.layer_panel.layers = []
                self.layer_panel.layer_list.delete(*self.layer_panel.layer_list.get_children())
                self.map_canvas.new_map(int(rows), int(cols),int(width), int(height))
                self.current_map_file = None
                self.update_window_title()
                self.map_canvas.center_map()
                self.update_map_info()
                if bg_music:
                    self.map_canvas.set_background_music(bg_music)
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ttk.Button(dialog, text=self.lang_data["ui"]["new_map_dialog"]["ok"], command=on_ok).place(x=100, y=135 , width = 80)
        ttk.Button(dialog, text=self.lang_data["ui"]["new_map_dialog"]["cancel"], command=on_cancel).place(x=200, y=135 , width = 80)

    def open_map(self):
        file_path = filedialog.askopenfilename(filetypes=[(f"{self.lang_data["ui"]["mapfile"]}", "*.json")])
        if file_path:
            self.map_canvas.load_map(file_path)
            self.current_map_file = file_path
            self.update_window_title()
            self.config_manager.set_last_map_file(file_path)
            self.update_layer_list()
            self.map_canvas.center_map()
            self.update_map_info()

    def save_map(self):
        if self.current_map_file:
            self.map_canvas.save_map(self.current_map_file)
            messagebox.showinfo(self.lang_data["ui"]["save_success"], self.lang_data["ui"]["save_message"])
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[(f"{self.lang_data["ui"]["mapfile"]}", "*.json")])
            if file_path:
                self.map_canvas.save_map(file_path)
                self.current_map_file = file_path
                self.update_window_title()
                messagebox.showinfo(self.lang_data["ui"]["save_success"], self.lang_data["ui"]["save_message"])
                self.config_manager.set_last_map_file(file_path)

    def save_map_shortcut(self, event=None):
        self.save_map()

    def toggle_grid(self):
        self.map_canvas.toggle_grid()

    def toggle_grid_shortcut(self, event=None):
        self.toggle_grid()

    def undo(self):
        pass

    def redo(self):
        pass

    def show_about(self):
        messagebox.showinfo(self.lang_data["ui"]["about"]["title"], self.lang_data["ui"]["about"]["content"])

    def on_image_select(self, filename):
        self.map_canvas.selected_image = filename

    def update_layer_list(self):
        self.layer_panel.layer_list.delete(*self.layer_panel.layer_list.get_children())
        self.layer_panel.layer_counter = 1
        for layer in self.map_canvas.layers:
            layer_name = f"图层_{self.layer_panel.layer_counter}"
            self.layer_panel.layer_counter += 1
            self.layer_panel.layers.append({"name": layer_name, "visible": True})
            self.layer_panel.layer_list.insert("", "end", values=("✓", layer_name))

    def update_map_info(self):
        info_text = f"{self.lang_data['ui']['tiles']}:{self.map_canvas.rows} x {self.map_canvas.cols}  {self.lang_data['ui']['tilesize']}:{self.map_canvas.original_grid_width}x{self.map_canvas.original_grid_height}"
        self.map_info_label.config(text=info_text)

    def update_window_title(self):
        if self.current_map_file:
            self.title(f"{self.lang_data["ui"]["editor"]}- {self.current_map_file}")
        else:
            self.title(f"{self.lang_data["ui"]["editor"]}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
