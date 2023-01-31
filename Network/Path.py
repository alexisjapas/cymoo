from typing import List
from .Unit import Unit
from .Cable import Cable
from Solution import Solution

class Path:
    def __init__(self) -> None:
        self.unit: List[Unit] = []
        self.cable: List[Cable] = []
        pass

    def addUnit(self, unit):
        self.unit.append(unit)

    def addCable(self, cable):
        self.cable.append(cable)

    def createPath(self, units, cables):
        self.unit = units
        self.cable = cables

    def toSolution(self, task, id=None):
        if not id:
            id = Solution.max_id
            Solution.max_id += 1
        parameters = (self.unit, self.cable)
        solution = self.computeSolution(task)
        return Solution(id, solution, parameters)

    def computeSolution(self, task):
        time = self.computeTime(task)
        cost = self.computeCost(task)
        pollution = self.computePollution(task)
        return (time, cost, pollution)

    def computeTime(self, task):
        time = task.nInstruction/self.unit[-1].puissance
        latency = 0
        for cable in self.cable:
            latency += cable.distance/cable.vitesse + task.dataSize / cable.debit
        for unit in self.unit[:-1]:
            latency += task.dataSize / unit.debitTraitement
        latency *= 2
        latency += task.dataSize / self.unit[-1].debitTraitement
        time += latency
        return time

    def computeCost(self, task):
        cost = 0
        for unit in self.unit[:-1]:
            cost += task.dataSize * unit.cost / unit.debitTraitement
        cost *= 2
        cost += self.unit[-1].cost * ( task.dataSize / self.unit[-1].debitTraitement + task.nInstruction/self.unit[-1].puissance )
        return cost

    def computePollution(self, task):
        pollution = 0
        for unit in self.unit[:-1]:
            pollution += task.dataSize * unit.pollution / unit.debitTraitement
        pollution *= 2
        pollution += self.unit[-1].pollution * ( task.dataSize / self.unit[-1].debitTraitement + task.nInstruction/self.unit[-1].puissance )
        return pollution


    
