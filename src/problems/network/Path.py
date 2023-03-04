from problems.Solution import Solution
from .Unit import Unit
from .Cable import Cable
from .Task import Task


class Path(Solution):
    """
    TODO DOCSTRING
    """
    def __init__(self, _id: int = None, units: list[Unit] = None, cables: list[Cable] = None,
                 task: Task = None) -> None:
        if units is None:
            units = []
        if cables is None:
            cables = []
        super().__init__(_id, {"units": units, "cables": cables})
        if task is not None:
            self.compute_solution(task)
        self.rank = 0
        self.crowdingDistance = 0

    def add_unit(self, unit):
        self.parameters["units"].append(unit)

    def add_cable(self, cable):
        self.parameters["cables"].append(cable)

    def create_path(self, units, cables):
        self.parameters["units"] = units
        self.parameters["cables"] = cables

    def compute_solution(self, task):
        processingTime = self.compute_processing_time(task)
        cost = self.compute_cost(task)
        pollution = self.compute_pollution(task)
        self.solution = {"processingTime": processingTime,
                         "cost": cost,
                         "pollution": pollution}

    def compute_processing_time(self, task):
        # Computing time
        computingTime = task.nInstructions / self.parameters["units"][-1].computingSpeed

        # Transit time
        transitTime = 0
        for cable in self.parameters["cables"]:
            transitTime += cable.distance / cable.propagationSpeed + task.dataSize / cable.flowRate
        for unit in self.parameters["units"][:-1]:
            transitTime += task.dataSize / unit.throughput
        transitTime *= 2
        transitTime += task.dataSize / self.parameters["units"][-1].throughput

        # Processing time
        return computingTime + transitTime

    def compute_cost(self, task):
        cost = 0
        for unit in self.parameters["units"][:-1]:
            cost += task.dataSize * unit.cost / unit.throughput
        cost *= 2
        cost += self.parameters["units"][-1].cost *\
            (task.dataSize / self.parameters["units"][-1].throughput +
             task.nInstructions / self.parameters["units"][-1].computingSpeed)
        return cost

    def compute_pollution(self, task):
        pollution = 0
        for unit in self.parameters["units"][:-1]:
            pollution += task.dataSize * unit.pollution / unit.throughput
        pollution *= 2
        pollution += self.parameters["units"][-1].pollution *\
            (task.dataSize / self.parameters["units"][-1].throughput +
             task.nInstructions/self.parameters["units"][-1].computingSpeed)
        return pollution

    def __str__(self) -> str:
        expr = ''
        for unit in self.parameters["units"]:
            expr += str(unit)+'\n'
        for cable in self.parameters["cables"]:
            expr += str(cable)+'\n'
        return expr
