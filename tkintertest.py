# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 14:50:02 2020

@author: Rontc
"""
from tkinter import Tk, Label, Button, filedialog
from pathlib import Path

class pathFinder:
    def __init__(self, master, nowpath):
        self.master = master
        self.nowpath = nowpath
        master.title("A simple GUI")

        self.label = Label(master, text= nowpath)
        self.label.pack()

        self.greet_button = Button(master, text="Browse", command=self.greet)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command= self.destroy)
        self.close_button.pack()

    def greet(self):
          self.filename = filedialog.askdirectory()
          #print(self.filename)
          self.label.config(text = self.filename)
          #self.filename = filename
          #return self.filename
    def destroy(self):
          self.master.destroy()
    def filepath(self):
          return self.filename



#filepath = my_gui.filepath()

#test = Path(filepath)