#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Description:
# Autor:
# Date:
# todo:
# notes:
______
"""

import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp
from gui.windp import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    ''''
    control the app
    '''

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        qApp.installEventFilter(self)
        # here is where the issue is occurs
        self.show()
        self.setupUi(self)

# class Option


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
