# src/import_export.py

import csv
import json
from pathlib import Path


def import_movies_from_csv(path):
    """Import movies from a CSV file.

    Expected columns (case-insensitive):
      - title
      - genre
      - year
    Optional:
      - movie_id

    Returns:
        list[dict]: Each dict has movie_id/title/genre/year/ratings
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    movies = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file has no header row")

        # normalize headers
        headers = [h.strip().lower() for h in reader.fieldnames]

        def get_col(row, name):
            for key in row:
                if key and key.strip().lower() == name:
                    return row.get(key)
            return None

        for i, row in enumerate(reader, start=1):
            title = (get_col(row, "title") or "").strip()
            genre = (get_col(row, "genre") or "").strip()
            year_raw = (get_col(row, "year") or "").strip()
            movie_id = (get_col(row, "movie_id") or "").strip()

            if not title:
                # skip blank rows
                continue

            try:
                year = int(year_raw) if year_raw else 0
            except Exception:
                year = 0

            if not movie_id:
                movie_id = f"CSV-{i}"

            movies.append({
                "movie_id": movie_id,
                "title": title,
                "genre": genre,
                "year": year,
                "ratings": [],
            })

    return movies


def export_report_to_json(report, path):
    """Export an analytics report dict to a JSON file."""
    if not isinstance(report, dict):
        raise ValueError("report must be a dict")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def export_report_to_csv(top_list, path):
    """Export a simple list of (name/value) pairs to CSV.

    Example: top movies by views from get_most_watched_movies:
      [("MOV123", 10), ("MOV555", 7)]
    """
    if not isinstance(top_list, list):
        raise ValueError("top_list must be a list")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "value"])
        for item in top_list:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                writer.writerow([item[0], item[1]])

