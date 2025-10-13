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


               
