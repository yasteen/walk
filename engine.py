from __future__ import annotations
import pymunk
import pymunk.pygame_util
import pygame
import creatures
import neat.NEAT as neat

import sys
import time

windowSize = (800, 800)
speed = 1

# floor
baseGroundSpeed = 30
groundSpeed = 30
groundAcceleration = 0.01
floor1_1 = None
floor1_2 = None

engine : Engine = None

def dieResetCallback(space, arbiter, data : Engine):
    data.die = True

class Engine(object):
    def __init__(self, creatureName : str, completedGen : int, isDisplayOn : bool):
        self.space = pymunk.Space()
        self.space.gravity = (0, 500)
        # pygame modules
        self.screen = None
        self.font = None
        self.clock = None
        self.draw_options = None
        self.die = False
        
        self.isDisplayOn = isDisplayOn
        self.creatureName = creatureName

        if isDisplayOn: 
            pygame.init()
            self.screen = pygame.display.set_mode(windowSize)
            self.clock = pygame.time.Clock()
            self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            self.font = pygame.font.SysFont('Arial', 32)

        Engine.__addBoundaries(self.space)
        self.creature = creatures.creatures[creatureName](self.space, (500, windowSize[1] / 2))
        self.collide : pymunk.collision_handler.CollisionHandler = self.space.add_collision_handler(1, 2)
        self.collide._data = self
        self.collide.post_solve = dieResetCallback
        neat.init(len(self.creature.getInputs()), len(self.creature.getInputs()) - 2)
        self.gen = neat.Generation()
        if completedGen == 0 : self.gen.createGeneration(creatureName)
        else : self.gen = neat.Generation.loadGeneration(neat.path + creatureName + "/" + str(completedGen) + ".neat")
        self.fitness = 0

    def iterate(self):
        inputs = self.creature.getInputs()
        outputs = []
        neat.init(len(inputs), len(inputs) - 2)
        if self.gen.currentFrame % 5 == 0:
            outputs = self.gen.evaluateCurrent(inputs)
            for i in range(len(outputs)):
                output = outputs[i]
                if output < -0.5: self.creature.muscles[i].rate = -speed
                elif output > 0.5: self.creature.muscles[i].rate = speed
                else: self.creature.muscles[i].rate = 0
        self.gen.currentFrame = self.gen.currentFrame + 1
        self.space.step(1/40)
        self.fitness = self.fitness + 1

    def reset(self):
        global groundSpeed
        self.gen.currentFrame = 0
        self.gen.species[self.gen.currentSpecies].individuals[self.gen.currentIndividual].fitness = self.fitness
        if self.fitness > self.gen.maxFitness : self.gen.maxFitness = self.fitness
        self.creature.remove(self.space)
        groundSpeed = baseGroundSpeed
        self.creature = creatures.creatures[self.creatureName](self.space, (500, windowSize[1] / 2))
        self.fitness = 0
        self.die = False

    def learn_loop(self):
        global floor1_1, floor1_2
        self.gen.gen = self.gen.gen + 1
        while True:
            while self.gen.fitnessAlreadyMeasured():
                print("Generation: " + str(self.gen.gen) +
                        ", Individual: " + str(self.gen.currentIndividual) +
                        ", Species: " + str(self.gen.currentSpecies) +
                        ", Fitness: " + str(self.gen.species[self.gen.currentSpecies].individuals[self.gen.currentIndividual].fitness))
                self.gen.nextIndividual()

            if self.isDisplayOn: self.draw()

            incrementGround()

            if not self.die: self.iterate()
            else:
                self.reset()

            if self.isDisplayOn:
                pygame.display.update()
                self.clock.tick(60)

    def top_loop(self):
        if self.gen.gen == 0 :
            print("No generation saved.")
            return
        top = self.gen.getTopIndividual()
        self.gen.currentSpecies = top[0]
        self.gen.currentIndividual = top[1]
        print(self.gen.species[top[0]].individuals[top[1]].__dict__)
        while not self.die:
            self.draw()
            incrementGround()
            self.iterate()
            if self.isDisplayOn:
                pygame.display.update()
                self.clock.tick(60)
        time.sleep(1)
        pygame.quit()
        if __name__ == "__main__": sys.exit()

    def draw(self):
        self.screen.fill((200, 200, 200))
        self.space.debug_draw(self.draw_options)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                if __name__ == 'main': sys.exit()
        genRect = self.addText("Generation: " + str(self.gen.gen), (0,0))
        specRect = self.addText("Species: " + str(self.gen.currentSpecies), genRect.bottomleft)
        indRect = self.addText("Individual: " + str(self.gen.currentIndividual), specRect.bottomleft)
        fitRect = self.addText("Fitness: " + str(self.fitness), indRect.bottomleft)
        maxFit = self.addText("Max Fitness: " + str(self.gen.maxFitness), fitRect.bottomleft)

    @staticmethod
    def __addBoundaries(space : pymunk.Space):
        global floor1_1, floor1_2
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

    def addText(self, text : str, topLeft : tuple):
        text = self.font.render(text, True, [0,0,0])
        rect = text.get_rect()
        rect.topleft = topLeft
        self.screen.blit(text, rect)
        return rect

def incrementGround():
    global groundSpeed
    groundSpeed = groundSpeed + groundAcceleration
    floor1_1.velocity = (-groundSpeed, 0)
    floor1_2.velocity = (-groundSpeed, 0)
    if floor1_1.position.x < -500: floor1_1.position = (800 + 500, floor1_1.position.y)
    if floor1_2.position.x < -500: floor1_2.position = (800 + 500, floor1_2.position.y)

if __name__ == '__main__':
    # engine = Engine("human", 0, True)
    # engine.learn_loop()
    engine = Engine("human", 25, True)
    engine.top_loop()
    