# tests/test_units.py

import unittest
from datetime import datetime

from src.movie_systems import (
    WatchLog,
    get_average_watch_time,
    get_most_watched_movies,
    get_user_engagement,
    check_recommendation_accuracy,
)
from src.persistence import save_system_state, load_system_state


class DummyCatalog:
    """Small catalog stub for persistence unit tests."""
    def __init__(self, movies):
        self._movies = movies

    @property
    def movies(self):
        return list(self._movies)


class DummyWatchLog:
    """Small watch log stub for persistence unit tests."""
    def __init__(self, events):
        self._events = events

    @property
    def events(self):
        return list(self._events)


class TestWatchLogUnit(unittest.TestCase):
    def test_add_event_increases_count(self):
        wl = WatchLog()
        wl.add_event(user_id="u1", movie_id="m1", event="finish", watch_seconds=10)
        self.assertEqual(wl.count(), 1)

    def test_add_event_requires_user_id(self):
        wl = WatchLog()
        with self.assertRaises(ValueError):
            wl.add_event(user_id="", movie_id="m1", event="finish")

    def test_add_event_requires_movie_id(self):
        wl = WatchLog()
        with self.assertRaises(ValueError):
            wl.add_event(user_id="u1", movie_id="", event="finish")

    def test_add_event_requires_valid_event(self):
        wl = WatchLog()
        with self.assertRaises(ValueError):
            wl.add_event(user_id="u1", movie_id="m1", event="bad_event")

    def test_add_event_invalid_timestamp_string(self):
        wl = WatchLog()
        with self.assertRaises(ValueError):
            wl.add_event(user_id="u1", movie_id="m1", event="finish", timestamp="not-a-time")

    def test_events_returns_copy(self):
        wl = WatchLog()
        wl.add_event(user_id="u1", movie_id="m1", event="finish")
        events_copy = wl.events
        events_copy.append({"user_id": "x", "movie_id": "y", "event": "finish", "timestamp": datetime.utcnow().isoformat()})
        # original should not change
        self.assertEqual(wl.count(), 1)


class TestAnalyticsFunctionsUnit(unittest.TestCase):
    def test_get_average_watch_time_empty(self):
        self.assertEqual(get_average_watch_time([]), 0)

    def test_get_average_watch_time_basic(self):
        events = [
            {"watch_seconds": 10},
            {"watch_seconds": 30},
        ]
        self.assertEqual(get_average_watch_time(events), 20)

    def test_get_most_watched_movies_counts_finishes_only(self):
        events = [
            {"event": "finish", "movie_id": "m1"},
            {"event": "finish", "movie_id": "m1"},
            {"event": "start", "movie_id": "m1"},
            {"event": "finish", "movie_id": "m2"},
        ]
        top = get_most_watched_movies(events, top_n=2)
        self.assertEqual(top[0], ("m1", 2))

    def test_get_user_engagement_structure(self):
        events = [
            {"user_id": "u1", "event": "finish", "watch_seconds": 10},
            {"user_id": "u1", "event": "start", "watch_seconds": 5},
        ]
        eng = get_user_engagement(events)
        self.assertIn("u1", eng)
        self.assertEqual(eng["u1"]["events"], 2)
        self.assertEqual(eng["u1"]["finishes"], 1)

    def test_check_recommendation_accuracy_no_users(self):
        result = check_recommendation_accuracy({}, {}, k=5)
        self.assertEqual(result["precision@k"], 0)
        self.assertEqual(result["recall@k"], 0)

    def test_check_recommendation_accuracy_simple_case(self):
        recommendations = {"u1": ["m1", "m2", "m3"]}
        actual = {"u1": ["m2", "m4"]}
        result = check_recommendation_accuracy(recommendations, actual, k=2)
        # top 2 recs: m1, m2 -> 1 hit
        self.assertAlmostEqual(result["precision@k"], 0.5)
        # recall: hit / actual size = 1/2
        self.assertAlmostEqual(result["recall@k"], 0.5)


class TestPersistenceUnit(unittest.TestCase):
    def test_save_system_state_validates_inputs(self):
        with self.assertRaises(ValueError):
            save_system_state("state.json", catalog="bad", users={}, watch_log=DummyWatchLog([]))

        with self.assertRaises(ValueError):
            save_system_state("state.json", catalog=DummyCatalog([]), users=[], watch_log=DummyWatchLog([]))

    def test_load_system_state_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_system_state("this_file_should_not_exist_12345.json")


if __name__ == "__main__":
    unittest.main()

