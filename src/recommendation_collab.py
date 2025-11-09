# recommendation_collab.py

#---Imports---
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle 
import os

#---Parameters---
DATA_DIR = "/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data"
BOOKS_FILE = os.path.join(DATA_DIR,"books_clean.csv")
RATINGS_FILE = os.path.join(DATA_DIR,"ratings_clean.csv")
USER_ITEM_PICKLE = os.path.join(DATA_DIR, "user_item_matrix.pkl")
SIMILARITY_PICKLE = os.path.join(DATA_DIR, "user_similarity.pkl")

#---Load cleaned datasets---
#We load ratings (core) and books (for display of titles).
books = pd.read_csv(BOOKS_FILE)
ratings = pd.read_csv(RATINGS_FILE)

#Quick check
print(f"Loaded books: {books.shape},ratings : {ratings.shape}")

#---Build or load User-Item Matrix---
def build_user_item_matrix(ratings_df,rebuild=False):
    """
    Build a user-item matrix (users x books). Missing ratings are NaN.
    We fill with 0 for similarity computation later, but keep NaNs in
    the stored DataFrame if desired. We save/load the matrix as a pickle
    to avoid recomputing every time.
    """
    if (not rebuild) and os.path.exists(USER_ITEM_PICKLE) : 
        print("Loading precomputed user-item matrix from pickle.")
        return pickle.load(open(USER_ITEM_PICKLE,"rb"))
    print("Building user-item matrix from ratings")
    user_item = ratings_df.pivot_table(index = 'User-ID',columns='ISBN',values='Book-Rating')
    #Save for reuse
    pickle.dump(user_item,open(USER_ITEM_PICKLE,"wb"))
    return user_item

#--- Create user-item matrix (use pivot)----
user_item_matrix = build_user_item_matrix(ratings,rebuild=False)
print("User-Item matrix shape : ", user_item_matrix.shape)

#--- Compute or load user similarity (cosine) ---
def compute_user_similarity(user_item_df, rebuild=False):
    """
    Compute cosine similarity between users. We fill NaN with 0 for the
    similarity computation because missing == no rating.
    """
    if (not rebuild) and os.path.exists(SIMILARITY_PICKLE):
        print("Loading precomputed user similarity from pickle.")
        return pickle.load(open(SIMILARITY_PICKLE,"rb"))
    print("Computing user similarity (cosine).")
    #fill NaN with 0 for similarity calculation
    sim = cosine_similarity(user_item_df.fillna(0).values)
    sim_df = pd.DataFrame(sim,index = user_item_df.index, columns=user_item_df.index)
    #Save for reuse 
    pickle.dump(sim_df,open(SIMILARITY_PICKLE,"wb"))
    return sim_df

user_similarity_df = compute_user_similarity(user_item_matrix,rebuild=False)
print("User similarity matrix shape : ", user_similarity_df.shape)

