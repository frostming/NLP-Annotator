#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ====================================
# Title:  Customized UI python file
# Author: Frost Ming
# Email:  mianghong@gmail.com
# Date:   2016/4/10
# ====================================
import wx
import wx.richtext


class Grid(wx.grid.Grid):
    def __init__(self, parent, data):
        super(Grid, self).__init__(parent)
        self.SetRowLabelSize(0)
        self.SetDefaultRowSize(30)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetDefaultCellFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.CreateGrid(0, 2, self.wxGridSelectRows)
        self.EnableDragRowSize(False)
        self.SetColLabelValue(0, 'Key')
        self.SetColSize(0, 50)
        self.SetColLabelValue(1, 'Label')
        self.SetColSize(1, 120)
        row = 0
        for k, v in data.items():
            self.AppendRows()
            self.SetCellValue(row, 0, k)
            self.SetCellValue(row, 1, v)
            row += 1

    def update(self, data):
        row_num = self.GetNumberRows()
        if row_num:
            self.DeleteRows(0, row_num)
        row = 0
        for k, v in data.items():
            self.AppendRows()
            self.SetCellValue(row, 0, k)
            self.SetCellValue(row, 1, v)
            row += 1


class MyEditor(wx.richtext.RichTextCtrl):
    def __init__(self, parent, keymap=None):
        super(MyEditor, self).__init__(parent)
        self.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.SetEditable(False)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.onLeftDoubleClick)
        self.keymap = keymap

    def onKeyDown(self, evt):
        key_char = chr(evt.GetUniChar()).lower()
        if key_char in self.keymap:
            start, end = self.GetSelection()
            if start == end:
                return
            attr = wx.richtext.TextAttrEx()
            attr.SetFlags(wx.TEXT_ATTR_BACKGROUND_COLOUR|wx.TEXT_ATTR_FONT_WEIGHT)
            attr.SetBackgroundColour(wx.GREEN)
            attr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.SetStyle((start, end), attr)
            self.SetInsertionPoint(end)
            attr.SetBackgroundColour(wx.CYAN)
            self.BeginStyle(attr)
            self.WriteText('[#%s*]' % self.keymap[key_char])
            self.EndStyle()
        else:
            evt.Skip()

    def onLeftDoubleClick(self, evt):
        pass

if __name__ == '__main__':
    pass