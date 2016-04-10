#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ====================================
# Title:  A simple annotation tool for NLP
# Author: Frost Ming
# Email:  mianghong@gmail.com
# Date:   2016/3/13
# ====================================
import wx
import wx.grid
import wx.lib.buttons as buttons
import wx.richtext
from ui import *


def loadIcon(icon, w, h):
    img = wx.Image(icon, wx.BITMAP_TYPE_ICO)
    img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
    return img.ConvertToBitmap()


class Frame(wx.Frame):
    def __init__(self, title):
        super(Frame, self).__init__(None, -1, title, size=(800, 600))
        self.SetMinSize((800, 600))
        self.keymap = {'a': 'ACTION', 'c': 'CONT', 'd': 'DATA', 'e': 'EDU', 'g': 'GEND',
                       'l': 'LOC', 'm': 'MISC', 'n': 'NAME', 'o': 'ORG', 'p': 'PRO',
                       'r': 'RACE', 't': 'TITLE', 'u': 'UNIV'}
        self.initUI()
        self.Center()
        self.Show()

    def initUI(self):
        self.SetBackgroundColour(wx.WHITE)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        lbox = wx.BoxSizer(wx.VERTICAL)
        rbox = wx.BoxSizer(wx.VERTICAL)
        fbox = wx.BoxSizer(wx.HORIZONTAL)
        self.filename = wx.StaticText(self, -1, 'File: ')
        fbox.Add(self.filename, 1, wx.ALL | wx.ALIGN_CENTRE, border=3)
        open_btn = wx.Button(self, wx.ID_OPEN)
        save_btn = wx.Button(self, wx.ID_SAVEAS)
        fbox.Add(open_btn, 0, wx.LEFT | wx.ALIGN_CENTER, border=3)
        fbox.Add(save_btn, 0, wx.ALL | wx.ALIGN_CENTER, border=3)
        lbox.Add(fbox, 0, wx.EXPAND, 3)
        self.editor = MyEditor(self, self.keymap)
        lbox.Add(self.editor, 1, flag=wx.EXPAND | wx.ALL, border=3)
        self.Bind(wx.EVT_BUTTON, self.onOpen, open_btn)
        self.Bind(wx.EVT_BUTTON, self.onExport, save_btn)
        #self.Bind(wx.EVT_CLOSE, self.onClose)
        hbox.Add(lbox, 1, flag=wx.EXPAND | wx.ALL, border=3)
        rbox.Add(wx.StaticText(self, -1, 'Labels Shortcuts Map'), 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        self.grid = Grid(self, self.keymap)
        rbox.Add(self.grid, 1, flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=3)
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        for label in ['add', 'delete', 'apply', 'saveas', 'load']:
            bmp = loadIcon('icons/%s.ico' % label, 15, 15)
            btn = buttons.GenBitmapButton(self, bitmap=bmp)
            btn.SetToolTipString(label.capitalize())
            self.Bind(wx.EVT_BUTTON, getattr(self, 'on' + label.capitalize()), btn)
            bbox.Add(btn, 0, wx.ALIGN_CENTER | wx.RIGHT, 3)
        rbox.Insert(1, bbox, 0, wx.EXPAND | wx.ALL, 3)
        hbox.Add(rbox, 0, flag=wx.EXPAND | wx.ALL, border=3)
        self.SetSizer(hbox)

    def onOpen(self, evt):
        filedlg = wx.FileDialog(self, wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*")
        if filedlg.ShowModal() == wx.ID_OK:
            self.filepath = filedlg.GetPath()
            self.filename.SetLabel('File: ' + self.filepath)
            content = open(self.filepath).read()
            self.editor.SetValue(content)
            self.editor.SetFocus()

    def onExport(self, evt):
        file = wx.FileDialog(self, wildcard="Plain text(*.txt)|*.txt",
                             style=wx.FD_SAVE)
        if file.ShowModal() == wx.ID_OK:
            filepath = file.GetPath()
            with open(filepath, 'w') as fp:
                fp.write(self.editor.GetValue())

    def onClose(self, evt):
        pass

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

    def onSaveas(self, evt):
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


if __name__ == '__main__':
    app = wx.App(False)
    Frame('Simple Annotator for NLP')
    app.MainLoop()
