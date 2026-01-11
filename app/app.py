#app.py
#Common import
import sys
import os
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from recommendation_collab import recommend_books_from_favorites, book_similarity, books

books_enriched = pd.read_pickle(os.path.join(os.path.dirname(__file__),"..","data","books_enriched.pkl"))
min_year = int(books_enriched["published_year"].min())
max_year = int(books_enriched["published_year"].max())

max_pages = int(books_enriched["pageCount"].max())


#path for BookCoverNotFound.png image
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NO_COVER_PATH = os.path.join(BASE_DIR, "..", "assets", "BookCoverNotFound.png")

@st.cache_data(show_spinner=False)
def is_valid_book_cover(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        r = requests.get(url, headers=headers, timeout=5)

        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        img = Image.open(BytesIO(r.content)).convert("RGB")
        arr = np.array(img)

        # Image trop petite
        if img.width < 50 or img.height < 50:
            return False, "Too small"

        # Image quasi blanche
        if arr.mean() > 245:
            return False, f"Too white ({arr.mean():.1f})"

        return True, "OK"

    except Exception as e:
        return False, str(e)


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
    ("📚 Based on my favorite books", "🔍 Based on metadata"),
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
                            #st.markdown(f"**{i}**")
                            st.markdown(f"""<div style="text-align:center;font-size:22px;font-weight:700;margin-bottom:6px;">{i}</div>""",unsafe_allow_html=True)

                            # Book Image
                            #if pd.notna(row["Image-URL-M"]):
                                #st.image(row["Image-URL-M"], width=120)
                            #    st.markdown(f"""<div style="text-align:center;"><img src="{row['Image-URL-M']}"width="120"style="margin:auto;"onerror="this.onerror=null; this.src='{NO_COVER_PATH}';"> </div> """,unsafe_allow_html=True)
                            #else:
                            #    st.image(NO_COVER_PATH, width=120)

                            # st.markdown(
                            # f"""
                            # <div style="
                            # width:120px;
                            # height:180px;
                            # background-image:url('{NO_COVER_PATH}');
                            # background-size:cover;
                            # background-position:center;
                            # margin:auto;
                            # ">
                            # <img src="{row['Image-URL-M']}"
                            # style="
                            # width:100%;
                            # height:100%;
                            # object-fit:cover;
                            # ">
                            # </div>
                            # """,
                            # unsafe_allow_html=True
                            # )

                            is_valid, _ = is_valid_book_cover(row["Image-URL-M"])

                            if is_valid:
                                st.markdown(
                                f"""
                                <div style="display: flex; justify-content: center;">
                                <img src="{row['Image-URL-M']}" width="120">
                                </div>
                                """,
                                unsafe_allow_html=True
                                )
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
elif mode == "🔍 Based on metadata":
    st.markdown("### Find books using metadata")

    books_meta=books_enriched.copy()

    #---Filter---
    categories = sorted(
        set(
            cat
            for cats in books_meta["categories"].dropna()
            if isinstance(cats, list)
            for cat in cats
        )
    )

    authors = sorted(books_meta["Book-Author"].dropna().unique())
    publishers = sorted(books_meta["publisher"].dropna().unique())
    languages = sorted(books_meta["language"].dropna().unique())
    #print_types = sorted(books_meta["printType"].dropna().unique())

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_category = st.multiselect("Category", [""] + categories)
        selected_author = st.multiselect("Author", [""] + authors)

    with col2:
        selected_publisher = st.multiselect("Publisher", [""] + publishers)
        

    with col3:
        selected_language = st.multiselect("Language", [""] + languages)
    #    selected_print = st.multiselect("Print type", [""] + print_types)

    use_year_filter = st.checkbox("Filter by publication year")

    year_min, year_max = st.slider(
        "Publication year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        disabled=not use_year_filter
    )

    use_page_filter = st.checkbox("Filter by number of pages")

    page_min, page_max = st.slider(
        "Number of pages",
        min_value=0,
        max_value=max_pages,
        value=(0, max_pages),
        disabled=not use_page_filter
    )

    # ---------- SEARCH ----------
    if st.button("Show Recommendations "):

        filtered = books_meta.copy()

        if selected_category:
            filtered = filtered[
                filtered["categories"].apply(
                    lambda cats: any(cat in cats for cat in selected_category)
                    if isinstance(cats, list)
                     else False
                )
            ]


        if selected_author:
            filtered = filtered[filtered["Book-Author"].isin(selected_author)]

        if selected_publisher:
            filtered = filtered[filtered["publisher"].isin(selected_publisher)]

        if selected_language:
            filtered = filtered[filtered["language"].isin(selected_language)]

        #if selected_print:
        #    filtered = filtered[filtered["printType"].isin(selected_print)]

        #filtered = filtered[
        #    (filtered["published_year"].between(year_min, year_max)) &
        #    (filtered["pageCount"].between(page_min, page_max))
        #]

        if use_year_filter:
            filtered_books = filtered[
            (filtered["published_year"] >= year_min) &
            (filtered["published_year"] <= year_max)
             ]

        if use_page_filter:
            filtered_books = filtered[
            (filtered["pageCount"] >= page_min) &
            (filtered["pageCount"] <= page_max)
            ]

        # ---------- RESULTS ----------
        if filtered.empty:
            st.error(" No book matches all these criteria.")
        else:
            results = (
                filtered
                .sort_values(by="averageRating", ascending=False)
                .head(5)
            )

            st.markdown("### 📚 Recommended books")

            cols = st.columns(len(results))


            #for  col, (_, row) in zip(cols, results.iterrows()):
            for i, (col, (_, row)) in enumerate(zip(cols, results.iterrows()), start=1):
                with col:
                    st.markdown(f"""<div style="text-align:center;font-size:22px;font-weight:700;margin-bottom:6px;">{i}</div>""",unsafe_allow_html=True)
                    
    
                    
                    is_valid, _ = is_valid_book_cover(row["Image-URL-M"])

                    if is_valid:
                        #st.image(row["Image-URL-M"], width=120)
                        st.markdown(
                                f"""
                                <div style="display: flex; justify-content: center;">
                                <img src="{row['Image-URL-M']}" width="120">
                                </div>
                                """,
                                unsafe_allow_html=True
                                )
                    else:
                        st.image(NO_COVER_PATH, width=120)
                        

                       
                    st.markdown(
                            f"<div style='font-weight:600; text-align:center;'>{row['Book-Title']}</div>",
                            unsafe_allow_html=True
                            )
                    st.markdown(
                            f"<div style='color:gray; font-size:14px; text-align:center;'>{row['Book-Author']}</div>",
                            unsafe_allow_html=True
                            )
                    
                    if pd.isna(row['description']) or row['description'] is None or str(row['description']).strip() == "" : 
                        description_text = "No description"
                    else:
                        description_text = row['description']

                    st.markdown(
                            f"<div style='color:gray; font-size:14px; text-align:center;font-style:italic;'>{description_text}</div>",
                            unsafe_allow_html=True
                            )

    