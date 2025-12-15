# Movie Function Library
This is our group project for INST326.
We’re building a Python library that can help search, clean, and recommend movies like a mini version of Netflix.

## Team Members
- Kristina Mathurin — Search & Retrieval
— Johnny Data Validation
- Jimmy Recommendations & Analytics

## How It Works
We’re each making 3–5 functions inside one main Python file called `movie_lib.py`.

Example:
```python
def validate_year(year):
    """Check if a movie year is valid."""
    return 1888 <= int(year) <= 2100
```



## Polymorphism

For Project 3, I added polymorphism to our movie recommendation system.

We already had a base abstract class called `BaseRecommender`, and two subclasses:
- `GenreRecommender`
- `RatingRecommender`

To show polymorphism, I added a method in the base class called `describe()`.  
Each subclass overrides this method to explain its own recommendation strategy.

**BaseRecommender**
```python
def describe(self):
    return "Base recommendation strategy."

## Video Presentation

Project 4 video presentation demonstrating system functionality, data persistence, testing, and team collaboration:

https://drive.google.com/file/d/1914B_zw9sRIvdPhQt_I5tXlcJGSyn4d8/view?usp=drive_link
