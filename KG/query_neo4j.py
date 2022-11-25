from neo4j import GraphDatabase

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"

class KGQuerier:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_restuarants_near_attraction(self, attraction_name):
        query_str = f"""MATCH (z)-[:HasAttraction]->(:AttractionNode{{attraction_name: "{attraction_name}"}})
        MATCH (z)-[:Nearby]->(nz) MATCH (nz)-[:HasRestaurant]->(r)
        RETURN r.restaurant_name"""

        restaurants =  self.query(query_str)
        restaurants = list(map(lambda a:a["r.restaurant_name"],restaurants))
        return restaurants
    
    def query(self, query_str):
        with self.driver.session() as session:
            response = list(session.run(query_str))
        return response

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
querier = KGQuerier(uri, user, password)

nearby_restaurants = querier.get_restuarants_near_attraction("Redwood National Park")
print(nearby_restaurants)
querier.close()