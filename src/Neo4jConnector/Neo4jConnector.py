from http.client import SERVICE_UNAVAILABLE
import logging
from neo4j import GraphDatabase, Neo4jDriver


class Neo4jConnector:
    READ = 0
    WRITE = 1

    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def run(self, execution, query, **kargs):
        with self.driver.session(database=self.database) as session:
            exec_function = {self.WRITE: session.execute_write, self.READ: session.execute_read}

            if execution in exec_function.keys():
                return exec_function[execution](self.gen_static_method(query), **kargs)
            else:
                logging.error("Invalid Execution")
                return []

    @staticmethod
    def staticmethod(tx, query, **kargs):
        result = tx.run(query, kargs)
        try:
            return [row for row in result]
        except SERVICE_UNAVAILABLE as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise

    def gen_static_method(self, query):
        return lambda tx, **kargs: self.staticmethod(tx, query, **kargs)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    a = Neo4jConnector(
        os.environ["NEO4J_URI"], os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"], os.environ["NEO4J_DATABASE"]
    )
    c = a.run(a.WRITE, "CREATE (n:Person {name:$name})", name="Michel")
    b = a.run(a.READ, "MATCH (n:Person {name:$name})-[:Poto]->(p:Person {name:'Elie'}) RETURN n, p", name="Alexis")

    print(c)
    for i in b:
        print(i)

    a.close()
