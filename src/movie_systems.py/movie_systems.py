from src.movie_lib import search_movies, filter_by_genre, recommend_by_rating
from datetime import datetime


try:
    from src.movie_lib import search_movies, filter_by_genre, recommend_by_rating
except Exception:
    # fallback stubs so file still runs
    def search_movies(movies, query):
        q = query.lower()
        return [m for m in movies if q in m.title.lower()]

    def filter_by_genre(movies, genre):
        g = genre.lower()
        return [m for m in movies if g in [x.lower() for x in m.genres]]

    def recommend_by_rating(movies, min_rating):
        return [m for m in movies if getattr(m, "rating", None) and m.rating >= min_rating]


class MovieCatalog:
    """Stores all Movie objects and connects to our Project 1 functions."""

    def __init__(self, name, max_size=5000):
        if not name.strip():
            raise ValueError("Catalog name cannot be empty")
        if max_size <= 0:
            raise ValueError("Max size must be positive")

        self._catalog_id = f"CAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._name = name.strip()
        self._max_size = max_size
        self._movies = {}   # {movie_id: Movie}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("Catalog name cannot be empty")
        self._name = value.strip()

    @property
    def movies(self):
        """Return all movies as a list."""
        return list(self._movies.values())

    def add_movie(self, movie):
        """Add a Movie to the catalog."""
        # we don't redefine Movie here b/c your teammate already did it
        if len(self._movies) >= self._max_size:
            raise RuntimeError("Catalog is full")

        # use the movie_id from the Movie class
        self._movies[movie.movie_id] = movie

    def remove_movie(self, movie_id):
        """Remove movie from catalog if exists."""
        self._movies.pop(movie_id, None)

    def find_by_title(self, query):
        """Search movies by title using our Project 1 search function."""
        return search_movies(self.movies, query)

    def filter_by_genre(self, genre):
        """Filter movies by genre using our Project 1 function."""
        return filter_by_genre(self.movies, genre)

    def top_rated(self, min_rating=7.0):
        """Return only movies at or above the given rating."""
        return recommend_by_rating(self.movies, min_rating)

    def count(self):
        """Return how many movies are in the catalog."""
        return len(self._movies)

    def __str__(self):
        return f"MovieCatalog '{self._name}' ({len(self._movies)} movies)"
