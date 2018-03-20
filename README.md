# Simple Annotator for Natural Language Process

[![Build Status](https://travis-ci.org/frostming/NLP-Annotator.svg?branch=master)](https://travis-ci.org/frostming/NLP-Annotator)

Implemented by wxPython 2.8.12 and Python 2.7.11

**Deprecated:** This is a experimental project that may not run correctly, and wxPython2.8.12 is no longer available from https://www.wxpython.org/.

Inspired by Jie Yang's project [https://github.com/jiesutd/SUTDAnnotator](https://github.com/jiesutd/SUTDAnnotator)

## Version Log

### Beta2
- Left single click to select the annotated block.
- Press `Tab` to jump between annotated blocks.
- Press `Delete` to delete the annotation.
- When an annotated block is selected, press shortcut key to modify in place.
- Save as ***.ann*** file to keep the annotation information. GUI will do render automatically when one loads an ***.ann*** file.
- Save as ***Annotation list file(.csv)*** will export the word - label pairs to a CSV file.
- Implement a setting dialog to customize the colors and font.
- Improve the GUI look.

### Beta1
- Implement main GUI.
- Upload some icons to beautify the interface. All icons are downloaded free from [http://www.easyicon.net/](http://www.easyicon.net/)
- Support dynamically add key map settings and save&load.
