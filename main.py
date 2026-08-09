import streamlit as st
import pymongo
import pandas as pd
import certifi
home_page = st.Page("home.py",title="Home",icon="🏠",default=True)
profile_page = st.Page("profile_page.py", title = "My Profile", icon = "👤")
review_page = st.Page("review_page.py", title = "Write a review", icon = "📝")
search_page = st.Page("search_page.py", title = "Search", icon = "🔎")

if st.user.is_logged_in:
    st.sidebar.markdown(f"# Welcome, {st.user.name}")
else:
    st.sidebar.markdown("# Welcome, Guest")


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"],tlsCAFile=certifi.where())
    

client = init_connection()

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_data():
    db = client.RollerRoster
    items = db.reviews.find()
    items = list(items)  # make hashable for st.cache_data
    return items

items = get_data()
#st.write(items)


pg = st.navigation([home_page,review_page, profile_page, search_page])

pg.run()