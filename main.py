#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from PyQt5 import QtWidgets
from src.view.main_window import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.lastWindowClosed.connect(app.quit)
    main_window = MainWindow(app)
    main_window.iniciar()
    sys.exit(app.exec_())