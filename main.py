# -*- coding: utf8 -*-

__author__ = 'Evgeny'

import sys

from PyQt5 import QtWidgets

from field_dialog import FDialog

SIZE = 100


if __name__ == '__main__':
    qApp = QtWidgets.QApplication(sys.argv)
    dialog = FDialog()
    dialog.show()
    qApp.exec_()

    sys.exit(0)
