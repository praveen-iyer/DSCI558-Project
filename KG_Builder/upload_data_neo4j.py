import json
import os
from neo4j import GraphDatabase

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
            v = int(v)
        if k=="average_rating":
            v = float(v)
        
        if  type(v)==str:
            l.append(f"""{k}:'{v}'""")
        else:
            l.append(f"""{k}:{v}""")
    return "{" + " , ".join(l) + "}"

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
        query_str = "MATCH (z1:ZIPNode{zip_code:"+ str(z1) + "}),(z2:ZIPNode{zip_code: "+ str(z2) + "}) MERGE (n1)-[:Nearby]->(n2)"
        tx.run(query_str)

    @staticmethod
    def _create_attraction_edges(tx,z,a):
        query_str = "MATCH (z:ZIPNode{zip_code:"+ str(z) + "}),(a:AttractionNode{attraction_name: '"+ str(a) + "'}) MERGE (z)-[:HasAttraction]->(a)"
        tx.run(query_str)

    @staticmethod
    def _create_restaurant_edges(tx,z,r,nr,ar):
        query_str = "MATCH (z:ZIPNode{zip_code:"+ str(z) + "}),(r:RestaurantNode{restaurant_name: '"+ str(r) + "' , n_reviews: " + str(nr) + ", average_rating: " + str(ar) + "}) MERGE (z)-[:HasRestaurant]->(a)"
        tx.run(query_str)


    def create_zip_nodes(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:    
            with self.driver.session() as session:
                session.execute_write(self._create_zip_nodes,d)

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
            base_zip, nearby_zips = d["zip_code"], d["nearby_zip_codes"]
            for nearby_zip in nearby_zips:
                with self.driver.session() as session:
                    session.execute_write(self._create_nearby_zip_edges,base_zip,nearby_zip)

    def create_attraction_edges(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            zip, attraction = d["zip_code"], d["attraction_name"]
            with self.driver.session() as session:
                session.execute_write(self._create_attraction_edges, zip, attraction)

    def create_restaurant_edges(self, f):
        fdata = read_jsonl(f)
        
        for d in fdata:
            zip, restaurant, n_reviews, average_rating = d["zip_code"], d["restaurant_name"], d["n_reviews"], d["average_rating"]
            with self.driver.session() as session:
                session.execute_write(self._create_restaurant_edges, zip, restaurant, n_reviews, average_rating)
            

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = ""

zip_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "zip_code_data.jsonl")
tripadvisor_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "tripadvisor_data.jsonl")
yelp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_scraper", "yelp_data.jsonl")

builder = KGBuilder(uri, user, password)
builder.create_zip_nodes(zip_file)
builder.create_attraction_nodes(tripadvisor_file)
builder.create_restaurant_nodes(yelp_file)
builder.create_nearby_zip_edges(zip_file)
builder.create_attraction_edges(tripadvisor_file)
builder.create_restaurant_edges(yelp_file)
builder.close()