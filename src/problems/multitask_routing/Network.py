import uuid
import random

from ...problems.Problem import Problem
from .Unit import Unit
from .Cable import Cable
from .Paths import Paths


class Network(Problem):
    """
    TODO DOCSTRING
    """

    def __init__(
        self,
        startTag,
        tasks,
        optimDirections: dict,
        minDepth: int,
        maxDepth: int,
        mutationRate: float,
        layers: list[dict],
    ) -> None:
        super().__init__(optimDirections)
        self.units = []
        self.cables = []
        self.startTag = startTag
        self.tasks = tasks
        self.minDepth = minDepth
        self.maxDepth = maxDepth
        self.mutationRate = mutationRate
        self.layers = layers

    def pre_optimize(self):
        self.generate_basic_network()

    def post_optimize(self):
        pass

    def generate_parameters(self, expression, *parameters):
        if callable(expression):
            if expression.__code__.co_argcount == 0:
                return expression()
            else:
                return expression(*parameters)
        else:
            return expression

    def generate_basic_network(self):
        self.units.clear()
        self.cables.clear()

        def _generate_params(parameters: dict, *args):
            params = dict()
            for key, value in parameters.items():
                params[key] = self.generate_parameters(value, *args)
            return params

        def _generate_next_layer(unit: Unit, parameters: list[dict], units: list[Unit], cables: list[Cable]):
            if len(parameters) == 0:
                return None
            # Number of new units
            numberNewUnits = self.generate_parameters(parameters[0]["numberNewUnits"], unit)
            # Generate the new units
            for _ in range(numberNewUnits):
                id = str(uuid.uuid4()).replace("-", "")
                params = _generate_params(parameters[0]["unit"], unit)
                newUnit = Unit(id, **params)
                units.append(newUnit)
                if unit:
                    params = _generate_params(parameters[0]["cable"], unit, newUnit)
                    newCable = Cable(unit, newUnit, **params)
                    cables.append(newCable)
                _generate_next_layer(newUnit, parameters[1:], units, cables)

        # Check validity of parameters
        assert isinstance(self.layers, list) and all(
            [isinstance(param, dict) for param in self.layers]
        ), "self.layers must be a list of dict"

        _generate_next_layer(None, self.layers, self.units, self.cables)
        # Link all the units with the same startTag
        startingUnits = [unit for unit in self.units if unit.tag == self.startTag]
        # Create Couple of units
        # Create cables between them
        for couple in [
            (startingUnits[i], startingUnits[j])
            for i in range(len(startingUnits))
            for j in range(i + 1, len(startingUnits))
        ]:
            params = _generate_params(self.layers[0]["cable"], couple[0], couple[1])
            newCable = Cable(couple[0], couple[1], **params)
            self.cables.append(newCable)
        return True

    def populate(self, nSolution: int, nodeWeights=None) -> list[Paths]:
        solutions = []
        if nodeWeights:
            for _ in range(nSolution):
                parameters = tuple(
                    self.generate_path(random.randint(self.minDepth, self.maxDepth), nodeWeights=nodeWeights[i])
                    for i in range(len(self.tasks))
                )
                solutions.append(Paths(parameters=parameters, tasks=self.tasks))
        else:
            for _ in range(nSolution):
                parameters = tuple(
                    self.generate_path(random.randint(self.minDepth, self.maxDepth)) for _ in range(len(self.tasks))
                )
                solutions.append(Paths(parameters=parameters, tasks=self.tasks))
        return solutions

    def crossover(self, paths1: Paths, paths2: Paths) -> Paths:
        sharedUnits = tuple(
            [u for u in paths1.parameters[i]["units"] if u in paths2.parameters[i]["units"]]
            for i in range(len(self.tasks))
        )
        childPaths = None
        if any(sharedUnits):
            # choose a random list in sharedUnits among the non empty ones
            chosenList, index = random.choice([(sharedUnits[i], i) for i in range(len(sharedUnits)) if sharedUnits[i]])
            chosenOne = random.choice(chosenList)
            childPathUnits = (
                paths1.parameters[index]["units"][: paths1.parameters[index]["units"].index(chosenOne) + 1]
                + paths2.parameters[index]["units"][paths2.parameters[index]["units"].index(chosenOne) + 1:]
            )
            childPathCables = (
                paths1.parameters[index]["cables"][: paths1.parameters[index]["units"].index(chosenOne)]
                + paths2.parameters[index]["cables"][paths2.parameters[index]["units"].index(chosenOne):]
            )
            # create a tuple called parameters with the same structure as paths1.parameters and paths2.parameters
            # where each element is chosen randomly in paths1.parameters or paths2.parameters
            parameters = tuple(
                random.choice([paths1.parameters[i], paths2.parameters[i]]) for i in range(len(self.tasks))
            )
            # replace the element at index index in parameters with the dictionary
            # {"units": childPathUnits, "cables": childPathCables}
            parameters[index]["units"], parameters[index]["cables"] = childPathUnits, childPathCables

            childPaths = Paths(tasks=self.tasks, parameters=parameters)

        return childPaths

    def mutate(self, paths: Paths) -> Paths:
        if random.uniform(0, 1) < self.mutationRate and any([t["cables"] for t in paths.parameters]):
            pathIndex = random.choice([i for i, t in enumerate(paths.parameters) if t["cables"]])
            mutPathsUnits = paths.parameters[pathIndex]["units"][:-1]
            mutPathsCables = paths.parameters[pathIndex]["cables"][:-1]
            paths.parameters[pathIndex]["units"], paths.parameters[pathIndex]["cables"] = mutPathsUnits, mutPathsCables
        if random.uniform(0, 1) < self.mutationRate:
            unit, index = random.choice([(paths.parameters[i]["units"], i) for i in range(len(self.tasks))])
            last_unit = unit[-1]
            cable = random.choice(last_unit.cables)
            paths.parameters[index]["cables"].append(cable)
            paths.parameters[index]["units"].append(cable.get_other_unit(last_unit))
        return paths
    
    def add_final_node(self):
        unit = Unit("0", 'FINAL')
        self.units.append(unit)
        for u in self.units:
            cable = Cable(u, unit)

    def remove_final_node(self):
        for u in self.units:
            if u.tag == 'FINAL':
                self.units.remove(u)

    def generate_path(self, maxDepth: int, nodeWeights=None) -> dict:
        starting = random.choice([unit for unit in self.units if unit.tag == self.startTag])

        def _recursive_generate_path(unit: Unit, depth: int, path: dict, nodeWeights=None) -> dict:
            path["units"].append(unit)
            if depth == maxDepth:
                return path
            if nodeWeights is not None:
                weights = [nodeWeights[unit.id][cable.get_other_unit(unit).id] for cable in unit.cables]
                if sum(weights) == 0:
                    cable = random.choice(unit.cables)
                else:
                    cable = random.choices(unit.cables, weights=weights, k=1)[0]
            else:
                cable = random.choice(unit.cables)
            path["cables"].append(cable)
            return _recursive_generate_path(cable.get_other_unit(unit), depth + 1, path, nodeWeights)

        generatedPath = _recursive_generate_path(starting, 0, {"units": [], "cables": []}, nodeWeights)
        while generatedPath["units"][-1].tag == 'FINAL':
            generatedPath["units"].pop()
            generatedPath["cables"].pop()
        return generatedPath

    def to_Neo4j(self):
        expression = "CREATE "
        for unit in self.units:
            expression += f"{unit.to_Neo4j()},\n"
        for cable in self.cables:
            expression += f"{cable.to_Neo4j()},\n"
        return expression[:-2] + ";"

    def __str__(self) -> str:
        expression = f"Network: {len(self.units)} units, {len(self.cables)} cables\n"
        for unit in self.units:
            expression += f"{unit}\n"
        for cable in self.cables:
            expression += f"{cable}\n"
        return expression


if __name__ == "__main__":
    net = Network()
    net.generate_basic_network(
        [
            {
                "numberNewUnits": 3,
                "unit": {"power": lambda: random.random(), "tag": lambda: "DEVICE"},
                "cable": {"length": lambda: random.random() + 1},
            },
            {
                "numberNewUnits": 3,
                "unit": {"power": lambda: random.random() + 1},
                "cable": {"length": lambda: random.random()},
            },
        ]
    )
    print(net)
    print(net.to_Neo4j())
