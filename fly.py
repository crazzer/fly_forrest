# -*- coding: utf8 -*-

__author__ = 'Evgeny'

import datetime
import random

from PyQt5 import QtCore, QtWidgets


class Fly(QtCore.QObject):
    moved = QtCore.pyqtSignal(int, int, int, int)
    died = QtCore.pyqtSignal()

    def __init__(self, row, col, stupidity, worldSize, parent):
        super(Fly, self).__init__()
        self.row = row
        self.col = col
        self.stupidity = stupidity
        self.worldSize = worldSize
        self.birthTime = datetime.datetime.now()  # Для отчетности
        self.deathTime = self.birthTime + datetime.timedelta(seconds=self.stupidity * self.worldSize)
        self.parent = parent
        self._isDead = False
        self.steps = 0  # Для отчетности

    def run(self):
        while self.isAlive() and not self.thread().isFinished():
            self.thread().sleep(self.stupidity)
            QtWidgets.QApplication.processEvents()  # Обрабатываем внешние сигналы
            self.move()
        self.died.emit()

    def move(self):
        """Решаем, куда хочется полететь, и пытаемся сделать это
        """
        current_field_size = self.parent.size()
        choices = []
        if current_field_size > 1 and self.isAlive():
            if self.row > 0:
                choices.append((self.row - 1, self.col))
            if self.row < current_field_size - 1:
                choices.append((self.row + 1, self.col))
            if self.col > 0:
                choices.append((self.row, self.col - 1))
            if self.col < current_field_size - 1:
                choices.append((self.row, self.col + 1))
            new_pos = random.choice(choices)
            # TODO: наладить более безопасный процесс перелета:
            # сейчас мы проверяем возможность улететь здесь, и шлем сигнал, чтобы модель применила изменения у себя.
            # процесс не атомарный, и теоретически мы можем получить невалидные данные после выполнения функции
            # (мухоемкость может быть превышена, если в другом потоке мы выполним то же самое после отправки,
            # но до обработки сигнала отсюда)
            if not self.parent.isFull(*new_pos):
                old_row, old_col = self.row, self.col
                self.row, self.col = new_pos
                self.steps += 1
                self.moved.emit(self.row, self.col, old_row, old_col)

    # Вопросы жизни и смерти
    def die(self):
        self._isDead = True

    def isAlive(self):
        """Проверяем, что муха до сих пор жива
        В принципе можно было бы завязаться и на количество попыток перелетов, вместо непрерывной проверки времени. """

        # На случай, если всех мух разом прихлопнули, храним атрибут _isDead.
        if not self._isDead:
            self._isDead = datetime.datetime.now() > self.deathTime
        return not self._isDead
