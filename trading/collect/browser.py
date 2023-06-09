import tkinter
from tkinter import ttk

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

from collect.bar.engine import BarReader
from collect.news.engine import NewsReader
from collect.social.engine import SocialReader
from collect.symbol.engine import SymbolReader


class CollectBrowser(tkinter.Tk):
    READER_CLASSES = [
        BarReader,
        NewsReader,
        SocialReader,
        SymbolReader,
    ]

    def __init__(self):
        super().__init__()
        self.title("Collect browser")
        self.geometry("800x600")
        tab_control = ttk.Notebook(self)
        for reader_cls in self.READER_CLASSES:
            frame = ttk.Frame(tab_control)
            cls_name = reader_cls.__name__
            if cls_name.endswith("Reader"):
                cls_name = cls_name[:-6]
            tab_control.add(frame, text=cls_name)
        tab_control.pack(expand=1, fill="both")
