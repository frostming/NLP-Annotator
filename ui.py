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
import wx.grid
import os, json, re


def is_overlap(range1, range2):
    """Check if range1=(a, b), range2=(c, d) are overlapped.
    The left border is included while right border excluded"""
    return max(range1[0], range2[0]) < min(range1[1], range2[1])


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
        self.SetColSize(0, 40)
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
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMouseMove)
        self.keymap = keymap
        self.annotation_list = []
        self.textfont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.text_bgcolor = wx.GREEN
        self.label_bgcolor = wx.CYAN
        self.wrapper_bgcolor = wx.BLUE
        self.SetFont(self.textfont)
        self.SetEditable(False)
        self.SetModified(False)

    def onKeyDown(self, evt):
        if evt.GetKeyCode() == wx.WXK_DELETE:
            start, end = self.GetSelection()
            if not (start, end) in self.annotation_list:
                return
            target = self.GetStringSelection()
            text = re.match(r'\[(.+?)\#.*\*\]', target).group(1)
            self.DeleteSelectedContent()
            attr = wx.richtext.TextAttrEx()
            attr.SetFlags(wx.TEXT_ATTR_BACKGROUND_COLOUR | wx.TEXT_ATTR_FONT_WEIGHT)
            attr.SetBackgroundColour(wx.WHITE)
            attr.SetFont(self.textfont)
            attr.SetFontWeight(wx.NORMAL)
            self.BeginStyle(attr)
            self.WriteText(text)
            self.EndStyle()
            self.annotation_list.remove((start, end))
            bias = len(target) - len(text)
            for i in range(len(self.annotation_list)):
                item = self.annotation_list[i]
                if item[0] >= end:
                    self.annotation_list[i] = (item[0] - bias, item[1] - bias)
        elif evt.GetKeyCode() == wx.WXK_TAB:
            pos = self.GetCaretPosition()
            for item in self.annotation_list:
                if pos <= item[0]:
                    next_item = item
                    break
            else:
                next_item = self.annotation_list[0]
            self.SetSelection(*next_item)
        else:
            key_char = chr(evt.GetUniChar()).lower()
            if key_char not in self.keymap: return
            start, end = self.GetSelection()
            if start == end: return
            if not (start, end) in self.annotation_list and any(
                    is_overlap((start, end), item) for item in self.annotation_list):
                return
            target = self.GetStringSelection()
            if (start, end) in self.annotation_list:
                text = re.match(r'\[(.+?)\#.*\*\]', target).group(1)
                self.annotation_list.remove((start, end))
            else:
                text = target
            self.DeleteSelectedContent()
            self.SetInsertionPoint(start)
            self.RenderInput(text, self.keymap[key_char])
            new_item = (start, self.GetCaretPosition() + 1)
            self.annotation_list.append(new_item)
            self.annotation_list.sort()
            bias = len(self.keymap[key_char]) + 4 + len(text) - len(target)
            index = self.annotation_list.index(new_item)
            for i in range(index + 1, len(self.annotation_list)):
                item = self.annotation_list[i]
                self.annotation_list[i] = (item[0] + bias, item[1] + bias)

    def onLeftUp(self, evt):
        pos = self.GetCaretPosition()
        for item in self.annotation_list:
            if pos in range(*item):
                start, end = item
                break
        else:
            evt.Skip()
            return
        self.SetSelection(start, end)
        evt.Skip()

    def onMouseMove(self, evt):
        point = evt.GetPosition()
        pos = self.HitTest(point)[1]
        if any(pos in range(*item) for item in self.annotation_list):
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            evt.Skip()

    def loadFile(self, filepath):
        ext = os.path.splitext(filepath)[1]
        content = open(filepath).read()
        if ext.lower() == '.ann':
            content_dict = json.loads(content)
            text = content_dict['content']
            self.annotation_list = [tuple(i) for i in content_dict['annotation_list']]
        else:
            text = content
            self.annotation_list = []
        self.SetValue(text)
        self.RenderAll()
        self.SetFocus()
        self.SetModified(False)

    def saveFile(self, filepath):
        ext = os.path.splitext(filepath)[1]
        if ext.lower() == '.ann':
            content_dict = {'annotation_list': self.annotation_list, 'content': self.GetValue()}
            content = json.dumps(content_dict)
            with open(filepath, 'w') as fp:
                fp.write(content)
        elif ext.lower() == '.csv':
            output_list = []
            for start, end in self.annotation_list:
                target = self.GetRange(start, end)
                pat = re.match(r'\[(.+?)\#(\w+)\*\]', target)
                text, label = pat.groups()
                output_list.append(text + ',' + label + '\n')
            output_list = list(set(output_list))
            with open(filepath, 'w') as fp:
                fp.writelines(output_list)
        else:
            with open(filepath, 'w') as fp:
                fp.write(self.GetValue())
        self.SetModified(False)

    def RenderInput(self, text, label):
        attr = wx.richtext.TextAttrEx()
        attr.SetFlags(wx.TEXT_ATTR_BACKGROUND_COLOUR | wx.TEXT_ATTR_FONT_WEIGHT)
        attr.SetBackgroundColour(self.wrapper_bgcolor)
        attr.SetFont(self.textfont)
        attr.SetFontWeight(wx.BOLD)
        self.BeginStyle(attr)
        self.WriteText('[')
        self.EndStyle()
        attr.SetBackgroundColour(self.text_bgcolor)
        self.BeginStyle(attr)
        self.WriteText(text)
        self.EndStyle()
        attr.SetBackgroundColour(self.label_bgcolor)
        self.BeginStyle(attr)
        self.WriteText('#%s*' % label)
        self.EndStyle()
        attr.SetBackgroundColour(self.wrapper_bgcolor)
        self.BeginStyle(attr)
        self.WriteText(']')
        self.EndStyle()

    def RenderAll(self):
        for start, end in self.annotation_list:
            target = self.GetRange(start, end)
            pat = re.match(r'\[(.+?)\#(\w+)\*\]', target)
            text, label = pat.groups()
            self.SetInsertionPoint(start)
            self.Delete((start, end))
            self.RenderInput(text, label)
            self.SetCaretPosition(0)
        self.SetModified(False)


class SettingDlg(wx.Dialog):
    def __init__(self, parent, title):
        super(SettingDlg, self).__init__(parent, -1, title)
        editor = parent.editor
        self.text_bgcolor = editor.text_bgcolor
        self.label_bgcolor = editor.label_bgcolor
        self.wrapper_bgcolor = editor.wrapper_bgcolor
        self.textfont = editor.textfont
        self.initUi()

    def initUi(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(4, 2, 10,20)
        fgsizer.Add(wx.StaticText(self, -1, 'Text Background'), 0, wx.ALL |  wx.ALIGN_LEFT, 5)
        fgsizer.Add(wx.ColourPickerCtrl(self, 0, self.text_bgcolor), 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        fgsizer.Add(wx.StaticText(self, -1, 'Label Background'), 0, wx.ALL |  wx.ALIGN_LEFT, 5)
        fgsizer.Add(wx.ColourPickerCtrl(self, 1, self.label_bgcolor), 0, wx.ALL |  wx.ALIGN_RIGHT, 5)
        fgsizer.Add(wx.StaticText(self, -1, 'Wrapper Background'), 0, wx.ALL |  wx.ALIGN_LEFT, 5)
        fgsizer.Add(wx.ColourPickerCtrl(self, 2, self.wrapper_bgcolor), 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        fgsizer.Add(wx.StaticText(self, -1, 'Text Font'), 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, 5)
        fgsizer.Add(wx.FontPickerCtrl(self, -1, self.textfont), 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorChanged)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.onFontChanged)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        buttonsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(fgsizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(buttonsizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        self.SetSizerAndFit(sizer)


    def onColorChanged(self, evt):
        if evt.GetId() == 0:
            self.text_bgcolor = evt.GetColour()
        elif evt.GetId() == 1:
            self.label_bgcolor = evt.GetColour()
        elif evt.GetId() == 2:
            self.wrapper_bgcolor = evt.GetColour()
        evt.Skip()

    def onFontChanged(self, evt):
        self.textfont = evt.GetFont()
        evt.Skip()

    def onOK(self, evt):
        editor = self.GetParent().editor
        editor.textfont = self.textfont
        editor.text_bgcolor = self.text_bgcolor
        editor.label_bgcolor = self.label_bgcolor
        editor.wrapper_bgcolor = self.wrapper_bgcolor
        editor.SetFont(self.textfont)
        editor.RenderAll()
        evt.Skip()

if __name__ == '__main__':
    pass
