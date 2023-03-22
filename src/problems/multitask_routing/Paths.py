from problems.Solution import Solution
from .Unit import Unit
from .Cable import Cable
from .Task import Task


class Paths(Solution):
    """
    TODO DOCSTRING
    """

    def __init__(self, tasks: tuple[Task], _id: int = None, parameters: tuple[dict] = None) -> None:
        assert tasks is not None
        if parameters is None:
            parameters = tuple({"units": [], "cables": []} for _ in range(len(tasks)))
        super().__init__(_id, parameters)
        self.compute_solution(tasks)
        self.rank = 0
        self.crowdingDistance = 0

    def compute_solution(self, tasks):
        processingTime = max([self.compute_processing_time(t, i) for i, t in enumerate(tasks)])
        cost = sum([self.compute_cost(t, i) for i, t in enumerate(tasks)])
        pollution = sum([self.compute_pollution(t, i) for i, t in enumerate(tasks)])
        self.solution = {"processingTime": processingTime, "cost": cost, "pollution": pollution}

    def compute_processing_time(self, task, index):
        # Computing time
        computingTime = task.nInstructions / self.parameters[index]["units"][-1].computingSpeed

        # Transit time
        transitTime = 0
        for cable in self.parameters[index]["cables"]:
            transitTime += cable.distance / cable.propagationSpeed + task.dataSize / cable.flowRate
        for unit in self.parameters[index]["units"][:-1]:
            transitTime += task.dataSize / unit.throughput
        transitTime *= 2
        transitTime += task.dataSize / self.parameters[index]["units"][-1].throughput

        # Processing time
        return computingTime + transitTime

    def compute_cost(self, task, index):
        cost = 0
        for unit in self.parameters[index]["units"][:-1]:
            cost += task.dataSize * unit.cost / unit.throughput
        cost *= 2
        cost += self.parameters[index]["units"][-1].cost * (
            task.dataSize / self.parameters[index]["units"][-1].throughput
            + task.nInstructions / self.parameters[index]["units"][-1].computingSpeed
        )
        return cost

    def compute_pollution(self, task, index):
        pollution = 0
        for unit in self.parameters[index]["units"][:-1]:
            pollution += task.dataSize * unit.pollution / unit.throughput
        pollution *= 2
        pollution += self.parameters[index]["units"][-1].pollution * (
            task.dataSize / self.parameters[index]["units"][-1].throughput
            + task.nInstructions / self.parameters[index]["units"][-1].computingSpeed
        )
        return pollution

    def __str__(self) -> str:
        expr = ""
        for i, p in enumerate(self.parameters):
            units = " -> ".join([str(u) for u in p["units"]])
            cables = " -> ".join([str(c) for c in p["cables"]])
            expr += f"Path {i}: {units} ({cables})\t"
        return expr
