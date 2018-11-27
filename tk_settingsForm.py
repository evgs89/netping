#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 4.13
# In conjunction with Tcl version 8.6
#    May 11, 2018 05:46:12 PM

import sys

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

try: import tk_settingsForm_support
except: import ui.tk_settingsForm_support as tk_settingsForm_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    tk_settingsForm_support.set_Tk_var()
    top = New_Toplevel (root)
    tk_settingsForm_support.init(root, top)
    root.mainloop()

w = None
def create_New_Toplevel(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    tk_settingsForm_support.set_Tk_var()
    top = New_Toplevel (w)
    tk_settingsForm_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_New_Toplevel():
    global w
    w.destroy()
    w = None


class New_Toplevel:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("305x350-20+50")
        top.title("Settings")
        top.configure(highlightcolor="black")



        self.style.configure('TNotebook.Tab', background=_bgcolor)
        self.style.configure('TNotebook.Tab', foreground=_fgcolor)
        self.style.map('TNotebook.Tab', background=
            [('selected', _compcolor), ('active',_ana2color)])
        self.TNotebook1 = ttk.Notebook(top)
        self.TNotebook1.place(relx=0.0, rely=0.0, relheight=0.87, relwidth=0.99)
        self.TNotebook1.configure(width=302)
        self.TNotebook1.configure(takefocus="")
        self.TNotebook1_t0 = Frame(self.TNotebook1)
        self.TNotebook1.add(self.TNotebook1_t0, padding=3)
        self.TNotebook1.tab(0, text="IP & COM settings", compound="left"
                ,underline="-1", )
        self.TNotebook1_t1 = Frame(self.TNotebook1)
        self.TNotebook1.add(self.TNotebook1_t1, padding=3)
        self.TNotebook1.tab(1, text="Log settings", compound="left"
                ,underline="-1", )

        self.TLabel1 = ttk.Label(self.TNotebook1_t0)
        self.TLabel1.place(relx=0.03, rely=0.04, height=19, width=68)
        self.TLabel1.configure(background="#d9d9d9")
        self.TLabel1.configure(foreground="#000000")
        self.TLabel1.configure(font="TkDefaultFont")
        self.TLabel1.configure(relief=FLAT)
        self.TLabel1.configure(text='''IP1 address''')

        self.IP1Edit = ttk.Entry(self.TNotebook1_t0)
        self.IP1Edit.place(relx=0.37, rely=0.04, relheight=0.08, relwidth=0.55)
        self.IP1Edit.configure(textvariable=tk_settingsForm_support.ip1)
        self.IP1Edit.configure(takefocus="")
        self.IP1Edit.configure(cursor="xterm")

        self.TLabel2 = ttk.Label(self.TNotebook1_t0)
        self.TLabel2.place(relx=0.03, rely=0.14, height=19, width=68)
        self.TLabel2.configure(background="#d9d9d9")
        self.TLabel2.configure(foreground="#000000")
        self.TLabel2.configure(font="TkDefaultFont")
        self.TLabel2.configure(relief=FLAT)
        self.TLabel2.configure(text='''IP2 address''')

        self.IP2Edit = ttk.Entry(self.TNotebook1_t0)
        self.IP2Edit.place(relx=0.37, rely=0.14, relheight=0.08, relwidth=0.55)
        self.IP2Edit.configure(textvariable=tk_settingsForm_support.ip2)
        self.IP2Edit.configure(takefocus="")
        self.IP2Edit.configure(cursor="xterm")

        self.TLabel3 = ttk.Label(self.TNotebook1_t0)
        self.TLabel3.place(relx=0.03, rely=0.25, height=19, width=190)
        self.TLabel3.configure(background="#d9d9d9")
        self.TLabel3.configure(foreground="#000000")
        self.TLabel3.configure(font="TkDefaultFont")
        self.TLabel3.configure(relief=FLAT)
        self.TLabel3.configure(text='''Reboot modem on unavialibility of''')

        self.style.map('TCheckbutton',background=
            [('selected', _bgcolor), ('active', _ana2color)])
        self.ip1reboot = ttk.Checkbutton(self.TNotebook1_t0)
        self.ip1reboot.place(relx=0.7, rely=0.25, relwidth=0.12, relheight=0.0
                , height=21)
        self.ip1reboot.configure(variable=tk_settingsForm_support.ip1rebootChecked)
        self.ip1reboot.configure(takefocus="")
        self.ip1reboot.configure(text='''IP1''')

        self.ip2reboot = ttk.Checkbutton(self.TNotebook1_t0)
        self.ip2reboot.place(relx=0.87, rely=0.25, relwidth=0.12, relheight=0.0
                , height=21)
        self.ip2reboot.configure(variable=tk_settingsForm_support.ip2rebootChecked)
        self.ip2reboot.configure(takefocus="")
        self.ip2reboot.configure(text='''IP2''')

        self.comPortEnabled = ttk.Checkbutton(self.TNotebook1_t0)
        self.comPortEnabled.place(relx=0.03, rely=0.39, relwidth=0.37
                , relheight=0.0, height=21)
        self.comPortEnabled.configure(variable=tk_settingsForm_support.comPortEnabledChecked)
        self.comPortEnabled.configure(takefocus="")
        self.comPortEnabled.configure(text='''Enable COM-port''')

        self.comEdit = ttk.Entry(self.TNotebook1_t0)
        self.comEdit.place(relx=0.43, rely=0.39, relheight=0.08, relwidth=0.48)
        self.comEdit.configure(textvariable=tk_settingsForm_support.comPort)
        self.comEdit.configure(takefocus="")
        self.comEdit.configure(cursor="xterm")

        self.TLabel4 = ttk.Label(self.TNotebook1_t0)
        self.TLabel4.place(relx=0.03, rely=0.5, height=19, width=66)
        self.TLabel4.configure(background="#d9d9d9")
        self.TLabel4.configure(foreground="#000000")
        self.TLabel4.configure(font="TkDefaultFont")
        self.TLabel4.configure(relief=FLAT)
        self.TLabel4.configure(text='''COM-speed''')

        self.enableAutoSpeedCheckbox = ttk.Checkbutton(self.TNotebook1_t0)
        self.enableAutoSpeedCheckbox.place(relx=0.27, rely=0.5, relwidth=0.14
                , relheight=0.0, height=21)
        self.enableAutoSpeedCheckbox.configure(variable=tk_settingsForm_support.enableAutoSpeed)
        self.enableAutoSpeedCheckbox.configure(takefocus="")
        self.enableAutoSpeedCheckbox.configure(text='''auto''')

        self.TEntry4 = ttk.Entry(self.TNotebook1_t0)
        self.TEntry4.place(relx=0.43, rely=0.5, relheight=0.08, relwidth=0.48)
        self.TEntry4.configure(textvariable=tk_settingsForm_support.comSpeed)
        self.TEntry4.configure(takefocus="")
        self.TEntry4.configure(cursor="xterm")

        self.TEntry5 = ttk.Entry(self.TNotebook1_t0)
        self.TEntry5.place(relx=0.43, rely=0.61, relheight=0.08, relwidth=0.48)
        self.TEntry5.configure(textvariable=tk_settingsForm_support.critTemp)
        self.TEntry5.configure(takefocus="")
        self.TEntry5.configure(cursor="xterm")

        self.TLabel5 = ttk.Label(self.TNotebook1_t0)
        self.TLabel5.place(relx=0.03, rely=0.61, height=19, width=114)
        self.TLabel5.configure(background="#d9d9d9")
        self.TLabel5.configure(foreground="#000000")
        self.TLabel5.configure(font="TkDefaultFont")
        self.TLabel5.configure(relief=FLAT)
        self.TLabel5.configure(text='''Critical temperature''')

        self.maxLogSizeEdit = Spinbox(self.TNotebook1_t1, from_=1.0, to=100.0)
        self.maxLogSizeEdit.place(relx=0.43, rely=0.04, relheight=0.08
                , relwidth=0.52)
        self.maxLogSizeEdit.configure(activebackground="#f9f9f9")
        self.maxLogSizeEdit.configure(background="white")
        self.maxLogSizeEdit.configure(from_="1.0")
        self.maxLogSizeEdit.configure(highlightbackground="black")
        self.maxLogSizeEdit.configure(selectbackground="#c4c4c4")
        self.maxLogSizeEdit.configure(textvariable=tk_settingsForm_support.maxLogSize)
        self.maxLogSizeEdit.configure(to="100.0")
        self.value_list = [1048576,]
        self.maxLogSizeEdit.configure(values=self.value_list)

        self.TLabel6 = ttk.Label(self.TNotebook1_t1)
        self.TLabel6.place(relx=0.03, rely=0.04, height=19, width=110)
        self.TLabel6.configure(background="#d9d9d9")
        self.TLabel6.configure(foreground="#000000")
        self.TLabel6.configure(font="TkDefaultFont")
        self.TLabel6.configure(relief=FLAT)
        self.TLabel6.configure(text='''Max log size (bytes)''')

        self.TLabel7 = ttk.Label(self.TNotebook1_t1)
        self.TLabel7.place(relx=0.03, rely=0.14, height=19, width=130)
        self.TLabel7.configure(background="#d9d9d9")
        self.TLabel7.configure(foreground="#000000")
        self.TLabel7.configure(font="TkDefaultFont")
        self.TLabel7.configure(relief=FLAT)
        self.TLabel7.configure(text='''Show this events in log:''')

        self.TCheckbutton5 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton5.place(relx=0.03, rely=0.25, relwidth=0.34
                , relheight=0.0, height=21)
        self.TCheckbutton5.configure(variable=tk_settingsForm_support.sysStartUp)
        self.TCheckbutton5.configure(takefocus="")
        self.TCheckbutton5.configure(text='''System startup''')

        self.TCheckbutton6 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton6.place(relx=0.03, rely=0.36, relwidth=0.38
                , relheight=0.0, height=21)
        self.TCheckbutton6.configure(variable=tk_settingsForm_support.sysShutdown)
        self.TCheckbutton6.configure(takefocus="")
        self.TCheckbutton6.configure(text='''System shutdown''')

        self.TCheckbutton7 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton7.place(relx=0.03, rely=0.46, relwidth=0.3
                , relheight=0.0, height=21)
        self.TCheckbutton7.configure(variable=tk_settingsForm_support.ip1Log)
        self.TCheckbutton7.configure(takefocus="")
        self.TCheckbutton7.configure(text='''IP1 avialiblity''')

        self.TCheckbutton8 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton8.place(relx=0.03, rely=0.57, relwidth=0.3
                , relheight=0.0, height=21)
        self.TCheckbutton8.configure(variable=tk_settingsForm_support.ip2Log)
        self.TCheckbutton8.configure(takefocus="")
        self.TCheckbutton8.configure(text='''IP2 avialiblity''')

        self.TCheckbutton9 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton9.place(relx=0.03, rely=0.68, relwidth=0.28
                , relheight=0.0, height=21)
        self.TCheckbutton9.configure(variable=tk_settingsForm_support.comPortLog)
        self.TCheckbutton9.configure(takefocus="")
        self.TCheckbutton9.configure(text='''COM events''')

        self.TCheckbutton10 = ttk.Checkbutton(self.TNotebook1_t1)
        self.TCheckbutton10.place(relx=0.03, rely=0.79, relwidth=0.5
                , relheight=0.0, height=21)
        self.TCheckbutton10.configure(variable=tk_settingsForm_support.tempLog)
        self.TCheckbutton10.configure(takefocus="")
        self.TCheckbutton10.configure(text='''Temperature changings''')

        self.TButton1 = ttk.Button(top)
        self.TButton1.place(relx=0.49, rely=0.89, height=28, width=74)
        self.TButton1.configure(takefocus="")
        self.TButton1.configure(text='''OK''')

        self.TButton2 = ttk.Button(top)
        self.TButton2.place(relx=0.75, rely=0.89, height=28, width=74)
        self.TButton2.configure(takefocus="")
        self.TButton2.configure(text='''Cancel''')






if __name__ == '__main__':
    vp_start_gui()


