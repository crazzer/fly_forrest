# -*- coding: utf8 -*-

__author__ = 'Evgeny'

from PyQt5 import QtCore, QtWidgets

from constants import SIZE
from field_model import FTableModel

class FDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FDialog, self).__init__(parent)
        self.setupUi()

        self.fieldModel = FTableModel()
        self.tblField.setModel(self.fieldModel)
        self.connectSignals()

    def connectSignals(self):
        self.sbSize.valueChanged.connect(self.on_sbFieldSize_valueChanged)
        self.sbStupidity.valueChanged.connect(self.on_sbStupidity_valueChanged)
        self.sbCapacity.valueChanged.connect(self.on_sbCapacity_valueChanged)
        self.btnStop.clicked.connect(self.on_btnStop_clicked)
        self.tblField.clicked.connect(self.on_tblField_clicked)

    # Slots
    def on_sbFieldSize_valueChanged(self, value):
        isOk, oldValue = self.fieldModel.changeSize(value)
        if not isOk: self.sbSize.setValue(oldValue)
        # self.fieldModel.setSize(value)

    def on_sbStupidity_valueChanged(self, value):
        self.fieldModel.setStupidity(value)

    def on_sbCapacity_valueChanged(self, value):
        isOk, oldValue = self.fieldModel.changeCapacity(value)
        if not isOk:
            self.sbCapacity.setValue(oldValue)

    def on_tblField_clicked(self, index):
        if index.isValid():
            row = index.row()
            col = index.column()
            if not self.fieldModel.isFull(index.row(), index.column()):
                fly = self.fieldModel.addFly(row, col)

    def on_btnStop_clicked(self, index):
        self.fieldModel.killAll.emit()

    def setupUi(self):
        layout = QtWidgets.QHBoxLayout()

        settingsLayout = QtWidgets.QGridLayout()
        self.lblSize = QtWidgets.QLabel()
        settingsLayout.addWidget(self.lblSize, 0, 0)
        self.sbSize = QtWidgets.QSpinBox()
        self.sbSize.setRange(1, 99)
        settingsLayout.addWidget(self.sbSize, 0, 1)

        self.lblStupidity = QtWidgets.QLabel()
        settingsLayout.addWidget(self.lblStupidity, 1, 0)
        self.sbStupidity = QtWidgets.QSpinBox()
        self.sbStupidity.setRange(1, 99)
        settingsLayout.addWidget(self.sbStupidity, 1, 1)

        self.lblCapacity = QtWidgets.QLabel()
        settingsLayout.addWidget(self.lblCapacity, 2, 0)
        self.sbCapacity = QtWidgets.QSpinBox()
        self.sbCapacity.setRange(1, 99)
        settingsLayout.addWidget(self.sbCapacity, 2, 1)
        self.btnStop = QtWidgets.QPushButton()
        settingsLayout.addWidget(self.btnStop, 3, 0, 1, -1)

        spacerLayout = QtWidgets.QHBoxLayout()
        spacerLayout.addSpacerItem(QtWidgets.QSpacerItem(40, 20,
                                                         QtWidgets.QSizePolicy.Minimum,
                                                         QtWidgets.QSizePolicy.Expanding))
        settingsLayout.addLayout(spacerLayout, 4, 0)

        layout.addLayout(settingsLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        self.tblField = QtWidgets.QTableView()
        verticalHeader = self.tblField.verticalHeader()
        verticalHeader.sectionResizeMode(QtWidgets.QHeaderView.Fixed)
        verticalHeader.setDefaultSectionSize(SIZE)
        horizontalHeader = self.tblField.horizontalHeader()
        horizontalHeader.sectionResizeMode(QtWidgets.QHeaderView.Fixed)
        horizontalHeader.setDefaultSectionSize(SIZE)

        mainLayout.addWidget(self.tblField)

        layout.addLayout(mainLayout)

        self.setLayout(layout)
        self.retranslateUi()
        self.setMinimumSize(800, 800)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

    def retranslateUi(self):
        self.lblSize.setText(self.tr('Размер стороны поля'))
        self.lblStupidity.setText(self.tr('Врожденная тупость'))
        self.lblCapacity.setText(self.tr('Мухоемкость'))

        self.btnStop.setText(self.tr('Стоп'))
        self.setWindowTitle('Fly, Forrest, fly!')
