#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import math

from utilities import UpdateChecker, tuple_version, ismacos, iswindows

from PySide6.QtCore import Qt, QByteArray, QCoreApplication, QLibraryInfo, QTimer, QMargins, qVersion
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton
from PySide6.QtWidgets import QStyleFactory, QTextEdit, QMainWindow, QWidget, QLayout
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPalette, QPixmap, QImage


def launch_gui(bk, prefs):
    if not ismacos:
        try:
            setup_highdpi(bk._w.highdpi)
        except Exception:
            pass
    try:
        setup_ui_font(bk._w.uifont)
    except Exception:
        pass
    if not ismacos and not iswindows:
        # Qt 5.10.1 on Linux resets the global font on first event loop tick.
        # So workaround it by setting the font once again in a timer.
        try:
            QTimer.singleShot(0, lambda : setup_ui_font(bk._w.uifont))
        except Exception:
            pass
    app = QApplication([])
    icon = os.path.join(bk._w.plugin_dir, bk._w.plugin_name, 'plugin.png')
    app.setWindowIcon(QIcon(icon))
    
    # Make plugin match Sigil's light/dark theme
    dark_palette(bk, app)
    
    win = guiMain(bk, prefs)
    app.exec_()

def dark_palette(bk, app):
    if not (bk.launcher_version() >= 20200117):
        return
    if bk.colorMode() != "dark":
        return

    p = QPalette()
    sigil_colors = bk.color
    dark_color = QColor(sigil_colors("Window"))
    disabled_color = QColor(127,127,127)
    dark_link_color = QColor(108, 180, 238)
    text_color = QColor(sigil_colors("Text"))
    p.setColor(p.Window, dark_color)
    p.setColor(p.WindowText, text_color)
    p.setColor(p.Base, QColor(sigil_colors("Base")))
    p.setColor(p.AlternateBase, dark_color)
    p.setColor(p.ToolTipBase, dark_color)
    p.setColor(p.ToolTipText, text_color)
    p.setColor(p.Text, text_color)
    p.setColor(p.Disabled, p.Text, disabled_color)
    p.setColor(p.Button, dark_color)
    p.setColor(p.ButtonText, text_color)
    p.setColor(p.Disabled, p.ButtonText, disabled_color)
    p.setColor(p.BrightText, Qt.red)
    p.setColor(p.Link, dark_link_color)
    p.setColor(p.Highlight, QColor(sigil_colors("Highlight")))
    p.setColor(p.HighlightedText, QColor(sigil_colors("HighlightedText")))
    p.setColor(p.Disabled, p.HighlightedText, disabled_color)

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(p)

def setup_highdpi(highdpi):
    has_env_setting = False
    env_vars = ('QT_AUTO_SCREEN_SCALE_FACTOR', 'QT_SCALE_FACTOR', 'QT_SCREEN_SCALE_FACTORS', 'QT_DEVICE_PIXEL_RATIO')
    for v in env_vars:
        if os.environ.get(v):
            has_env_setting = True
            break
    if highdpi == 'on' or (highdpi == 'detect' and not has_env_setting):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    elif highdpi == 'off':
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
        for p in env_vars:
            os.environ.pop(p, None)

def setup_ui_font(font_str):
    font = QFont()
    font.fromString(font_str)
    QApplication.setFont(font)


class guiMain(QMainWindow):
    def __init__(self, bk, prefs):
        super(guiMain, self).__init__()
        # Edit Plugin container object
        self.bk = bk
        self.prefs = prefs
        
        self._ok_to_close = False
        self.setWindowTitle('Remove Duplicates')
        self.setup_ui()
    
    def setup_ui(self):
        app = QApplication.instance()
        p = app.palette()
        link_color = p.color(p.ColorGroup.Active, p.ColorRole.Link).name()
        
        layout = QVBoxLayout()
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        self.process_button = QPushButton('Remove Duplicates', self)
        self.process_button.clicked.connect(self._remove_duplicates)
        button_layout.addWidget(self.process_button)
        
        button_layout.addStretch(-1)
        
        self.abort_button = QPushButton('Abort', self)
        self.abort_button.clicked.connect(self._abort_clicked)
        button_layout.addWidget(self.abort_button)
        
        
        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self._quit_clicked)
        button_layout.addWidget(self.quit_button)
        
        layout.addStretch(-1)
        
        images_layout = FlowLayout(self)
        layout.addLayout(images_layout)
        
        for id, path, minetype in self.bk.image_iter():
            images_layout.addWidget(ImageCheck(self.bk.id_to_bookpath(id), self.bk.readfile(id)))
        
        
        if 'windowGeometry' in self.prefs:
            try:
                self.restoreGeometry(QByteArray.fromHex(self.prefs['windowGeometry'].encode('ascii')))
            except Exception:
                pass
        
        self.show()
    
    
    def _remove_duplicates(self):
        print('_remove_duplicates()')
        print('Remove Duplicates')
    
    def _quit_clicked(self):
        self._ok_to_close = True
        
        
        self.close()
    
    def _abort_clicked(self):
        self._ok_to_close = True
        self.close()
    
    def closeEvent(self, event):
        self.prefs['windowGeometry'] = self.saveGeometry().toHex().data().decode('ascii')
        if self._ok_to_close:
            event.accept()
        else:
            self._abort_clicked()


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))
        
        self._item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self._item_list.append(item)
    
    def count(self):
        return len(self._item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
    
    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            layout_spacing_y = style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class ImageCheck(QWidget):
    def __init__(self, image_path, bytes):
        QWidget.__init__(self)
        self.setStyleSheet("border: 1px solid black")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.image_name = os.path.basename(image_path)
        self.check = QCheckBox(self.image_name, self)
        
        image = QPixmap()
        image.loadFromData(bytes)
        image.scaled(100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, transformMode=Qt.TransformationMode.FastTransformation)
        label = QLabel(self)
        label.setPixmap(image)
        layout.addWidget(label)
        
        info_layout = QHBoxLayout()
        layout.addLayout(info_layout)
        
        size = str(image.width()) +'x'+ str(image.height())
        info_layout.addWidget(QLabel(size))
        
        info_layout.addStretch(-1)
        
        size = len(bytes) / 1024
        size = str(size)+'Kb'
        info_layout.addWidget(QLabel(size))
    
    def checkState(self):
        return self.check.checkState()


def main():
    return -1

if __name__ == "__main__":
    sys.exit(main())
