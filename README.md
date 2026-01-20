# book_recommendation_project

## Overview

This project aims to develop a book recommendation web application that suggests books to users based on their preferences and previous ratings.
The system combines data analysis and machine learning techniques to provide personalized book suggestions.
A simple web interface will be implemented locally to allow users to input their preferences and receive personalized book suggestions. On this interface, users will either be able to enter the titles of books they liked to get similar recommendations, or select metadata such as genre or author to receive the most popular or highly rated books matching their criteria.

The main objective is to demonstrate how data science can enhance user experience in digital reading platforms by learning from user behavior.

## Dataset 
The project uses the public Book Recommendation Dataset available on [Kaggle](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset/data).

| File  | Description     |
|-------|--------------------------------------------|
|  `Books.csv ` | Contains metadata such as title, author, and publication year.  | 
|  `Users.csv `   | Contains user demographic data (location, age). | 
|  `Ratings.csv ` | Links users to the books they have rated.  | 

After cleaning and processing, these datasets, are used to build a recommendation model. 

## Methodology
The project follow several key stages : 
1. Data Exploration & Cleaning
    - Remove duplicates and missing values.
    - Drop or modify some columns
    - Filter out users and books with very few ratings.
    - Analyze rating distribution and detect potential biases.
2. Model Building, Recommendation Methods
    - Implement Item-Based Collaborative Filtering:
        - Builds a **Book-User matrix**
        - Compute **cosine similarity** between books based on user ratings.
        - Recommends books that are most similar to the user’s favorite books.
        - Particularly suitable since no user login system is required.
        - Implemented in `recommendation_collab.py`  
    - Metadata-Based Recommendation: 
        - Uses enriched book metadata retrieved from the **Google Books API**.
        - Allows filtering by: Author, Category, Language, Publisher, Publication year range and Number of pages range.
        - Returns the top 5 highest-rated books matching the selected criteria
        - Implemented in `enrich_books_metadata.py`

3. Web Application 
    - The user interface is built with **Streamlit** (`app.py`) and offers:
        - A selection between **favorite-books mode** and **metadata mode**.
        - Dropdown menus and sliders for easy interaction.
        - Display of recommended books with titles, authors, covers, and descriptions.
        - Run locally with:
        ```bash
        streamlit run app.py
        ```



## Implementation Details 

- Language : Python
- Librairies : 
    - `pandas `,  `numpy ` – data processing
    - `matplotlib, seaborn ` – visualization
    - `scikit-learn ` – cosine similarity (machine learning)
    - `streamlit` – web application
    - `requests` – Google Books API
- Data formats : CSV, Pickle (`.pkl`)
- Expected Size: 1000–1500 lines of code


## 📁 Project Structure

```
book_recommendation_project/
├── app/
│   ├── app.py                    # Streamlit application
│
├── assets/
│   ├── BookCoverNotFound.png     # For books with no cover
│
├── data/
│   ├── Books.csv
│   ├── Users.csv
│   ├── Ratings.csv
│   ├── books_clean.csv
│   ├── ratings_clean.csv
│   ├── users_clean.csv
│   ├── book_similarity.pkl
│   ├── book_user_matrix.pkl
│   ├── books_enriched.pkl
│
├── src/
│   ├── exploration.py            # Data exploration and cleaning
│   ├── recommendation_collab.py  # Item-based collaborative filtering
│   ├── enrich_books_metadata.py  # Google Books API enrichment
│
├── venv
├── .gitignore
├── requirements.txt
└── README.md
```


## How to run 
1. Clone the repesoritory

```bash
git clone https://github.com/chloexie02/book_recommendation_project.git
cd book_recommendation_project
```

2. Create a virtual environment and install dependencies 

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Launch the application:

```bash
streamlit run app.py
```




## Author
Xie Chloe

Keio University