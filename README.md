**Movie Listing API**

This FastAPI-based project is a RESTful API that allows users to list movies, add comments, rate them, and manage user authentication using JWT (JSON Web Tokens). 
It ensures that only the movie owner can edit or delete their listings.

**Features**

User Authentication: 
    Registration, login, and JWT-based authentication.
Movie Management: 
    Create, view, edit, and delete movies.
Comments: 
    Add, view, and delete comments on movies.
Ratings: 
    Rate movies and view ratings.


**Tech Stack**

Backend: FastAPI
Database: SQLite (default, configurable)
Authentication: JWT
Testing: Pytest, HTTPX


**Getting Started**

Clone the repo: 
    git clone https://github.com/Oluwatomiyosilorun/movie_listing

Install dependencies: 
    pip install -r requirements.txt

Run the app: 
    uvicorn app.main:app --reload

Access API docs: 
    Visit http://127.0.0.1:8000/docs

Running Tests: Run tests with pytest.


**API Endpoints**
Authentication: 
  * Register (POST /auth/register), 
  * Login (POST /auth/token)

Movies: 
  * Create (POST /movies/), 
  * Read all (GET /movies/), 
  * Read one (GET /movies/{movie_id}), 
  * Update (PUT /movies/{movie_id}), 
  * Delete (DELETE /movies/{movie_id})

Comments: 
  * Add (POST /comments/{movie_id}), 
  * View (GET /comments/{movie_id}), 
  * Delete (DELETE /comments/{comment_id})

Ratings: 
  * Add (POST /ratings/{movie_id}), 
  * View (GET /ratings/{movie_id})


**Database Schema**

The database includes tables for users, movies, comments, and ratings, all linked by foreign keys.


****

**Deployment**

Deployed on render.com. Here is the url https://movie-listing-hdyk.onrender.com/



**Contributing**

Fork the repo, create a feature branch, make your changes, and open a pull request.