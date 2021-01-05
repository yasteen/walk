import pygame
import pymunk
import pymunk.pygame_util
import sys
from creatures import human


def addBoundaries(space):
    floor1 = pymunk.Body(body_type = pymunk.Body.STATIC)
    pymunk.Body()
    shape1 = pymunk.Segment(floor1, (0, 800), (800, 800), 10)
    shape1.friction = 1.00

    floor2 = pymunk.Body(body_type = pymunk.Body.STATIC)
    pymunk.Body()
    shape2 = pymunk.Segment(floor2, (0, 0), (800, 0), 10)
    shape2.friction = 1.00

    floor3 = pymunk.Body(body_type = pymunk.Body.STATIC)
    pymunk.Body()
    shape3 = pymunk.Segment(floor3, (0, 0), (0, 800), 10)
    shape3.friction = 1.00

    floor4 = pymunk.Body(body_type = pymunk.Body.STATIC)
    pymunk.Body()
    shape4 = pymunk.Segment(floor4, (800, 0), (800, 800), 10)
    shape4.friction = 1.00
    space.add(floor1, shape1, floor2, shape2, floor3, shape3, floor4, shape4)


def addObjects(space):
    person = human(space, (400, 300))
    addBoundaries(space)
    return person

def start():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
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
                    person.muscles[0].rate = -2
                    person.muscles[1].rate = 2
                elif event.key == pygame.K_DOWN:
                    person.muscles[0].rate = 2
                    person.muscles[1].rate = -2

        ## draw
        screen.fill((200, 200, 200))
        space.debug_draw(draw_options)

        ## frames/updates
        space.step(1 / 40)      ## update
        pygame.display.update()
        clock.tick(60)          ## fps

if __name__ == '__main__': start()