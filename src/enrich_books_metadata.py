#This file is aim to add metadata to books dataset Google Books API 
# Common import 
import requests 
import pandas as pd
import time
from collections import Counter
import re
from collections import defaultdict
import os
import pickle

#--- STEP 1 : Analyze the data of google books api --- 

#We want to analyze  the data characteristics of google books api for : author, pubisher, published date, categories, language, average rating, page count and print type.

#---Config---
DATA_DIR = "/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data"
BOOKS_CSV = os.path.join(DATA_DIR,"books_clean.csv")
OUTPUT_PKL= os.path.join(DATA_DIR,"books_enriched.pkl")
N_SAMPLE = 300
SLEEP_TIME = 0.1
TIMEOUT = 5

#---LOAD BOOK---
books = pd.read_csv(BOOKS_CSV)
isbns = books["ISBN"].dropna().astype(str).unique()[:N_SAMPLE]

#--- CONTAINERS --- 
all_categories = []
all_authors = []
all_publishers = []
all_languages = []
#all_print_types=[]
all_dates=[]
all_page_counts=[]
all_avg_ratings =[]

type_tracker=defaultdict(set)
#--- API LOOP ---
for isbn in isbns:
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            continue

        data = r.json()
        if "items" not in data:
            continue

        volume_info = data["items"][0]["volumeInfo"]

        #Categories
        categories = volume_info.get("categories", [])
        if categories is not None:
            type_tracker["categories"].add(type(categories))
            for cat in categories:
                all_categories.append(cat)
        
        #Authors
        authors = volume_info.get("authors")
        if authors is not None:
            type_tracker["authors"].add(type(authors))
            for author in authors:
                all_authors.append(author)

        #Publisher
        publisher = volume_info.get("publisher")
        if publisher is not None:
            type_tracker["publisher"].add(type(publisher))
            all_publishers.append(publisher)
        
        #Language
        language = volume_info.get("language")
        if language is not None:
            type_tracker["language"].add(type(language))
            all_languages.append(language)

        #Print Type
        #print_type = volume_info.get("printType")
        #if print_type is not None:
        #    type_tracker["printType"].add(type(print_type))
        #    all_print_types.append(print_type)

        #Published date
        published_date = volume_info.get("publishedDate")
        if published_date is not None:
            type_tracker["publishedDate"].add(type(published_date))
            all_dates.append(published_date)
        
        #Average rating
        avg_rating = volume_info.get("averageRating")
        if avg_rating is not None:
            type_tracker["averageRating"].add(type(avg_rating))
            all_avg_ratings.append(avg_rating)

        #Page count
        page_count = volume_info.get("pageCount")
        if page_count in volume_info:
            type_tracker["pageCount"].add(type(page_count))
            all_page_counts.append(page_count)

        time.sleep(SLEEP_TIME)

    except Exception as e:
        continue

# ---- ANALYSIS ----
def print_top(counter, title, n=20):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for item, count in counter.most_common(n):
        print(f"{item} ({count})")

#Categories
print_top(Counter(all_categories), "CATEGORIES (top 30)", 30)

#Authors
print_top(Counter(all_authors), "AUTHORS (top 20)", 20)

#Publishers
print_top(Counter(all_publishers), "PUBLISHERS (top 20)", 20)

#Languages
print("\nLANGUAGES:")
print(Counter(all_languages))

#Print types
#print("\nPRINT TYPES:")
#print(Counter(all_print_types))

#Published date formats
print("\nPUBLISHED DATE EXAMPLES:")
unique_dates = list(set(all_dates))[:20]
for d in unique_dates:
    print(d)

#Average ratings
print("\nAVERAGE RATING STATS:")
if all_avg_ratings:
    print("min:", min(all_avg_ratings))
    print("max:", max(all_avg_ratings))
    print("unique examples:", sorted(set(all_avg_ratings))[:10])

#Page count
print("\nPAGE COUNT STATS:")
if all_page_counts:
    print("min:", min(all_page_counts))
    print("max:", max(all_page_counts))
    print("examples:", sorted(set(all_page_counts))[:10])

#Print the type
print("\n" + "=" * 60)
print("DATA TYPES OBSERVED")
print("=" * 60)

for field, types in type_tracker.items():
    type_names = [t.__name__ for t in types]
    print(f"{field}: {type_names}")

#--- STEP 2 : Creating the pickle books_enriched composed of book_clean.csv and google books api data ---

# ---------------- FUNCTIONS ----------------

def extract_year(published_date):
    """
    Extract year from Google Books publishedDate
    Examples:
    - "2004" -> 2004
    - "2004-05-12" -> 2004
    - "2004-05" -> 2004
    """
    if pd.isna(published_date):
        return None
    match = re.match(r"\d{4}", str(published_date))
    return int(match.group()) if match else None


def fetch_google_metadata(isbn):
    """
    Call Google Books API for a given ISBN
    Return volumeInfo dict or empty dict
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return {}

        data = r.json()
        if "items" not in data:
            return {}

        return data["items"][0]["volumeInfo"]

    except Exception:
        return {}
    

def main():
    print(" Loading books_clean.csv...")
    # --- Safety: make sure output directory exists ---
    os.makedirs(os.path.dirname(OUTPUT_PKL), exist_ok=True)
    # --- LOAD OR RESUME ---
    if os.path.exists(OUTPUT_PKL):
        print(" Loading existing books_enriched.pkl...")
        with open(OUTPUT_PKL, "rb") as f:
            books = pickle.load(f)
    else:

        books = pd.read_csv(BOOKS_CSV)
        books["ISBN"] = books["ISBN"].astype(str)
    
        # ---- New metadata columns ----
        books["categories"] = None
        books["description"] = None
        books["publisher"] = None
        books["published_year"] = None
        books["pageCount"] = None
        books["language"] = None
        #books["printType"] = None
        books["averageRating"] = None

        print(" Enriching books with Google Books metadata...")

        SAVE_EVERY = 500  # checkpoint frequency

        for idx, row in books.iterrows():
            isbn = row["ISBN"]

            # --- Skip already processed books ---
            if pd.notna(books.at[idx, "categories"]):
                continue

            meta = fetch_google_metadata(isbn)

            if not meta:
                continue

            books.at[idx, "categories"] = meta.get("categories")
            books.at[idx, "description"] = meta.get("description")
            books.at[idx, "publisher"] = meta.get("publisher")
            books.at[idx, "published_year"] = extract_year(meta.get("publishedDate"))
            books.at[idx, "pageCount"] = meta.get("pageCount")
            books.at[idx, "language"] = meta.get("language")
            #books.at[idx, "printType"] = meta.get("printType")
            books.at[idx, "averageRating"] = meta.get("averageRating")

            if idx % 100 == 0:
                print(f"  → {idx}/{len(books)} books processed")
             # --- CHECKPOINT ---
            if idx % SAVE_EVERY == 0 and idx > 0:
                print(f" Saving checkpoint at {idx} books...")
                with open(OUTPUT_PKL, "wb") as f:
                    pickle.dump(books, f)

            time.sleep(SLEEP_TIME)

        print(" Saving books_enriched.pkl...")
        with open(OUTPUT_PKL, "wb") as f:
            pickle.dump(books, f)


        print(" books_enriched.pkl created successfully")
        print("Columns:")
        print(books.columns.tolist())


if __name__ == "__main__":
    main()