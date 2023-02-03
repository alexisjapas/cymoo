from .Unit import Unit
from .Cable import Cable
from Solution import Solution


class Path:
    """
    TODO DOCSTRING
    """
    def __init__(self) -> None:
        self.unit: list[Unit] = []
        self.cable: list[Cable] = []


    def add_unit(self, unit):
        self.unit.append(unit)


    def add_cable(self, cable):
        self.cable.append(cable)


    def create_path(self, units, cables):
        self.unit = units
        self.cable = cables


    def to_solution(self, task, id=None):
        if not id:
            id = Solution.maxId
            Solution.maxId += 1
        parameters = (self.unit, self.cable)
        solution = self.compute_solution(task)
        return Solution(id, solution, parameters)


    def compute_solution(self, task):
        processingTime = self.compute_processing_time(task)
        cost = self.compute_cost(task)
        pollution = self.compute_pollution(task)
        return (processingTime, cost, pollution)


    def compute_processing_time(self, task):
        # Computing time
        computingTime = task.nInstructions / self.unit[-1].computingSpeed

        # Transit time
        transitTime = 0
        for cable in self.cable:
            transitTime += cable.distance / cable.propagationSpeed + task.dataSize / cable.flowRate
        for unit in self.unit[:-1]:
            transitTime += task.dataSize / unit.throughput
        transitTime *= 2
        transitTime += task.dataSize / self.unit[-1].throughput

        # Processing time
        return computingTime + transitTime


    def compute_cost(self, task):
        cost = 0
        for unit in self.unit[:-1]:
            cost += task.dataSize * unit.cost / unit.throughput
        cost *= 2
        cost += self.unit[-1].cost * (task.dataSize / self.unit[-1].throughput + task.nInstructions / self.unit[-1].computingSpeed)
        return cost


    def compute_pollution(self, task):
        pollution = 0
        for unit in self.unit[:-1]:
            pollution += task.dataSize * unit.pollution / unit.throughput
        pollution *= 2
        pollution += self.unit[-1].pollution * (task.dataSize / self.unit[-1].throughput + task.nInstructions/self.unit[-1].computingSpeed)
        return pollution


    def __str__(self) -> str:
        expr = ''
        for unit in self.unit:
            expr += str(unit)+'\n'
        for cable in self.cable:
            expr += str(cable)+'\n'
        return expr

