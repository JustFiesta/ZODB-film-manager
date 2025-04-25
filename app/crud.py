from .database import DatabaseManager
from .models import Movie, Person, Genre
import datetime
from BTrees.OOBTree import OOBTree

class MovieManager:
    """
    Zarządza operacjami CRUD dla filmów i powiązanych obiektów.
    
    Zapewnia metody do tworzenia, odczytu, aktualizacji i usuwania filmów,
    a także do zarządzania powiązanymi osobami (reżyserzy, aktorzy) i gatunkami.
    """
    
    def __init__(self, db_path=None):
        """Inicjalizuje menedżera filmu z połączeniem do bazy danych."""
        self.db = DatabaseManager(db_path)
        self.root = self.db.get_root()
        self.movies = self.root.movies
        self.persons = self.root.persons
        self.genres = self.root.genres
        self.movies_by_year = self.root.movies_by_year
        self.movies_by_genre = self.root.movies_by_genre
        self.movies_by_director = self.root.movies_by_director

    # ----- Operacje na filmach -----
    
    def add_movie(self, title, director_name, year, actors=None, genres=None, rating=None, comment="", date_watched=None):
        print(f"Dodawanie filmu: {title}")  # Debug
        
        if title in self.root.movies:
            print(f"Film {title} już istnieje")  # Debug
            return False
            
        # Znajdź lub utwórz reżysera
        director = self.get_or_create_person(director_name)
        
        # Utwórz film i dodaj do root
        movie = Movie(title, director, year)
        self.root.movies[title] = movie  # Używamy self.root.movies zamiast self.movies
        
        # Ustaw opcjonalne pola
        if rating is not None:
            movie.rating = rating
        movie.comment = comment
        movie.date_watched = date_watched
        
        # Dodaj aktorów
        if actors:
            for actor_name in actors:
                actor = self.get_or_create_person(actor_name)
                movie.add_actor(actor)
        
        # Dodaj gatunki
        if genres:
            for genre_name in genres:
                self.add_genre_to_movie(title, genre_name)
        
        print(f"Stan bazy przed commitem: {list(self.root.movies.keys())}")  # Debug
        self.db.commit()
        print(f"Stan bazy po commicie: {list(self.root.movies.keys())}")  # Debug
        
        return movie

    def get_movie(self, title):
        """Pobiera film z bazy po tytule."""
        print(f"Próba pobrania filmu: {title}")  # Debug
        print(f"Dostępne filmy: {list(self.root.movies.keys())}")  # Debug
        return self.root.movies.get(title)

    def update_movie(self, title, new_director=None, new_year=None, 
                    new_rating=None, new_comment=None, new_date_watched=None):
        """
        Aktualizuje dane istniejącego filmu.
        
        Args:
            title: Tytuł filmu do aktualizacji
            new_director: Nowy reżyser (opcjonalnie)
            new_year: Nowy rok produkcji (opcjonalnie)
            new_rating: Nowa ocena 1-10 (opcjonalnie)
            new_comment: Nowy komentarz (opcjonalnie)
            new_date_watched: Nowa data obejrzenia (opcjonalnie)
            
        Returns:
            True jeśli aktualizacja się powiodła, False w przeciwnym razie
        """
        movie = self.get_movie(title)
        if not movie:
            return False

        # Usuń z indeksów przed aktualizacją
        self.db.remove_from_indexes(movie)

        # Aktualizacja roku
        if new_year is not None and movie.year != new_year:
            movie.year = new_year
            
        # Aktualizacja reżysera
        if new_director is not None and movie.director.name != new_director:
            # Usuń z listy starego reżysera
            if movie in movie.director.movies_directed:
                movie.director.movies_directed.remove(movie)
                
            # Znajdź lub utwórz nowego reżysera
            director = self.get_or_create_person(new_director)
            movie.director = director
            director.movies_directed.append(movie)

        # Aktualizacja pozostałych pól
        if new_rating is not None and 1 <= new_rating <= 10:
            movie.rating = new_rating
            
        if new_comment is not None:
            movie.comment = new_comment
            
        if new_date_watched is not None:
            movie.date_watched = new_date_watched

        # Aktualizuj indeksy po zmianach
        self.db.update_indexes(movie)
        
        # Zatwierdź zmiany
        self.db.commit()
        return True

    def delete_movie(self, title):
        """
        Usuwa film i aktualizuje wszystkie powiązane relacje.
        
        Args:
            title: Tytuł filmu do usunięcia
            
        Returns:
            True jeśli usunięcie się powiodło, False w przeciwnym razie
        """
        if title not in self.movies:
            return False
            
        movie = self.movies[title]
        
        # Usuń z indeksów
        self.db.remove_from_indexes(movie)
        
        # Usuń z list reżysera
        if movie in movie.director.movies_directed:
            movie.director.movies_directed.remove(movie)
        
        # Usuń z list aktorów
        for actor in movie.cast:
            if movie in actor.movies_acted:
                actor.movies_acted.remove(movie)
                
        # Usuń z list gatunków
        for genre in movie.genres:
            if movie in genre.movies:
                genre.movies.remove(movie)
        
        # Usuń film
        del self.movies[title]
        
        # Zatwierdź zmiany
        self.db.commit()
        return True

    def list_movies(self, limit=None, sort_by=None, watched_only=False, with_rating_only=False):
        """
        Zwraca listę filmów z opcjonalnym filtrowaniem i sortowaniem.
        
        Args:
            limit: Maksymalna liczba filmów do zwrócenia
            sort_by: Pole sortowania ('title', 'year', 'rating', 'date_added', 'date_watched')
            watched_only: Jeśli True, zwraca tylko obejrzane filmy
            with_rating_only: Jeśli True, zwraca tylko filmy z oceną
            
        Returns:
            Lista obiektów filmu
        """
        movies_list = list(self.movies.values())
        
        # Filtrowanie
        if watched_only:
            movies_list = [m for m in movies_list if m.date_watched is not None]
            
        if with_rating_only:
            movies_list = [m for m in movies_list if m.rating is not None]
        
        # Sortowanie
        if sort_by == "title":
            movies_list.sort(key=lambda m: m.title)
        elif sort_by == "year":
            movies_list.sort(key=lambda m: m.year)
        elif sort_by == "rating":
            # Filmy bez oceny na końcu
            movies_list.sort(key=lambda m: m.rating if m.rating is not None else -1, reverse=True)
        elif sort_by == "date_added":
            movies_list.sort(key=lambda m: m.date_added, reverse=True)
        elif sort_by == "date_watched":
            # Filmy nieobejrzane na końcu
            def get_date_watched(m):
                return m.date_watched if m.date_watched is not None else datetime.datetime(1900, 1, 1)
            movies_list.sort(key=get_date_watched, reverse=True)
            
        # Limit
        if limit:
            return movies_list[:limit]
            
        return movies_list

    def search_movies(self, query):
        """
        Wyszukuje filmy według tytułu, reżysera, aktora lub gatunku.
        
        Args:
            query: Zapytanie wyszukiwania
            
        Returns:
            Lista pasujących filmów
        """
        results = []
        query_lower = query.lower()
        
        for movie in self.movies.values():
            # Wyszukiwanie po tytule
            if query_lower in movie.title.lower():
                results.append(movie)
                continue
                
            # Wyszukiwanie po reżyserze
            if isinstance(movie.director, str):
                if query_lower in movie.director.lower():
                    results.append(movie)
            else:
                if query_lower in movie.director.name.lower():
                    results.append(movie)
                continue
                
            # Wyszukiwanie po aktorach
            if hasattr(movie, 'cast'):
                for actor in movie.cast:
                    if isinstance(actor, str):
                        if query_lower in actor.lower():
                            results.append(movie)
                            break
                    else:
                        if query_lower in actor.name.lower():
                            results.append(movie)
                            break
                    
            # Wyszukiwanie po gatunkach
            if hasattr(movie, 'genres'):
                for genre in movie.genres:
                    if isinstance(genre, str):
                        if query_lower in genre.lower():
                            results.append(movie)
                            break
                    else:
                        if query_lower in genre.name.lower():
                            results.append(movie)
                            break
                    
        return list(set(results))  # Usuwa duplikaty
        
    def get_movies_by_year(self, year):
        """Zwraca wszystkie filmy z danego roku."""
        if year not in self.movies_by_year:
            return []
        return list(self.movies_by_year[year].values())
        
    def get_movies_by_director(self, director_name):
        """Zwraca wszystkie filmy danego reżysera."""
        if director_name not in self.movies_by_director:
            return []
        return list(self.movies_by_director[director_name].values())
        
    def get_movies_by_genre(self, genre_name):
        """Zwraca wszystkie filmy w danym gatunku."""
        if genre_name not in self.movies_by_genre:
            return []
        return list(self.movies_by_genre[genre_name].values())

    # ----- Operacje na osobach -----
    
    def get_or_create_person(self, name):
        """
        Zwraca osobę o podanym imieniu i nazwisku lub tworzy nową.
        
        Args:
            name: Imię i nazwisko osoby
            
        Returns:
            Obiekt Person
        """
        if name in self.persons:
            return self.persons[name]
        else:
            person = Person(name)
            self.persons[name] = person
            self.db.commit()
            return person
            
    def add_actor_to_movie(self, movie_title, actor_name):
        """
        Dodaje aktora do obsady filmu.
        
        Args:
            movie_title: Tytuł filmu
            actor_name: Imię i nazwisko aktora
            
        Returns:
            True jeśli dodanie się powiodło, False w przeciwnym razie
        """
        movie = self.get_movie(movie_title)
        if not movie:
            return False
            
        actor = self.get_or_create_person(actor_name)
        movie.add_actor(actor)
        self.db.commit()
        return True
        
    def get_all_persons(self):
        """Zwraca wszystkie osoby (aktorów i reżyserów)."""
        return list(self.persons.values())
        
    def get_directors(self):
        """Zwraca osoby, które są reżyserami."""
        return [p for p in self.persons.values() if p.movies_directed]
        
    def get_actors(self):
        """Zwraca osoby, które są aktorami."""
        return [p for p in self.persons.values() if p.movies_acted]
        
    # ----- Operacje na gatunkach -----
    
    def add_genre(self, name):
        """
        Dodaje nowy gatunek.
        
        Args:
            name: Nazwa gatunku
            
        Returns:
            Obiekt Genre lub False jeśli gatunek już istnieje
        """
        if name in self.genres:
            return self.genres[name]
            
        genre = Genre(name)
        self.genres[name] = genre
        
        # Utwórz indeks dla tego gatunku
        if name not in self.movies_by_genre:
            self.movies_by_genre[name] = OOBTree()
            
        self.db.commit()
        return genre
        
    def add_genre_to_movie(self, movie_title, genre_name):
        """
        Dodaje gatunek do filmu.
        
        Args:
            movie_title: Tytuł filmu
            genre_name: Nazwa gatunku
            
        Returns:
            True jeśli dodanie się powiodło, False w przeciwnym razie
        """
        movie = self.get_movie(movie_title)
        if not movie:
            return False
            
        # Znajdź lub utwórz gatunek
        genre = self.add_genre(genre_name)
        
        # Aktualizuj relację
        movie.add_genre(genre)
        
        # Aktualizuj indeks
        if genre_name not in self.movies_by_genre:
            self.movies_by_genre[genre_name] = OOBTree()
        self.movies_by_genre[genre_name][movie_title] = movie
        
        self.db.commit()
        return True
        
    def get_all_genres(self):
        """Zwraca wszystkie gatunki."""
        return list(self.genres.values())
        
    # ----- Operacje na bazie danych -----
    
    def close(self):
        """Zamyka połączenie z bazą danych."""
        self.db.close()
        
    def pack_database(self):
        """Pakuje bazę danych aby zaoszczędzić miejsce."""
        self.db.pack()
        return True
