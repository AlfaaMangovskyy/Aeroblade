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
        self.speed : float = 0.35
        self.jumpTimer : int = 0
        self.jumpInputTimer : int = 0
        self.canJump : bool = False

        self.healFactor : int = 5

        self.damage : int = 0
        self.damageTimer : int = 0

    def tick(self):

        if self.jumpInputTimer > 0:
            self.jumpInputTimer -= 1
            if self.canJump:
                self.canJump = False
                self.jumpTimer = 15

        if self.jumpTimer > 0:
            self.y -= self.gravity * 0.8
            self.jumpTimer -= 1
        else:
            self.y += self.gravity * self.py
            self.py += 0.075

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
            self.py = 0.00
            if not self.canJump:
                self.canJump = True
                self.camera.shake(5, FRAMERATE // 4, 90)
        if (self.y - self.h / 2 <= block.y + block.h <= self.y + self.h / 2) and (self.x + self.w / 2 >= block.x) and (self.x - self.w / 2 <= block.x + block.w):
            self.y = block.y + block.h + self.h / 2

        if (self.x - self.w / 2 <= block.x <= self.x + self.w / 2) and (block.y <= self.y <= block.y + block.h):
            self.x = block.x - self.w / 2
        if (self.x - self.w / 2 <= block.x + block.w <= self.x + self.w / 2) and (block.y <= self.y <= block.y + block.h):
            self.x = block.x + block.w + self.w / 2

    def static(self):
        self.direction = 0

    def left(self):
        self.direction = -1

    def right(self):
        self.direction = 1

    def jump(self):
        self.jumpInputTimer = 4

    def hitDamage(self, amount : int):
        self.damage += round(amount)
        if self.damage > 200:
            self.damage = 200
        self.damageTimer = FRAMERATE * 5



    def ability(self, _id : str, **args):
        getattr(self, f"ability_{_id}", null)(**args)

    def ability_torpedoes(self, **args):
        for i in range(6):
            self.arena.newEntity("missile", self.x, self.y, {"angle" : 60 * i})

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


def null(*args): return 0

ENTITY_CLASS_OPPONENT = [
    "bug",
]

class Entity:

    def __init__(self, arena, _id : str, x : float, y : float, args : dict = {}):
        self.arena : Arena = arena
        self.id = _id
        self.x, self.y = x, y
        self.args = args
        self.timer : int = 0
        self.damage : int = 0
        self.destroy : bool = False

    def tick(self):
        self.timer += 1
        getattr(self, f"tick_{self.id}", null)()

    def hitDamage(self, amount : int) -> int:
        return getattr(self, f"hitDamage_{self.id}", null)(amount)

    def tick_missile(self):
        minimalDistance = 5000
        target = None
        for entity in self.arena.entities:
            if entity == self: continue
            distance = math.sqrt((self.y - entity.y) ** 2 + (self.x - entity.x) ** 2)
            if distance < minimalDistance:
                if entity.id in ENTITY_CLASS_OPPONENT:
                    minimalDistance = distance
                    target = entity

            if distance <= 1:
                if entity.id in ENTITY_CLASS_OPPONENT:
                    entity.hitDamage(25)
                    self.destroy = True

        if not "angle" in self.args:
            self.args["angle"] = 0
        if not target:
            self.x += 0.25 * math.cos(self.args.get("angle") / 180 * math.pi)
            self.y += 0.25 * math.sin(self.args.get("angle") / 180 * math.pi)
            return

        angle = math.atan2(target.y - self.y, target.x - self.x) * 180 / math.pi
        delta = angle - self.args["angle"]
        self.args["angle"] += delta / self.args.get("inaccuracy", 2)

        self.x += 0.25 * math.cos(self.args.get("angle") / 180 * math.pi)
        self.y += 0.25 * math.sin(self.args.get("angle") / 180 * math.pi)

    def tick_bug(self):
        if not "damage" in self.args:
            self.args["damage"] = 0

        angle = math.atan2(self.arena.player.y - self.y, self.arena.player.x - self.x)
        self.x += 0.15 * math.cos(angle)
        self.y += 0.15 * math.sin(angle)

        distance = math.sqrt((self.arena.player.y - self.y) ** 2 + (self.arena.player.x - self.x) ** 2)
        if distance <= 1:
            self.x += -0.35 * math.cos(angle)
            self.y += -0.35 * math.sin(angle)
            self.arena.player.hitDamage(7)

    def hitDamage_missile(self, amount : int):
        return 0

    def hitDamage_bug(self, amount : int):
        self.args["damage"] += amount
        if self.args["damage"] >= 20:
            self.destroy = True
        return amount

class Arena:
    def __init__(self, blocks : list[Block] = []):
        self.player = Player(self)
        self.blocks = blocks

        self.entities : list[Entity] = []

        self.scale : int = 75

    def tick(self):
        self.player.tick()
        self.player.camera.tick()
        for entity in self.entities:
            entity.tick()
            if entity.destroy:
                self.entities.remove(entity)

    def newEntity(self, _id : str, x : float, y : float, args : dict = {}):
        entity = Entity(self, _id, x, y, args)
        self.entities.append(entity)
        return entity