from model import Creature
import pygame
import pymunk
import pymunk.pygame_util
import sys
import creatures
import neat.NEAT as neat

path = "./neat/data/"
speed = 1
die = False
floor1_1 = None
floor1_2 = None

def addBoundaries(space):
    global floor1_1, floor1_2, shape1_1, shape1_2
    floor1_1 = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
    floor1_1.velocity = (-30, 0)
    floor1_1.position = (400, 800)
    shape1_1 = pymunk.Segment(floor1_1, (-500, -20), (500, -20), 10)
    shape1_1.color = (0, 0, 255, 255)
    shape1_1.friction = 0.69

    floor1_2 = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
    floor1_2.velocity = (-30, 0)
    floor1_2.position = (800+500, 800)
    shape1_2 = pymunk.Segment(floor1_2, (-500, 0), (500, 0), 10)
    shape1_2.friction = 0.69

    floor2 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape2 = pymunk.Segment(floor2, (0, 0), (800, 0), 10)
    shape2.friction = 1.00

    floor3 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape3 = pymunk.Segment(floor3, (0, 0), (0, 800), 10)
    shape3.friction = 1.00
    shape3.color = (255, 0, 0, 255)
    shape3._set_collision_type(1)

    floor4 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape4 = pymunk.Segment(floor4, (800, 0), (800, 800), 10)
    shape4.friction = 1.00
    space.add(floor1_1, shape1_1, floor1_2, shape1_2, floor2, shape2, floor3, shape3, floor4, shape4)

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


def ripGG(space, arbiter, data):
    global die
    die = True

def startNEAT(creature : str, completedGen : int, isDisplayOn : bool):
    global die
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

    collide = space.add_collision_handler(1, 2)
    collide.post_solve = ripGG

    neat.init(len(person.getInputs()), len(person.getInputs()))
    gen : neat.Generation = neat.Generation()
    if completedGen == 0: gen.createGeneration()
    else : gen.loadGeneration(path + creature + "/" + str(completedGen) + ".neat")

    fitness = 0
    while True:
        while gen.fitnessAlreadyMeasured():
            gen.nextIndividual()
            print("Individual: " + str(gen.currentIndividual) + ", Species: " + str(gen.currentSpecies))

        if isDisplayOn:                     ## DISPLAY ON
            screen.fill((200, 200, 200))
            space.debug_draw(draw_options)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        if (die == False):
            iterate(space, person, gen)
            fitness = fitness + 1
        else:
            reset(space, person, gen, creature, fitness)
            person = creatures.creatures[creature](space, (400, 400))

        if floor1_1.position.x < -500: floor1_1.position = (800 + 500, floor1_1.position.y)
        if floor1_2.position.x < -500: floor1_2.position = (800 + 500, floor1_2.position.y)

        if isDisplayOn:                     ## DISPLAY ON
            pygame.display.update()
            clock.tick(60)

def iterate(space : pymunk.Space, person : Creature, generation : neat.Generation):
    inputs = person.getInputs()
    outputs = []
    neat.init(len(inputs), len(inputs) - 1)
    if generation.currentFrame % 5 == 0: outputs = generation.evaluateCurrent(inputs)
    for i in range(len(outputs)):
        output = outputs[i]
        if output < -0.5: person.muscles[i].rate = -speed
        elif output > 0.5: person.muscles[i].rate = speed
        else: person.muscles[i].rate = 0
    generation.currentFrame = generation.currentFrame + 1

    space.step(1 / 10)

def reset(space : pymunk.Space, person : Creature, generation: neat.Generation, creature : str, fitness : int):
    global die
    generation.currentFrame = 0
    generation.species[generation.currentSpecies].individuals[generation.currentIndividual].fitness = fitness
    fitness = 0
    die = False
    person.remove(space)

    

if __name__ == '__main__': startNEAT("human", 0, True)