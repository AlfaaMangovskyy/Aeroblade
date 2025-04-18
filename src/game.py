import pygame
from static import *

pygame.init()
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.NOFRAME,
)
clock = pygame.time.Clock()

arena = Arena([
    Block(-5, 3, 10, 3)
])
arena.newEntity("missile", 7, 7, {"inaccuracy" : 9})
for x in range(-9, 9, 1):
    arena.newEntity("bug", x, -3,)

running = True
while running:

    for e in pygame.event.get():

        if e.type == pygame.KEYDOWN:

            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                running = False
                break

            if e.key == pygame.K_SPACE:
                arena.player.camera.shake(15, FRAMERATE * 2, 90)

            if e.key == pygame.K_s:
                arena.player.jump()

        if e.type == pygame.MOUSEBUTTONDOWN:

            if e.button == 1:
                arena.player.ability("torpedoes")

    if not running: break

    keymap = pygame.key.get_pressed()
    if keymap[pygame.K_a]:
        arena.player.left()
    if keymap[pygame.K_d]:
        arena.player.right()
    if not (keymap[pygame.K_a] or keymap[pygame.K_d]):
        arena.player.static()

    arena.tick()
    camX, camY = arena.player.camera.get()

    screen.fill("#030303")

    pygame.draw.rect(
        screen, "#FFFFFF",
        (
            (arena.player.x - arena.player.w / 2 - camX) * arena.scale + WIDTH // 2,
            (arena.player.y - arena.player.h / 2 - camY) * arena.scale + HEIGHT // 2,
            arena.player.w * arena.scale,
            arena.player.h * arena.scale,
        )
    )

    for block in arena.blocks:
        pygame.draw.rect(
            screen, "#FFFFFF",
            (
                (block.x - camX) * arena.scale + WIDTH // 2,
                (block.y - camY) * arena.scale + HEIGHT // 2,
                block.w * arena.scale,
                block.h * arena.scale,
            )
        )

    for entity in arena.entities:

        if entity.id == "missile":
            rx = (entity.x - camX) * arena.scale + WIDTH // 2
            ry = (entity.y - camY) * arena.scale + HEIGHT // 2
            pygame.draw.polygon(
                screen, "#FF0000",
                (
                    (rx + 25, ry),
                    (rx, ry + 25),
                    (rx - 25, ry),
                    (rx, ry - 25),
                )
            )

        if entity.id == "bug":
            rx = (entity.x - camX) * arena.scale + WIDTH // 2
            ry = (entity.y - camY) * arena.scale + HEIGHT // 2
            pygame.draw.polygon(
                screen, "#33FF33",
                (
                    (rx + 25, ry),
                    (rx, ry + 25),
                    (rx - 25, ry),
                    (rx, ry - 25),
                )
            )

    pygame.display.update()
    clock.tick(FRAMERATE)