from Neo4jConnector import Neo4jConnector
import random
import os
from dotenv import load_dotenv
import time
from math import sqrt

from NSWGE import NSWGE
from Task import Task
from Network import Network


load_dotenv()


if __name__ == "__main__":

    a = Neo4jConnector(os.environ['NEO4J_URI'], os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'], os.environ['NEO4J_DATABASE'])

    task = Task(100000, 100)
    reseau = Network('DEVICE', task, ["min", "min", "min"], mutation_rate=1)

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
        'numberNewUnits': 5
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
        'numberNewUnits': 2
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
        'numberNewUnits': 2
    }

    reseau.generateBasicNetwork([paramsLayerOne, paramsLayerTwo, paramsLayerThree, paramsLayerTwo, paramsLayerThree])

    queries = []


    fourmi = NSWGE(reseau)

    q = fourmi.optimize(1000, 1000, 10, Task(1000000,100))
    for key1 in q:
        for key2 in q[key1]:
            queries.append(', (id'+str(key1)+')-[:WEIGHT {weight: '+str(q[key1][key2])+'}]->(id'+str(key2)+')\n')

    query = reseau.toNeo4j()
    query = query.replace(';', '')
    for quer in queries:
        query += quer
    query += ';'

    a.run(a.WRITE, query)
    a.close()

    print("DONE")
