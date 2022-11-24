import json
import os
from neo4j import GraphDatabase
from datetime import datetime

def read_jsonl(fpath):
    with open(fpath,"r") as f:
        data = f.read().split("\n")[:-1]
    data = list(map(lambda a:json.loads(a),data))
    return data

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

class KGBuilder:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    @staticmethod
    def _create_zip_nodes(tx,d):
        d_str = make_d_str(d)
        query_str = f"CREATE (z1:ZIPNode {d_str})"
        tx.run(query_str)

    @staticmethod
    def _create_city_nodes(tx,d):
        d_str = make_d_str(d)
        query_str = f"CREATE (c1:CityNode {d_str})"
        tx.run(query_str)

    @staticmethod
    def _create_attraction_nodes(tx,d):
        d_str = make_d_str(d)
        query_str = f"CREATE (a1:AttractionNode {d_str})"
        tx.run(query_str)

    @staticmethod
    def _create_restaurant_nodes(tx,d):
        d_str = make_d_str(d)
        query_str = f"CREATE (z1:RestaurantNode {d_str})"
        tx.run(query_str)

    @staticmethod
    def _create_nearby_zip_edges(tx,z1,z2):
        query_str = "MATCH (z1:ZIPNode{zip_code:"+ str(z1) + "}),(z2:ZIPNode{zip_code: "+ str(z2) + "}) MERGE (z1)-[:Nearby]->(z2)"
        tx.run(query_str)

    @staticmethod
    def _create_city_edges(tx, z, c):
        query_str = "MATCH (z:ZIPNode{zip_code:"+ str(z) + "}),(c:CityNode{city_name: '"+ str(c) + "'}) MERGE (z)-[:InCity]->(c)"
        tx.run(query_str)

    @staticmethod
    def _create_attraction_edges(tx,z,a):
        query_str = "MATCH (z:ZIPNode{zip_code:"+ str(z) + "}),(a:AttractionNode{attraction_name: '"+ str(a) + "'}) MERGE (z)-[:HasAttraction]->(a)"
        tx.run(query_str)

    @staticmethod
    def _create_restaurant_edges(tx,z,r,nr,ar):
        query_str = "MATCH (z:ZIPNode{zip_code:"+ str(z) + "}),(r:RestaurantNode{restaurant_name: '"+ str(r) + "' , n_reviews: " + str(nr) + ", average_rating: " + str(ar) + "}) MERGE (z)-[:HasRestaurant]->(r)"
        tx.run(query_str)


    def create_zip_nodes(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            d["nearby_zip_codes"]  = list(map(int,d["nearby_zip_codes"]))
            with self.driver.session() as session:
                session.execute_write(self._create_zip_nodes,d)

    def create_city_nodes(self, f):
        fdata = read_jsonl(f)
        cities = {one["city"] for one in fdata}
        city_d = [{"city_name":city} for city in cities]
        for d in city_d:
            with self.driver.session() as session:
                session.execute_write(self._create_city_nodes,d)

    def create_attraction_nodes(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:    
            with self.driver.session() as session:
                session.execute_write(self._create_attraction_nodes,d)

    def create_restaurant_nodes(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:    
            with self.driver.session() as session:
                session.execute_write(self._create_restaurant_nodes,d)

    def create_nearby_zip_edges(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            base_zip, nearby_zips = int(d["zip_code"]), d["nearby_zip_codes"]
            nearby_zips = list(map(int,nearby_zips))
            for nearby_zip in nearby_zips:
                with self.driver.session() as session:
                    session.execute_write(self._create_nearby_zip_edges,base_zip,nearby_zip)

    def create_city_edges(self, f):
        fdata = read_jsonl(f)

        for d in fdata:
            z,c = int(d["zip_code"]),d["city"]
            with self.driver.session() as session:
                session.execute_write(self._create_city_edges,z,c)

    def create_attraction_edges(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            zip, attraction = d["zip_code"], d["attraction_name"].replace("'","")
            with self.driver.session() as session:
                session.execute_write(self._create_attraction_edges, zip, attraction)

    def create_restaurant_edges(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            zip, restaurant, n_reviews, average_rating = d["zip_code"], d["restaurant_name"].replace("'",""), d["n_reviews"], d["average_rating"]
            n_reviews = n_reviews if n_reviews else "Unknown"
            average_rating = average_rating if average_rating else "Unknown"
            with self.driver.session() as session:
                session.execute_write(self._create_restaurant_edges, zip, restaurant, n_reviews, average_rating)
            

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"

zip_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "zip_code_data.jsonl")
tripadvisor_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "tripadvisor_data.jsonl")
yelp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "yelp_data.jsonl")

builder = KGBuilder(uri, user, password)
print("Initialized",datetime.now().time())
builder.create_zip_nodes(zip_file)
print("Zip nodes created",datetime.now().time())
builder.create_attraction_nodes(tripadvisor_file)
print("Attraction nodes created",datetime.now().time())
builder.create_city_nodes(zip_file)
print("City nodes created",datetime.now().time())
builder.create_restaurant_nodes(yelp_file)
print("Restauarant nodes created",datetime.now().time())
builder.create_nearby_zip_edges(zip_file)
print("Nearby relations created",datetime.now().time())
builder.create_city_edges(zip_file)
print("City relations created",datetime.now().time())
builder.create_attraction_edges(tripadvisor_file)
print("Atrraction relations created",datetime.now().time())
builder.create_restaurant_edges(yelp_file)
print("Restaurant relations created",datetime.now().time())
builder.close()