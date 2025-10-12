"""
movie_lib.py — Function library for our Movie Recommendation System
Each person will add their 3–5 functions in this file.
"""

def validate_year(year):
    """Check if the movie year is valid (between 1888 and 2100)."""
    try:
        y = int(year)
        return 1888 <= y <= 2100
    except ValueError:
        return False
