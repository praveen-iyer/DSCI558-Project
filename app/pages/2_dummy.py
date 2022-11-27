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


# "has_vegetarian": 1, "has_parking": 1, "has_takeout": 1, "has_drivethru": 0, "has_reservation": 1, "is_good_for_kids": 1, "dogs_allowed": 0, "smoking_allowed": 0

with st.form("City Based Recommender"):
    city = st.selectbox("Enter city you want to visit", cities)

    entity = st.radio("What do you want to explore?",("Attractions","Restaurants"),horizontal = True, key="main")

    submitted = st.form_submit_button("Go!")
    if submitted:
        if entity == "Attractions":
            recommendations = get_top_attractions_from_city(city)
            st.write(recommendations)
        else:
            veg_flag = st.radio("Are you looking for vegetarian options?",("Yes","No"),horizontal = True, key="veg")
            parking_flag = st.radio("Are you looking for parking?",("No","Yes"),horizontal = True, key="parking")
            takeout_flag = st.radio("Are you looking for takeout?",("No","Yes"),horizontal = True, key="takeout")
            drivethru_flag = st.radio("Are you looking for drive-thru?",("No","Yes"),horizontal = True, key="drivethru")
            reservation_flag = st.radio("Are you looking for reservations?",("No","Yes"),horizontal = True, key="reservation")
            kid_flag = st.radio("Are you looking for a place which is good for kids?",("No","Yes"),horizontal = True, key="kid")
            dog_flag = st.radio("Are you looking for a place which is good for dogs?",("No","Yes"),horizontal = True, key="dog")
            smoking_flag = st.radio("Are you looking for a place which allows smoking?",("No","Yes"),horizontal = True, key="smoking")

            # veg_flag = 1 if veg_flag=="Yes" else 0
            # parking_flag = 1 if parking_flag=="Yes" else 0
            # takeout_flag = 1 if takeout_flag=="Yes" else 0
            # drivethru_flag = 1 if drivethru_flag=="Yes" else 0
            # reservation_flag = 1 if reservation_flag=="Yes" else 0
            # kid_flag = 1 if kid_flag=="Yes" else 0
            # dog_flag = 1 if dog_flag=="Yes" else 0
            # smoking_flag = 1 if smoking_flag=="Yes" else 0

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
            st.write(recommendations)