# tests/test_system.py

import unittest
import tempfile
from pathlib import Path

from src.movie_systems import MovieCatalog, MovieSystem
from src.persistence import load_system_state


class DummyUser:
    """Simple user stub for system tests."""

    def __init__(self, username):
        self._username = username

    @property
    def username(self):
        return self._username

    def list_watched(self):
        return []


class TestSystem(unittest.TestCase):
    # 1) End-to-end: import CSV -> add user -> log -> report -> export JSON
    def test_end_to_end_import_log_report_export(self):
        catalog = MovieCatalog("Test")
        system = MovieSystem(catalog)
        system.add_user(DummyUser("u1"))

        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "movies.csv"
            csv_path.write_text("title,genre,year\nMovie A,Action,2020\n", encoding="utf-8")

            system.import_movies_csv(csv_path)
            self.assertEqual(system.catalog.count(), 1)

            system.log_finish("u1", "CSV-1", watch_seconds=15)
            report = system.usage_report()
            self.assertIn("Totals", report)

            out_path = Path(tmp) / "report.json"
            system.export_usage_report_json(out_path)
            self.assertTrue(out_path.exists())

    # 2) Save -> Load -> state contains movies/events
    def test_save_and_load_state_roundtrip(self):
        catalog = MovieCatalog("Test")
        system = MovieSystem(catalog)
        system.add_user(DummyUser("u1"))

        catalog._movies["m1"] = {"movie_id": "m1", "title": "T", "genre": "Action", "year": 2020, "ratings": []}
        system.log_finish("u1", "m1", watch_seconds=10)

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            system.save(state_path)

            data = load_system_state(state_path)
            self.assertEqual(len(data["movies"]), 1)
            self.assertEqual(len(data["watch_events"]), 1)

    # 3) Load missing file should raise FileNotFoundError
    def test_load_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.json"
            with self.assertRaises(FileNotFoundError):
                load_system_state(missing)

    # 4) Corrupt JSON should raise ValueError
    def test_load_corrupt_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_system_state(bad)

    # 5) Save state, load into new system, verify catalog and watch log rebuilt
    def test_system_load_rebuilds_objects(self):
        catalog1 = MovieCatalog("Test1")
        system1 = MovieSystem(catalog1)
        system1.add_user(DummyUser("u1"))
        catalog1._movies["m1"] = {"movie_id": "m1", "title": "T", "genre": "Action", "year": 2020, "ratings": []}
        system1.log_finish("u1", "m1", watch_seconds=12)

        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            system1.save(state_path)

            catalog2 = MovieCatalog("Test2")
            system2 = MovieSystem(catalog2)
            system2.load(state_path)

            self.assertEqual(system2.catalog.count(), 1)
            self.assertEqual(system2.watch_log.count(), 1)


if __name__ == "__main__":
    unittest.main()

