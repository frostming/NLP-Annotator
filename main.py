#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ====================================
# Title:  A simple annotation tool for NLP
# Author: Frost Ming
# Email:  mianghong@gmail.com
# Date:   2016/3/13
# ====================================
import wx
import icons
from ui import *


def loadIcon(icon, w, h):
    py_icon = eval('icons.' + icon + 'Icon')
    img = py_icon.GetImage()
    img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
    return img.ConvertToBitmap()


class Frame(wx.Frame):
    def __init__(self, title):
        super(Frame, self).__init__(None, -1, title, size=(1024, 768))
        self.SetMinSize((800, 600))
        self.keymap = {'a': 'ACTION', 'c': 'CONT', 'd': 'DATA', 'e': 'EDU', 'g': 'GEND',
                       'l': 'LOC', 'm': 'MISC', 'n': 'NAME', 'o': 'ORG', 'p': 'PRO',
                       'r': 'RACE', 't': 'TITLE', 'u': 'UNIV'}
        self.filepath = ''
        self.initUI()
        self.Center()
        self.Show()

    def initUI(self):
        self.SetBackgroundColour(wx.WHITE)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        lbox = wx.BoxSizer(wx.VERTICAL)
        rbox = wx.BoxSizer(wx.VERTICAL)
        toolbar = wx.ToolBar(self, style=wx.NO_BORDER | wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
        open_tool = toolbar.AddSimpleTool(0, icons.getLoadIconBitmap(), "Open a file from local...")
        save_tool = toolbar.AddSimpleTool(1, icons.getSaveAsIconBitmap(), "Save File")
        saveas_tool = toolbar.AddSimpleTool(2, icons.getExportIconBitmap(), "Save As File...")
        toolbar.AddSeparator()
        setting_tool = toolbar.AddSimpleTool(3, icons.getSettingIconBitmap(), "Preferences...")
        self.editor = MyEditor(self, self.keymap)
        toolbar.Bind(wx.EVT_TOOL, self.onOpen, open_tool)
        toolbar.Bind(wx.EVT_TOOL, self.onSave, save_tool)
        toolbar.Bind(wx.EVT_TOOL, self.onExport, saveas_tool)
        toolbar.Bind(wx.EVT_TOOL, self.onSetting, setting_tool)
        # toolbar.Bind(wx.EVT_TOOL, lambda evt: self.editor.Undo(), undo_tool)
        # toolbar.Bind(wx.EVT_TOOL, lambda evt: self.editor.Redo(), redo_tool)
        toolbar.Realize()
        lbox.Add(toolbar, 0, wx.EXPAND | wx.ALL, 3)
        lbox.Add(self.editor, 1, flag=wx.EXPAND | wx.ALL, border=3)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        hbox.Add(lbox, 1, flag=wx.EXPAND | wx.ALL, border=3)
        rbox.Add(wx.StaticText(self, -1, 'Labels Shortcuts Map'), 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        self.grid = Grid(self, self.keymap)
        rbox.Add(self.grid, 1, flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=3)
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        for label in ['Add', 'Delete', 'Apply', 'SaveAs', 'Load']:
            bmp = loadIcon(label, 18, 18)
            btn = wx.BitmapButton(self, -1, bmp)
            btn.SetToolTipString(label)
            self.Bind(wx.EVT_BUTTON, getattr(self, 'on' + label), btn)
            bbox.Add(btn, 0, wx.ALIGN_CENTER | wx.RIGHT, 3)
        rbox.Insert(1, bbox, 0, wx.EXPAND | wx.ALL, 3)
        hbox.Add(rbox, 0, flag=wx.EXPAND | wx.ALL, border=3)
        self.SetSizer(hbox)

    def onOpen(self, evt):
        if self.editor.IsModified():
            ans = wx.MessageBox("The file content is changed, do you want to save?", "NLP Annotator", wx.YES_NO)
            if ans == wx.YES:
                savedlg = wx.FileDialog(self, wildcard="Annotation file(*.ann)|*.ann|Plain text(*.txt)|*.txt|"
                                                       "Annotation list(*.csv)|*.csv", style=wx.FD_SAVE)
                if savedlg.ShowModal() == wx.ID_OK:
                    filepath = savedlg.GetPath()
                    self.editor.saveFile(filepath)
                else:
                    return
        filedlg = wx.FileDialog(self, wildcard="Annotation files(*.ann;*.txt)|*.ann;*.txt")
        if filedlg.ShowModal() == wx.ID_OK:
            filepath = filedlg.GetPath()
            self.SetTitle(filepath + ' - NLP Annotator')
            self.editor.loadFile(filepath)
            self.filepath = filepath

    def onSave(self, evt):
        self.editor.saveFile(self.filepath)

    def onExport(self, evt):
        file = wx.FileDialog(self, wildcard="Annotation file(*.ann)|*.ann|Plain text(*.txt)|*.txt|"
                                            "Annotation list(*.csv)|*.csv", style=wx.FD_SAVE)
        if file.ShowModal() == wx.ID_OK:
            filepath = file.GetPath()
            self.editor.saveFile(filepath)

    def onClose(self, evt):
        if self.editor.IsModified():
            ans = wx.MessageBox("The file content is changed, do you want to save?", "NLP Annotator",
                                wx.YES_NO | wx.CANCEL)
            if ans == wx.YES:
                self.editor.saveFile(self.filepath)
            elif ans == wx.CANCEL:
                return
        self.Destroy()

    def onAdd(self, evt):
        self.grid.AppendRows(updateLabels=False)

    def onDelete(self, evt):
        while len(self.grid.GetSelectionBlockTopLeft()) > 0:
            uprow = self.grid.GetSelectionBlockTopLeft()[0][0]
            self.grid.DeleteRows(uprow)
        self.grid.ClearSelection()

    def onApply(self, evt):
        key_dict = dict()
        for row in range(self.grid.GetNumberRows()):
            key = self.grid.GetCellValue(row, 0)
            label = self.grid.GetCellValue(row, 1)
            if len(key) > 0 and len(label) > 0:
                key_dict[key] = label
            elif any([len(key) > 0, len(label) > 0]):
                wx.MessageBox("Some rows are incomplete, please set them!", "Warning", wx.OK | wx.ICON_ERROR)
                return

        self.keymap = key_dict
        self.editor.keymap = key_dict
        wx.MessageBox("The changes are applied.", "Information")

    def onSaveAs(self, evt):
        import json
        file = wx.FileDialog(self, defaultFile="keymap.conf", wildcard="Configure file(*.conf)|*.conf",
                             style=wx.FD_SAVE)
        if file.ShowModal() == wx.ID_OK:
            filepath = file.GetPath()
            with open(filepath, 'w') as fp:
                content = json.dumps(self.keymap)
                fp.write(content)

    def onLoad(self, evt):
        import json
        file = wx.FileDialog(self, defaultFile="keymap.conf", wildcard="Configure file(*.conf)|*.conf")
        if file.ShowModal() == wx.ID_OK:
            filepath = file.GetPath()
            with open(filepath, 'r') as fp:
                self.keymap = json.loads(fp.read())
                self.grid.update(self.keymap)
                self.editor.keymap = self.keymap

    def onSetting(self, evt):
        settingdlg = SettingDlg(self, 'Settings')
        settingdlg.SetIcon(icons.SettingIcon.GetIcon())
        settingdlg.Show()


if __name__ == '__main__':
    app = wx.App(False)
    fr = Frame('NLP Annotator')
    app.MainLoop()
