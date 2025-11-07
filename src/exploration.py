#Common import
#.ipynb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import seaborn as sns

##----------------------GET DATA------------------------------------------------------------
#----------------------DATA EXPLORATION-----------------------------------------------------
# Take a quick look at the data structure

books = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/Books.csv",delimiter=",",encoding="latin-1",on_bad_lines="skip",low_memory=False)
users = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/Users.csv",delimiter=",",encoding="latin-1",on_bad_lines="skip",low_memory=False)
ratings = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/Ratings.csv",delimiter=",",encoding="latin-1",on_bad_lines="skip",low_memory=False)


print("Books dataset : ")
print(books.head(),"\n")

print("Users dataset :")
print(users.head(),"\n")

print ("Ratings dataset :")
print(ratings.head(),"\n")

#all instance is useful in our case?

print("Books info : ")
books.info()
#There are 8 columns to caracterize books. For each instance, there are 271360 values. All columns are object.

print("\nUsers info : ")
users.info()
#There are 3 columns to caracterize users informations. For each instance, there are 278858 values. User-ID is a integer, location is an object and the age is a float.

print("\nRatings info : ")
ratings.info()
#There are 3 columns to caracterize ratings. For each instance, there are 1149780 values. User-ID and Book-Rating are integers, while ISBN is an object.

#STEP 1 : Analyze data
print("=== STEP 1 : Analyze data ===")
#Initial dimensions
print(f"Books : {books.shape}")
print(f"Users : {users.shape}")
print(f"Ratings : {ratings.shape}")

#Missing values
print("\n---Missing values---")
print("Books : ")
missing_values_books = books.isnull().sum()
print(missing_values_books[missing_values_books > 0]) #Show only columns with missing values
print("Users : ")
missing_values_users = users.isnull().sum()
print(missing_values_users[missing_values_users > 0])
print("Ratings : ")
missing_values_ratings = ratings.isnull().sum()
print(missing_values_ratings[missing_values_ratings > 0])

#Duplicates
print ("\n--- Duplicates ---")
print(f"Books duplicates: {books.duplicated(subset=['ISBN']).sum()}")
print(f"Ratings duplicates: {ratings.duplicated().sum()}")


#STEP 2 : Cleaning data


#1.Remove duplicates
books.drop_duplicates(subset=['ISBN'],inplace=True) #each book should have a unique ISBN, so we keep one per book
ratings.drop_duplicates(inplace=True) #some users might have rated the same book twice
users.drop_duplicates(subset=['User-ID'],inplace=True) #each user should appear once

#2.Remove missing values
#Books : drop rows where Book-Title or Book-Author is missing
books.dropna(subset=['Book-Title','Book-Author'],inplace=True)
#Ratings : normally no missing values, but keep for safety
ratings.dropna(subset=['User-ID','ISBN','Book-Rating'],inplace=True)
#Users : drop rows where User-ID is missing (shoud not happen)
users.dropna(subset=['User-ID'],inplace=True)
# Optional: drop Age column because too many missing values and not useful
#if 'Age' in users.columns:
#    users.drop(columns=['Age'], inplace=True)

#3.Keep only active users (those who rated more than 5 books)
user_counts = ratings['User-ID'].value_counts()
ratings = ratings[ratings['User-ID'].isin(user_counts[user_counts>5].index)]

#4.Keep only popular books (those with more than 3 ratings)
book_counts = ratings['ISBN'].value_counts()
ratings = ratings[ratings['ISBN'].isin(book_counts[book_counts >3].index)]

#Show final shapes
print("Cleaned data :")
print(f"Books : {books.shape}")
print(f"Ratings : {ratings.shape}")
print(f"Users : {users.shape}")

#Pour Books, on passe de 271360 à 271358 instances. On en a supprimé seulement deux.
#Pour Ratings on passe de 1149780 à 648799. On a supprimé peut être la moitié des ratings.

#Save cleaned files
books.to_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/books_clean.csv",index=False)
ratings.to_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/ratings_clean.csv",index=False)
users.to_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/users_clean.csv", index=False)

#STEP 3 : Exploratory Data Analysis (EDA)
# Reload cleaned data (optional if you already have them in memory)
books = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/books_clean.csv")
users = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/users_clean.csv")
ratings = pd.read_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/ratings_clean.csv")

#1. Basic statistics for Ratings

print("Ratings statistics : ")
print(ratings['Book-Rating'].describe())

#Remove implicit ratings (0) if needed
ratings = ratings[ratings['Book-Rating'] > 0] 

print("\nAfter removing implicit ratings (0):")
print(ratings['Book-Rating'].describe())

# Before removing 0-ratings, most values were 0 (implicit ratings), meaning many users did not explicitly rate books.
# After removing them, the average rating is around 7.7 — users tend to give high scores (positive bias in ratings).


#2.Distribution of Ratings

plt.figure(figsize=(8,5))
sns.countplot(x='Book-Rating', data=ratings, palette='viridis')
plt.title("Distribution of Book Ratings (1–10)")
plt.xlabel("Book Rating")
plt.ylabel("Count")
plt.show()

# The distribution is highly skewed towards high ratings (8–10).
# Very few low ratings (<5) — users mostly rate books they like.
# This bias can affect recommendation results.


#3. Most rated books
top_books = ratings['ISBN'].value_counts().head(10)
print("\nTop 10 most rated books :")
print(top_books)

# The most rated books are likely best-sellers or very popular titles.
# Popular books are overrepresented, which may bias recommendations towards them.


#4. Most active users 
top_users = ratings['User-ID'].value_counts().head(10)
print("\nTop 10 most active users:")
print(top_users)

# A few users are extremely active and rated hundreds of books.
# These "power users" can strongly influence collaborative filtering models.
# The dataset is imbalanced — most users rated only a few books.


plt.figure(figsize=(8,5))
sns.barplot(x=top_users.index.astype(str), y=top_users.values, palette='coolwarm')
plt.title("Top 10 Most Active Users")
plt.xlabel("User ID")
plt.ylabel("Number of Ratings")
plt.show()

#5. Correlation check (numeric only)
plt.figure(figsize=(5,3))
sns.heatmap(ratings.corr(numeric_only=True), annot=True, cmap='coolwarm')
plt.title("Correlation Matrix (Ratings dataset)")
plt.show()

# There is almost no correlation between User-ID and Book-Rating (as expected).
# Since most variables are categorical, a correlation matrix is not very informative here.

#STEP 3 : Merge data
#We merge the datasets to combine user, book, and rating information into a single structure. 
# This allows us to build a complete view of which users rated which books, enabling meaningful analysis and recommendation modeling.

# Merge ratings with book information
ratings_books = pd.merge(ratings, books, on='ISBN', how= 'inner')

#Merge with users (using User-ID)
ratings_books_users = pd.merge(ratings_books,users,on='User-ID',how='inner')

print("Merged dataset shape : ",ratings_books_users.shape)
print(ratings_books_users.head())

#Save merged dataset
ratings_books_users.to_csv("/Users/chloexie/Documents/3A IMT/Keio/computer science/book_recommendation_project/data/merged_clean.csv", index=False)

#Create the User-Item Matrix 

user_item_matrix = ratings.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')

print("User-Item matrix shape:", user_item_matrix.shape)
print(user_item_matrix.head())

# The user-item matrix represents users as rows and books as columns.
# Each cell contains the rating a user gave to a book (NaN if not rated).
# This matrix is the foundation for collaborative filtering models.

print(user_item_matrix.isnull().sum().sum())  # Count missing ratings (NaN)
# Visualize sparsity of the user-item matrix
plt.figure(figsize=(8,6))
plt.spy(user_item_matrix, markersize=1, color='black')
plt.title("User-Item Matrix Sparsity")
plt.xlabel("Books")
plt.ylabel("Users")
plt.show()

# The plot shows that the matrix is extremely sparse, meaning most users have rated only a few books.
# This sparsity is typical in recommendation systems and is a key challenge to handle when training models.
