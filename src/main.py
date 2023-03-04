import random
from math import sqrt

from MOO import MOO
from optimizers.NSGA2 import NSGA2
from optimizers.NSWGE import NSWGE
from optimizers.NSRA import NSRA
from problems.network.Task import Task
from problems.network.Network import Network

from problems.Solution import Solution


# PROBLEM DEFINITION
task = Task(100000, 100)

paramsLayerOne = {
    'unit': {
        'tag': 'DEVICE',
        'computingSpeed': lambda: random.randint(5, 10),
        'positionX': 0,
        'positionY': 0,
        'throughput': .5,
        'pollution': lambda: round(random.random(), 2),
        'cost': lambda: round(random.random(), 2),
    },
    'cable': {
        'distance': lambda x, y: sqrt(pow(x.positionX-y.positionX, 2)+pow(x.positionY-y.positionY, 2)),
        'propagationSpeed': lambda: 1,
        'flowRate': lambda: 1,
    },
    'numberNewUnits': 10
}

paramsLayerTwo = {
    'unit': {
        'tag': 'FOG',
        'computingSpeed': lambda x: x.computingSpeed*random.randint(5, 10),
        'positionX': lambda x: x.positionX + random.randint(-2, 2),
        'positionY': lambda x: x.positionY + random.randint(-2, 2),
        'throughput': lambda x: x.throughput * round(random.random(), 2) * 2 + 1,
        'pollution': lambda x: (x.pollution + 1) * (round(random.random(), 2) + 1),
        'cost': lambda x: (x.cost + 1) * (round(random.random(), 2) + 1),
    },
    'cable': {
        'distance': lambda x, y: sqrt(pow(x.positionX-y.positionX, 2) + pow(x.positionY-y.positionY, 2)),
        'propagationSpeed': lambda: 2,
        'flowRate': lambda: 3,
    },
    'numberNewUnits': 20
}

paramsLayerThree = {
    'unit': {
        'tag': 'CLOUD',
        'computingSpeed': lambda x: x.computingSpeed * random.randint(50, 100),
        'positionX': lambda x: x.positionX + random.randint(-5, 5),
        'positionY': lambda x: x.positionY + random.randint(-5, 5),
        'throughput': lambda x: x.throughput * round(random.random(), 2) * 3 + 1,
        'pollution': lambda x: (x.pollution + 1) * (round(random.random(), 2) + 1),
        'cost': lambda x: (x.cost + 1) * (round(random.random(), 2) + 1),
    },
    'cable': {
        'distance': lambda x, y: sqrt(pow(x.positionX-y.positionX, 2)+pow(x.positionY-y.positionY, 2)),
        'propagationSpeed': lambda: 2,
        'flowRate': lambda: 3,
    },
    'numberNewUnits': 10
}

problem = Network('DEVICE', task=task,
                  optimDirections={"processingTime": "min",
                                   "cost": "min",
                                   "pollution": "min"},
                  minDepth=10, maxDepth=20,
                  mutationRate=0.1,
                  layers=[paramsLayerOne, paramsLayerTwo, paramsLayerThree])

# OPTIMIZATION
nIterations = 100
nSolutions = 1000
seed = 11


moo = MOO(problem)

nsga2_paretos = moo.optimize(NSGA2, nSolutions, nIterations, seed=seed, ratioKept=0.5)
#nswge_paretos = moo.optimize(NSWGE, nSolutions, nIterations, seed=seed)


# DISPLAYING RESULTS
#MOO.relative_efficiency(nswge_paretos, nsga2_paretos, Solution.optimDirections, verbose=True)
