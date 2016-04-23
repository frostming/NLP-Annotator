import unittest
import sys
import os
import wx
import fnmatch

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import *


def get_top_win(title=None):
    winlist = wx.GetTopLevelWindows()
    wins = []
    if title is None:
        return winlist[0] if isinstance(winlist, list) else winlist
    if type(title) == str:
        for win in winlist:
            if fnmatch.fnmatch(win.GetTitle(), title):
                wins.append(win)
    elif isinstance(title, type):
        for win in winlist:
            if isinstance(win, title):
                wins.append(win)
    if len(wins) == 0:
        return None
    elif len(wins) == 1:
        return wins[0]
    return wins


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = wx.App(False)
        frame = Frame('Test UI')

    def test_something(self):
        wins = wx.GetTopLevelWindows()
        for win in wins:
            if win.GetTitle() == 'Test UI':
                break
        else:
            raise RuntimeError("The main window didn't show.")


if __name__ == '__main__':
    unittest.main()
