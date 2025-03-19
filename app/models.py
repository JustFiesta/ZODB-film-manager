from persistent import Persistent

class Movie(Persistent):
    def __init__(self, title, director, year):
        self.title = title
        self.director = director
        self.year = year

    def __repr__(self):
        return f"<Movie {self.title} ({self.year}), directed by {self.director}>"
