import tkinter
from tkinter import ttk

from collect.engine import Environment
from collect.browser.frame import CollectBrowserFrame

# import subclasses of CollectBrowserFrame
import collect.browser.news

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class CollectBrowser(tkinter.Tk):
    env: Environment

    def __init__(self, env: Environment, screenName=None, baseName=None, className='Tk', useTk=True, sync=False, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.env = env
        self.title("Collect browser")
        self.geometry("800x600")

        tab_control = ttk.Notebook(self)
        for frame_cls in CollectBrowserFrame.__subclasses__():
            frame = frame_cls(tab_control)
            tab_control.add(frame, text=frame.NAME)
        tab_control.pack(expand=1, fill="both")
