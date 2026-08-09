import streamlit as st
import pymongo
import certifi
# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"],tlsCAFile=certifi.where())

client = init_connection()
db=client.RollerRoster
# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_data():
    items = db.reviews.find()
    items = list(items)  # make hashable for st.cache_data
    return items

items = get_data()



def login_screen():
    st.markdown("# Log in for personal stats", text_alignment = "center")
    st.markdown("## Login is secure using Google.", text_alignment = "center")
    with st.container(horizontal_alignment="center"):
        st.button("Log in with Google", on_click=st.login)

if not st.user.is_logged_in:
    login_screen()
    st.stop()

st.button("Log out", on_click=st.logout)


st.markdown("# My Profile")
reviews = []
for item in items:
    if item["reviewer_id"] == st.user.sub:
        reviews.append(item)

if reviews:
    st.write(f"You have written **{len(reviews)}** reviews")
    for review in reviews:
        attraction = db.attractions.find_one({"_id": review["attraction_id"]})
        park = db.parks.find_one({"_id": attraction["park_id"]})
        with st.container(border=True):
            st.subheader(attraction["name"])
            st.caption(f"{park["name"]} | {attraction["type"]}")
            st.markdown(f"{review["stars"]}/5⭐")
            st.write(review["review"])
            if st.button("Remove Review 🗑️", key=f"delete_{review["_id"]}"):
                db.reviews.delete_one({"_id": review["_id"], "reviewer_id": st.user.sub})
                st.cache_data.clear()
                st.rerun()

else:
    st.info("Go write some reviews and come back :D")