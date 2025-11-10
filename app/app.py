#app.py
#Common import
import sys
import os
import streamlit as st
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from recommendation_collab import recommend_books_from_favorites, book_similarity, books

#---Page congif---
st.set_page_config(page_title = "Book Recommendation", page_icon="📚", layout="centered")

#--- CSS CUSTOM ---
st.markdown("""
    <style>
    body {
        background-color: #F8F9FA;
        font-family: 'Poppins', sans-serif;
    }
    .title {
        text-align: center;
        color: #2E4053;
        font-size: 40px;
        font-weight: 700;
    }
    .subtitle {
        text-align: center;
        color: #5D6D7E;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True
)

#--- APP TITLE ---
st.markdown("<h1 class='title'> Book Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Choose your recommendation mode</p>", unsafe_allow_html=True)

#--- Choice page ---
mode = st.radio(
    "Select a recommendation type:",
    ("📚 Based on my favorite books", "🔍 Based on metadata (coming soon!)"),
    index=0
)

#--- Option 1 : favorites ---
if mode == "📚 Based on my favorite books":
    st.markdown("### Enter your 5 favorite books")

    favorite_books = []
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        fav1 = st.text_input("Book 1")
    with col2:
        fav2 = st.text_input("Book 2")
    with col3:
        fav3 = st.text_input("Book 3")
    with col4:
        fav4 = st.text_input("Book 4")
    with col5:
        fav5 = st.text_input("Book 5")

    favorite_books = [fav for fav in [fav1, fav2, fav3, fav4, fav5] if fav]

    if st.button("Show Recommendations"):
        if len(favorite_books) == 0:
            st.warning("Please enter at least one favorite book.")
        else:
            # Convert titles to ISBNs if needed
            favorite_isbns = books[books["Book-Title"].isin(favorite_books)]["ISBN"].tolist()

            if len(favorite_isbns) == 0:
                st.error("None of these books were found in the dataset :(")
            else:
                st.success("Generating your recommendations...")
                recs = recommend_books_from_favorites(favorite_isbns, book_similarity, books, top_n=5)

                st.markdown("### Recommended Books for You:")
                st.table(recs[["Book-Title", "Book-Author", "score"]])

# --- Option 2: Metadata (inactive) ---
elif mode == "🔍 Based on metadata (coming soon!)":
    st.info("🚧 This feature will be available soon! You'll be able to search by author, genre etc.")