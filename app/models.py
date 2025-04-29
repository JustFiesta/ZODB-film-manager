import datetime
from persistent import Persistent
from persistent.list import PersistentList

class Person(Persistent):
    """Reprezentuje osobę - aktora lub reżysera"""
    def __init__(self, name):
        self.name = name
        self.movies_directed = PersistentList()  # Filmy wyreżyserowane przez osobę
        self.movies_acted = PersistentList()     # Filmy, w których osoba grała

    def __repr__(self):
        return f"<Person {self.name}>"

class Genre(Persistent):
    """Reprezentuje gatunek filmowy"""
    def __init__(self, name):
        self.name = name
        self.movies = PersistentList()  # Filmy należące do tego gatunku

    def __repr__(self):
        return f"<Genre {self.name}>"

class Movie(Persistent):
    """Reprezentuje film"""
    def __init__(self, title, director, year):
        self.title = title            # Tytuł filmu
        self.director = director      # Reżyser (obiekt Person)
        self.year = year              # Rok produkcji
        self.genres = PersistentList()  # Lista gatunków (obiekty Genre)
        self.cast = PersistentList()    # Lista aktorów (obiekty Person)
        self.date_watched = None        # Data obejrzenia filmu
        self.rating = None              # Ocena (1-10)
        self.comment = ""               # Komentarz/recenzja
        self.date_added = datetime.datetime.now()  # Data dodania do bazy

        # Dodaj ten film do listy filmów wyreżyserowanych przez reżysera
        if hasattr(director, 'movies_directed') and self not in director.movies_directed:
            director.movies_directed.append(self)

    def add_genre(self, genre):
        """Dodaje gatunek do filmu i aktualizuje dwukierunkową relację"""
        if genre not in self.genres:
            self.genres.append(genre)
            if self not in genre.movies:
                genre.movies.append(self)

    def add_actor(self, actor):
        """Dodaje aktora do obsady filmu i aktualizuje dwukierunkową relację"""
        if actor not in self.cast:
            self.cast.append(actor)
            if self not in actor.movies_acted:
                actor.movies_acted.append(self)

    def rate(self, score, comment=""):
        """Ocenia film w skali 1-10 z opcjonalnym komentarzem"""
        if 1 <= score <= 10:
            self.rating = score
            self.comment = comment

    def watch(self, date=None):
        """Oznacza film jako obejrzany z opcjonalną datą obejrzenia"""
        if date is None:
            date = datetime.datetime.now()
        self.date_watched = date

    def __repr__(self):
        return f"<Movie {self.title} ({self.year})>"
