from Neo4jConnector import Neo4jConnector
from Task import Task
from NSGA2 import NSGA2
from Network import Network
import random
from math import sqrt
import os
from dotenv import load_dotenv
from matplotlib import pyplot as plt, image as mpimg
import imageio
import io
from PIL import Image
import numpy

load_dotenv()

class MOO:
    def __init__(self, problem, optimizer, n_solutions, minDepth, maxDepth):
        self.problem = problem
        self.optimizer = optimizer(problem,n_solutions, minDepth, maxDepth)

    def optimize(self, n_iter, **kwargs):
        def _create_frame(t, max_x, max_y, max_z):
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.set_xlim3d(0, max_x)
            ax.set_ylim3d(0, max_y)
            ax.set_zlim3d(0, max_z)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Cost (€)")
            ax.set_zlabel("Pollution (gCO2)")
            ax.yaxis.set_ticks_position("left")

            ax.scatter(*tuple([sol.solution[i] for sol in self.optimizer.solutions] for i in range(len(self.problem.optim_directions))))

            plt.title(f'Iteration n°{t}', fontsize=14)
            img_buf = io.BytesIO()
            plt.savefig(img_buf, transparent = False, facecolor = 'white')
            im = Image.open(img_buf)
            im = numpy.array(im)
            img_buf.close()
            plt.close()
            return im

        # optimisation
        max_x, max_y, max_z = tuple(max([sol.solution[i] for sol in self.optimizer.solutions]) for i in range(len(self.problem.optim_directions)))
        frames = []
        n = 1
        while n <= n_iter:
            print(f"Iteration n°{n}")
            frames.append(_create_frame(n, max_x, max_y, max_z))
            self.optimizer.optimize(**kwargs)
            n += 1

        imageio.mimsave("./img/test.gif", frames, fps = 1)

        for sol in set([tuple(sol.parameters[0]) for sol in self.optimizer.solutions]):
            print(list(map(lambda x: tuple(x.parameters[0]),self.optimizer.solutions)).count(sol))


if __name__ == "__main__":
    from matplotlib import pyplot as plt


    task = Task(100000, 100)
    problem = Network('DEVICE', task, ["min", "min", "min"], mutation_rate=1)

    paramsLayerOne = {
        'unit':{
        'tag': 'DEVICE',
        'puissance': lambda: random.randint(5,10),
        'positionx': 0,
        'positiony': 0,
        'debitTraitement': .5,
        'pollution': lambda: round(random.random(),2),
        'cost': lambda: round(random.random(),2),
        },
        'cable':{
        'distance': lambda x,y: sqrt(pow(x.positionx-y.positionx,2)+pow(x.positiony-y.positiony,2)),
        'vitesse': lambda: 1,
        'debit': lambda: 1,
        },
        'numberNewUnits': 10
    }

    paramsLayerTwo = {
        'unit':{
        'tag': 'FOG',
        'puissance': lambda x: x.puissance*random.randint(5,10),
        'positionx': lambda x: x.positionx+random.randint(-2,2),
        'positiony': lambda x: x.positiony+random.randint(-2,2),
        'debitTraitement': lambda x: x.debitTraitement*round(random.random(),2)*2+1,
        'pollution': lambda x: (x.pollution+1)*(round(random.random(),2)+1),
        'cost': lambda x: (x.cost+1)*(round(random.random(),2)+1),
        },
        'cable':{
        'distance': lambda x,y: sqrt(pow(x.positionx-y.positionx,2)+pow(x.positiony-y.positiony,2)),
        'vitesse': lambda: 2,
        'debit': lambda: 3,
        },
        'numberNewUnits': 20
    }

    paramsLayerThree = {
        'unit':{
        'tag': 'CLOUD',
        'puissance': lambda x: x.puissance*random.randint(50,100),
        'positionx': lambda x: x.positionx+random.randint(-5,5),
        'positiony': lambda x: x.positiony+random.randint(-5,5),
        'debitTraitement': lambda x: x.debitTraitement*round(random.random(),2)*3+1,
        'pollution': lambda x: (x.pollution+1)*(round(random.random(),2)+1),
        'cost': lambda x: (x.cost+1)*(round(random.random(),2)+1),
        },
        'cable':{
        'distance': lambda x,y: sqrt(pow(x.positionx-y.positionx,2)+pow(x.positiony-y.positiony,2)),
        'vitesse': lambda: 2,
        'debit': lambda: 3,
        },
        'numberNewUnits': 10
    }

    problem.generateBasicNetwork([paramsLayerOne, paramsLayerTwo, paramsLayerThree])

    optimizer = NSGA2

    moo = MOO(problem, optimizer, 100, 10, 50)
    moo.optimize(10, ratio_kept=0.5)

