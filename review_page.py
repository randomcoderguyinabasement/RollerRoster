import streamlit as st
import pymongo
import pandas as pd
from bson import ObjectId
import certifi
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"],tlsCAFile=certifi.where())

client = init_connection()
db = client.RollerRoster

# Get parks and get attractions=======================

#Returns a list of park DICTIONARIES
@st.cache_data(ttl=600)
def get_parks():
    return list(
        db.parks.find().sort("name", 1)
    )

#Returns a list of attractions matching the chosen park
@st.cache_data(ttl=600)
def get_attractions(park_id):
    return list(
        db.attractions.find(
            {"park_id": ObjectId(park_id)}
        ).sort("name", 1)
    )


st.markdown("# Write a Review")

#encourage the user to log in to an account to reduce the amount of spam reviews
if not st.user.is_logged_in:
    st.markdown("## Log in with Google to save your reviews")
    st.button(
    "Log in with Google",
    on_click=st.login
)



parks = get_parks()

park_names = [park["name"] for park in parks]

location = st.selectbox("Theme park", options=park_names, index=None, placeholder = "Start typing a park name",accept_new_options=False)
if location is None:
    st.stop()

for park in parks:
    if location == park['name']:
        selected_park = park



attractions = get_attractions(str(selected_park['_id']))


attraction_names = [attraction['name'] for attraction in attractions]

selected_attraction_name = st.selectbox(
    "Attraction",
    options=attraction_names,
    index=None,
    placeholder="Choose an attraction",
    accept_new_options=False
)

if selected_attraction_name is None: 
    st.stop()

for a in attractions:
    if selected_attraction_name == a["name"]:
        cool = a

attraction_type = cool.get("type")
inversions = cool.get("inversions")

st.write("Type: ",attraction_type, " Inversions: ", inversions)

with st.form("review_form", clear_on_submit=True):
    stars = st.slider("Rating ⭐", min_value=0.0, max_value=5.0, value=4.0, step=0.5)
    review_text = st.text_area("Review", placeholder="This ride gave me whiplash...", max_chars=650)
    submitted = st.form_submit_button("Submit", type="primary")
if submitted:
    if not review_text.strip():
        st.error("Your review lacks text. Please write something!")
    else:
        if st.user.is_logged_in:
            username = st.user.name
            user_id = st.user.sub 
        else:
            username = "Guest"
            user_id = 0
        new_review = {
            "attraction_id": cool["_id"],
            "reviewer_name": username,
            "reviewer_id": user_id,
            "stars": float(stars),
            "review": review_text.strip()
        }
        db.reviews.insert_one(new_review)
        st.cache_data.clear()
        st.success(f"Saved review for **{cool["name"]}**")
