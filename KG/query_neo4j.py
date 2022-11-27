from neo4j import GraphDatabase

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"

def make_d_str(d):
    l = []
    for k,v in d.items():
        
        if v is None:
            v = "Unknown"
        if k=="n_reviews" or k=="zip_code":
            if not v:
                v = -1
            v = int(v)
        if k=="average_rating":
            if not v:
                v = "Unknown"
            v = float(v)
        
        if  type(v)==str:
            v = v.replace("'","")
            l.append(f"""{k}:'{v}'""")
        else:
            l.append(f"""{k}:{v}""")
    return ("{" + " , ".join(l) + "}")

class KGQuerier:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_restuarants_near_attraction(self, attraction_name):
        query_str = f"""MATCH (z)-[:HasAttraction]->(:AttractionNode{{attraction_name: "{attraction_name}"}})
        MATCH (z)-[:Nearby]->(nz) MATCH (nz)-[:HasRestaurant]->(r)
        RETURN r.restaurant_name, r.zip_code"""

        restaurants =  self.query(query_str)
        restaurants_with_zip = list(map(lambda a:(a["r.restaurant_name"],a["r.zip_code"]),restaurants))
        return restaurants_with_zip
    
    def get_all_attraction_names(self):
        query_str = f"""MATCH (n:AttractionNode)
        RETURN DISTINCT n.attraction_name"""
        
        attractions =  self.query(query_str)
        attractions = list(map(lambda a:a["n.attraction_name"], attractions))
        return attractions

    def get_all_restaurant_names(self):
        query_str = f"""MATCH (n:RestaurantNode)
        RETURN DISTINCT n.restaurant_name"""
        
        restaurants =  self.query(query_str)
        restaurants = list(map(lambda a:a["n.restaurant_name"], restaurants))
        return restaurants

    def get_all_city_names(self):
        query_str = f"""MATCH (n:CityNode)
        RETURN DISTINCT n.city_name"""
        
        cities =  self.query(query_str)
        cities = list(map(lambda a:a["n.city_name"], cities))
        return cities

    def get_attractions_with_zip_from_city(self,city_name):
        query_str = f"""MATCH (z)-[:InCity]-(c:CityNode{{city_name:"{city_name}"}})
        MATCH(z)-[:HasAttraction]->(a:AttractionNode)
        RETURN a.attraction_name, a.zip_code"""

        attractions_with_zip = self.query(query_str)
        attractions_with_zip = list(map(lambda a:(a["a.attraction_name"],a["a.zip_code"]),attractions_with_zip))
        return attractions_with_zip

    def get_restaurants_with_zip_from_city(self,city_name, flags_d):
        flags_str = make_d_str(flags_d)
        query_str = f"""MATCH (z)-[:InCity]-(c:CityNode{{city_name:"{city_name}"}})
        MATCH(z)-[:HasRestaurant]->(r:RestaurantNode{flags_str})
        RETURN r.restaurant_name, r.zip_code"""

        restaurants_with_zip = self.query(query_str)
        restaurants_with_zip = list(map(lambda a:(a["r.restaurant_name"],a["r.zip_code"]), restaurants_with_zip))
        return restaurants_with_zip
    
    def query(self, query_str):
        with self.driver.session() as session:
            response = list(session.run(query_str))
        return response

if __name__=="__main__":
    uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
    user = "neo4j"
    password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
    querier = KGQuerier(uri, user, password)

    nearby_restaurants = querier.get_restuarants_near_attraction("Redwood National Park")
    nearby_restaurants_with_zip = querier.get_restuarants_near_attraction("Gossamer Cellars")
    print(nearby_restaurants_with_zip)
    
    attractions = querier.get_all_attraction_names()
    print(len(attractions))
    
    restaurants = querier.get_all_restaurant_names()
    print(len(restaurants))
    
    querier.close()