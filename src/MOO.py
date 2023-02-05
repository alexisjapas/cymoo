import random
from math import sqrt
import os
from dotenv import load_dotenv
from matplotlib import pyplot as plt, image as mpimg
import imageio
import io
from PIL import Image
import numpy
from tqdm import tqdm
from time import sleep

from Neo4jConnector import Neo4jConnector
from Task import Task
from NSGA2 import NSGA2
from NSWGE import NSWGE
from Network import Network


load_dotenv()


class MOO:
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, optimizer, nSolutions):
        self.problem = problem
        self.optimizer = optimizer(problem, nSolutions)


    def optimize(self, nIter, **kwargs):
        print(f"Optimizing with {self.optimizer}...")
        def _create_frame(t, pareto: bool, maxX, maxY, maxZ):
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")

            if pareto:
                maxX, maxY, maxZ = tuple(max([sol.solution[i] for sol in self.optimizer.pareto_solutions]) for i in range(len(self.problem.optimDirections)))
                values = tuple([sol.solution[i] for sol in self.optimizer.pareto_solutions] for i in range(len(self.problem.optimDirections)));
                ax.scatter(*values)
                plt.title(f'{self.optimizer} - Pareto optimums: {len(values[0])} values\nIteration n°{t}', fontsize=12)
            else:
                ax.scatter(*tuple([sol.solution[i] for sol in self.optimizer.solutions] for i in range(len(self.problem.optimDirections))))
                plt.title(f'{self.optimizer} - All solutions\nIteration n°{t}', fontsize=12)

            ax.set_xlim3d(0, maxX)
            ax.set_ylim3d(0, maxY)
            ax.set_zlim3d(0, maxZ)
            ax.set_xlabel("Processing time (s)")
            ax.set_ylabel("Cost (€)")
            ax.set_zlabel("Pollution (gCO2)")

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
        pareto_frames = []
        for n in tqdm(range(1, nIter+1)):
            frames.append(_create_frame(n, False, maxX, maxY, maxZ))
            pareto_frames.append(_create_frame(n, True, maxX, maxY, maxZ))
            self.optimizer.optimize(**kwargs)

        # POST OPTI (NSWGE norm)
        self.optimizer.post_optimization()

        # Create GIF with frames of each iteration
        imageio.mimsave(f"../img/{self.optimizer}.gif", frames, fps=1)
        imageio.mimsave(f"../img/{self.optimizer}_pareto.gif", pareto_frames, fps=1)

        # Display final solutions and count
        print("Displaying pareto solutions...")
        for sol in self.optimizer.pareto_solutions:
            print(sol.parameters[0])
            sleep(0.2)
        print()

        return self.optimizer.pareto_solutions


    @staticmethod
    def relative_efficiency(X, Y, optimDirections):
        """
        Number of solutions of X undominated by Y solutions.
        """
        undominatedValues = X.copy()
        for x in X:
            for y in Y:
                if all([y.solution[i] < x.solution[i] if opti_dir == 'min' else y.solution[i] > x.solution[i] for i, opti_dir in enumerate(optimDirections)]):
                    while x in undominatedValues:
                        undominatedValues.remove(x)
                    break

        return len(undominatedValues) / len(X)


if __name__ == "__main__":
    from matplotlib import pyplot as plt


    #### PROBLEM DEFINITION
    task = Task(100000, 100)
    problem = Network('DEVICE', task=task,
                      optimDirections=["min", "min", "min"],
                      minDepth=10, maxDepth=20,
                      mutationRate=1)

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
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX, 2)+pow(x.positionY-y.positionY, 2)),
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
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX, 2) + pow(x.positionY-y.positionY, 2)),
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
            'distance': lambda x,y: sqrt(pow(x.positionX-y.positionX,2)+pow(x.positionY-y.positionY,2)),
            'propagationSpeed': lambda: 2,
            'flowRate': lambda: 3,
        },
        'numberNewUnits': 10
    }

    problem.generate_basic_network([paramsLayerOne, paramsLayerTwo, paramsLayerThree])

    #### OPTIMIZATION
    nIterations = 100
    nSolutions = 1000

    optimizer = NSGA2
    moo_nsga2 = MOO(problem, optimizer, nSolutions=nSolutions)
    nsga2_paretos = moo_nsga2.optimize(nIterations, ratioKept=0.5)

    optimizer = NSWGE
    moo_nswge = MOO(problem, optimizer, nSolutions=nSolutions)
    nswge_paretos = moo_nswge.optimize(nIterations)

    print(f"Relative efficiency: {round(MOO.relative_efficiency(nsga2_paretos, nswge_paretos, problem.optimDirections) * 100)}% of NSGA2 solutions are undominated by NSWGE solutions")
    print(f"Relative efficiency: {round(MOO.relative_efficiency(nswge_paretos, nsga2_paretos, problem.optimDirections) * 100)}% of NSWGE solutions are undominated by NSGA2 solutions")

