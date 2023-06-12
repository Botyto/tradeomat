import os
import tkinter as tk
from tkinter import ttk
import typing

from collect.engine import Environment, BaseReader


class CollectBrowserFrame(ttk.Frame):
    READER_CLS: typing.Type[BaseReader]
    NAMESPACED: bool = False
    NAME: str
    env: Environment
    reader: BaseReader|None
    namespace: str|None
    _var_namespace: tk.StringVar

    def __init__(self, env: Environment, master=None, **kw):
        super().__init__(master, **kw)
        self.env = env
        self.reader = None
        self.namespace = None
        self._build_all()

    def _build_all(self):
        if self.NAMESPACED:
            self._var_namespace = tk.StringVar(self, None, "Namespace")
            namespaces = self.list_namespaces()
            options = ttk.OptionMenu(self, self._var_namespace, *namespaces)
            options.pack()
        self.build(self)

    def build(self, master):
        raise NotImplementedError()

    def list_namespaces(self):
        root = self.READER_CLS(self.collector, None).get_ns_data_path()
        result = []
        for ns in os.listdir(root):
            ns_path = os.path.join(root, ns)
            if not os.path.isdir(ns_path):
                continue
            result.append(ns)
        return result

    def get_reader(self, namespace: str|None):
        if self.reader.namespace == namespace:
            return self.reader
        self.reader = self.READER_CLS(self.collector, namespace)
        return self.reader
    
    @property
    def collector(self):
        raise NotImplementedError()
