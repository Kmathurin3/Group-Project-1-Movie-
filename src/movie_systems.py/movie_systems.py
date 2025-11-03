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


class Movie:
    """
    Represents a movie with title, genre, year, and viewer ratings.
    """

    def __init__(self, title: str, genre: str, year: int):
        if not title.strip():
            raise ValueError("Movie title cannot be empty.")
        self._title = title
        self._genre = genre
        self._year = year
        self._ratings = []  # list of floats

    @property
    def title(self) -> str:
        """Get the movie title."""
        return self._title

    @property
    def genre(self) -> str:
        """Get the movie genre."""
        return self._genre

    @property
    def year(self) -> int:
        """Get the movie release year."""
        return self._year

    def add_rating(self, rating: float):
        """
        Add a rating between 0 and 5 (inclusive).
        Raises ValueError if out of range.
        """
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5.")
        self._ratings.append(rating)

    def average_rating(self) -> float:
        """
        Compute and return the average rating.
        Returns 0.0 if no ratings exist.
        """
        if not self._ratings:
            return 0.0
        return sum(self._ratings) / len(self._ratings)

    def __str__(self) -> str:
        """String representation of a movie."""
        avg = self.average_rating()
        return f"{self._title} ({self._year}) - {self._genre} | Avg Rating: {avg:.1f}"



class User:
    """
    Represents a user who can watch and rate movies.
    """

    def __init__(self, username: str):
        if not username.strip():
            raise ValueError("Username cannot be empty.")
        self._username = username
        self._watched = {}  # {Movie: rating}

    @property
    def username(self) -> str:
        """Return the username."""
        return self._username

    def watch_movie(self, movie: Movie, rating: float | None = None):
        """
        Record that a user has watched a movie and optionally rated it.
        """
        self._watched[movie] = rating
        if rating is not None:
            try:
                movie.add_rating(rating)
            except ValueError as e:
                print(f"[Error] {e} — rating not added for '{movie.title}'")

    def has_watched(self, movie: Movie) -> bool:
        """Check if the user has watched a given movie."""
        return movie in self._watched

    def list_watched(self):
        """Return a list of watched movie titles."""
        return [m.title for m in self._watched]

    def __str__(self) -> str:
        """Readable representation of user activity."""
        count = len(self._watched)
        return f"User: {self._username} | Movies watched: {count}"

# Jonathan Bressman - WatchLog and AnalyticsReporting

class WatchLog:

    """ Stores watch events in a simple, validated list. """

    def __init__(self, events=None):
        self._events = []
        if events:
            for e in events:
                self.add_event(
                    user_id=e.get("user_id"),
                    movie_id=e.get("movie_id"),
                    event=e.get("event"),
                    timestamp=e.get("timestamp"),
                    watch_seconds=e.get("watch_seconds", 0),
                )

    @property
    def events(self):
        return [dict(e) for e in self._events]

    def _to_iso(self, ts):
        if ts is None:
            return datetime.utcnow().isoformat()
        if isinstance(ts, str):
            try:
                datetime.fromisoformat(ts)
                return ts
            except Exception:
                raise ValueError(f"Invalid ISO timestamp: {ts}")
        if isinstance(ts, datetime):
            return ts.isoformat()
        raise ValueError("timestamp must be ISO string or datetime")

    def add_event(self, user_id, movie_id, event, timestamp=None, watch_seconds=0):
        if not user_id:
            raise ValueError("user_id is required")
        if not movie_id:
            raise ValueError("movie_id is required")
        if event not in {"start", "finish", "rate"}:
            raise ValueError('event must be one of: "start", "finish", "rate"')
        if watch_seconds is None:
            watch_seconds = 0
        if not isinstance(watch_seconds, (int, float)) or watch_seconds < 0:
            raise ValueError("watch_seconds must be a positive number")

        iso = self._to_iso(timestamp)
        self._events.append({
            "user_id": user_id,
            "movie_id": movie_id,
            "event": event,
            "timestamp": iso,
            "watch_seconds": int(watch_seconds),
        })

    def count(self):
        return len(self._events)

    def unique_users(self):
        users = set(e["user_id"] for e in self._events if e.get("user_id") is not None)
        return len(users)

    def finishes_for_movie(self, movie_id):
        return sum(1 for e in self._events if e.get("movie_id") == movie_id and e.get("event") == "finish")

    def recent_finishes(self, n_days=7):
        if n_days <= 0:
            raise ValueError("n_days must be > 0")
        cutoff = datetime.utcnow() - timedelta(days=n_days)
        counts = {}
        for e in self._events:
            if e.get("event") != "finish":
                continue
            try:
                ts = datetime.fromisoformat(e["timestamp"])
            except Exception:
                continue
            if ts >= cutoff:
                mid = e.get("movie_id")
                if mid:
                    counts[mid] = counts.get(mid, 0) + 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    def __str__(self):
        return f"WatchLog({self.count()} events, {self.unique_users()} users)"

    def __repr__(self):
        return f"WatchLog(events={self.count()})"

def get_most_watched_movies(watch_events, top_n=5):
    """Show the movies that were finished the most times."""
    counts = {}
    for event in watch_events:
        if event.get("event") == "finish":
            movie = event.get("movie_id")
            if movie:
                counts[movie] = counts.get(movie, 0) + 1
    sorted_movies = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies[:top_n]


def get_highest_rated_movies(movies, top_n=5):
    """Show the movies with the highest ratings."""
    rated = []
    for movie in movies:
        if isinstance(movie, dict):
            title = movie.get("title", "")
            r = movie.get("rating", 0)
        else:
            title = getattr(movie, "title", "")
            r = getattr(movie, "rating", 0)
        if isinstance(r, (int, float)):
            rated.append((title, r))
    rated.sort(key=lambda x: x[1], reverse=True)
    return rated[:top_n]


def get_user_engagement(watch_events):
    """Track how much each user has watched and how many movies they finished."""
    engagement = {}
    for event in watch_events:
        user = event.get("user_id")
        if not user:
            continue
        if user not in engagement:
            engagement[user] = {"events": 0, "finishes": 0, "watch_seconds": 0}
        engagement[user]["events"] += 1
        if event.get("event") == "finish":
            engagement[user]["finishes"] += 1
        engagement[user]["watch_seconds"] += event.get("watch_seconds", 0)
    return engagement


def get_average_watch_time(watch_events):
    """Find the average amount of time spent watching per event."""
    times = []
    for e in watch_events:
        if "watch_seconds" in e:
            times.append(e["watch_seconds"])
    if not times:
        return 0
    return sum(times) / len(times)


def check_recommendation_accuracy(recommendations, actual, k=5):
    """See how accurate recommendations were based on what users actually watched."""
    total_precision = 0
    total_recall = 0
    user_count = 0

    for user, rec_list in recommendations.items():
        real_list = actual.get(user, [])
        if not real_list:
            continue
        user_count += 1
        hits = 0
        for movie in rec_list[:k]:
            if movie in real_list:
                hits += 1
        precision = hits / len(rec_list[:k]) if rec_list else 0
        recall = hits / len(real_list) if real_list else 0
        total_precision += precision
        total_recall += recall

    if user_count == 0:
        return {"precision@k": 0, "recall@k": 0}

    return {
        "precision@k": total_precision / user_count,
        "recall@k": total_recall / user_count,
    }


def get_popular_trending_movies(watch_events, recent_days=7):
    """Find movies that have been watched most in the last few days."""
    now = datetime.utcnow()
    cutoff = now - timedelta(days=recent_days)
    counts = {}

    for event in watch_events:
        if event.get("event") != "finish":
            continue
        time = event.get("timestamp")
        if not time:
            continue
        try:
            time_dt = datetime.fromisoformat(time)
        except Exception:
            continue
        if time_dt >= cutoff:
            movie = event.get("movie_id")
            if movie:
                counts[movie] = counts.get(movie, 0) + 1

    sorted_movies = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies


def make_usage_report(movies, watch_events):
    """Make a short report showing totals and top movies (user-facing labels)."""
    total_movies = len(movies)
    total_users = len(set(e.get("user_id") for e in watch_events if e.get("user_id")))
    total_events = len(watch_events)
    avg_watch = get_average_watch_time(watch_events)
    top_views = get_most_watched_movies(watch_events)
    top_rated = get_highest_rated_movies(movies)
    trending = get_popular_trending_movies(watch_events)

    return {
        "Totals": {
            "Total Movies": total_movies,
            "Unique Users": total_users,
            "Total Events": total_events,
            "Average Watch Time (seconds)": round(avg_watch, 2)
        },
        "Top Movies by Views": top_views,
        "Top Movies by Rating": top_rated,
        "Trending Movies": trending
    }

class AnalyticsDashboard:

    """Simple OOP wrapper around analytics helpers. Provides methods to analyze movie and watch event data."""

    def __init__(self, movies, watch_log):
        if not isinstance(movies, list):
            raise ValueError("movies must be a list (of dicts or Movie objects)")
        if not hasattr(watch_log, "events"):
            raise ValueError("watch_log must have an 'events' attribute (e.g., a WatchLog)")
        self._movies = movies
        self._watch_log = watch_log

    @property
    def movies(self):
        return list(self._movies)

    @movies.setter
    def movies(self, value):
        if not isinstance(value, list):
            raise ValueError("movies must be a list")
        self._movies = value

    @property
    def watch_events(self):
        return self._watch_log.events

    def most_watched(self, top_n=5):
        return get_most_watched_movies(self.watch_events, top_n=top_n)

    def highest_rated(self, top_n=5):
        return get_highest_rated_movies(self._movies, top_n=top_n)

    def average_watch_time(self):
        return get_average_watch_time(self.watch_events)

    def trending(self, recent_days=7):
        return get_popular_trending_movies(self.watch_events, recent_days=recent_days)

    def accuracy(self, recommendations, actual, k=5):
        return check_recommendation_accuracy(recommendations, actual, k=k)

    def usage_report(self):
        return make_usage_report(self._movies, self.watch_events)

    def __str__(self):
        return f"AnalyticsDashboard({len(self._movies)} movies, {len(self.watch_events)} events)"

    def __repr__(self):
        return f"AnalyticsDashboard(movies={len(self._movies)}, events={len(self.watch_events)})"
