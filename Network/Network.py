from .Unit import Unit
from .Cable import Cable
from .Path import Path
import uuid
import random

class Network():
    def __init__(self, startTag, task, optim_directions: list, mutation_rate: float) -> None:
        self.units = []
        self.cables = []
        self.startTag = startTag
        self.task = task
        self.optim_directions = optim_directions
        self.mutation_rate = mutation_rate
        pass


    def generateParameters(self, expression, *parameters):
        if callable(expression):
            if expression.__code__.co_argcount==0:
                return expression()
            else:
                return expression(*parameters)
        else:
            return expression

    def generateBasicNetwork(self, parameters: list[dict]):
        self.units.clear()
        self.cables.clear()


        def generateParams(parameters: dict, *args):
            params = dict()
            for key, value in parameters.items():
                params[key] = self.generateParameters(value, *args)
            return params

        def generateNextLayer(unit: Unit, parameters: list[dict], units: list[Unit], cables: list[Cable]):
            if len(parameters) == 0:
                return None
            # Number of new units
            numberNewUnits = self.generateParameters(parameters[0]['numberNewUnits'], unit)
            # Generate the new units
            for _ in range(numberNewUnits):
                id = str(uuid.uuid4()).replace('-','')
                params = generateParams(parameters[0]['unit'], unit)
                newUnit = Unit(id, **params)
                units.append(newUnit)
                if unit:
                    params = generateParams(parameters[0]['cable'], unit, newUnit)
                    newCable = Cable(unit, newUnit, **params)
                    cables.append(newCable)
                generateNextLayer(newUnit, parameters[1:], units, cables)

        ## Check validity of parameters
        if isinstance(parameters, list):
            for param in parameters:
                if not isinstance(param, dict):
                    raise TypeError("parameters must be a list of dict")
        generateNextLayer(None, parameters, self.units, self.cables)
        ## Link all the units with the same startTag
        startingunits = [unit for unit in self.units if unit.tag == self.startTag]
        ## Create Couple of units
        ## Create cables between them
        for couple in [(startingunits[i], startingunits[j]) for i in range(len(startingunits)) for j in range(i+1, len(startingunits))]:
                params = generateParams(parameters[0]['cable'], couple[0], couple[1])
                newCable = Cable(couple[0], couple[1], **params)
                self.cables.append(newCable)
        return True

    def populate(self, nSolution: int, minDepth: int, maxDepth: int, nodeWeights = None):
        solutions = []
        for _ in range(nSolution):
            solutions.append(self.generatePath(random.randint(minDepth, maxDepth), nodeWeights).toSolution(self.task))
        return solutions

    def crossover(self, path_1, path_2):
        p_1 = path_1.parameters
        p_2 = path_2.parameters
        shared_units = [u for u in p_1[0] if u in p_2[0]]
        new_solution = None
        if shared_units:
            chosen_one = random.choice(shared_units)
            new_path_units = p_1[0][:p_1[0].index(chosen_one)+1] + p_2[0][p_2[0].index(chosen_one)+1:]
            new_path_cables = p_1[1][:p_1[0].index(chosen_one)]+p_2[1][p_2[0].index(chosen_one):]
            new_path = Path()
            new_path.createPath(new_path_units, new_path_cables)
            new_solution = new_path.toSolution(self.task)
        return new_solution

    def mutate(self, solution):
        new_solution = solution
        if solution.parameters[1] and random.uniform(0, 1) < self.mutation_rate:
            last_new_unit_index = random.randint(1, len(solution.parameters[0])-1)
            new_path_units = solution.parameters[0][:-last_new_unit_index]
            new_path_cables = solution.parameters[1][:-last_new_unit_index]
            new_path = Path()
            new_path.createPath(new_path_units, new_path_cables)
            new_solution = new_path.toSolution(self.task, id=solution.id)
        return new_solution

    def generatePath(self, maxDepth: int, nodeWeights = None):
        starting = random.choice([unit for unit in self.units if unit.tag == self.startTag])

        def recursiveGeneratePath(unit: Unit, depth: int, path: Path, nodeWeights = None):
            path.addUnit(unit)
            if depth == maxDepth:
                return path
            if nodeWeights is not None:
                weights = [nodeWeights[unit.id][cable.getOtherUnit(unit).id] for cable in unit.cables]
                if (sum(weights)==0):
                    cable = random.choice(unit.cables)
                else:
                    cable = random.choices(unit.cables, weights=weights, k=1)[0]
            else:
                cable = random.choice(unit.cables)
            path.addCable(cable)
            return recursiveGeneratePath(cable.getOtherUnit(unit), depth+1, path, nodeWeights)

        return recursiveGeneratePath(starting, 0, Path(), nodeWeights)

    def toNeo4j(self):
        expression = 'CREATE '
        for unit in self.units:
            expression += f'{unit.toNeo4J()},\n'
        for cable in self.cables:
            expression += f'{cable.toNeo4J()},\n'
        return expression[:-2]+';'

    def __str__(self) -> str:
        expression = f'Network: {len(self.units)} units, {len(self.cables)} cables\n'
        for unit in self.units:
            expression += f'{unit}\n'
        for cable in self.cables:
            expression += f'{cable}\n'
        return expression

if __name__ == '__main__':
    net = Network()
    net.generateBasicNetwork([{'numberNewUnits': 3, 'unit':{'power': lambda: random.random(), 'tag': lambda: 'DEVICE'}, 'cable':{'length': lambda: random.random()+1}}, {'numberNewUnits': 3, 'unit':{'power': lambda: random.random()+1}, 'cable':{'length': lambda: random.random()}}])
    print(net)
    print(net.toNeo4j())

