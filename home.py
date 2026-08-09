import streamlit as st
with st.container(horizontal_alignment="center"):
    st.markdown("# 🎢 RollerRoster", text_alignment="center")
    st.markdown("## Discover, rate, and review theme park attractions",text_alignment="center")
    if st.button("Write a Review", type="primary"):
        st.switch_page("review_page.py")
    if st.button("See what others are saying", type="primary"):
        st.switch_page("search_page.py")
    st.markdown("6 parks and 100+ rides are ready to review.", text_alignment="center")
    st.markdown("Reviewing can be done anonymously, or you can save your reviews by logging in with Google.", text_alignment="center")