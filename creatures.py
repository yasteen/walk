import pymunk
from model import Creature
from typing import Dict, Tuple, Callable


def human(space : pymunk.Space, position : Tuple[int, int]) -> Creature:
    size = (40, 100)
    person = Creature(40, size, position, "rectangle")
    armsize = (16, 80)
    arm1 = person.addLimb(10, armsize, (0,  -armsize[1] / 2), (0, -size[1] / 4), True, True, "rectangle")
    arm2 = person.addLimb(10, armsize, (0,  -armsize[1] / 2), (0, -size[1] / 4), False, True, "rectangle")
    thighsize = (20, 40)
    thigh1 = person.addLimb(10, thighsize, (0, -thighsize[1] / 2), (0, size[1] / 2), True, True, "rectangle")
    thigh2 = person.addLimb(10, thighsize, (0, -thighsize[1] / 2), (0, size[1] / 2), False, True, "rectangle")
    shinsize = (15, 30)
    shin1 = thigh1.addLimb(5, shinsize, (0, -shinsize[1] / 2), (0, thighsize[1] / 2), True, True, "rectangle")
    shin2 = thigh2.addLimb(5, shinsize, (0, -shinsize[1] / 2), (0, thighsize[1] / 2), False, True, "rectangle")

    headRadius = 30
    head = person.addLimb(12, (0, headRadius), (0,0), (0, -size[1] / 2), False, False, "circle")

    person.create(space)
    return person
    
def dog(space: pymunk.Space, position : Tuple[int, int]) -> Creature:
    size = (100, 40)
    dog = Creature(40, size, position, "rectangle")
    legsize = (15, 30)
    leg1 = dog.addLimb(10, legsize, (0, -legsize[1] / 2), (-size[0]/2+legsize[0]/2, size[1]/2), True, True, "rectangle")
    leg2 = dog.addLimb(10, legsize, (0, -legsize[1] / 2), (-size[0]/2+legsize[0]/2, size[1]/2), False, True, "rectangle")

    leg3 = dog.addLimb(10, legsize, (0, -legsize[1] / 2), (size[0]/2-legsize[0]/2, size[1]/2), True, True, "rectangle")
    leg4 = dog.addLimb(10, legsize, (0, -legsize[1] / 2), (size[0]/2-legsize[0]/2, size[1]/2), False, True, "rectangle")

    lleg1 = leg1.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), True, True, "rectangle")
    lleg2 = leg2.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), False, True, "rectangle")

    lleg3 = leg3.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), True, True, "rectangle")
    lleg4 = leg4.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), False, True, "rectangle")

    headRadius = 30
    head = dog.addLimb(12, (0, headRadius), (0, 0), (size[0] / 2, -size[1] / 2), False, False, "circle")

    dog.create(space)
    return dog

def test(space: pymunk.Space, position : Tuple[int, int]) -> Creature:
    radius = (0, 20)
    body = Creature(40, radius, position, "circle")
    legsize = (5, 50)
    leg1 = body.addLimb(10, legsize, (0, -legsize[1] / 2), (0, 0), True, True, "rectangle")
    leg2 = body.addLimb(10, legsize, (0, -legsize[1] / 2), (0, 0), False, True, "rectangle")

    lleg1 = leg1.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), True, True, "rectangle")
    lleg2 = leg2.addLimb(10, legsize, (0, -legsize[1] / 2), (0, legsize[1] / 2), False, True, "rectangle")

    headSize = (20, 20)
    head = body.addLimb(15, headSize, (0, 0), (0, radius[1] / 2), False, False, "rectangle")

    body.create(space)
    return body
    

    ## DICTIONARY ##

creatures : Dict[str, Callable[[pymunk.Space, Tuple[int, int]], Creature]] = {"human" : human, "dog" : dog, "test" : test}