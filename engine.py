from model import Creature
import pygame
import pymunk
import pymunk.pygame_util
import sys
import creatures
import neat.NEAT as neat
import tkinter as tk
import os

speed = 1
groundSpeed = 30

windowSize = (800, 800)

die = False
floor1_1 = None
floor1_2 = None

def addBoundaries(space):
    global floor1_1, floor1_2, shape1_1, shape1_2
    floor1_1 = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
    floor1_1.velocity = (-groundSpeed, 0)
    floor1_1.position = (windowSize[0] / 2, windowSize[1])
    shape1_1 = pymunk.Segment(floor1_1, (-500, 0), (500, 0), 10)
    shape1_1.color = (0, 0, 255, 255)
    shape1_1.friction = 0.69

    floor1_2 = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
    floor1_2.velocity = (-groundSpeed, 0)
    floor1_2.position = (windowSize[0] + 500, windowSize[1])
    shape1_2 = pymunk.Segment(floor1_2, (-500, 0), (500, 0), 10)
    shape1_2.friction = 0.69

    floor2 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape2 = pymunk.Segment(floor2, (0, 0), (windowSize[0], 0), 10)
    shape2.friction = 1.00

    floor3 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape3 = pymunk.Segment(floor3, (0, 0), (0, windowSize[1]), 10)
    shape3.friction = 1.00
    shape3.color = (255, 0, 0, 255)
    shape3._set_collision_type(1)

    floor4 = pymunk.Body(body_type = pymunk.Body.STATIC)
    shape4 = pymunk.Segment(floor4, (windowSize[0], 0), (windowSize[0], windowSize[1]), 10)
    shape4.friction = 1.00
    space.add(floor1_1, shape1_1, floor1_2, shape1_2, floor2, shape2, floor3, shape3, floor4, shape4)

def startVisual():
    pygame.init()
    screen = pygame.display.set_mode((windowSize[0], windowSize[1]))
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


def dieCallback(space, arbiter, data):
    global die
    die = True

def startNEAT(creatureName : str, completedGen : int, isDisplayOn : bool):
    global die
    space = pymunk.Space()
    space.gravity = (0, 500)
    font = None

    screen = None
    clock = None
    draw_options = None
    if isDisplayOn:                         ## DISPLAY ON
        pygame.init()
        screen = pygame.display.set_mode((windowSize[0], windowSize[1]))
        clock = pygame.time.Clock()
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        font = pygame.font.SysFont('ubuntu', 32)

    addBoundaries(space)
    creature = creatures.creatures[creatureName](space, (500, windowSize[1] / 2))

    collide = space.add_collision_handler(1, 2)
    collide.post_solve = dieCallback

    neat.init(len(creature.getInputs()), len(creature.getInputs()) - 2)
    print(len(creature.getInputs()))
    gen : neat.Generation = neat.Generation()
    if completedGen == 0: gen.createGeneration(creatureName)
    else : gen = neat.Generation.loadGeneration(neat.path + creatureName + "/" + str(completedGen) + ".neat")

    fitness = 0
    while True:
        while gen.fitnessAlreadyMeasured():
            gen.nextIndividual()
            print("Generation: " + str(gen.gen) + ", Individual: " + str(gen.currentIndividual) + ", Species: " + str(gen.currentSpecies) + ", Max Fitness before current: " + str(gen.maxFitness))

        if isDisplayOn:                     ## DISPLAY ON
            screen.fill((200, 200, 200))
            space.debug_draw(draw_options)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    if __name__ == '__main__': sys.exit()
            genRect = addText(screen, font, "Generation: " + str(gen.gen), (0,0))
            specRect = addText(screen, font, "Species: " + str(gen.currentSpecies), genRect.bottomleft)
            indRect = addText(screen, font, "Individual: " + str(gen.currentIndividual), specRect.bottomleft)
            fitRect = addText(screen, font, "Fitness: " + str(fitness), indRect.bottomleft)
            maxFit = addText(screen, font, "Max Fitness: " + str(gen.maxFitness), fitRect.bottomleft)

        if (die == False):
            iterate(space, creature, gen)
            fitness = fitness + 1
        else:
            reset(space, creature, gen, creatureName, fitness)
            creature = creatures.creatures[creatureName](space, (500, 400))
            fitness = 0
            die = False

        if floor1_1.position.x < -500: floor1_1.position = (800 + 500, floor1_1.position.y)
        if floor1_2.position.x < -500: floor1_2.position = (800 + 500, floor1_2.position.y)

        if isDisplayOn:                     ## DISPLAY ON
            pygame.display.update()
            clock.tick(60)

def addText(screen, font, text : str, topLeft : tuple):
        text = font.render(text, True, [0,0,0])
        rect = text.get_rect()
        rect.topleft = topLeft
        screen.blit(text, rect)
        return rect

def iterate(space : pymunk.Space, creature : Creature, generation : neat.Generation):
    inputs = creature.getInputs()
    outputs = []
    neat.init(len(inputs), len(inputs) - 2)
    if generation.currentFrame % 5 == 0: outputs = generation.evaluateCurrent(inputs)
    for i in range(len(outputs)):
        output = outputs[i]
        if output < -0.5: creature.muscles[i].rate = -speed
        elif output > 0.5: creature.muscles[i].rate = speed
        else: creature.muscles[i].rate = 0
    generation.currentFrame = generation.currentFrame + 1

    space.step(1 / 40)

def reset(space : pymunk.Space, creature : Creature, generation: neat.Generation, creatureName : str, fitness : int):
    generation.currentFrame = 0
    generation.species[generation.currentSpecies].individuals[generation.currentIndividual].fitness = fitness
    if fitness > generation.maxFitness: generation.maxFitness = fitness
    creature.remove(space)

    

if __name__ == '__main__': startNEAT("human", 0, True)