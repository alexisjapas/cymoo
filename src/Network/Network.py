import uuid
import random

from .Unit import Unit
from .Cable import Cable
from .Path import Path


class Network():
    """
    TODO DOCSTRING
    """
    def __init__(self, startTag, task, optimDirections: list, minDepth: int, maxDepth: int, mutationRate: float, layers: list[dict]) -> None:
        self.units = []
        self.cables = []
        self.startTag = startTag
        self.task = task
        self.optimDirections = optimDirections
        self.minDepth = minDepth
        self.maxDepth = maxDepth
        self.mutationRate = mutationRate
        self.layers = layers


    def pre_optimization(self):
        self.generate_basic_network()


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
            numberNewUnits = self.generate_parameters(parameters[0]['numberNewUnits'], unit)
            # Generate the new units
            for _ in range(numberNewUnits):
                id = str(uuid.uuid4()).replace('-','')
                params = _generate_params(parameters[0]['unit'], unit)
                newUnit = Unit(id, **params)
                units.append(newUnit)
                if unit:
                    params = _generate_params(parameters[0]['cable'], unit, newUnit)
                    newCable = Cable(unit, newUnit, **params)
                    cables.append(newCable)
                _generate_next_layer(newUnit, parameters[1:], units, cables)

        ## Check validity of parameters
        assert isinstance(self.layers, list) and all([isinstance(param, dict) for param in self.layers]), "self.layers must be a list of dict"

        _generate_next_layer(None, self.layers, self.units, self.cables)
        ## Link all the units with the same startTag
        startingUnits = [unit for unit in self.units if unit.tag == self.startTag]
        ## Create Couple of units
        ## Create cables between them
        for couple in [(startingUnits[i], startingUnits[j]) for i in range(len(startingUnits)) for j in range(i+1, len(startingUnits))]:
            params = _generate_params(self.layers[0]['cable'], couple[0], couple[1])
            newCable = Cable(couple[0], couple[1], **params)
            self.cables.append(newCable)
        return True


    def populate(self, nSolution: int, nodeWeights=None):
        solutions = []
        for _ in range(nSolution):
            solutions.append(self.generate_path(random.randint(self.minDepth, self.maxDepth), nodeWeights).to_solution(self.task))
        return solutions


    def crossover(self, path1, path2):
        p1 = path1.parameters
        p2 = path2.parameters
        sharedUnits = [u for u in p1[0] if u in p2[0]]
        newSolution = None
        if sharedUnits:
            chosenOne = random.choice(sharedUnits)
            newPathUnits = p1[0][:p1[0].index(chosenOne)+1] + p2[0][p2[0].index(chosenOne)+1:]
            newPathCables = p1[1][:p1[0].index(chosenOne)] + p2[1][p2[0].index(chosenOne):]
            newPath = Path()
            newPath.create_path(newPathUnits, newPathCables)
            newSolution = newPath.to_solution(self.task)
        return newSolution


    def mutate(self, solution):
        newSolution = solution
        if solution.parameters[1] and random.uniform(0, 1) < self.mutationRate:
            nUnitsToRemove = random.randint(1, len(solution.parameters[0])-1)
            newPathUnits = solution.parameters[0][:-nUnitsToRemove]
            newPathCables = solution.parameters[1][:-nUnitsToRemove]
            newPath = Path()
            newPath.create_path(newPathUnits, newPathCables)
            newSolution = newPath.to_solution(self.task, id=solution.id)
        return newSolution


    def generate_path(self, maxDepth: int, nodeWeights=None):
        starting = random.choice([unit for unit in self.units if unit.tag == self.startTag])

        def _recursive_generate_path(unit: Unit, depth: int, path: Path, nodeWeights=None):
            path.add_unit(unit)
            if depth == maxDepth:
                return path
            if nodeWeights is not None:
                weights = [nodeWeights[unit.id][cable.get_other_unit(unit).id] for cable in unit.cables]
                if (sum(weights)==0):
                    cable = random.choice(unit.cables)
                else:
                    cable = random.choices(unit.cables, weights=weights, k=1)[0]
            else:
                cable = random.choice(unit.cables)
            path.add_cable(cable)
            return _recursive_generate_path(cable.get_other_unit(unit), depth+1, path, nodeWeights)

        return _recursive_generate_path(starting, 0, Path(), nodeWeights)


    def to_Neo4j(self):
        expression = 'CREATE '
        for unit in self.units:
            expression += f'{unit.to_Neo4j()},\n'
        for cable in self.cables:
            expression += f'{cable.to_Neo4j()},\n'
        return expression[:-2] + ';'


    def __str__(self) -> str:
        expression = f'Network: {len(self.units)} units, {len(self.cables)} cables\n'
        for unit in self.units:
            expression += f'{unit}\n'
        for cable in self.cables:
            expression += f'{cable}\n'
        return expression


if __name__ == '__main__':
    net = Network()
    net.generate_basic_network([{'numberNewUnits': 3, 'unit':{'power': lambda: random.random(), 'tag': lambda: 'DEVICE'}, 'cable':{'length': lambda: random.random()+1}}, {'numberNewUnits': 3, 'unit':{'power': lambda: random.random()+1}, 'cable':{'length': lambda: random.random()}}])
    print(net)
    print(net.to_Neo4j())

