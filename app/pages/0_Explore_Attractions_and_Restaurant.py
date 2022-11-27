import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "KG"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recommendation_engine"))

from city_based_recommender import get_top_attractions_from_city, get_top_restaurants_from_city

from query_neo4j import KGQuerier

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
querier = KGQuerier(uri, user, password)

cities = querier.get_all_city_names()

def render_attraction(attraction_list):
    out_str = ""
    for i,attraction in enumerate(attraction_list,start=1):
        if attraction["expert_recommended"] == "Yes":
            out_str += f"{i}) **[{attraction['attraction_name']}]({attraction['attraction_url']})**\n\n**Expert Recommended!**\n\nAverage rating: {attraction['attraction_rating']} , Number of reviews: {attraction['attraction_n_reviews']}\n\nAddress: {attraction['attraction_address']}\n\nExpert Review: {attraction['expert_review']}\n\n\n\n\n"
        else:
            out_str += f"{i}) **[{attraction['attraction_name']}]({attraction['attraction_url']})**\n\nAverage rating: {attraction['attraction_rating']} , Number of reviews: {attraction['attraction_n_reviews']}\n\nAddress: {attraction['attraction_address']}\n\n\n\n\n"
    return out_str

def render_restaurant(r_list):
    out_str = ""
    for i,r in enumerate(r_list,start=1):
        out_str += f"{i}) **[{r['restaurant_name']}]({r['restaurant_url']})**\n\nAverage rating: {r['average_rating']} , Number of reviews: {r['n_reviews']}\n\nAddress: {r['restaurant_address']}\n\n\n\n\n"
    return out_str

city = st.selectbox("Enter city you want to visit", cities)

entity = st.radio("What do you want to explore?",("Attractions","Restaurants"),horizontal = True, key="main")

if entity == "Attractions":
    recommendations = get_top_attractions_from_city(city)
    st.write(render_attraction(recommendations),unsafe_allow_html=True)
else:
    with st.form("restaurant_flags"):
        veg_flag = st.radio("Are you looking for vegetarian options?",("Yes","No"),horizontal = True, key="veg")
        parking_flag = st.radio("Are you looking for parking?",("Yes","No"),horizontal = True, key="parking")
        takeout_flag = st.radio("Are you looking for takeout?",("Yes","No"),horizontal = True, key="takeout")
        drivethru_flag = st.radio("Are you looking for drive-thru?",("Yes","No"),horizontal = True, key="drivethru")
        reservation_flag = st.radio("Are you looking for reservations?",("Yes","No"),horizontal = True, key="reservation")
        kid_flag = st.radio("Are you looking for a place which is good for kids?",("Yes","No"),horizontal = True, key="kid")
        dog_flag = st.radio("Are you looking for a place which is good for dogs?",("Yes","No"),horizontal = True, key="dog")
        smoking_flag = st.radio("Are you looking for a place which allows smoking?",("Yes","No"),horizontal = True, key="smoking")

        # veg_flag = 1 if veg_flag=="Yes" else 0
        # parking_flag = 1 if parking_flag=="Yes" else 0
        # takeout_flag = 1 if takeout_flag=="Yes" else 0
        # drivethru_flag = 1 if drivethru_flag=="Yes" else 0
        # reservation_flag = 1 if reservation_flag=="Yes" else 0
        # kid_flag = 1 if kid_flag=="Yes" else 0
        # dog_flag = 1 if dog_flag=="Yes" else 0
        # smoking_flag = 1 if smoking_flag=="Yes" else 0


        submitted = st.form_submit_button("Go!")
        if submitted:
            flag_d = {}
            if veg_flag=="Yes":
                flag_d["has_vegetarian"] = 1
            if parking_flag=="Yes":
                flag_d["has_parking"] = 1
            if takeout_flag=="Yes":
                flag_d["has_takeout"] = 1
            if drivethru_flag=="Yes":
                flag_d["has_drivethru"] = 1
            if reservation_flag=="Yes":
                flag_d["has_reservation"] = 1
            if kid_flag=="Yes":
                flag_d["is_good_for_kids"] = 1
            if dog_flag=="Yes":
                flag_d["dogs_allowed"] = 1
            if smoking_flag=="Yes":
                flag_d["smoking_allowed"] = 1
            recommendations = get_top_restaurants_from_city(city,flag_d)
            st.write(render_restaurant(recommendations),unsafe_allow_html=True)