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
    head = person.addLimb(12, (0, 30), (0,0), (0, -size[1] / 2), False, False, "circle")

    person.create(space)
    return person
    

    ## DICTIONARY ##

creatures : Dict[str, Callable[[pymunk.Space, Tuple[int, int]], Creature]] = {"human" : human}