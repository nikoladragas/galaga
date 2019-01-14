import sys
import multiprocessing
import _thread
from random import randint
from PyQt5.QtCore import (
    QBasicTimer,
    QTimer)
from PyQt5.QtGui import QBrush, QFont
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QApplication)
from galaga.galaga.Player1 import *
from galaga.galaga.Player2 import *
from galaga.galaga.Enemy import *


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_BULLET_X_OFFSETS = [0, 32]
PLAYER_BULLET_Y = -20
ENEMY_BULLET_X_OFFSET = 14
ENEMY_BULLET_Y_OFFSET = 26


class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        # set pritisnutih tastera
        self.keys_pressed = set()

        # pozadina
        self.bg = QGraphicsRectItem()
        self.bg.setRect(-1, -1, SCREEN_WIDTH + 2, SCREEN_HEIGHT + 2)
        self.bg.setBrush(QBrush(Qt.black))
        self.addItem(self.bg)

        # brojaci za pomeranje protivnika
        self.left = 1
        self.right = 5

        # lista protivnika
        self.enemies = []
        # nasumicni indeks protivnika koji puca
        self.randomEnemyIndex = randint(0, len(self.enemies))
        # nasumicna lista indeksa protivnika koji ce imati specijalnu moc
        self.enemyPowerUps = []

        # pravljenje i iscrtavanje protivnika
        self.threadFinished = False
        _thread.start_new_thread(self.draw_enemies, ())
        while not self.threadFinished:
            continue
        self.threadFinished = False

        # igrac 1 (plavi)
        self.player1 = Player1()
        self.player1.setPos(20, 530)
        self.addItem(self.player1)

        # igrac 2 (crveni)
        self.player2 = Player2()
        self.player2.setPos(589, 530)
        self.addItem(self.player2)

        # metak igraca 1 (plavi)
        self.bullet1 = Bullet1(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
        self.bullet1.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet1)

        # metak igraca 2 (crveni)
        self.bullet2 = Bullet2(PLAYER_BULLET_X_OFFSETS[1], PLAYER_BULLET_Y)
        self.bullet2.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bullet2)

        # protivnicki metak (narandzasti)
        self.bulletEnemy = BulletEnemy(ENEMY_BULLET_X_OFFSET, ENEMY_BULLET_Y_OFFSET)
        self.bulletEnemy.setPos(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.addItem(self.bulletEnemy)

        # polje za rezultate
        self.scoreField = QGraphicsRectItem()
        self.scoreField.setRect(672, -1, 128, SCREEN_HEIGHT + 2)
        self.scoreField.setBrush(QBrush(Qt.darkGray))
        self.addItem(self.scoreField)

        # trenutni nivo
        self.level = 1

        # iscrtavanje trenutnog nivoa
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

        # iscrtavanje broja zivota igraca 1
        self.player1Lives = QGraphicsSimpleTextItem("Player 1: ")
        self.player1Lives.setBrush(QBrush(Qt.blue))
        self.player1Lives.setPos(674, 130)
        self.player1Lives.setFont(self.playerFont)
        self.addItem(self.player1Lives)
        self.livesPlayer1 = [LifePlayer1(680, 175), LifePlayer1(720, 175), LifePlayer1(760, 175)]
        for l in self.livesPlayer1:
            self.addItem(l)

        # iscrtavanje broja zivota igraca 2
        self.player2Lives = QGraphicsSimpleTextItem("Player 2: ")
        self.player2Lives.setBrush(QBrush(Qt.blue))
        self.player2Lives.setPos(674, 330)
        self.player2Lives.setFont(self.playerFont)
        self.addItem(self.player2Lives)
        self.livesPlayer2 = [LifePlayer2(680, 375), LifePlayer2(720, 375), LifePlayer2(760, 375)]
        for l in self.livesPlayer2:
            self.addItem(l)

        self.scoreFont = QFont()
        self.scoreFont.setPixelSize(20)
        self.scoreFont.setBold(1)

        # iscrtavanje rezultata igraca 1
        self.player1Score = 0
        self.player1Scores = QGraphicsSimpleTextItem("Score: \n" + str(self.player1Score))
        self.player1Scores.setBrush(QBrush(Qt.blue))
        self.player1Scores.setPos(674, 220)
        self.player1Scores.setFont(self.scoreFont)
        self.addItem(self.player1Scores)

        # iscrtavanje rezultata igraca 1
        self.player2Score = 0
        self.player2Scores = QGraphicsSimpleTextItem("Score: \n" + str(self.player2Score))
        self.player2Scores.setBrush(QBrush(Qt.blue))
        self.player2Scores.setPos(674, 420)
        self.player2Scores.setFont(self.scoreFont)
        self.addItem(self.player2Scores)

        # tajmer za iscrtavanje slike 60 puta u sekndi (60 fps)
        self.timer = QBasicTimer()
        self.timer.start(16, self)

        # tajmer za pomeranje neprijatelja
        self.timerEnemy = QTimer()
        self.timerEnemy.timeout.connect(self.game_update_enemy)
        self.timerEnemy.start(1000)

        # icrtavanje scene
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
            # ako je neprijatelj zavrsio sa padanjem, brisemo ga
            if e.frames == -1:
                self.removeItem(e)
                self.enemies.remove(e)
                continue
            # ako je neprijatelj izabran za padanje, nastavlja da pada
            if e.chosen:
                e.collapse()

            # igrac 1 pogodio neprijatelja
            if e.x() <= self.bullet1.x() <= e.x() + 32:
                if e.y() <= self.bullet1.y() <= e.y() + 26:
                    if e.powerUp:
                        temp = randint(0, 3)
                        if temp == 0:
                            self.player1.speed = 8
                        elif temp == 1:
                            self.player1.speed = 2
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

            # igrac 2 pogodio neprijatelja
            if e.x() <= self.bullet2.x() <= e.x() + 32:
                if e.y() <= self.bullet2.y() <= e.y() + 26:
                    if e.powerUp:
                        temp = randint(0, 3)
                        if temp == 0:
                            self.player2.speed = 8
                        elif temp == 1:
                            self.player2.speed = 2
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

            # na igraca 1 se obrusio neprijatelj
            if self.player1.y() <= e.y() + 26 <= self.player1.y() + 53:
                if self.player1.x() <= e.x() <= self.player1.x() + 69 or self.player1.x() <= e.x() +32 <= self.player1.x() + 69:
                    if self.player1.lives > 0:
                        self.player1.speed = 4
                        e.frames = -1
                        self.player1.lives -= 1
                        self.removeItem(self.livesPlayer1[-1])
                        self.livesPlayer1.remove(self.livesPlayer1[-1])
                        self.player1.setPos(20, 530)
                        if self.player1.lives <= 0:
                            self.removeItem(self.player1)

            # na igraca 2 se obrusio neprijatelj
            if self.player2.y() <= e.y() + 26 <= self.player2.y() + 53:
                if self.player2.x() <= e.x() <= self.player2.x() + 69 or self.player2.x() <= e.x() + 32 <= self.player2.x() + 69:
                    if self.player2.lives > 0:
                        self.player2.speed = 4
                        e.frames = -1
                        self.player2.lives -= 1
                        self.removeItem(self.livesPlayer2[-1])
                        self.livesPlayer2.remove(self.livesPlayer2[-1])
                        self.player2.setPos(589, 530)
                        if self.player2.lives <= 0:
                            self.removeItem(self.player2)

        # igraca 1 pogodio laser neprijatelja
        if self.player1.x()+69 >= self.bulletEnemy.x() >= self.player1.x():
            if self.player1.y() + 53 >= self.bulletEnemy.y() >= self.player1.y():
                if self.player1.lives > 0:
                    self.player1.speed = 4
                    self.bulletEnemy.active = False
                    self.player1.lives -= 1
                    self.removeItem(self.livesPlayer1[-1])
                    self.livesPlayer1.remove(self.livesPlayer1[-1])
                    self.player1.setPos(20, 530)
                    if self.player1.lives <= 0:
                        self.removeItem(self.player1)

        # igraca 1 pogodio laser neprijatelja
        if self.player2.x()+69 >= self.bulletEnemy.x() >= self.player2.x():
            if self.player2.y() + 53 >= self.bulletEnemy.y() >= self.player2.y():
                if self.player2.lives > 0:
                    self.player2.speed = 4
                    self.bulletEnemy.active = False
                    self.player2.lives -= 1
                    self.removeItem(self.livesPlayer2[-1])
                    self.livesPlayer2.remove(self.livesPlayer2[-1])
                    self.player2.setPos(589, 530)
                    if self.player2.lives <= 0:
                        self.removeItem(self.player2)

        # pomeranje metaka
        self.bullet1.game_update(self.keys_pressed, self.player1)
        self.bullet2.game_update(self.keys_pressed, self.player2)
        try:
            self.bulletEnemy.game_update(self.enemies[self.randomEnemyIndex])
            if not self.bulletEnemy.active:
                self.randomEnemyIndex = randint(0, len(self.enemies))
        except:
            self.randomEnemyIndex = randint(0, len(self.enemies))

        # nasumicno biranje obrusavanja
        try:
            if randint(0, 500) == 0:
                self.enemies[randint(0, len(self.enemies))].chosen = True
        except:
            pass

        # kraj igre
        if self.player1.lives == 0 and self.player2.lives == 0:
            sys.exit(app.exec_())

        # pobedjen nivo
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

    # pomeranje neprijatelja
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

    # pravljenje novog nivoa
    def new_level(self):
        self.level += 1
        self.levelField.setText("Level: " + str(self.level))

        self.left = 1
        self.right = 5

        self.threadFinished = False
        _thread.start_new_thread(self.draw_enemies, ())
        while not self.threadFinished:
            continue
        self.threadFinished = False

        for e in self.enemies:
            e.collapseSpeed += self.level
            e.collapseFrames = 700/e.collapseSpeed

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
        self.bulletEnemy.speed += self.level
        self.bulletEnemy.frames = 700 / self.bulletEnemy.speed
        self.addItem(self.bulletEnemy)

        self.timer.start(16, self)
        self.timerEnemy.start(1000)

    def draw_enemies(self):
        self.threadFinished = False
        self.enemies = [Enemy(131, 10), Enemy(173, 10), Enemy(215, 10), Enemy(257, 10), Enemy(299, 10), Enemy(341, 10),
                        Enemy(383, 10), Enemy(425, 10), Enemy(467, 10), Enemy(509, 10),
                        Enemy(131, 50), Enemy(173, 50), Enemy(215, 50), Enemy(257, 50), Enemy(299, 50), Enemy(341, 50),
                        Enemy(383, 50), Enemy(425, 50), Enemy(467, 50), Enemy(509, 50),
                        Enemy(131, 90), Enemy(173, 90), Enemy(215, 90), Enemy(257, 90), Enemy(299, 90), Enemy(341, 90),
                        Enemy(383, 90), Enemy(425, 90), Enemy(467, 90), Enemy(509, 90)]

        pool = multiprocessing.Pool(processes=1)
        result = pool.apply_async(get_enemy_power_ups, (29, 5))
        self.enemyPowerUps = result.get(timeout=1)
        pool.close()

        for i in self.enemyPowerUps:
            self.enemies[i].setPixmap(QPixmap("Images/enemyPowerUp.png"))
            self.enemies[i].powerUp = True

        for e in self.enemies:
            self.addItem(e)

        self.randomEnemyIndex = randint(0, len(self.enemies))

        self.threadFinished = True


def get_enemy_power_ups(numOfEnemies, numOfPowerUps):
    ret = []
    while len(ret) != numOfPowerUps:
        temp = randint(0, numOfEnemies)
        if ret.__contains__(temp):
            continue
        else:
            ret.append(temp)
    return ret


def get_random_num(start, stop):
    return randint(start, stop)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = Scene()
    sys.exit(app.exec_())
