from .database import DatabaseManager
from .models import Movie

class MovieManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.movies = self.db.get_root().movies

    def add_movie(self, title, director, year):
        if title in self.movies:
            return False
        self.movies[title] = Movie(title, director, year)
        self.db.commit()
        return True

    def get_movie(self, title):
        return self.movies.get(title, None)

    def update_movie(self, title, new_director=None, new_year=None):
        movie = self.movies.get(title)
        if not movie:
            return False

        if new_director:
            movie.director = new_director
        if new_year:
            movie.year = new_year

        self.db.commit()
        return True

    def delete_movie(self, title):
        if title in self.movies:
            del self.movies[title]
            self.db.commit()
            return True
        return False

    def list_movies(self):
        return list(self.movies.values())

    def close(self):
        self.db.close()
