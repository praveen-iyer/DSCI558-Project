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


with st.form("City Based Recommender"):
    city = st.selectbox("Enter city you want to visit", cities)

    entity = st.radio("What do you want to explore?",("Attractions","Restaurants"))

    submitted = st.form_submit_button("Go!")
    if submitted:
        if entity == "Attractions":
            recommendations = get_top_attractions_from_city(city)
        else:
            recommendations = get_top_restaurants_from_city(city)
        st.write(recommendations)