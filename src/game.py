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

    pygame.display.update()
    clock.tick(FRAMERATE)