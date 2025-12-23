#This file is aim to add metadata to books dataset Google Books API 
# Common import 
import requests 
import pandas as pd
import time
from collections import Counter
import re

#--- STEP 1 : Analyze the data of google books api --- 

#We want to analyze  the data characteristics of google books api for : author, pubisher, published date, categories, language, average rating, page count and print type.

#---Config---
BOOKS_CSV = "data/books_clean.csv"
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
all_print_types=[]
all_dates=[]
all_page_counts=[]
all_avg_ratings =[]

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
        for cat in categories:
            all_categories.append(cat)
        
        #Authors
        for author in volume_info.get("authors", []):
            all_authors.append(author)

        #Publisher
        if "publisher" in volume_info:
            all_publishers.append(volume_info["publisher"])
        
        #Language
        if "language" in volume_info:
            all_languages.append(volume_info["language"])

        #Print Type
        if "printType" in volume_info:
            all_print_types.append(volume_info["printType"])

        #Published date
        if "publishedDate" in volume_info:
            all_dates.append(volume_info["publishedDate"])
        
        #Average rating
        if "averageRating" in volume_info:
            all_avg_ratings.append(volume_info["averageRating"])

        #Page count
        if "pageCount" in volume_info:
            all_page_counts.append(volume_info["pageCount"])

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
print("\nPRINT TYPES:")
print(Counter(all_print_types))

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


def fetch_google_books_metadata(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None

        data = r.json()
        if "items" not in data:
            return None

        info = data["items"][0]["volumeInfo"]

        return {
            "ISBN": isbn,
            "categories": info.get("categories"),
            "description": info.get("description"),
            "google_rating": info.get("averageRating"),
            "google_ratings_count": info.get("ratingsCount")
        }

    except:
        return None
