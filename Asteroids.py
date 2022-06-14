
'''
    *Eksikler:
    - Şekillerde yanlışlıklar oluyor

'''

import sys,random,math
import pygame as pg
import time
from pygame.locals import *
from pygame.sprite import Sprite


# Global Constants
VERSION     = "0.01"
NAME        = "Asteroids " + VERSION
SCREEN_X    = 1200
SCREEN_Y    = 600
FPS         = 60

DEGTORAD = 0.017453

# pygame başlıyor
pg.init()
screen          = pg.display.set_mode((SCREEN_X,SCREEN_Y))
caption         = pg.display.set_caption(NAME)
clock           = pg.time.Clock()


Ast_sprite_list = pg.sprite.Group()
Blt_sprite_list = pg.sprite.Group()

class Animation():
    def __init__(self,address,x,y,w,h,count,speed):
        super().__init__()
        self.life   = True
        self.speed  = speed
        self.count  = count
        self.Frame  = 0
        self.T      = time.time()
        self.frames = []

        for i in range(self.count):
            tFrame =pg.image.load(address).subsurface( x+i*w,y,w,h).convert_alpha()
            self.frames.append(tFrame)

        self.image = self.frames[int(self.Frame)]

    def Update(self):
        if time.time() - self.T >self.speed:
            self.T = time.time()
            self.Frame += 1
            if self.Frame > self.count - 1:
                self.life  = False
                self.Frame = 0
        self.image = self.frames[int(self.Frame)]

    def Show(self,x,y,screen):
        screen.blit(self.image, (x, y))


sExplosion      = Animation("images/explosions/type_C.png", 0,0,256,256, 48, 0.04)
sRock           = Animation("images/rock.png",              0,0,64,64, 16, 0.1)
sRock_small     = Animation("images/rock_small.png",        0,0,64,64, 16, 0.1)
sBullet         = Animation("images/fire_blue.png",         0,0,32,64, 16, 0.8)
sPlayer         = Animation("images/spaceship.png",        40,0,40,40, 1, 0)
sPlayer_go      = Animation("images/spaceship.png",        40,40,40,40, 1, 0)
sExplosion_ship = Animation("images/explosions/type_B.png", 0,0,192,192, 64, 0.5)

#----------------------------------------------------------------------------
#
#----------------------------------------------------------------------------
class ENTİTY(pg.sprite.Sprite):
    def __init__(self,a,X,Y,Angle,radius):
        super().__init__()

        self.animate = a
        self.image   = self.animate.image
        self.rect    = self.image.get_rect()
        self.rect.x  = X
        self.rect.y  = Y
        self.dx      = 0.0
        self.dy      = 0.0
        self.angle   = Angle
        self.speed   = 10
        self.radius  = radius

        self.shoot   = False
        self.life    = True

    def Show(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class player(ENTİTY):
    def __init__(self,a,X,Y,Angle,radius):
        super().__init__(a,X,Y,Angle,radius)
        self.name    = 'Player'
        self.thrust  = False
        self.speed   = 10
        self.Death   = 10

    def Update(self):
        self.animate.Update()
        self.image = pg.transform.flip(pg.transform.rotate(self.animate.image, self.angle), 1, 0)

        if self.thrust == True :  # ileri tuşuna basıldıysa
            self.animate = sPlayer_go  # Geminin arkasından ateş çıkaran resmi göster
            self.dx = int(math.sin(math.radians(self.angle)) * self.speed)
            self.dy = int(math.cos(math.radians(self.angle)) * self.speed)
        else:
            self.animate = sPlayer
            self.dx *= 0.93
            self.dy *= 0.93


        self.rect.x += self.dx
        self.rect.y -= self.dy
                    # Sahne Dışına çıkmalarını engelle
        if self.rect.x < 0: self.rect.x = 0
        if self.rect.x > SCREEN_X - 40:
            self.rect.x = SCREEN_X - 40
        if self.rect.y < 0: self.rect.y = 0
        if self.rect.y > SCREEN_Y - 40:
            self.rect.y = SCREEN_Y - 40

        caption = pg.display.set_caption(str(self.Death))

class Asteroid(ENTİTY):
    def __init__(self,a,X,Y,Angle,radius):
        super().__init__(a,X,Y,Angle,radius)
        self.speed = 5

    def Update(self):
        if self.animate == sRock or self.animate == sRock_small :
            self.animate.Update()
            self.image = self.animate.image

            self.dx = int(math.sin(math.radians(self.angle)) * self.speed)
            self.dy = int(math.cos(math.radians(self.angle)) * self.speed)
            self.rect.x += self.dx
            self.rect.y -= self.dy

            if (self.rect.x > SCREEN_X): self.rect.x = 0
            if (self.rect.x < 0): self.rect.x = SCREEN_X
            if (self.rect.y > SCREEN_Y): self.rect.y = 0
            if (self.rect.y < 0): self.rect.y = SCREEN_Y

class Bullet(ENTİTY):
    def __init__(self, a, X, Y, Angle, radius):
        super().__init__(a, X, Y, Angle, radius)
        self.speed = 30

    def Update(self):
        self.animate.Update()
        self.image = pg.transform.flip(pg.transform.rotate(self.animate.image, self.angle), 1, 0)

        self.dx = int(math.sin(math.radians(self.angle)) * self.speed)
        self.dy = int(math.cos(math.radians(self.angle)) * self.speed)
        self.rect.x += self.dx
        self.rect.y -= self.dy

        if self.rect.x < 0 or self.rect.x > SCREEN_X or\
                self.rect.y < 0 or self.rect.y > SCREEN_Y :
            self.life = False

class Explosion(ENTİTY):
    def __init__(self, a, X, Y, Angle, radius):
        super().__init__(a, X, Y, Angle, radius)


    def Update(self):
        if self.animate.life  == False:
            self.life = False
        else :
            self.animate.Update()
            self.image = self.animate.image

# oyun döngüsünü çalıştırıyoruz
class main():
    def __init__(self):
        self.Background = pg.image.load("images/background.jpg").convert_alpha()

        self.Player = player(sPlayer, 200, 200, 0, 20)
        self.bulletTime      = time.time()
        self.blt = []
        self.ast = []
        self.exb = []

        for i in range(20):
            r = Asteroid(sRock, random.randint(0, SCREEN_X - 100), random.randint(0, SCREEN_Y - 100), random.randint(0,360), 20)
            self.ast.append(r)
            #Ast_sprite_list.add(self.ast[i])

        self.game_loop()

    def CollidePlayerWithAstroid(self):
        for astro in self.ast:
            if (self.Player.rect.x - astro.rect.x) * (self.Player.rect.x - astro.rect.x) \
                + (self.Player.rect.y - astro.rect.y) * (self.Player.rect.y - astro.rect.y) < \
                (self.Player.radius + astro.radius) * (self.Player.radius + astro.radius):

                self.Player.rect.x = 600
                self.Player.rect.y = 300
                self.Player.Death -= 1


    def CollideBulletWithAstroid(self):
        for bullet in self.blt:
            for astroid in self.ast:
                if (bullet.rect.x - astroid.rect.x)*(bullet.rect.x - astroid.rect.x)\
                    +(bullet.rect.y - astroid.rect.y)*(bullet.rect.y - astroid.rect.y) < \
                    (bullet.radius + astroid.radius)*(bullet.radius + astroid.radius):

                    astroid.life  = False
                    bullet.life   = False

                    if astroid.radius == 20:
                        for i in (1, 2):
                            r = Asteroid(sRock_small, astroid.rect.x, astroid.rect.y, random.randint(0, 360), 10)
                            self.ast.append(r)
                    else:
                        e = Explosion(sExplosion, astroid.rect.x, astroid.rect.y, 0, 0)
                        self.exb.append(e)

    def game_loop(self):
        while True:
            clock.tick(FPS)

            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    pass

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] :self.Player.angle -= 3
            if keys[pg.K_RIGHT]:self.Player.angle += 3

            if keys[pg.K_UP]:self.Player.thrust = True
            else: self.Player.thrust = False

            if keys[pg.K_SPACE]:
                if time.time()-self.bulletTime > 0.1:
                    self.bulletTime      = time.time()
                    r = Bullet(sBullet, self.Player.rect.x, self.Player.rect.y, self.Player.angle, 15)
                    self.blt.append(r)

                    # Blt_sprite_list.add(r)


            # <- SHOW ->

            screen.blit(self.Background, (0, 0))

            self.Player.Update()
            self.Player.Show()

            for i in self.ast:
                i.Update()
                i.Show()

            for i in self.blt:
                i.Update()
                i.Show()

            for i in self.exb:
                i.Update()
                i.Show()

                    # Silinecek Mermileri sil
            for OneBullet in self.blt:
                if OneBullet.life == False:
                    self.blt.remove(OneBullet)

            for OneAstroid in self.ast:
                if OneAstroid.life == False:
                    self.ast.remove(OneAstroid)

            for exbl in self.exb:
                if exbl.life == False:
                    self.exb.remove(exbl)

            self.CollidePlayerWithAstroid()
            self.CollideBulletWithAstroid()

            clock.tick(FPS)
            pg.display.flip()


    # self.rect.collidelistall(blocks)]

if __name__ == '__main__':
    main()


