import math
import random

WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60

def sign(n : float) -> int:
    if n != 0: return n / abs(n)
    return 0

class Block:
    def __init__(
        self,
        x : float,
        y : float,
        w : float,
        h : float,
    ):
        self.x, self.y = x, y
        self.w, self.h = w, h

class Player:
    def __init__(
        self,
        arena,
    ):
        self.arena : Arena = arena
        self.x, self.y = 0.0, 0.0
        self.w, self.h = 1.0, 1.0

        self.px, self.py = 0.0, 0.0
        self.direction : int = 0

        self.camera = Camera(self)

        self.gravity : float = 0.25
        self.speed : float = 0.25

        self.healFactor : int = 5

        self.damage : int = 0
        self.damageTimer : int = 0

    def tick(self):

        self.y += self.gravity

        self.x += self.speed * self.px
        if self.direction > 0:
            self.px += 0.05
            if self.px < 0:
                self.px += 0.15
            if self.px > 1.00:
                self.px = 1.00
        elif self.direction < 0:
            self.px -= 0.05
            if self.px > 0:
                self.px -= 0.15
            if self.px < -1.00:
                self.px = -1.00
        else:
            self.px += 0.10 * -sign(self.px)
            if abs(self.px) <= 0.10:
                self.px = 0.00

        for block in self.arena.blocks:
            self.checkCollision(block)

        if self.damageTimer > 0:
            self.damageTimer -= 1

        if self.damageTimer == 0:
            if self.damage > 0:
                self.damage -= self.healFactor
            if self.damage < 0:
                self.damage = 0

    def checkCollision(self, block : Block):

        if (self.y - self.h / 2 <= block.y <= self.y + self.h / 2) and (self.x + self.w / 2 >= block.x) and (self.x - self.w / 2 <= block.x + block.w):
            self.y = block.y - self.h / 2
        if (self.y - self.h / 2 <= block.y + block.h <= self.y + self.h / 2) and (self.x + self.w / 2 >= block.x) and (self.x - self.w / 2 <= block.x + block.w):
            self.y = block.y + block.h + self.h / 2

    def static(self):
        self.direction = 0

    def left(self):
        self.direction = -1

    def right(self):
        self.direction = 1

    def hitDamage(self, amount : int):
        self.damage += round(amount)
        if self.damage > 200:
            self.damage = 200
        self.damageTimer = FRAMERATE * 5

class Camera:
    def __init__(self, player : Player):
        self.player = player
        self.x = self.player.x
        self.y = self.player.y

        self.speed : float = 0.15

        self.shakeForce : float = 0.0
        self.shakeTimer : int = 0
        self.shakeAngle : int = 0

    def tick(self):
        # self.x = self.player.x
        # self.y = self.player.y
        distance = math.sqrt((self.y - self.player.y) ** 2 + (self.x - self.player.x) ** 2)

        if distance <= 0.15:
            self.x = self.player.x
            self.y = self.player.y

        else:
            angle = math.atan2(self.y - self.player.y, self.x - self.player.x)
            self.x += self.speed * -math.cos(angle)
            self.y += self.speed * -math.sin(angle)

        if self.shakeTimer > 0:
            self.shakeTimer -= 1
            if self.shakeTimer == 0:
                self.shakeForce = 0.0
                self.shakeAngle = 0

    def get(self) -> tuple[float, float]:
        return (
            self.x + self.shakeForce / 100 * random.randint(-100, 100) / 100 * math.cos(self.shakeAngle / 180 * math.pi), #
            self.y + self.shakeForce / 100 * random.randint(-100, 100) / 100 * math.sin(self.shakeAngle / 180 * math.pi), #
        )

    def shake(self, force : float, time : int, angle : int = 0):
        if force > self.shakeForce:
            self.shakeForce = force
        self.shakeTimer += time
        self.shakeAngle = angle

class Arena:
    def __init__(self, blocks : list[Block] = []):
        self.player = Player(self)
        self.blocks = blocks

        self.scale : int = 75

    def tick(self):
        self.player.tick()
        self.player.camera.tick()