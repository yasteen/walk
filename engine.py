import pygame
import pymunk
import pymunk.pygame_util
import sys
from creatures import human


def addFloor(space):
    floor = pymunk.Body(body_type = pymunk.Body.STATIC)
    pymunk.Body()
    shape = pymunk.Segment(floor, (0, 500), (800, 500), 10)
    space.add(floor, shape)


def addObjects(space):
    person = human(space, (400, 300))
    addFloor(space)
    return person

def start():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0, 500)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    person = addObjects(space)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    person.muscles[0].rate = -3
                    person.muscles[1].rate = 3
                elif event.key == pygame.K_DOWN:
                    person.muscles[0].rate = 3
                    person.muscles[1].rate = -3

        ## draw
        screen.fill((200, 200, 200))
        space.debug_draw(draw_options)

        ## frames/updates
        space.step(1 / 40)      ## update
        pygame.display.update()
        clock.tick(60)          ## fps

if __name__ == '__main__': start()