import wx
from .layer_panel import LayerPanel
from .resource_tree import ResourceTree

class EditorPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 主布局
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧地图画布区域
        self.map_canvas = wx.Panel(self, style=wx.SUNKEN_BORDER)
        main_sizer.Add(self.map_canvas, 1, wx.EXPAND | wx.ALL, 5)
        
        # 右侧面板
        right_panel = wx.Panel(self)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 图层列表面板
        layer_panel = wx.Panel(right_panel)
        layer_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.layer_panel = LayerPanel(layer_panel)
        layer_sizer.Add(self.layer_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # 添加/删除图层按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_layer_btn = wx.Button(layer_panel, label="添加图层")
        delete_layer_btn = wx.Button(layer_panel, label="删除图层")
        button_sizer.Add(add_layer_btn, 0, wx.ALL, 5)
        button_sizer.Add(delete_layer_btn, 0, wx.ALL, 5)
        layer_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
        
        layer_panel.SetSizer(layer_sizer)
        right_sizer.Add(layer_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # 资源树控件
        self.resource_tree = ResourceTree(right_panel)
        right_sizer.Add(self.resource_tree, 2, wx.EXPAND | wx.ALL, 5)
        
        right_panel.SetSizer(right_sizer)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
