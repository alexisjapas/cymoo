class Unit:
    pass

from typing import Tuple, List
import math;
from Cable import Cable

class Unit():
    def __init__(self,
    id: str,
    power: float, # Power of Tasks Execution ~ Instruction / Second
    pollution: float, # Amount of Pullution per Second of any usage ~ CO_2 / Second
    cost: float, # Amount paid per Second of any usage ~ $ / Second
    transfertRate: float, # Number of second needed to transfer a Bit ~ Second / bit
    position: Tuple[int, int] # Position of the Unit in the grid
    ) -> None:
        self.id = id; #TODO: Inherit from Node Class
        self.power = power;
        self.pollution = pollution;
        self.cost = cost;
        self.transfertRate = transfertRate;
        self.position = position;
        # Generated Values
        self.cables: List[Cable] = []; # Array of pointer to cableList

    def distanceWithOtherUnit(self, secondUnit: Unit):
        return math.sqrt(sum([(val[0]-val[1])**2 for val in zip(self.position, secondUnit.position)]))

if __name__ == '__main__':
    # Test Fonction distanceWithOtherUnit
    unit1 = Unit(0,1,1,1,1,(1,3))
    unit2 = Unit(1,1,1,1,1,(-2,7))
    print(unit1.distanceWithOtherUnit(unit2))

