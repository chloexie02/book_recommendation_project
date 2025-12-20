#app.py
#Common import
import sys
import os
import streamlit as st
import pandas as pd
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from recommendation_collab import recommend_books_from_favorites, book_similarity, books

#path for BookCoverNotFound.png image
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NO_COVER_PATH = os.path.join(BASE_DIR, "..", "assets", "BookCoverNotFound.png")


#---Page congif---
st.set_page_config(page_title = "Book Recommendation", page_icon="📚", layout="wide")

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
#st.markdown("<p class='subtitle'>Choose your recommendation mode</p>", unsafe_allow_html=True)

#--- Choice page ---
mode = st.radio(
    "Select a recommendation type:",
    ("📚 Based on my favorite books", "🔍 Based on metadata (coming soon!)"),
    index=0
)

#--- Option 1 : favorites ---
if mode == "📚 Based on my favorite books":
    st.markdown("### Choose your 5 favorite books")

    #Extract unique authors from the books dataset (already loaded from recommendation_collab)
    authors = sorted(books["Book-Author"].dropna().unique())

    favorite_books = []
    favorite_authors = []

    # Create 5 columns for 5 favorite book selections

    #col1, col2, col3, col4, col5 = st.columns(5)
    #with col1:
    #    fav1 = st.text_input("Book 1")
    #with col2:
    #    fav2 = st.text_input("Book 2")
    #with col3:
    #    fav3 = st.text_input("Book 3")
    #with col4:
    #    fav4 = st.text_input("Book 4")
    #with col5:
    #    fav5 = st.text_input("Book 5")

    #favorite_books = [fav for fav in [fav1, fav2, fav3, fav4, fav5] if fav]

    cols = st.columns([3, 3, 3, 3, 3])
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Book {i+1}**")

            # Select author from dropdown
            selected_author = st.selectbox(
                f"Author {i+1}",
                options=[""] + authors,
                key=f"author_{i}"
            )

            # If an author is selected, filter books by that author
            if selected_author:
                filtered_books = books[books["Book-Author"] == selected_author]["Book-Title"].sort_values().unique()
                selected_book = st.selectbox(
                    f"Title {i+1}",
                    options=[""] + list(filtered_books),
                    key=f"title_{i}"
                )
            else:
                selected_book = None

            # Append to favorites if a book is selected
            if selected_book:
                favorite_books.append(selected_book)
                favorite_authors.append(selected_author)

    if st.button("Show Recommendations"):
        if len(favorite_books) == 0:
            st.warning("Please enter at least one favorite book.")
        else:
            # Convert titles to ISBNs if needed
            #favorite_isbns = books[books["Book-Title"].isin(favorite_books)]["ISBN"].tolist()
            # Retrieve ISBNs based on both Author and Title to avoid duplicates
            favorite_isbns = []
            for author, title in zip(favorite_authors, favorite_books):
                matched = books[(books["Book-Author"] == author) & (books["Book-Title"] == title)]
                if not matched.empty:
                    favorite_isbns.append(matched.iloc[0]["ISBN"])


            if len(favorite_isbns) == 0:
                st.error("None of these books were found in the dataset :(")
            else:
                #st.success("Generating your recommendations...")
                recs = recommend_books_from_favorites(favorite_isbns, book_similarity, books, top_n=5)

                st.markdown("### Recommended Books for You:")
                #recs = recs.reset_index(drop=True)
                #recs.index = recs.index + 1 # to have the favorite index from 1 to 5 instead of 0 to 4
                #if recs.empty:
                #    st.error("No recommendation possible: these books do not have enough ratings.")
                #else:
                #    st.table(recs[["Book-Title", "Book-Author"]])#, "score"]])
                # UI security

                if recs.empty:
                    st.error("No reccomendation possible")
                else:
                    cols2 = st.columns(len(recs))

                for i, (col, (_, row)) in enumerate(zip(cols2, recs.iterrows()), start=1):
                    with col:
                        st.markdown(f"**{i}**")

                        # Book Image
                        if pd.notna(row["Image-URL-M"]):
                            st.image(row["Image-URL-M"], width=120)
                        else:
                            st.image(NO_COVER_PATH, width=120)

                        # Title
                        st.markdown(
                        f"<div style='font-weight:600; text-align:center;'>{row['Book-Title']}</div>",
                        unsafe_allow_html=True
                        )

                        # Author
                        st.markdown(
                        f"<div style='color:gray; font-size:14px; text-align:center;'>{row['Book-Author']}</div>",
                        unsafe_allow_html=True
                        )
# --- Option 2: Metadata (inactive) ---
elif mode == "🔍 Based on metadata (coming soon!)":
    st.info("🚧 This feature will be available soon! You'll be able to search by author, genre etc.")