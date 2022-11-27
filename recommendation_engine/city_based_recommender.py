import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),"KG"))
from query_neo4j import KGQuerier

attractions_file = yelp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","tripadvisor_linked_data.jsonl")

restaurants_file = yelp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","yelp_data_with_amenity_flags.jsonl")

def get_entity_info(fdata, name, zip_code = None, entity_type = "restaurant"):
    k = "restaurant_name" if entity_type=="restaurant" else "attraction_name"
    if zip_code:
        for d in fdata:
            if d[k]== name and int(d["zip_code"]) == zip_code:
                return d
    else:
        for d in fdata:
            if d[k]== name:
                return d

def get_top_attractions_from_city(city_name):
    uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
    user = "neo4j"
    password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
    querier = KGQuerier(uri, user, password)

    attractions_with_zip_in_city = querier.get_attractions_with_zip_from_city(city_name)

    with open(attractions_file,"r") as f:
        fdata = f.read().split("\n")[:-1]
    fdata = list(map(lambda a:json.loads(a),fdata))

    attraction_data = []
    for attraction_with_zip in attractions_with_zip_in_city:
        info = get_entity_info(fdata, *attraction_with_zip, entity_type = "attraction")
        attraction_data.append(info)
    
    attraction_data = sorted(attraction_data,key=lambda a:(-int(a["expert_recommended"]=="Yes"), -a["attraction_rating"], -a["attraction_n_reviews"]))

    attraction_data = attraction_data[:min(5,len(attraction_data))]

    return attraction_data

def get_top_restaurants_from_city(city_name,flag_d):
    uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
    user = "neo4j"
    password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
    querier = KGQuerier(uri, user, password)

    restaurants_with_zip_in_city = querier.get_restaurants_with_zip_from_city(city_name, flag_d)

    with open(restaurants_file,"r") as f:
        fdata = f.read().split("\n")[:-1]
    fdata = list(map(lambda a:json.loads(a),fdata))

    restaurant_data = []
    for restaurant_with_zip in restaurants_with_zip_in_city:
        info = get_entity_info(fdata, *restaurant_with_zip, entity_type = "restaurant")
        restaurant_data.append(info)
    
    restaurant_data = sorted(restaurant_data,key=lambda a:(-float(a["average_rating"]), -int(a["n_reviews"])))

    restaurant_data = restaurant_data[:min(5,len(restaurant_data))]

    return restaurant_data