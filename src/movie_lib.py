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
