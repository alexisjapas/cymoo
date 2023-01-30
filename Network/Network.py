from .Unit import Unit
from .Cable import Cable
from .Path import Path
import uuid
import random

class Network():
    def __init__(self, startTag, task) -> None:
        self.units = []
        self.cables = []
        self.startTag = startTag
        self.task = task
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
            print(numberNewUnits)
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

    def populate(self, nSolution: int, minDepth: int, maxDepth: int): ## TODO: Add tache cast
        solutions = []
        for _ in range(nSolution):
            solutions.append(self.generatePath(random.randint(minDepth, maxDepth)).toSolution(self.task))
        return solutions

    def generatePath(self, maxDepth: int):
        starting = random.choice([unit for unit in self.units if unit.tag == self.startTag])
        
        def recursiveGeneratePath(unit: Unit, depth: int, path: Path):
            if depth == maxDepth:
                return path
            cable = random.choice(unit.cables)
            path.addUnit(unit)
            path.addCable(cable)
            return recursiveGeneratePath(cable.getOtherUnit(unit), depth+1, path)

        return recursiveGeneratePath(starting, 0, Path())

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
        
        

        

