from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.Qt import Qt


class Player2(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player2.png"))
        self.lives = 3
        self.speed = 4

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_A in keys_pressed:
            if self.x() > 20:
                dx -= self.speed
        if Qt.Key_D in keys_pressed:
            if self.x() < 589:
                dx += self.speed
        self.setPos(self.x() + dx, self.y())


class Bullet2(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player2Laser.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.speed = 10
        self.frames = 55
        self.framesPassed = 0

    def game_update(self, keys_pressed, player2):
        if not self.active:
            if Qt.Key_Space in keys_pressed and player2.lives > 0:
                self.active = True
                self.setPos(player2.x() + self.offset_x, player2.y() + self.offset_y)
                self.framesPassed = self.frames

        else:
            self.setPos(self.x(), self.y() - self.speed)
            self.framesPassed -= 1
            if self.framesPassed <= 0:
                self.framesPassed = -1
                self.active = False
                self.setPos(800, 600)


class LifePlayer2(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/player2Life.png"))
        self.setPos(x, y)
