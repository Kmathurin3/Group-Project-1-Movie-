# Kristina Mathurin - Search and Retrieval

def parse_search_query(query):
    """Take what the user types in and turn it into simple keywords."""
    if not isinstance(query, str):
        return []
    query = query.lower()
    words = ""
    for ch in query:
        if ch.isalnum() or ch.isspace():
            words += ch
        else:
            words += " "
    return words.split()


def clean_text_content(text):
    """Clean up text by taking out symbols, HTML, and extra spaces."""
    if not isinstance(text, str):
        return ""
    import re
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip()


def filter_movies(movies, genre=None, min_rating=None, year=None):
    """Filter movies by genre, rating, or year to narrow down results."""
    results = []
    for movie in movies:
        if genre and genre.lower() not in [g.lower() for g in movie.get("genres", [])]:
            continue
        if min_rating and movie.get("rating", 0) < min_rating:
            continue
        if year and movie.get("year") != year:
            continue
        results.append(movie)
    return results


def paginate(movie_list, page_size, page_number):
    """Show a certain number of movies per page."""
    start = (page_number - 1) * page_size
    end = start + page_size
    return movie_list[start:end]


def search_catalog(movies, query):
    """Find movies that match the user’s search keywords."""
    keywords = parse_search_query(query)
    results = []
    for movie in movies:
        text = f"{movie.get('title', '')} {movie.get('description', '')}".lower()
        match = True
        for word in keywords:
            if word not in text:
                match = False
                break
        if match:
            results.append(movie)
    return results

# Jimmy Tolton - Recommendations and Analytics


def search_movies_by_title(movies, keyword):
    """Return movies that have the keyword in their title."""
    if not isinstance(keyword, str) or not keyword.strip():
        return []
    keyword = keyword.lower()
    results = []
    for movie in movies:
        title = movie.get('title', '').lower()
        if keyword in title:
            results.append(movie)
    return results


def trending_movies(movies, top_n=5):
    """Return the top N movies based on number of ratings."""
    if not isinstance(top_n, int) or top_n <= 0:
        top_n = 5
    movies_sorted = movies[:]
    movies_sorted.sort(key=lambda m: len(m.get('ratings', [])), reverse=True)
    return movies_sorted[:top_n]


def recommend_by_genre(users, username, movies, genre):
    """Recommend movies of a specific genre that the user hasn't watched."""
    if username not in users or not isinstance(genre, str) or not genre.strip():
        return []
    genre = genre.lower()
    watched = users[username].get('watch_history', [])
    recommendations = []
    for movie in movies:
        title = movie.get('title', '')
        movie_genre = movie.get('genre', '').lower()
        if title and genre in movie_genre and title not in watched:
            recommendations.append(movie)
    return recommendations


def filter_movies_by_genre_and_year(movies, genre=None, year=None):
    """Return movies that match a given genre and/or release year."""
    results = []
    for movie in movies:
        title = movie.get('title', '')
        movie_genre = movie.get('genre', '').lower()
        movie_year = movie.get('year')
        if title:
            if genre and genre.lower() not in movie_genre:
                continue
            if year and movie_year != year:
                continue
            results.append(movie)
    return results


def recommend_trending_unwatched(users, username, movies, top_n=5):
    """Recommend trending movies that the user hasn't watched yet."""
    if username not in users:
        return []
    watched = users[username].get('watch_history', [])
    movies_sorted = movies[:]
    movies_sorted.sort(key=lambda m: len(m.get('ratings', [])), reverse=True)
    recommendations = []
    for movie in movies_sorted:
        if movie.get('title', '') not in watched:
            recommendations.append(movie)
        if len(recommendations) >= top_n:
            break
    if len(recommendations) < top_n:
        for movie in movies:
            if movie.get('title', '') not in watched and movie not in recommendations:
                recommendations.append(movie)
            if len(recommendations) >= top_n:
                break
    return recommendations

# Jonathan Bressman - Analytics and Reporting

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
        rating = movie.get("rating")
        if isinstance(rating, (int, float)):
            rated.append((movie.get("title", ""), rating))
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
    from datetime import datetime, timedelta
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
            time = datetime.fromisoformat(time)
        except Exception:
            continue
        if time >= cutoff:
            movie = event.get("movie_id")
            if movie:
                counts[movie] = counts.get(movie, 0) + 1

    sorted_movies = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies

def make_usage_report(movies, watch_events):
    """Make a short report showing totals and top movies."""
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
