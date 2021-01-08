from __future__ import annotations
from numpy.core.fromnumeric import shape
import pymunk
from typing import Tuple
from typing import List

from pymunk.space import Space

class Part(object):

    def __init__(self, mass: int, size: Tuple[int, int], shapeVar : str):
        if (shapeVar == "rectangle"):
            self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
            self.shape = pymunk.Poly.create_box(self.body, size, 0)
        elif (shapeVar == "circle"):
            self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, min(size[0], size[1]), max(size[0], size[1])))
            self.shape = pymunk.Circle(self.body, max(size[0], size[1]))
        else:
            self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
            self.shape = pymunk.Poly.create_box(self.body, size, 0)
            print("INVALID SHAPEEEEEEEEEEEEEEEEEEEEEEEEE")
        self.shape._set_collision_type(2)
        self.shape.friction = 0.69
        filter = pymunk.ShapeFilter(group = 0x1)
        self.shape.filter = filter
        self.limbs = []
        self.creature : Creature = None

    def addLimb(self, mass: int, size: Tuple[int, int], childPivotOffset: Tuple,
                    selfOffset: Tuple[int, int], isUnderBody: bool, hasMuscle: bool, shapeVar : str = "rectangle"):
        limb = Limb(self.creature, mass, size, isUnderBody, shapeVar)
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
    def __init__(self, mass: int, size: Tuple[int, int], position: Tuple[int, int], shapeVar : str = "rectangle"):
        super().__init__(mass, size, shapeVar)
        self.body.position = position
        self.pivots : List[pymunk.constraints.PivotJoint] = []
        self.muscles : List[pymunk.constraints.SimpleMotor] = []
        self.creature = self

    def create(self, space: pymunk.Space):
        Creature.__create(self.limbs, space, True)
        space.add(self.body, self.shape)
        Creature.__create(self.limbs, space, False)
        for pivot in self.pivots: space.add(pivot)
        for muscle in self.muscles: space.add(muscle)

        
    @staticmethod
    def __create(listoflimbs: List[Limb], space: pymunk.Space, isUnderBody: bool):
        for limb in listoflimbs:
            if limb.isUnderBody == isUnderBody:
                space.add(limb.body, limb.shape)
            Creature.__create(limb.limbs, space, isUnderBody)
    
    def remove(self, space: pymunk.Space):
        for pivot in self.pivots: space.remove(pivot)
        for muscle in self.muscles: space.remove(muscle)
        Creature.__remove(self, space)

    @staticmethod
    def __remove(part, space : pymunk.Space):
        space.remove(part.body)
        space.remove(part.shape)
        for limb in part.limbs:
            Creature.__remove(limb, space)

    def getInputs(self):
        return list(map(lambda pivot : pivot._a._get_angle() - pivot._b._get_angle(), self.pivots))


class Limb(Part):
    def __init__(self, creature: Creature, mass: int, size: Tuple[int, int], isUnderBody: bool, shapeVar : str):
        super().__init__(mass, size, shapeVar)
        self.isUnderBody = isUnderBody
        self.creature = creature
        self.pivot : pymunk.constraints.PivotJoint = None
        self.muscle : pymunk.constraints.SimpleMotor = None


