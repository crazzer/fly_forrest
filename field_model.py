# -*- coding: utf8 -*-

__author__ = 'Evgeny'

import math

from PyQt5 import QtCore, QtGui

from constants import SIZE
from fly import Fly

class FTableModel(QtCore.QAbstractTableModel):
    killAll = QtCore.pyqtSignal()

    def __init__(self):
        super(FTableModel, self).__init__()
        self._size = 1
        self._capacity = 1
        self._values = [[[] for _ in range(self._size)] for _ in range(self._size)]
        self._stupidity = 1
        self._threads = []
        self._mutex = QtCore.QMutex()

    # Переопределяем родительские методы
    def rowCount(self, parent=None):
        return self._size

    def columnCount(self, parent=None):
        return self._size

    def flags(self, index):
        return super(FTableModel, self).flags(index) & ~QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DecorationRole:
            row = index.row()
            column = index.column()

            if len(self._values) > row and len(self._values[row]) > column:
                values = self._values[row][column]
                if values:
                    paintPixmap = QtGui.QPixmap(SIZE, SIZE)
                    paintPixmap.fill(QtGui.QColor(255, 255, 255))
                    painter = QtGui.QPainter(paintPixmap)
                    x = 0
                    y = 0
                    for index, fly in enumerate(values):
                        amount = len(values)
                        row_amount = math.ceil(amount**0.5)
                        edge_size = SIZE/row_amount
                        if fly.isAlive():
                            pixmap = QtGui.QPixmap('img/fly1.jpg').scaled(QtCore.QSize(edge_size, edge_size),
                                                                      QtCore.Qt.KeepAspectRatio,
                                                                      QtCore.Qt.SmoothTransformation)
                        else:
                            pixmap = QtGui.QPixmap('img/dead_bug.jpg').scaled(QtCore.QSize(edge_size, edge_size),
                                                                          QtCore.Qt.KeepAspectRatio,
                                                                          QtCore.Qt.SmoothTransformation)
                        painter.drawPixmap(x, y, pixmap)
                        x += pixmap.width()
                        if not (index+1) % row_amount:
                            x = 0
                            y += pixmap.height()
                    return paintPixmap

    # setters/getters
    def setSize(self, size):
        '''Изменяем размер поля и сбрасываем состояние модели

        :param size: Новый размер грани поля
        '''
        self.beginResetModel()
        self._size = size
        self.endResetModel()

    def size(self):
        return self._size

    def setStupidity(self, stupidity):
        self._stupidity = stupidity

    def setCapacity(self, capacity):
        self._capacity = capacity

    # changers - сеттеры с проверкой возможности и отправкой флага успеха операции для возможности откатить изменения
    def changeSize(self, size):
        old_size = self._size
        success = True
        if size > self._size:
            diff = size - self._size
            for row in self._values:
                row += [[] for _ in range(diff)]  # Добавляем столбцы
            self._values += [[[] for _ in range(size)] for _ in range(diff)]
        elif size < self._size:
            # Блокируем возможность перелета мух в ячейки, которые могут быть удалены
            self._mutex.lock()
            diff = self._size - size
            for index, row in enumerate(self._values):
                if (index < size and any(row[-diff:])) or \
                        (index >= size and any(row)):
                    success = False
                    break
            if success:
                del self._values[size:]
                for row in self._values:
                    del row[size:]
            self._mutex.unlock()
        if success:
            self.setSize(size)
        return success, old_size

    def changeCapacity(self, capacity):
        success = True
        old_capacity = self._capacity
        if capacity < self._capacity:
            # Блокируем возможность изменения количества мух в проверенных ячейках пока идем по циклу
            self._mutex.lock()
            for row in self._values:
                for _ in filter(lambda cell: len(cell) > capacity, row):
                    success = False
                    break
                if not success:
                    break
            self._mutex.unlock()
        if success:
            self._capacity = capacity
        return success, old_capacity

    # Работа с мухами
    def isFull(self, row, col):
        if not self.index(row, col).isValid():
            return True     # для нас отсутствующая ячейка равнозначна полной - мы точно так же не можем больше ничего с ней сделать
        return len(self._values[row][col]) >= self._capacity

    def addFly(self, row, column):
        """Добавление мухи в указанную ячейку

        :param row: строка
        :param column: столбец
        """
        thread = QtCore.QThread()
        self._mutex.lock()
        fly = Fly(row, column, self._stupidity, self._size, self)
        self._values[row][column].append(fly)
        self._mutex.unlock()
        fly.moveToThread(thread)
        thread.started.connect(fly.run)
        fly.died.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.clearDeadThreads)
        self.killAll.connect(fly.die)
        fly.moved.connect(self.moveFly)
        fly.died.connect(self.resetInternalData)
        fly.died.connect(self.reset)
        thread.start()
        self._threads.append(thread) # Препятствуем удалению соовтетствующей переменной сборщиком мусора в python.
        # TODO: удалять ссылки на потоки после того, как они закончат работу


    def moveFly(self, new_row, new_col, old_row, old_col):
        """Перемещение мухи между ячейками"""
        self.beginResetModel()
        self._mutex.lock()
        self._values[new_row][new_col].append(self.sender())
        self._values[old_row][old_col].remove(self.sender())
        self._mutex.unlock()
        self.endResetModel()

    def reset(self):
        # Для отработки умерших, которые ничего в данных по сути не меняют, но требуют обновления представления
        self.beginResetModel()
        self.endResetModel()

    def clearDeadThreads(self):
        for thread in self._threads:
            if thread.isFinished():
                self._threads.remove(thread)

    def getReport(self):
        report = '<ul>'
        for row, rowValues in enumerate(self._values):
            for col, cellValues in enumerate(rowValues):
                if cellValues:
                    report += '<li>{0}-{1}</li>'.format(row+1, col+1)
                    report += '<ul>'
                    for index, fly in enumerate(cellValues):
                        report += '<li>Муха {0}: время жизни - {1}c, пройденное расстояние - {2} шага'.format(index+1,
                                                                                                        fly.age(),
                                                                                                        fly.distance())

                    report += '</ul>'
        report += '</ul>'
        return report