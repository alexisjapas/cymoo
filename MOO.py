import random
from math import sqrt
import os
from dotenv import load_dotenv
from matplotlib import pyplot as plt, image as mpimg
import imageio
import io
from PIL import Image
import numpy

from Neo4jConnector import Neo4jConnector
from Task import Task
from NSGA2 import NSGA2
from Fourmi import Fourmi
from Network import Network


load_dotenv()


class MOO:
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, optimizer, nSolutions, minDepth, maxDepth):
        self.problem = problem
        self.optimizer = optimizer(problem, nSolutions, minDepth, maxDepth)


    def optimize(self, nIter, **kwargs):
        def _create_frame(t, maxX, maxY, maxZ):
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.set_xlim3d(0, maxX)
            ax.set_ylim3d(0, maxY)
            ax.set_zlim3d(0, maxZ)
            ax.set_xlabel("Processing time (s)")
            ax.set_ylabel("Cost (€)")
            ax.set_zlabel("Pollution (gCO2)")

            ax.scatter(*tuple([sol.solution[i] for sol in self.optimizer.solutions] for i in range(len(self.problem.optimDirections))))

            plt.title(f'Iteration n°{t}', fontsize=14)
            imgBuf = io.BytesIO()
            plt.savefig(imgBuf, transparent = False, facecolor = 'white')
            im = Image.open(imgBuf)
            im = numpy.array(im)
            imgBuf.close()
            plt.close()
            return im

        # optimisation
        maxX, maxY, maxZ = tuple(max([sol.solution[i] for sol in self.optimizer.solutions]) for i in range(len(self.problem.optimDirections)))
        frames = []
        n = 1
        while n <= nIter:
            print(f"Iteration n°{n}")
            frames.append(_create_frame(n, maxX, maxY, maxZ))
            self.optimizer.optimize(**kwargs)
            n += 1

        imageio.mimsave("./img/test.gif", frames, fps=1)

        for sol in set([tuple(sol.parameters[0]) for sol in self.optimizer.solutions]):
            print(list(map(lambda x: tuple(x.parameters[0]),self.optimizer.solutions)).count(sol))


if __name__ == "__main__":
    from matplotlib import pyplot as plt


    task = Task(100000, 100)
    problem = Network('DEVICE', task, ["min", "min", "min"], mutationRate=1)

    paramsLayerOne = {
        'unit': {
            'tag': 'DEVICE',
            'computingSpeed': lambda: random.randint(5,10),
            'positionX': 0,
            'positionY': 0,
            'throughput': .5,
            'pollution': lambda: round(random.random(),2),
            'cost': lambda: round(random.random(),2),
        },
        'cable': {
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX,2)+pow(x.positionY-y.positionY,2)),
            'propagationSpeed': lambda: 1,
            'flowRate': lambda: 1,
        },
        'numberNewUnits': 10
    }

    paramsLayerTwo = {
        'unit': {
            'tag': 'FOG',
            'computingSpeed': lambda x: x.computingSpeed*random.randint(5,10),
            'positionX': lambda x: x.positionX+random.randint(-2,2),
            'positionY': lambda x: x.positionY+random.randint(-2,2),
            'throughput': lambda x: x.throughput*round(random.random(),2)*2+1,
            'pollution': lambda x: (x.pollution+1)*(round(random.random(),2)+1),
            'cost': lambda x: (x.cost+1)*(round(random.random(),2)+1),
        },
        'cable': {
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX,2)+pow(x.positionY-y.positionY,2)),
            'propagationSpeed': lambda: 2,
            'flowRate': lambda: 3,
        },
        'numberNewUnits': 20
    }

    paramsLayerThree = {
        'unit': {
            'tag': 'CLOUD',
            'computingSpeed': lambda x: x.computingSpeed*random.randint(50,100),
            'positionX': lambda x: x.positionX+random.randint(-5,5),
            'positionY': lambda x: x.positionY+random.randint(-5,5),
            'throughput': lambda x: x.throughput*round(random.random(),2)*3+1,
            'pollution': lambda x: (x.pollution+1)*(round(random.random(),2)+1),
            'cost': lambda x: (x.cost+1)*(round(random.random(),2)+1),
        },
        'cable': {
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX,2)+pow(x.positionY-y.positionY,2)),
            'propagationSpeed': lambda: 2,
            'flowRate': lambda: 3,
        },
        'numberNewUnits': 10
    }

    problem.generate_basic_network([paramsLayerOne, paramsLayerTwo, paramsLayerThree])

    #### NSGA2 OPTIMIZATION
    optimizer = Fourmi

    moo = MOO(problem, optimizer, 100, 10, 50)
    moo.optimize(10, ratioKept=0.5)

