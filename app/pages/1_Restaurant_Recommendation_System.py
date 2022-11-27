import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "KG"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recommendation_engine"))

from query_neo4j import KGQuerier
from nearby_restaurant_recommend import nearby_restaurant_recommendation_based_on_attraction

uri = "neo4j+s://3b90e4fd.databases.neo4j.io"
user = "neo4j"
password = "4_PR6r6i7V3k-i4dgkUygZcgU-G5ceCZRwUnrOlqLpo"
querier = KGQuerier(uri, user, password)

attractions = querier.get_all_attraction_names()
restaurants = querier.get_all_restaurant_names()

def render_restaurant(r_list):
    out_str = ""
    for i,r in enumerate(r_list,start=1):
        out_str += f"{i}) **[{r['restaurant_name']}]({r['restaurant_url']})**\n\nAverage rating: {r['average_rating']} , Number of reviews: {r['n_reviews']}\n\nAddress: {r['restaurant_address']}\n\n\n\n\n"
    return out_str

with st.form("Recommender"):
    nearby_attraction = st.selectbox("Enter Attraction you will be visiting", attractions)
    base_restaurant = st.selectbox("Enter Restaurant you like", restaurants)

    submitted = st.form_submit_button("Go!")
    if submitted:
        recommendations = nearby_restaurant_recommendation_based_on_attraction(nearby_attraction, base_restaurant)
        st.write(render_restaurant(recommendations),unsafe_allow_html=True)