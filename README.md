# book_recommendation_project

## Overview

This project aims to develop a book recommendation web application that suggests books to users based on their preferences and previous ratings.
The system combines data analysis and machine learning techniques to provide personalized book suggestions.

The main objective is to demonstrate how data science can enhance user experience in digital reading platforms by learning from user behavior.

## Dataset 
The project uses the public Book Recommendation Dataset available on [Kaggle](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset?utm_source=chatgpt.com).

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
    - Filter out users and books with very few ratings.
    - Analyze rating distribution and detect potential biases.
2. Model Building 
    - Create a User-Item Matrix.
    - Implement Collaborative Filtering (user-based similarity using cosine distance).
    - Optionally, extend with a Content-Based approach using book metadata.
3. Evaluation & Visualization
    - Visualize rating distributions, user activity, and book popularity.
    - Generate and test sample recommendations.
4. Web Application (Future Work)
    - Develop an interactive interface (using Flask or Streamlit) where users can input books they liked, receive personalized recommendations and filter results by author or genre.

## Implementation Details 

- Language : Python
- Librairies : 
    -  `pandas `,  `numpy ` : Data analysis
    -  `matplotlib, seaborn ` : Visualization
    -   `scikit-learn ` : Machine learning (cosine similarity)
    - Flask or Streamlit  Web application
- Expected Size: 1000–1500 lines of code

Structured into multiple modules:

- exploration.py : Data exploration & cleaning

- recommendation_collab.py : Collaborative filtering model

- app/ : Web interface

## How to run 
1. Clone the repesoritory

```
git clone https://github.com/chloexie02/book_recommendation_project.git
cd book_recommendation_p
```

2. Create a virtual environment and install dependencies 

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Author
Xie Chloe