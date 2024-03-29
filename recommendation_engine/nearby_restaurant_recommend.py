import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),"KG"))
from query_neo4j import KGQuerier

def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(set(list1)) + len(set(list2))) - intersection
    return 0 if union==0 else float(intersection) / union

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

def get_similarity_between_restaurants(restaurant_data, nearby_restaurant_data):
    c1 = restaurant_data["cuisine_list"] + ["INTERSECTOR"]*2
    c2 = nearby_restaurant_data["cuisine_list"] + ["INTERSECTOR"]*2

    ap1,aa1 = restaurant_data["amenities_present"], restaurant_data["amenities_absent"]
    ap2,aa2 = nearby_restaurant_data["amenities_present"], nearby_restaurant_data["amenities_absent"]

    s1 = jaccard_similarity(c1,c2)
    sp = jaccard_similarity(ap1,ap2)
    sa = jaccard_similarity(aa1,aa2)

    s = (4*s1 + sp + sa)/6
    return s

def get_highest_simalirity(restaurant,nearby_restaurants_with_zip, yelp_path):
    with open(yelp_path,"r") as f:
        fdata = f.read().split("\n")[:-1]
    fdata = list(map(lambda a:json.loads(a),fdata))

    restaurant_data = get_entity_info(fdata, restaurant,entity_type = "restaurant")

    similarities = []
    nearby_restaurants_data = []
    for nearby_restaurant_with_zip in nearby_restaurants_with_zip:
        nearby_restaurant_data = get_entity_info(fdata, *nearby_restaurant_with_zip,entity_type = "restaurant")
        nearby_restaurants_data.append(nearby_restaurant_data)
        similarity = get_similarity_between_restaurants(restaurant_data, nearby_restaurant_data)
        similarities.append(similarity)
    top_indices = sorted(range(len(similarities)), key = lambda i:-similarities[i])
    recommended_restauarants = [nearby_restaurants_data[ind] for ind in top_indices[:min(5,len(top_indices))]]
    return recommended_restauarants


def nearby_restaurant_recommendation_based_on_attraction(attraction, restaurant):
    uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
    user = "neo4j"
    password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
    yelp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","yelp_data_with_amenity_flags.jsonl")
    
    attraction, restaurant = attraction.replace("'",""), restaurant.replace("'","")


    querier = KGQuerier(uri, user, password)

    nearby_restaurants_with_zip = querier.get_restuarants_near_attraction(attraction)

    recommendations = get_highest_simalirity(restaurant,nearby_restaurants_with_zip, yelp_path)

    return recommendations


if __name__=="__main__":
    attraction = "Griffith Observatory"
    restaurant = "Himalayan Magic Masala"

    recommendations = nearby_restaurant_recommendation_based_on_attraction(attraction, restaurant)
    print(recommendations)