import random
from math import sqrt

from .MOO import MOO
from .optimizers.NSGA2 import NSGA2
from .optimizers.NSRA import NSRA
from .optimizers.NSWGE import NSWGE
from .problems.multitask_routing.Task import Task
from .problems.multitask_routing.Network import Network
from .problems.Solution import Solution


# PROBLEM DEFINITION
paramsLayerOne = {
    "unit": {
        "tag": "DEVICE",
        "computingSpeed": lambda: random.randint(5, 10),
        "positionX": 0,
        "positionY": 0,
        "throughput": 0.5,
        "pollution": lambda: round(random.random(), 2),
        "cost": lambda: round(random.random(), 2),
    },
    "cable": {
        "distance": lambda x, y: sqrt(pow(x.positionX - y.positionX, 2) + pow(x.positionY - y.positionY, 2)),
        "propagationSpeed": lambda: 1,
        "flowRate": lambda: 1,
    },
    "numberNewUnits": 2,
}

paramsLayerTwo = {
    "unit": {
        "tag": "FOG",
        "computingSpeed": lambda x: x.computingSpeed * random.randint(5, 10),
        "positionX": lambda x: x.positionX + random.randint(-2, 2),
        "positionY": lambda x: x.positionY + random.randint(-2, 2),
        "throughput": lambda x: x.throughput * round(random.random(), 2) * 2 + 1,
        "pollution": lambda x: (x.pollution + 1) * (round(random.random(), 2) + 1),
        "cost": lambda x: (x.cost + 1) * (round(random.random(), 2) + 1),
    },
    "cable": {
        "distance": lambda x, y: sqrt(pow(x.positionX - y.positionX, 2) + pow(x.positionY - y.positionY, 2)),
        "propagationSpeed": lambda: 2,
        "flowRate": lambda: 3,
    },
    "numberNewUnits": 2,
}

paramsLayerThree = {
    "unit": {
        "tag": "CLOUD",
        "computingSpeed": lambda x: x.computingSpeed * random.randint(50, 100),
        "positionX": lambda x: x.positionX + random.randint(-5, 5),
        "positionY": lambda x: x.positionY + random.randint(-5, 5),
        "throughput": lambda x: x.throughput * round(random.random(), 2) * 3 + 1,
        "pollution": lambda x: (x.pollution + 1) * (round(random.random(), 2) + 1),
        "cost": lambda x: (x.cost + 1) * (round(random.random(), 2) + 1),
    },
    "cable": {
        "distance": lambda x, y: sqrt(pow(x.positionX - y.positionX, 2) + pow(x.positionY - y.positionY, 2)),
        "propagationSpeed": lambda: 2,
        "flowRate": lambda: 3,
    },
    "numberNewUnits": 2,
}

tasks = tuple(Task(random.randint(1, 1000), random.randint(1, 1000)) for _ in range(3))

problem = Network(
    "DEVICE",
    tasks=tasks,
    optimDirections={"processingTime": "min", "cost": "min", "pollution": "min"},
    minDepth=10,
    maxDepth=20,
    mutationRate=0.1,
    layers=[paramsLayerOne, paramsLayerTwo, paramsLayerThree],
)

# OPTIMIZATION
nIterations = 100
nSolutions =1500
seed = 10

moo = MOO(problem)

nsga2_paretos = moo.optimize(NSGA2, nSolutions, nIterations, seed=seed, ratioKept=0.5, saveDir="imgs")
nswge_paretos = moo.optimize(NSWGE, nSolutions, nIterations, seed=seed, saveDir="imgs")
nsra_paretos = moo.optimize(NSRA, nSolutions, nIterations, seed=seed, ratioKept=0.5, saveDir="imgs")

# nswge_paretos = moo.optimize(NSWGE, nSolutions, nIterations, seed=seed)

# DISPLAYING RESULTS
MOO.relative_efficiency(nsra_paretos, nsga2_paretos, Solution.optimDirections, verbose=True)
MOO.relative_efficiency(nsra_paretos, nswge_paretos, Solution.optimDirections, verbose=True)
MOO.relative_efficiency(nsga2_paretos, nswge_paretos, Solution.optimDirections, verbose=True)


