from Neo4jConnector import Neo4jConnector
from Network import Network
import random
import os
from dotenv import load_dotenv
import time
from math import sqrt
load_dotenv()

if __name__ == "__main__":

    a = Neo4jConnector(os.environ['NEO4J_URI'], os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'], os.environ['NEO4J_DATABASE'])
    
    reseau = Network();

    paramsLayerOne = {  
        'unit':{
        'tag': 'DEVICE',
        'puissance': lambda: random.randint(25,100),
        'positionx': lambda: random.randint(-10,10),
        'positiony': lambda: random.randint(-10,10),
        'debitTraitement': lambda: .5,
        'pollution': lambda: 1,
        'cout': 1,
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
        'puissance': lambda: random.randint(25,100),
        'positionx': lambda x: x.positionx+random.randint(-1,1),
        'positiony': lambda: random.randint(-10,10),
        'debitTraitement': lambda: .5,
        'pollution': lambda: 1,
        'cout': lambda: 1,
        },
        'cable':{
        'vitesse': lambda: 1,
        'debit': lambda: 1,
        },
        'numberNewUnits': lambda: random.randint(0,3)
    }

    reseau.generateBasicNetwork([paramsLayerOne, paramsLayerOne, paramsLayerOne])


    query = reseau.toNeo4j()
    print(query)
    a.run(a.WRITE, query)
    a.close()

    print("DONE")