from Neo4jConnector import Neo4jConnector
from graph import Network
import random
import os
from dotenv import load_dotenv
import time
load_dotenv()

if __name__ == "__main__":

    a = Neo4jConnector(os.environ['NEO4J_URI'], os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'], os.environ['NEO4J_DATABASE'])
    
    reseau = Network();

    paramsLayerOne = {
        'puissance': lambda: random.randint(1,10),
        'position': lambda: (random.randint(-10,10),random.randint(-10,10)),
        'debitTraitement': lambda: 1,
        'pollution': lambda: 1,
        'cout': lambda: 1,
        'vitesse': lambda: 1,
        'debit': lambda: 1,
        'nNextLayer': lambda: random.randint(0,3)
    }

    paramsLayerTwo = {
        'puissance': lambda: random.randint(25,100),
        'position': lambda: (random.randint(-10,10),random.randint(-10,10)),
        'debitTraitement': lambda: .5,
        'pollution': lambda: 1,
        'cout': lambda: 1,
        'vitesse': lambda: 1,
        'debit': lambda: 1,
        'nNextLayer': lambda: random.randint(0,3)
    }

    reseau.generateSimpleStructure(1, [paramsLayerOne, paramsLayerTwo, paramsLayerOne])

    for i in reseau.devices:
        print(i)
    for i in reseau.cables:
        print(i)

    query = reseau.uploadToNeo4J()
    a.run(a.WRITE, query)
    a.close()

    print("DONE")