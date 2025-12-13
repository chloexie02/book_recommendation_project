# recommendation_collab.py
# The script builds a user-item matrix from cleaned ratings and computes user-user similarity (cosine).
# It provides a function to recommend books for a target user using user-based collaborative filtering.


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
BOOK_USER_PICKLE = os.path.join(DATA_DIR, "book_user_matrix.pkl")
SIMILARITY_PICKLE = os.path.join(DATA_DIR, "book_similarity.pkl")

#---Load cleaned datasets---
#We load ratings (core) and books (for display of titles).
books = pd.read_csv(BOOKS_FILE)
ratings = pd.read_csv(RATINGS_FILE)


#Quick check
print(f"Loaded books: {books.shape},ratings : {ratings.shape}")

#---Build or load User-Item Matrix---
def build_user_item_matrix(ratings_df,rebuild=False):
    """
    Build a book-user matrix (books x users). Missing ratings are NaN.
    We fill with 0 for similarity computation later, but keep NaNs in
    the stored DataFrame if desired. We save/load the matrix as a pickle
    to avoid recomputing every time.
    """
    if (not rebuild) and os.path.exists(BOOK_USER_PICKLE) : 
        print("Loading precomputed book-user matrix from pickle.")
        return pickle.load(open(BOOK_USER_PICKLE,"rb"))
    print("Building book-user matrix from ratings")
    user_item = ratings_df.pivot_table(index = 'ISBN',columns='User-ID',values='Book-Rating')
    #Save for reuse
    pickle.dump(user_item,open(BOOK_USER_PICKLE,"wb"))
    return user_item

#--- Create book-user matrix (use pivot)----
book_user_matrix = build_user_item_matrix(ratings,rebuild=False)
print("Book-User matrix shape : ", book_user_matrix.shape)

#--- Compute or load user similarity (cosine) ---
def compute_book_similarity(book_item_df, rebuild=False):
    """
    Compute cosine similarity between books. We fill NaN with 0 for the
    similarity computation because missing == no rating.
    """
    if (not rebuild) and os.path.exists(SIMILARITY_PICKLE):
        print("Loading precomputed book similarity from pickle.")
        return pickle.load(open(SIMILARITY_PICKLE,"rb"))
    print("Computing book similarity (cosine).")
    #fill NaN with 0 for similarity calculation
    sim = cosine_similarity(book_item_df.fillna(0).values)
    sim_df = pd.DataFrame(sim,index = book_item_df.index, columns=book_item_df.index)
    #Save for reuse 
    pickle.dump(sim_df,open(SIMILARITY_PICKLE,"wb"))
    return sim_df

book_similarity = compute_book_similarity(book_user_matrix,rebuild=False)
print("Book similarity matrix shape : ", book_similarity.shape)

#print for debug
print("BOOK ISBN type:", type(books['ISBN'].iloc[0]))
print("SIM INDEX type:", type(book_similarity.index[0]))

#--- Recommendation function ---
def recommend_books_from_favorites(favorite_isbns, book_similarity_df, books_df, top_n=5):
    """
    Recommend books based on a list of favorite ISBNs (item-based CF).
    Steps:
    1) For each favorite book, find similarity scores to all other books.
    2) Aggregate similarity scores for all favorites.
    3) Exclude books already in favorite list.
    4) Return top-N recommendations with title/author.
    """
    #Check favorites exist in matrix
    valid_isbns=[isbn for isbn in favorite_isbns if isbn in book_similarity_df.index]
    if not valid_isbns:
        print('No valid ISBNS found in matrix.')
        #return pd.DataFrame()
        return pd.DataFrame(colums=['ISBN','Book-Title','Book-Author','score'])
    #print for debug
    print("favorite_isbns: ",favorite_isbns)
    print("valid_isbns: ", valid_isbns)
    # Aggregate similarity scores
    sim_scores = book_similarity_df.loc[valid_isbns].sum(axis=0)
    sim_scores = sim_scores.drop(labels=valid_isbns,errors='ignore')

    #Top N recommendations
    top_isbns = sim_scores.sort_values(ascending=False).head(top_n).index
    
    #print for debug
    print("top_isbns: ",list(top_isbns))
    
    # Keep only top_isbns present in books_df
    #top_isbns_in_books = [isbn for isbn in top_isbns if isbn in books_df['ISBN'].values]
    recommended_books = books_df[books_df['ISBN'].isin(top_isbns)][['ISBN', 'Book-Title', 'Book-Author']].copy()
    recommended_books['score']=recommended_books['ISBN'].map(lambda x: sim_scores.get(x, 0))
    recommended_books = recommended_books.set_index('ISBN').loc[top_isbns].reset_index()
    print(recommended_books[['ISBN', 'score']])
    return recommended_books

# --- Example  ---
if __name__ == "__main__":
    sample_favorites = ['0345417623', '0441172717']  # example ISBNs
    recs = recommend_books_from_favorites(sample_favorites, book_similarity, books, top_n=5)
    print("Recommended books:\n", recs)