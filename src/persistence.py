import json
from pathlib import Path


def save_system_state(path, movies, users, watch_events):
    """
    Save the full system state to a JSON file.

    Arguments:
        path (str or Path): File location to save data
        movies (list): List of movie dictionaries
        users (list): List of user dictionaries
        watch_events (list): List of watch event dictionaries
    """
    data = {
        "movies": movies,
        "users": users,
        "watch_events": watch_events
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError as e:
        raise OSError(f"Could not save system state: {e}")


def load_system_state(path):
    """
    Load system state from a JSON file.

    Returns:
        dict: Dictionary with movies, users, and watch_events
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError("Save file does not exist")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        raise ValueError("Save file contains invalid JSON")

    if "movies" not in data or "users" not in data or "watch_events" not in data:
        raise ValueError("Save file is missing required data")

    return data
