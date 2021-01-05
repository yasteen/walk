from __future__ import annotations
import pymunk
from typing import Tuple
from typing import List

class Part(object):

    def __init__(self, mass: int, size: Tuple[int, int]):
        self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        self.shape = pymunk.Poly.create_box(self.body, size, 0)
        self.shape.friction = 0.69
        filter = pymunk.ShapeFilter(group = 0x1)
        self.shape.filter = filter
        self.limbs = []
        self.creature = None

    def addLimb(self, mass: int, size: Tuple[int, int], childPivotOffset: Tuple,
                    selfOffset: Tuple[int, int], isUnderBody: bool, hasMuscle: bool):
        limb = Limb(self.creature, mass, size, isUnderBody)
        limb.body.position = (self.body.position.x + selfOffset[0] - childPivotOffset[0],
                                self.body.position.y + selfOffset[1] - childPivotOffset[1])
        pivotpos = (self.body.position.x + selfOffset[0], self.body.position.y + selfOffset[1])
        limb.pivot = pymunk.constraints.PivotJoint(self.body, limb.body, pivotpos)
        self.creature.pivots.append(limb.pivot)
        if hasMuscle:
            limb.muscle = pymunk.constraints.SimpleMotor(self.body, limb.body, 0)
            self.creature.muscles.append(limb.muscle)
        else: limb.muscle = None
        self.limbs.append(limb)
        return limb


class Creature(Part):
    def __init__(self, mass: int, size: Tuple[int, int], position: Tuple[int, int]):
        super().__init__(mass, size)
        self.body.position = position
        self.pivots = []
        self.muscles = []
        self.creature = self

    def create(self, space: pymunk.space):
        Creature.__create(self.limbs, space, True)
        space.add(self.body, self.shape)
        Creature.__create(self.limbs, space, False)
        for pivot in self.pivots: space.add(pivot)
        for muscle in self.muscles: space.add(muscle)

        
    @staticmethod
    def __create(listoflimbs: List[Limb], space: pymunk.space, isUnderBody: bool):
        for limb in listoflimbs:
            if limb.isUnderBody == isUnderBody:
                space.add(limb.body, limb.shape)
                print("added")
            Creature.__create(limb.limbs, space, isUnderBody)


class Limb(Part):
    def __init__(self, creature: Creature, mass: int, size: Tuple[int, int], isUnderBody: bool):
        super().__init__(mass, size)
        self.isUnderBody = isUnderBody
        self.creature = creature
        ## Might not be necessary
        self.pivot = None
        self.muscle = None


