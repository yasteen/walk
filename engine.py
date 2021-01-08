import pygame
import pymunk
import pymunk.pygame_util
import sys
import creatures
import neat.NEAT as neat

path = "./neat/data/"
speed = 1

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

def startVisual():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0, 500)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    addBoundaries(space)
    person = creatures.human(space, (400, 400))

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

def startNEAT(creature : str, completedGen : int, isDisplayOn : bool):
    space = pymunk.Space()
    space.gravity = (0, 500)

    screen = None
    clock = None
    draw_options = None
    if isDisplayOn:                         ## DISPLAY ON
        pygame.init()
        screen = pygame.display.set_mode((800, 800))
        clock = pygame.time.Clock()
        draw_options = pymunk.pygame_util.DrawOptions(screen)

    addBoundaries(space)

    person = creatures.creatures[creature](space, (400, 400))
    neat.init(len(person.getInputs()), len(person.getInputs()))
    gen : neat.Generation = neat.Generation()
    if completedGen == 0: gen.createGeneration()
    else : gen.loadGeneration(path + creature + "/" + str(completedGen) + ".neat")


    while True:
        if isDisplayOn:                     ## DISPLAY ON
            screen.fill((200, 200, 200))
            space.debug_draw(draw_options)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        neat.Generation
        inputs = person.getInputs()
        outputs = []
        neat.init(len(inputs), len(inputs))
        if gen.currentFrame % 5 == 0: outputs = gen.evaluateCurrent(inputs)
        for i in range(len(outputs)):
            output = outputs[i]
            if output < -0.5: person.muscles[i].rate = -speed
            elif output > 0.5: person.muscles[i].rate = speed
            else: person.muscles[i].rate = 0
        space.step(1 / 40)
        if isDisplayOn:                     ## DISPLAY ON
            pygame.display.update()
            clock.tick(60)



if __name__ == '__main__': startVisual()