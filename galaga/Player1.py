from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.Qt import Qt


class Player1(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player1.png"))
        self.lives = 3
        self.speed = 4

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_Left in keys_pressed:
            if self.x() > 15:
                dx -= self.speed
        if Qt.Key_Right in keys_pressed:
            if self.x() < 590:
                dx += self.speed
        self.setPos(self.x() + dx, self.y())


class Bullet1(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player1Laser.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.speed = 10
        self.frames = 55
        self.framesPassed = 0

    def game_update(self, keys_pressed, player1):
        if not self.active:
            if Qt.Key_0 in keys_pressed and player1.lives > 0:
                self.active = True
                self.setPos(player1.x() + self.offset_x, player1.y() + self.offset_y)
                self.framesPassed = self.frames

        else:
            self.setPos(self.x(), self.y() - self.speed)
            self.framesPassed -= 1
            if self.framesPassed <= 0:
                self.active = False
                self.setPos(800, 600)


class LifePlayer1(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player1Life.png"))
        self.setPos(x, y)
