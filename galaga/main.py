
import sys
from PyQt5.QtCore import (
    Qt,
    QBasicTimer,
    QEvent, QTimer)
from PyQt5.QtGui import (
    QBrush,
    QPixmap
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView
)

SCREEN_WIDTH            = 800
SCREEN_HEIGHT           = 600
PLAYER_SPEED            = 7   # pix/frame
PLAYER_BULLET_X_OFFSETS = [25,45]
PLAYER_BULLET_Y         = 15
BULLET_SPEED            = 10  # pix/frame
BULLET_FRAMES           = 90
FRAME_TIME_MS           = 16  # ms/frame

ENEMY_BULLET_X_OFFSETS  = [25, 25]
ENEMY_BULLET_Y          = 15
ENEMY_SPEED             = 14


class Player(QGraphicsPixmapItem):
    def __init__(self, parent = None):
        QGraphicsPixmapItem.__init__(self,parent)
        self.setPixmap(QPixmap("brod.jpg"))

    def game_update(self, keys_pressed):
        dx = 0
        #dy = 0
        if Qt.Key_Left in keys_pressed:
            dx -= PLAYER_SPEED
        if Qt.Key_Right in keys_pressed:
            dx += PLAYER_SPEED
        self.setPos(self.x()+dx, 520)


class Enemy(QGraphicsPixmapItem):
    def __init__(self, x, y, parent = None):
        QGraphicsPixmapItem.__init__(self,parent)
        self.setPixmap(QPixmap("ptica.jpg"))
        self.setPos(x,y)


    def enemy_update(self):
        self.setPos(self.x()+20, 30)


class BulletEnemy(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent = None):
        QGraphicsPixmapItem.__init__(self,parent)
        self.setPixmap(QPixmap("puca.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.frames = 0

    def game_update(self, keys_pressed, player):
        if not self.active:
            if Qt.Key_Space in keys_pressed:
                self.active = True
                self.setPos(player.x()+self.offset_x,player.y()+self.offset_y)
                self.frames = BULLET_FRAMES
        else:
            self.setPos(self.x(),self.y()-BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.active = False
                self.setPos(SCREEN_WIDTH,SCREEN_HEIGHT)


class Bullet(QGraphicsPixmapItem):
    def __init__(self, offset_x, offset_y, parent = None):
        QGraphicsPixmapItem.__init__(self,parent)
        self.setPixmap(QPixmap("puca.png"))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.active = False
        self.frames = 0

    def game_update(self, keys_pressed, player):
        if not self.active:
            if Qt.Key_Space in keys_pressed:
                self.active = True
                self.setPos(player.x()+self.offset_x,player.y()+self.offset_y)
                self.frames = BULLET_FRAMES
        else:
            self.setPos(self.x(),self.y()-BULLET_SPEED)
            self.frames -= 1
            if self.frames <= 0:
                self.active = False
                self.setPos(SCREEN_WIDTH,SCREEN_HEIGHT)



class Scene(QGraphicsScene):
    def __init__(self, parent = None):
        QGraphicsScene.__init__(self, parent)

        # hold the set of keys we're pressing
        self.keys_pressed = set()

        # use a timer to get 60Hz refresh (hopefully)
        self.timer = QBasicTimer()
        self.timer.start(FRAME_TIME_MS, self)

        self.timerEnemy = QTimer()
        #self.timerEnemy.timeout.connect(self.enemy_update)
        self.timerEnemy.start(1000)


        bg = QGraphicsRectItem()
        bg.setRect(-1,-1,SCREEN_WIDTH+2,SCREEN_HEIGHT+2)
        bg.setBrush(QBrush(Qt.black))
        self.addItem(bg)

        self.enemies = [Enemy(10, 10), Enemy(50, 10), Enemy(90, 10), Enemy(130, 10), Enemy(170, 10), Enemy(210, 10),
                        Enemy(250, 10), Enemy(290, 10), Enemy(330, 10), Enemy(370, 10), Enemy(10, 50), Enemy(50, 50),
                        Enemy(90, 50), Enemy(130, 50), Enemy(170, 50), Enemy(210, 50), Enemy(250, 50), Enemy(290, 50),
                        Enemy(330, 50), Enemy(370, 50), Enemy(10, 90), Enemy(50, 90), Enemy(90, 90), Enemy(130, 90),
                        Enemy(170, 90), Enemy(210, 90), Enemy(250, 90), Enemy(290, 90), Enemy(330, 90), Enemy(370, 90)]

        for e in self.enemies:
            self.addItem(e)

        self.player = Player()
        self.player.setPos((SCREEN_WIDTH-self.player.pixmap().width())/2/2,
                           (SCREEN_HEIGHT-self.player.pixmap().height())-80)
        self.bullets = [Bullet(PLAYER_BULLET_X_OFFSETS[0],PLAYER_BULLET_Y)]
                        #Bullet(PLAYER_BULLET_X_OFFSETS[1],PLAYER_BULLET_Y)]

        for b in self.bullets:
            b.setPos(SCREEN_WIDTH,SCREEN_HEIGHT)
            self.addItem(b)
        self.addItem(self.player)

        self.view = QGraphicsView(self)
        self.view.setWindowTitle("Galaga")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.show()
        self.view.setFixedSize(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.setSceneRect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        self.keys_pressed.remove(event.key())

    def timerEvent(self, event):
        self.game_update()
        self.update()

    def game_update(self):
        self.player.game_update(self.keys_pressed)
        for b in self.bullets:
            b.game_update(self.keys_pressed, self.player)

    def enemy_update1(self):
        for e in self.enemies:
            e.enemy_update(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = Scene()
    sys.exit(app.exec_())