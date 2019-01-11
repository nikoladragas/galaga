import sys

import multiprocessing
from PyQt5.QtCore import (
    Qt,
    QBasicTimer,
    QTimer)
from PyQt5.QtGui import (
    QBrush,
    QPixmap,
    QFont)
from PyQt5.QtWidgets import *
import random
from random import *
from multiprocessing import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER1_SPEED = 4   # pix/frame
PLAYER2_SPEED = 4
PLAYER_BULLET_X_OFFSETS = [0, 32]
PLAYER_BULLET_Y = -20
BULLET_SPEED = 10  # pix/frame
BULLET_FRAMES = 55
FRAME_TIME_MS = 16  # ms/frame
ENEMY_BULLET_X_OFFSET = 14
ENEMY_BULLET_Y_OFFSET = 26
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_FRAMES = 700/ENEMY_BULLET_SPEED
ENEMY_COLLAPSE_SPEED = 2
ENEMY_COLLAPSE_FRAMES = 700/ENEMY_COLLAPSE_SPEED


class Enemy(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("enemyRed2.png"))
        self.setPos(x, y)
        self.active = False
        self.frames = 0
        self.chosen = False
        self.powerUp = False

    def move_left(self):
        if self.active == False:
            self.setPos(self.x() - 20, self.y())

    def move_right(self):
        if self.active == False:
            self.setPos(self.x() + 20, self.y())

    def collapse(self):
        if not self.active:
            self.active = True
            self.frames = ENEMY_COLLAPSE_FRAMES

        else:
            self.setPos(self.x(), self.y() + ENEMY_COLLAPSE_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.frames = -1
                self.active = False


class Player1(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerShip1_blue.png"))
        self.lives = 3

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_Left in keys_pressed:
            if self.x() > 15:
                dx -= PLAYER1_SPEED
        if Qt.Key_Right in keys_pressed:
            if self.x() < 590:
                dx += PLAYER1_SPEED
        self.setPos(self.x() + dx, self.y())


class Player2(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerShip1_red.png"))
        self.lives = 3

    def game_update(self, keys_pressed):
        dx = 0
        if Qt.Key_A in keys_pressed:
            if self.x() > 15:
                dx -= PLAYER2_SPEED
        if Qt.Key_D in keys_pressed:
            if self.x() < 590:
                dx += PLAYER2_SPEED
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
            if Qt.Key_0 in keys_pressed and player1.lives > 0:
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
            if Qt.Key_Space in keys_pressed and player2.lives > 0:
                self.active = True
                self.setPos(player2.x() + self.offset_x, player2.y() + self.offset_y)
                self.frames = BULLET_FRAMES

        else:
            self.setPos(self.x(), self.y() - BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.frames = -1
                self.active = False
                self.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)


class BulletEnemy(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("laserBlue07.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.frames = 0

    def game_update(self, enemy):
        if not self.active:
            self.active = True
            self.setPos(enemy.x() + self.offset_x, enemy.y() + self.offset_y)
            self.frames = ENEMY_BULLET_FRAMES

        else:
            self.setPos(self.x(), self.y() + ENEMY_BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.active = False
                self.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)


class LifePlayer1(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerLife_blue.png"))
        self.setPos(x, y)


class LifePlayer2(QGraphicsPixmapItem):
    def __init__(self, x, y, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setPixmap(QPixmap("playerLife_red.png"))
        self.setPos(x, y)


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

        self.left = 1
        self.right = 5

        self.enemies = [Enemy(131, 10), Enemy(173, 10), Enemy(215, 10), Enemy(257, 10), Enemy(299, 10), Enemy(341, 10),
                        Enemy(383, 10), Enemy(425, 10), Enemy(467, 10), Enemy(509, 10),
                        Enemy(131, 50), Enemy(173, 50), Enemy(215, 50), Enemy(257, 50), Enemy(299, 50), Enemy(341, 50),
                        Enemy(383, 50), Enemy(425, 50), Enemy(467, 50), Enemy(509, 50),
                        Enemy(131, 90), Enemy(173, 90), Enemy(215, 90), Enemy(257, 90), Enemy(299, 90), Enemy(341, 90),
                        Enemy(383, 90), Enemy(425, 90), Enemy(467, 90), Enemy(509, 90)]

        pool = multiprocessing.Pool(processes=1)
        result = pool.apply_async(get_enemy_power_ups, (29, 5))
        self.enemyPowerUps = result.get(timeout=1)

        for i in self.enemyPowerUps:
            self.enemies[i].setPixmap(QPixmap("enemyGreen2.png"))
            self.enemies[i].powerUp = True

        for e in self.enemies:
            self.addItem(e)

        self.player1 = Player1()
        self.player1.setPos(20, 530)
        self.player2 = Player2()
        self.player2.setPos(589, 530)
        self.bullet1 = Bullet1(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
        self.bullet2 = Bullet2(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
        self.bulletEnemy = BulletEnemy(ENEMY_BULLET_X_OFFSET, ENEMY_BULLET_Y_OFFSET)

        self.randomEnemyIndex = randint(0, len(self.enemies))

        self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet1)

        self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet2)

        self.bulletEnemy.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bulletEnemy)

        self.addItem(self.player1)
        self.addItem(self.player2)

        self.scoreField = QGraphicsRectItem()
        self.scoreField.setRect(672, -1, 128, SCREEN_HEIGHT + 2)
        self.scoreField.setBrush(QBrush(Qt.darkGray))
        self.addItem(self.scoreField)

        self.level = 1

        self.levelFont = QFont()
        self.levelFont.setPixelSize(25)
        self.levelFont.setBold(1)
        self.levelField = QGraphicsSimpleTextItem("Level: " + str(self.level))
        self.levelField.setBrush(QBrush(Qt.green))
        self.levelField.setPos(677, 20)
        self.levelField.setFont(self.levelFont)
        self.addItem(self.levelField)

        self.playerFont = QFont()
        self.playerFont.setPixelSize(25)
        self.playerFont.setBold(1)

        self.scoreFont = QFont()
        self.scoreFont.setPixelSize(20)
        self.scoreFont.setBold(1)

        self.player1Lives = QGraphicsSimpleTextItem("Player 1: ")
        self.player1Lives.setBrush(QBrush(Qt.blue))
        self.player1Lives.setPos(674, 130)
        self.player1Lives.setFont(self.playerFont)
        self.addItem(self.player1Lives)

        self.livesPlayer1 = [LifePlayer1(680, 175), LifePlayer1(720, 175), LifePlayer1(760, 175)]
        for l in self.livesPlayer1:
            self.addItem(l)

        self.player1Score = 0
        self.player1Scores = QGraphicsSimpleTextItem("Score: \n" + str(self.player1Score))
        self.player1Scores.setBrush(QBrush(Qt.blue))
        self.player1Scores.setPos(674, 220)
        self.player1Scores.setFont(self.scoreFont)
        self.addItem(self.player1Scores)

        self.player2Lives = QGraphicsSimpleTextItem("Player 2: ")
        self.player2Lives.setBrush(QBrush(Qt.blue))
        self.player2Lives.setPos(674, 330)
        self.player2Lives.setFont(self.playerFont)
        self.addItem(self.player2Lives)

        self.livesPlayer2 = [LifePlayer2(680, 375), LifePlayer2(720, 375), LifePlayer2(760, 375)]
        for l in self.livesPlayer2:
            self.addItem(l)

        self.player2Score = 0
        self.player2Scores = QGraphicsSimpleTextItem("Score: \n" + str(self.player2Score))
        self.player2Scores.setBrush(QBrush(Qt.blue))
        self.player2Scores.setPos(674, 420)
        self.player2Scores.setFont(self.scoreFont)
        self.addItem(self.player2Scores)

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
            if e.frames == -1:
                self.removeItem(e)
                self.enemies.remove(e)
                continue
            if e.chosen == True:
                e.collapse()

            if e.x() <= self.bullet1.x() <= e.x() + 32:
                if e.y() <= self.bullet1.y() <= e.y() + 26:
                    if e.powerUp:
                        temp = randint(0, 3)
                        global PLAYER1_SPEED
                        if temp == 0:
                            PLAYER1_SPEED = 8
                        elif temp == 1:
                            PLAYER1_SPEED = 2
                        elif temp == 2:
                            if self.player1.lives == 3:
                                pass
                            elif self.player1.lives == 2:
                                self.livesPlayer1.append(LifePlayer1(760, 175))
                                self.player1.lives += 1
                                self.addItem(self.livesPlayer1[-1])
                            elif self.player1.lives == 1:
                                self.livesPlayer1.append(LifePlayer1(720, 175))
                                self.player1.lives += 1
                                self.addItem((self.livesPlayer1[-1]))
                            else:
                                pass
                        else:
                            self.player1Score += 100
                            self.player1Scores.setText("Score: \n" + str(self.player1Score))
                    self.removeItem(e)
                    self.enemies.remove(e)
                    self.removeItem(self.bullet1)
                    self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.addItem(self.bullet1)
                    self.player1Score += 10
                    self.player1Scores.setText("Score: \n" + str(self.player1Score))
            if e.x() <= self.bullet2.x() <= e.x() + 32:
                if e.y() <= self.bullet2.y() <= e.y() + 26:
                    if e.powerUp:
                        temp = randint(0, 3)
                        global PLAYER2_SPEED
                        if temp == 0:
                            PLAYER2_SPEED = 8
                        elif temp == 1:
                            PLAYER2_SPEED = 2
                        elif temp == 2:
                            if self.player2.lives == 3:
                                pass
                            elif self.player2.lives == 2:
                                self.livesPlayer2.append(LifePlayer2(760, 375))
                                self.player2.lives += 1
                                self.addItem(self.livesPlayer2[-1])
                            elif self.player2.lives == 1:
                                self.livesPlayer2.append(LifePlayer2(720, 375))
                                self.player2.lives += 1
                                self.addItem((self.livesPlayer2[-1]))
                            else:
                                pass
                        else:
                            self.player2Score += 100
                            self.player2Scores.setText("Score: \n" + str(self.player2Score))
                    self.removeItem(e)
                    self.enemies.remove(e)
                    self.removeItem(self.bullet2)
                    self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.addItem(self.bullet2)
                    self.player2Score += 10
                    self.player2Scores.setText("Score: \n" + str(self.player2Score))

            if self.player1.y() <= e.y() + 26 <= self.player1.y() + 53:
                if self.player1.x() <= e.x() <= self.player1.x() + 69 or self.player1.x() <= e.x() +32 <= self.player1.x() + 69:
                    if self.player1.lives > 0:
                        PLAYER1_SPEED = 4
                        e.frames = -1
                        self.player1.lives -= 1
                        self.removeItem(self.livesPlayer1[-1])
                        self.livesPlayer1.remove(self.livesPlayer1[-1])
                        self.player1.setPos(20, 530)
                        if self.player1.lives <= 0:
                            self.removeItem(self.player1)
            if self.player2.y() <= e.y() + 26 <= self.player2.y() + 53:
                if self.player2.x() <= e.x() <= self.player2.x() + 69 or self.player2.x() <= e.x() + 32 <= self.player2.x() + 69:
                    if self.player2.lives > 0:
                        PLAYER2_SPEED = 4
                        e.frames = -1
                        self.player2.lives -= 1
                        self.removeItem(self.livesPlayer2[-1])
                        self.livesPlayer2.remove(self.livesPlayer2[-1])
                        self.player2.setPos(589, 530)
                        if self.player2.lives <= 0:
                            self.removeItem(self.player2)

        if self.player1.x()+69 >= self.bulletEnemy.x() >= self.player1.x():
            if self.player1.y() + 53 >= self.bulletEnemy.y() >= self.player1.y():
                if self.player1.lives > 0:
                    PLAYER1_SPEED = 4
                    self.bulletEnemy.active = False
                    self.player1.lives -= 1
                    self.removeItem(self.livesPlayer1[-1])
                    self.livesPlayer1.remove(self.livesPlayer1[-1])
                    self.player1.setPos(20, 530)
                    if self.player1.lives <= 0:
                        self.removeItem(self.player1)

        if self.player2.x()+69 >= self.bulletEnemy.x() >= self.player2.x():
            if self.player2.y() + 53 >= self.bulletEnemy.y() >= self.player2.y():
                if self.player2.lives > 0:
                    PLAYER2_SPEED = 4
                    self.bulletEnemy.active = False
                    self.player2.lives -= 1
                    self.removeItem(self.livesPlayer2[-1])
                    self.livesPlayer2.remove(self.livesPlayer2[-1])
                    self.player2.setPos(589, 530)
                    if self.player2.lives <= 0:
                        self.removeItem(self.player2)

        self.bullet1.game_update(self.keys_pressed, self.player1)
        self.bullet2.game_update(self.keys_pressed, self.player2)
        try:
            self.bulletEnemy.game_update(self.enemies[self.randomEnemyIndex])
            if not self.bulletEnemy.active:
                self.random_enemy_bullet()
        except:
            self.random_enemy_bullet()
        try:
            if randint(0, 500) == 0:
                self.enemies[randint(0, len(self.enemies))].chosen = True
        except:
            pass
        if self.player1.lives == 0 and self.player2.lives == 0:
            sys.exit(app.exec_())

        if len(self.enemies) == 0:
            self.timer.stop()
            self.timerEnemy.stop()
            if self.player1.lives > 0:
                self.removeItem(self.player1)
                self.removeItem(self.bullet1)
            if self.player2.lives > 0:
                self.removeItem(self.player2)
                self.removeItem(self.bullet2)
            self.removeItem(self.bulletEnemy)
            self.new_level()

    def game_update_enemy(self):
        if 0 < self.right < 9:
            self.right += 1
            if self.right == 9:
                self.right = 0
                self.left = 1
            for e in self.enemies:
                e.move_right()
        elif 0 < self.left < 9:
            self.left += 1
            if self.left == 9:
                self.left = 0
                self.right = 1
            for e in self.enemies:
                e.move_left()

    def random_enemy_bullet(self):
        self.randomEnemyIndex = randint(0, len(self.enemies))

    def new_level(self):
        self.timer.start(FRAME_TIME_MS, self)
        self.timerEnemy.start(1000)

        self.level += 1
        self.levelField.setText("Level: " + str(self.level))

        global ENEMY_BULLET_SPEED
        ENEMY_BULLET_SPEED += 2
        global ENEMY_BULLET_FRAMES
        ENEMY_BULLET_FRAMES = 700/ENEMY_BULLET_SPEED

        global ENEMY_COLLAPSE_SPEED
        ENEMY_COLLAPSE_SPEED += 2
        global ENEMY_COLLAPSE_FRAMES
        ENEMY_COLLAPSE_FRAMES = 700/ENEMY_COLLAPSE_SPEED

        self.left = 1
        self.right = 5

        self.enemies = [Enemy(131, 10), Enemy(173, 10), Enemy(215, 10), Enemy(257, 10), Enemy(299, 10), Enemy(341, 10),
                        Enemy(383, 10), Enemy(425, 10), Enemy(467, 10), Enemy(509, 10),
                        Enemy(131, 50), Enemy(173, 50), Enemy(215, 50), Enemy(257, 50), Enemy(299, 50), Enemy(341, 50),
                        Enemy(383, 50), Enemy(425, 50), Enemy(467, 50), Enemy(509, 50),
                        Enemy(131, 90), Enemy(173, 90), Enemy(215, 90), Enemy(257, 90), Enemy(299, 90), Enemy(341, 90),
                        Enemy(383, 90), Enemy(425, 90), Enemy(467, 90), Enemy(509, 90)]

        for e in self.enemies:
            self.addItem(e)

        if self.player1.lives > 0:
            self.player1.setPos(20, 530)
            self.bullet1 = Bullet1(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
            self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.addItem(self.bullet1)
            self.addItem(self.player1)
        if self.player2.lives > 0:
            self.player2.setPos(589, 530)
            self.bullet2 = Bullet2(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
            self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.addItem(self.bullet2)
            self.addItem(self.player2)

        self.bulletEnemy = BulletEnemy(ENEMY_BULLET_X_OFFSET, ENEMY_BULLET_Y_OFFSET)
        self.bulletEnemy.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bulletEnemy)

def get_enemy_power_ups(numOfEnemies, numOfPowerUps):
    ret = []
    while len(ret) != numOfPowerUps:
        temp = randint(0, numOfEnemies)
        if ret.__contains__(temp):
            continue
        else:
            ret.append(temp)
    return ret

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = Scene()
    sys.exit(app.exec_())
