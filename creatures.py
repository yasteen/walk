import pymunk
from model import Creature
from typing import Dict, Tuple, Callable


def human(space : pymunk.Space, position : Tuple[int, int]) -> Creature:
    size = (40, 100)
    person = Creature(40, size, position)
    armsize = (16, 80)
    arm1 = person.addLimb(10, armsize, (0,  -armsize[1] / 2), (0, -size[1] / 4), True, True)
    arm2 = person.addLimb(10, armsize, (0,  -armsize[1] / 2), (0, -size[1] / 4), False, True)
    thighsize = (20, 40)
    thigh1 = person.addLimb(10, thighsize, (0, -thighsize[1] / 2), (0, size[1] / 2), True, True)
    thigh2 = person.addLimb(10, thighsize, (0, -thighsize[1] / 2), (0, size[1] / 2), False, True)
    shinsize = (15, 30)
    shin1 = thigh1.addLimb(5, shinsize, (0, -shinsize[1] / 2), (0, thighsize[1] / 2), True, True)
    shin2 = thigh2.addLimb(5, shinsize, (0, -shinsize[1] / 2), (0, thighsize[1] / 2), False, True)

    person.create(space)

    headRadius = 30
    head = pymunk.Body(12, pymunk.moment_for_circle(12, 0, headRadius))
    head.position = (position[0], position[1] - size[1] / 2)
    headShape = pymunk.Circle(head, headRadius)
    headShape.filter = pymunk.ShapeFilter(group = 0x1)
    headPivot = pymunk.PivotJoint(person.body, head, (position[0], position[1] - size[1] / 2))
    space.add(head, headShape, headPivot)
    return person
    

    ## DICTIONARY ##

creatures : Dict[str, Callable[[pymunk.Space, Tuple[int, int]], Creature]] = {"human" : human}