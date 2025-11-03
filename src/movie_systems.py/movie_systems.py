# src/movie_systems.py

from datetime import datetime
from src.movie_lib import search_movies, filter_by_genre, recommend_by_rating


class MovieCatalog:
    """
    Stores Movie objects and connects to our Project 1 functions.

    This class is responsible for:
    - keeping track of all movies in one place
    - giving us search/filter/recommend features
    - making sure the catalog doesn't go over a max size
    """

    def __init__(self, name: str, max_size: int = 5000):
        """Create a new movie catalog.

        Args:
            name (str): name of the catalog (ex: "Fall 2025 Movies")
            max_size (int): max number of movies we want to store

        Raises:
            ValueError: if name is empty or max_size is not positive
        """
        if not name.strip():
            raise ValueError("Catalog name cannot be empty.")
        if max_size <= 0:
            raise ValueError("max_size must be positive.")

        # make a simple id so we can tell catalogs apart
        self._catalog_id = f"CAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._name = name.strip()
        self._max_size = max_size
        # we expect Movie objects from the other class in the project
        self._movies: dict[str, object] = {}   # {movie_id: Movie}

    @property
    def name(self) -> str:
        """Return the catalog name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Update the catalog name (can't be blank)."""
        if not value.strip():
            raise ValueError("Catalog name cannot be empty.")
        self._name = value.strip()

    @property
    def movies(self) -> list:
        """Return all movies as a list (read-only for outside)."""
        return list(self._movies.values())

    def add_movie(self, movie) -> None:
        """Add a Movie object to the catalog.

        Note: we assume the Movie class already has `movie_id`.
        """
        if len(self._movies) >= self._max_size:
            raise RuntimeError("Catalog is full.")
        # avoid overwriting the same movie
        self._movies[movie.movie_id] = movie

    def remove_movie(self, movie_id: str) -> None:
        """Remove a movie from the catalog if it exists."""
        self._movies.pop(movie_id, None)

    def search(self, query: str) -> list:
        """Use our Project 1 search to find movies by title/keywords."""
        return search_movies(self.movies, query)

    def filter(self, genre: str) -> list:
        """Use our Project 1 filter to get only movies from one genre."""
        return filter_by_genre(self.movies, genre)

    def recommend(self, min_rating: float = 7.0) -> list:
        """Use our Project 1 recommend function to show top movies."""
        return recommend_by_rating(self.movies, min_rating)

    def count(self) -> int:
        """How many movies are currently stored."""
        return len(self._movies)

    def __str__(self) -> str:
        return f"MovieCatalog('{self._name}', {len(self._movies)} movies)"

    def __repr__(self) -> str:
        return f"MovieCatalog(name={self._name!r}, max_size={self._max_size})"
    

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
