import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

class NewMapDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("新建地图")
        self.geometry("300x150")
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="行数:").grid(row=0, column=0, padx=5, pady=5)
        self.rows_entry = tk.Entry(self)
        self.rows_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="列数:").grid(row=1, column=0, padx=5, pady=5)
        self.cols_entry = tk.Entry(self)
        self.cols_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="格子大小:").grid(row=2, column=0, padx=5, pady=5)
        self.cell_size_entry = tk.Entry(self)
        self.cell_size_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self, text="确定", command=self.on_ok).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self, text="取消", command=self.destroy).grid(row=3, column=1, padx=5, pady=5)

    def on_ok(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            cell_size = int(self.cell_size_entry.get())
            if rows <= 0 or cols <= 0 or cell_size <= 0:
                raise ValueError
            self.callback(rows, cols, cell_size)
            self.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数")

class OpenMapDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("打开地图")
        self.geometry("300x100")
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="选择地图文件:").pack(pady=10)
        tk.Button(self, text="浏览", command=self.on_browse).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=20, pady=10)

    def on_browse(self):
        file_path = filedialog.askopenfilename(filetypes=[("地图文件", "*.json")])
        if file_path:
            self.callback(file_path)
            self.destroy()

class SaveConfirmDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("保存确认")
        self.geometry("300x100")
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="是否保存当前地图?").pack(pady=10)
        tk.Button(self, text="保存", command=self.on_save).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self, text="不保存", command=self.on_discard).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=20, pady=10)

    def on_save(self):
        self.callback(True)
        self.destroy()

    def on_discard(self):
        self.callback(False)
        self.destroy()

class ErrorDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("错误")
        self.geometry("300x100")
        self.init_ui(message)

    def init_ui(self, message):
        tk.Label(self, text=message).pack(pady=20)
        tk.Button(self, text="确定", command=self.destroy).pack(pady=10)
