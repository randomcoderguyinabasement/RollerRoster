import streamlit as st
import pymongo
from bson import ObjectId
import certifi
# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"],tlsCAFile=certifi.where())

client = init_connection()
db = client.RollerRoster
# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_reviews():
  
    items = db.reviews.find()
    items = list(items)  # make hashable for st.cache_data
    return items



def get_parks():
    items = db.parks.find()
    items = list(items)
    return items

def get_attractions():
    items = db.attractions.find()
    items = list(items)
    return items

parks_list = get_parks()
attractions_list = get_attractions()
reviews_list = get_reviews()



def attraction_card(attraction, park_name):
    with st.container(border=True):
        st.subheader(attraction['name'])
        st.caption(f"{park_name} | {attraction["type"]}")
        if st.button("View Info", key=f"attraction_{attraction['_id']}"):
            st.session_state["selected_attraction_id"] = str(attraction["_id"])
            st.rerun()

def park_card(park):
    with st.container(border=True):
        st.subheader(park['name'])
        st.caption(f"{park["city"]}, {park["state"]}")
        if st.button("View Info", key=f"park_{park['_id']}"):
            st.session_state["selected_park_id"] = str(park["_id"])
            st.rerun()


# MORE INFO on Attractions======================================================================

if "selected_attraction_id" in st.session_state:
    attraction_id = ObjectId(st.session_state["selected_attraction_id"])
    attraction = db.attractions.find_one({"_id": attraction_id})
    park = db.parks.find_one({"_id": attraction["park_id"]})
    reviews = list(db.reviews.find({"attraction_id":attraction_id}))
    #Back button
    if st.button("← Back"):
        del st.session_state["selected_attraction_id"]
        st.rerun()

    st.markdown(f"# {attraction["name"]}")
    st.caption(f"{park["name"]} | {attraction["type"]}")

    #calculate the average rating

    if reviews:
        average_stars = sum(review["stars"] for review in reviews) / len(reviews)
        st.metric("Average Rating", f"{average_stars:.2f}/5 • {len(reviews)} Reviews")
    else:
        st.write("No reviews yet.")

    #print out all the reviews with containers

    st.markdown("## Reviews")
    if reviews:
        for review in reviews:
            with st.container(border=True):
                st.markdown(f"{review["stars"]}/5⭐")
                st.caption(f"Written by {review["reviewer_name"]}")
                st.write(review["review"])
    else:
        st.info("Write the first review!")

    st.stop()


# MORE INFO on Parks ===========================================================================

if "selected_park_id" in st.session_state:
    park_id = ObjectId(st.session_state["selected_park_id"])
    park = db.parks.find_one({"_id": park_id})
    attractions = list(db.attractions.find({"park_id": park_id}))
    #Back button
    if st.button("← Back"):
        del st.session_state["selected_park_id"]
        st.rerun()

    st.markdown(f"# {park["name"]}")
    st.caption(f"{park["city"]}, {park["state"]} | {park["country"]}")

    #get attraction IDs for the park
    attraction_ids = [attraction["_id"] for attraction in attractions]

    #get reviews for attractions in the park
    reviews = list(db.reviews.find({"attraction_id": {"$in": attraction_ids}}))

    #Find the average rating
    if reviews:
        average_stars = sum(review["stars"] for review in reviews) / len(reviews)
        st.metric("Average Rating", f"{average_stars:.2f}/5⭐ • {len(reviews)} Reviews")
    else:
        st.write("No reviews have been made yet for this entire park...")
    st.markdown("## Attractions")

    for attraction in attractions:
        attraction_card(attraction,park["name"])
    st.stop()
        



# SEARCH BAR ===================================================================================

st.markdown("# Search")
input = st.text_input("", placeholder = "Search for a park or attraction", icon = "🔎")
park_results_list = []
attraction_results_list = []
if input:
    for park in parks_list:
        if input.lower() in park['name'].lower():
            park_results_list.append(park)
    for attraction in attractions_list:
        if input.lower() in attraction['name'].lower():
            attraction_results_list.append(attraction)
    st.markdown("## Results")
    if not park_results_list and not attraction_results_list:
        st.write(":( No results")
    for park in park_results_list:
        park_card(park)
    for attraction in attraction_results_list:
        park = db.parks.find_one({"_id": attraction["park_id"]})
        attraction_card(attraction,park["name"])
    