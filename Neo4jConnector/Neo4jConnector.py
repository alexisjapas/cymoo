from http.client import SERVICE_UNAVAILABLE
import logging
from neo4j import GraphDatabase, Neo4jDriver

class Neo4jConnector:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def run(self, query, **kargs):
        with self.driver.session(database=self.database) as session:
            result = session.execute_read(self.gen_static_method(query), **kargs)
            return result

    @staticmethod   
    def staticmethod(tx, query, **kargs):
        result = tx.run(query, kargs)
        try:
            return [row for row in result]
        except SERVICE_UNAVAILABLE as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def gen_static_method(self, query):
        return lambda tx, **kargs: self.staticmethod(tx, query, **kargs)

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()

    a = Neo4jConnector(os.environ['NEO4J_URI'], os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'], os.environ['NEO4J_DATABASE'])
    b = a.run("MATCH (n:Person {name:$name})-[:Poto]->(p:Person {name:'Elie'}) RETURN n, p", name="Alexis")

    for i in b:
        print(i)
        
    a.close()
