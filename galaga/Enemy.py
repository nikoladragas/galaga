from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Enemy(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/enemy.png"))
        self.setPos(x, y)
        self.active = False
        self.frames = 0
        self.chosen = False
        self.powerUp = False
        self.collapseSpeed = 2
        self.collapseFrames = 350

    def move_left(self):
        if not self.active:
            self.setPos(self.x() - 20, self.y())

    def move_right(self):
        if not self.active:
            self.setPos(self.x() + 20, self.y())

    def collapse(self):
        if not self.active:
            self.active = True
            self.frames = self.collapseFrames

        else:
            self.setPos(self.x(), self.y() + self.collapseSpeed)
            self.frames -= 1
            if self.frames <= 0:
                self.frames = -1
                self.active = False


class BulletEnemy(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("Images/enemyLaser.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.speed = 5
        self.frames = 140
        self.framesPassed = 0

    def game_update(self, enemy):
        if not self.active:
            self.active = True
            self.setPos(enemy.x() + self.offset_x, enemy.y() + self.offset_y)
            self.framesPassed = self.frames

        else:
            self.setPos(self.x(), self.y() + self.speed)
            self.framesPassed -= 1
            if self.framesPassed <= 0:
                self.active = False
                self.setPos(800, 600)
