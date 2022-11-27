import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "KG"))

from query_neo4j import KGQuerier

st.write("Something about our project")