# src/persistence.py

import json
from pathlib import Path


def _movie_to_dict(movie):
    """Convert a Movie object (or dict) into a JSON-safe dict."""
    if isinstance(movie, dict):
        data = dict(movie)
        data.setdefault("movie_id", data.get("movie_id") or data.get("id"))
        data.setdefault("title", data.get("title", ""))
        data.setdefault("genre", data.get("genre", ""))
        data.setdefault("year", data.get("year", 0))
        data.setdefault("ratings", data.get("ratings", []))
        return data

    movie_id = getattr(movie, "movie_id", None)
    title = getattr(movie, "title", "")
    genre = getattr(movie, "genre", "")
    year = getattr(movie, "year", 0)

    ratings = []
    if hasattr(movie, "_ratings"):
        ratings = list(getattr(movie, "_ratings", []))
    elif hasattr(movie, "ratings"):
        try:
            ratings = list(getattr(movie, "ratings"))
        except Exception:
            ratings = []

    return {
        "movie_id": movie_id,
        "title": title,
        "genre": genre,
        "year": year,
        "ratings": ratings,
    }


def _user_to_dict(user):
    """Convert a User object (or dict) into a JSON-safe dict."""
    if isinstance(user, dict):
        data = dict(user)
        data.setdefault("username", data.get("username", ""))
        data.setdefault("watched_titles", data.get("watched_titles", []))
        return data

    username = getattr(user, "username", "")
    watched_titles = []
    if hasattr(user, "list_watched"):
        try:
            watched_titles = list(user.list_watched())
        except Exception:
            watched_titles = []

    return {
        "username": username,
        "watched_titles": watched_titles,
    }


def save_system_state(path, catalog, users, watch_log):
    """Save the full system state to a JSON file.

    Args:
        path (str | Path): Where to save the JSON.
        catalog: MovieCatalog object (must have .movies).
        users (dict): {username: User}
        watch_log: WatchLog object (must have .events)

    Raises:
        ValueError: If required objects are missing needed attributes.
        OSError: If file cannot be written.
    """
    if not hasattr(catalog, "movies"):
        raise ValueError("catalog must have a movies attribute/property")
    if not isinstance(users, dict):
        raise ValueError("users must be a dict of {username: User}")
    if not hasattr(watch_log, "events"):
        raise ValueError("watch_log must have an events attribute/property")

    movies_data = [_movie_to_dict(m) for m in catalog.movies]
    users_data = [_user_to_dict(u) for u in users.values()]
    events_data = list(watch_log.events)

    payload = {
        "movies": movies_data,
        "users": users_data,
        "watch_events": events_data,
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_system_state(path):
    """Load system state from a JSON file.

    Returns:
        dict: {"movies": [...], "users": [...], "watch_events": [...]}

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If JSON is invalid or missing required keys.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No saved state found at: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Saved state is not valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("Saved state JSON must be an object/dict")

    movies = data.get("movies", [])
    users = data.get("users", [])
    watch_events = data.get("watch_events", [])

    if not isinstance(movies, list) or not isinstance(users, list) or not isinstance(watch_events, list):
        raise ValueError("Saved state must contain lists for movies, users, watch_events")

    return {
        "movies": movies,
        "users": users,
        "watch_events": watch_events,
    }

