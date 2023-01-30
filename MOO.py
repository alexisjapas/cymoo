from Neo4jConnector import Neo4jConnector
from Task import Task
from NSGA2 import NSGA2
from Network import Network
import random
from math import sqrt
import os
from dotenv import load_dotenv

load_dotenv()

class MOO:
    def __init__(self, problem, optimizer, n_solutions, minDepth, maxDepth):
        self.problem = problem
        self.optimizer = optimizer(problem,n_solutions, minDepth, maxDepth)
        self.population = problem.populate(n_solutions, minDepth, maxDepth)

    def plot(self):
        pass

    def optimize(self, optimizer, n_iter, **kwargs):
        while n_iter > 0:
            optimizer.optimize(self.population, **kwargs)


if __name__ == "__main__":
    task = Task(1000, 10)
    problem = Network('DEVICE', task)

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
        'numberNewUnits': 2
    }

    paramsLayerTwo = {  
        'unit':{
        'tag': 'FOG',
        'puissance': lambda x: x.puissance*random.randint(5,10),
        'positionx': lambda x: x.positionx+random.randint(-1,1),
        'positiony': lambda x: x.positiony+random.randint(-1,1),
        'debitTraitement': lambda x: x.debitTraitement*round(random.random(),2)+1,
        'pollution': lambda x: (x.pollution+1)*(round(random.random(),2)+1),
        'cost': lambda x: (x.cost+1)*(round(random.random(),2)+1),
        },
        'cable':{
        'distance': lambda x,y: sqrt(pow(x.positionx-y.positionx,2)+pow(x.positiony-y.positiony,2)),
        'vitesse': lambda: 2,
        'debit': lambda: 3,
        },
        'numberNewUnits': 2
    }

    problem.generateBasicNetwork([paramsLayerOne, paramsLayerTwo])
    
    optimizer = NSGA2
    
    moo = MOO(problem, optimizer, 1000, 2, 3)
    # moo.optimize(optimizer, 100, ratio_kept=0.5)

