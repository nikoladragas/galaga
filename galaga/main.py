import sys
from PyQt5.QtCore import (
    Qt,
    QBasicTimer,
    QTimer)
from PyQt5.QtGui import (
    QBrush,
    QPixmap
)
from PyQt5.QtWidgets import (
    QApplication,  # Sama QT aplikacija
    QGraphicsItem,  # Objekti ove klase mogu da se ubacuju u scenu, apstraktna,nasledjuje se
    QGraphicsPixmapItem,  # Nasledjuje QGraphicsItem
    QGraphicsRectItem,  # Nasledjuje QGraphicsItem
    QGraphicsScene,  # U objekat scene ubacujemo sve iteme koje zelimo da iscrtamo
    QGraphicsView  # Da bi nacrtali scenu treba nam objekat ove klase
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 3  # pix/frame
PLAYER_BULLET_X_OFFSETS = [0, 32]
PLAYER_BULLET_Y = 15
BULLET_SPEED = 10  # pix/frame
BULLET_FRAMES = 55
FRAME_TIME_MS = 16  # ms/frame


class Enemy(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("enemyRed2.png"))
        self.setPos(x, y)

    def move_left(self):
        self.setPos(self.x() - 20, self.y())

    def move_right(self):
        self.setPos(self.x() + 20, self.y())


class Player1(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerShip1_blue.png"))

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_Left in keys_pressed:
            if self.x() > 0:
                dx -= PLAYER_SPEED
        if Qt.Key_Right in keys_pressed:
            if self.x() < 604:
                dx += PLAYER_SPEED
        self.setPos(self.x() + dx, self.y())


class Player2(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerShip1_red.png"))

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_A in keys_pressed:
            if self.x() > 0:
                dx -= PLAYER_SPEED
        if Qt.Key_D in keys_pressed:
            if self.x() < 604:
                dx += PLAYER_SPEED
        self.setPos(self.x() + dx, self.y())


class Bullet1(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("laserBlue07.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.frames = 0

    def game_update(self, keys_pressed, player1):
        if not self.active:
            if Qt.Key_0 in keys_pressed:
                self.active = True
                self.setPos(player1.x() + self.offset_x, player1.y() + self.offset_y)
                self.frames = BULLET_FRAMES

        else:
            self.setPos(self.x(), self.y() - BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.active = False
                self.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)


class Bullet2(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("laserBlue07.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.frames = 0

    def game_update(self, keys_pressed, player2):
        if not self.active:
            if Qt.Key_Space in keys_pressed:
                self.active = True
                self.setPos(player2.x() + self.offset_x, player2.y() + self.offset_y)
                self.frames = BULLET_FRAMES

        else:
            self.setPos(self.x(), self.y() - BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.active = False
                self.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)


class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        # hold the set of keys we're pressing
        self.keys_pressed = set()

        # use a timer to get 60Hz refresh (hopefully)
        self.timer = QBasicTimer()
        self.timer.start(FRAME_TIME_MS, self)

        self.timerEnemy = QTimer()
        self.timerEnemy.timeout.connect(self.game_update_enemy)
        self.timerEnemy.start(1000)

        bg = QGraphicsRectItem()
        bg.setRect(-1, -1, SCREEN_WIDTH + 2, SCREEN_HEIGHT + 2)
        bg.setBrush(QBrush(Qt.black))
        self.addItem(bg)

        self.levo = 1
        self.desno = 5

        self.enemies = [Enemy(131, 10), Enemy(173, 10), Enemy(215, 10), Enemy(257, 10), Enemy(299, 10), Enemy(341, 10),
                        Enemy(383, 10), Enemy(425, 10), Enemy(467, 10), Enemy(509, 10),
                        Enemy(131, 50), Enemy(173, 50), Enemy(215, 50), Enemy(257, 50), Enemy(299, 50), Enemy(341, 50),
                        Enemy(383, 50), Enemy(425, 50), Enemy(467, 50), Enemy(509, 50),
                        Enemy(131, 90), Enemy(173, 90), Enemy(215, 90), Enemy(257, 90), Enemy(299, 90), Enemy(341, 90),
                        Enemy(383, 90), Enemy(425, 90), Enemy(467, 90), Enemy(509, 90)]

        for e in self.enemies:
            self.addItem(e)

        self.player1 = Player1()
        self.player1.setPos(20, 530)
        self.player2 = Player2()
        self.player2.setPos(589, 530)
        self.bullet1 = Bullet1(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
        self.bullet2 = Bullet2(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)

        self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet1)

        self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet2)
        self.addItem(self.player1)
        self.addItem(self.player2)

        score = QGraphicsRectItem()
        score.setRect(672, -1, 128, SCREEN_HEIGHT + 2)
        score.setBrush(QBrush(Qt.yellow))
        self.addItem(score)

        self.view = QGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.show()
        self.view.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setSceneRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        self.keys_pressed.remove(event.key())

    def timerEvent(self, event):
        self.game_update()
        self.update()

    def game_update(self):
        self.player1.game_update(self.keys_pressed)
        self.player2.game_update(self.keys_pressed)

        for e in self.enemies:
            if e.x() <= self.bullet1.x() <= e.x() + 32:
                if e.y() <= self.bullet1.y() <= e.y() + 26:
                    self.enemies.remove(e)
                    self.removeItem(e)
                    self.removeItem(self.bullet1)
                    self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.addItem(self.bullet1)
            if e.x() <= self.bullet2.x() <= e.x() + 32:
                if e.y() <= self.bullet2.y() <= e.y() + 26:
                    self.enemies.remove(e)
                    self.removeItem(e)
                    self.removeItem(self.bullet2)
                    self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.addItem(self.bullet2)

        self.bullet1.game_update(self.keys_pressed, self.player1)
        self.bullet2.game_update(self.keys_pressed, self.player2)

    def game_update_enemy(self):
        if 0 < self.desno < 9:
            self.desno += 1
            if self.desno == 9:
                self.desno = 0
                self.levo = 1
            for e in self.enemies:
                e.move_right()
        elif 0 < self.levo < 9:
            self.levo += 1
            if self.levo == 9:
                self.levo = 0
                self.desno = 1
            for e in self.enemies:
                e.move_left()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = Scene()
    sys.exit(app.exec_())
