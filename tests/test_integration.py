# tests/test_integration.py

import unittest
import tempfile
from pathlib import Path

from src.movie_systems import MovieCatalog, WatchLog, AnalyticsDashboard, MovieSystem
from src.import_export import import_movies_from_csv


class DummyUser:
    """Simple user stub for tests (matches what MovieSystem needs)."""

    def __init__(self, username):
        self._username = username
        self._watched_titles = []

    @property
    def username(self):
        return self._username

    def list_watched(self):
        return list(self._watched_titles)


class TestIntegration(unittest.TestCase):
    # 1) WatchLog + AnalyticsDashboard
    def test_dashboard_most_watched(self):
        catalog = MovieCatalog("Test")
        watch_log = WatchLog()
        watch_log.add_event(user_id="u1", movie_id="m1", event="finish")
        watch_log.add_event(user_id="u2", movie_id="m1", event="finish")
        watch_log.add_event(user_id="u1", movie_id="m2", event="finish")

        dashboard = AnalyticsDashboard(catalog.movies, watch_log)
        top = dashboard.most_watched(top_n=2)

        self.assertEqual(top[0][0], "m1")
        self.assertEqual(top[0][1], 2)

    # 2) WatchLog + AnalyticsDashboard avg watch time
    def test_dashboard_average_watch_time(self):
        catalog = MovieCatalog("Test")
        watch_log = WatchLog()
        watch_log.add_event(user_id="u1", movie_id="m1", event="finish", watch_seconds=40)
        watch_log.add_event(user_id="u1", movie_id="m2", event="finish", watch_seconds=20)

        dashboard = AnalyticsDashboard(catalog.movies, watch_log)
        avg = dashboard.average_watch_time()

        self.assertEqual(avg, 30)

    # 3) MovieSystem + add_user + log_finish updates watch log count
    def test_movie_system_log_finish_increases_events(self):
        catalog = MovieCatalog("Test")
        system = MovieSystem(catalog)
        system.add_user(DummyUser("u1"))

        system.log_finish("u1", "m1", watch_seconds=10)
        self.assertEqual(system.watch_log.count(), 1)

    # 4) MovieSystem + AnalyticsDashboard usage report structure
    def test_movie_system_usage_report_has_expected_keys(self):
        catalog = MovieCatalog("Test")
        system = MovieSystem(catalog)

        # add 2 movies as dicts
        catalog._movies["m1"] = {"movie_id": "m1", "title": "A", "genre": "Action", "year": 2020, "ratings": []}
        catalog._movies["m2"] = {"movie_id": "m2", "title": "B", "genre": "Comedy", "year": 2019, "ratings": []}

        system.add_user(DummyUser("u1"))
        system.log_finish("u1", "m1", watch_seconds=25)

        report = system.usage_report()
        self.assertIn("Totals", report)
        self.assertIn("Top Movies by Views", report)
        self.assertIn("Trending Movies", report)

    # 5) import_movies_from_csv produces list of dict movies (integration with file I/O)
    def test_import_movies_from_csv_reads_movies(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "movies.csv"
            p.write_text("title,genre,year\nMovie A,Action,2020\nMovie B,Comedy,2019\n", encoding="utf-8")

            movies = import_movies_from_csv(p)
            self.assertEqual(len(movies), 2)
            self.assertEqual(movies[0]["title"], "Movie A")

    # 6) MovieSystem.import_movies_csv integrates imported movies into catalog
    def test_movie_system_import_movies_csv_adds_to_catalog(self):
        catalog = MovieCatalog("Test")
        system = MovieSystem(catalog)

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "movies.csv"
            p.write_text("title,genre,year\nMovie A,Action,2020\n", encoding="utf-8")

            system.import_movies_csv(p)
            self.assertEqual(system.catalog.count(), 1)


if __name__ == "__main__":
    unittest.main()

