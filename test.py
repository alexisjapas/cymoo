from Neo4jConnector import Neo4jConnector
import os
from dotenv import load_dotenv
load_dotenv()

a = Neo4jConnector(os.environ['NEO4J_URI'], os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'], os.environ['NEO4J_DATABASE'])

b = a.run("MATCH (n:Person {name:$name})-[:Poto]->(p:Person {name:'Elie'}) RETURN n, p", name="Alexis")

for i in b:
    print(i)
