import datetime
from .database import DatabaseManager
from .models import Movie, Person, Genre
from BTrees.OOBTree import OOBTree

class MovieManager:
    """
    Zarządza operacjami CRUD dla filmów i powiązanych obiektów.
    
    Zapewnia metody do tworzenia, odczytu, aktualizacji i usuwania filmów,
    a także do zarządzania powiązanymi osobami (reżyserzy, aktorzy) i gatunkami.
    """

    _instance = None

    def __new__(cls, db_path="db/movies.fs"):
        if cls._instance is None:
            cls._instance = super(MovieManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path="db/movies.fs"):
        """Inicjalizuje menedżera filmu z połączeniem do bazy danych."""
        if not hasattr(self, 'db'):
            print(f"MovieManager: Inicjalizacja z bazą danych: {db_path}")
            self.db = DatabaseManager(db_path)
            self.root = self.db.get_root()
            print(f"MovieManager: Inicjalizacja zakończona, dostępne filmy: {list(self.root.movies.keys())}")

    # ----- Seedowanie bazy -----
    def seed_database(self):
        """
        Wypełnia bazę danych przykładowymi danymi, jeśli jest pusta.
        
        Dodaje przykładowe filmy, reżyserów, aktorów i gatunki, wraz z odpowiednimi relacjami.
        """
        # Sprawdź czy baza jest pusta
        if len(self.root.movies) > 0:
            print("Baza danych zawiera już dane, pomijam seedowanie.")
            return False

        print("Rozpoczynam seedowanie bazy danych przykładowymi filmami...")

        gatunki = ['Akcja', 'Komedia', 'Dramat', 'Sci-Fi', 'Horror', 'Thriller',
                   'Animacja', 'Przygodowy', 'Fantasy', 'Romans', 'Biograficzny']

        for nazwa_gatunku in gatunki:
            self.add_genre(nazwa_gatunku)
        print(f"Dodano {len(gatunki)} gatunków.")

        sample_movies = [
            {
                "title": "Incepcja",
                "director": "Christopher Nolan",
                "year": 2010,
                "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page", "Tom Hardy"],
                "genres": ["Sci-Fi", "Akcja", "Thriller"],
                "rating": 9,
                "comment": "Fascynujący film o włamywaniu się do snów i manipulowaniu podświadomością.",
                "date_watched": datetime.datetime(2020, 5, 12)
            },
            {
                "title": "Pulp Fiction",
                "director": "Quentin Tarantino",
                "year": 1994,
                "actors": ["John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis"],
                "genres": ["Thriller", "Komedia", "Dramat"],
                "rating": 10,
                "comment": "Kultowy film z nielinearną narracją i świetnymi dialogami.",
                "date_watched": datetime.datetime(2019, 11, 3)
            },
            {
                "title": "Władca Pierścieni: Drużyna Pierścienia",
                "director": "Peter Jackson",
                "year": 2001,
                "actors": ["Elijah Wood", "Ian McKellen", "Viggo Mortensen", "Sean Astin"],
                "genres": ["Fantasy", "Przygodowy"],
                "rating": 9,
                "comment": "Epicka adaptacja powieści Tolkiena z zapierającymi dech w piersiach krajobrazami Nowej Zelandii.",
                "date_watched": datetime.datetime(2018, 12, 25)
            },
            {
                "title": "Ojciec chrzestny",
                "director": "Francis Ford Coppola",
                "year": 1972,
                "actors": ["Marlon Brando", "Al Pacino", "James Caan", "Robert Duvall"],
                "genres": ["Dramat", "Thriller"],
                "rating": 10,
                "comment": "Klasyczny film o włoskiej mafii w Ameryce, uznawany za jedno z największych dzieł kinematografii.",
                "date_watched": datetime.datetime(2017, 8, 15)
            },
            {
                "title": "Matrix",
                "director": "Lana Wachowski",
                "year": 1999,
                "actors": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
                "genres": ["Sci-Fi", "Akcja"],
                "rating": 9,
                "comment": "Rewolucyjny film z przełomowymi efektami specjalnymi i głęboką filozofią.",
                "date_watched": datetime.datetime(2016, 6, 20)
            },
            {
                "title": "Milczenie owiec",
                "director": "Jonathan Demme",
                "year": 1991,
                "actors": ["Jodie Foster", "Anthony Hopkins", "Scott Glenn", "Ted Levine"],
                "genres": ["Thriller", "Horror"],
                "rating": 8,
                "comment": "Trzymający w napięciu thriller psychologiczny z niezapomnianą rolą Anthony'ego Hopkinsa.",
                "date_watched": datetime.datetime(2020, 10, 31)
            },
            {
                "title": "Skazani na Shawshank",
                "director": "Frank Darabont",
                "year": 1994,
                "actors": ["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
                "genres": ["Dramat"],
                "rating": 10,
                "comment": "Poruszająca historia o nadziei, przyjaźni i odkupieniu w więzieniu Shawshank.",
                "date_watched": datetime.datetime(2019, 4, 5)
            },
            {
                "title": "Forrest Gump",
                "director": "Robert Zemeckis",
                "year": 1994,
                "actors": ["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"],
                "genres": ["Dramat", "Komedia", "Romans"],
                "rating": 9,
                "comment": "Wzruszająca opowieść o niezwykłym życiu człowieka o ograniczonych możliwościach intelektualnych.",
                "date_watched": datetime.datetime(2018, 2, 14)
            },
            {
                "title": "Wyspa tajemnic",
                "director": "Martin Scorsese",
                "year": 2010,
                "actors": ["Leonardo DiCaprio", "Mark Ruffalo", "Ben Kingsley", "Michelle Williams"],
                "genres": ["Thriller", "Dramat"],
                "rating": 8,
                "comment": "Intrygujący thriller psychologiczny z zaskakującym zakończeniem.",
                "date_watched": datetime.datetime(2020, 8, 23)
            },
            {
                "title": "Gran Torino",
                "director": "Clint Eastwood",
                "year": 2008,
                "actors": ["Clint Eastwood", "Bee Vang", "Ahney Her", "Christopher Carley"],
                "genres": ["Dramat"],
                "rating": 8,
                "comment": "Poruszający film o weteranie wojny koreańskiej, który przełamuje swoje uprzedzenia wobec sąsiadów z Azji.",
                "date_watched": datetime.datetime(2019, 7, 10)
            },
            {
                "title": "Mroczny Rycerz",
                "director": "Christopher Nolan",
                "year": 2008,
                "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine"],
                "genres": ["Akcja", "Dramat", "Thriller"],
                "rating": 10,
                "comment": "Wyjątkowy film superbohaterski z genialną rolą Heatha Ledgera jako Jokera.",
                "date_watched": datetime.datetime(2018, 9, 17)
            },
            {
                "title": "Django",
                "director": "Quentin Tarantino",
                "year": 2012,
                "actors": ["Jamie Foxx", "Christoph Waltz", "Leonardo DiCaprio", "Samuel L. Jackson"],
                "genres": ["Dramat", "Western"],
                "rating": 9,
                "comment": "Stylowy western osadzony na amerykańskim Południu przed wojną secesyjną.",
                "date_watched": datetime.datetime(2020, 3, 8)
            }
        ]
        
        # Dodaj filmy do bazy
        for movie_data in sample_movies:
            self.add_movie(
                title=movie_data["title"],
                director_name=movie_data["director"],
                year=movie_data["year"],
                actors=movie_data["actors"],
                genres=movie_data["genres"],
                rating=movie_data["rating"],
                comment=movie_data["comment"],
                date_watched=movie_data["date_watched"]
            )
        
        print(f"Dodano {len(sample_movies)} filmów.")
        print("Seedowanie bazy danych zakończone pomyślnie!")
        
        # Zatwierdź wszystkie zmiany
        self.db.commit()
        return True

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
        self.root.movies[title] = movie

        # Dodaj film do listy reżysera
        if movie not in director.movies_directed:
            director.movies_directed.append(movie)

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

        # Aktualizuj indeksy
        self.db.update_indexes(movie)

        print(f"Stan bazy przed commitem: {list(self.root.movies.keys())}")  # Debug
        self.db.commit()
        print(f"Stan bazy po commicie: {list(self.root.movies.keys())}")  # Debug

        # Odczytaj film z bazy aby sprawdzić czy został zapisany
        test_movie = self.get_movie(title)
        if test_movie:
            print(f"Film {title} poprawnie dodany do bazy")
        else:
            print(f"BŁĄD: Film {title} nie został zapisany w bazie")

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
        if title not in self.root.movies:
            return False

        print(f"Rozpoczynam usuwanie filmu: {title}")
        movie = self.root.movies[title]

        # Usuń z indeksów
        print("Usuwanie z indeksów...")
        self.db.remove_from_indexes(movie)

        # Usuń z list reżysera
        print(f"Usuwanie z filmów reżysera: {movie.director.name}")
        if hasattr(movie.director, 'movies_directed') and movie in movie.director.movies_directed:
            movie.director.movies_directed.remove(movie)

        # Usuń z list aktorów
        print(f"Usuwanie z filmów aktorów...")
        if hasattr(movie, 'cast'):
            for actor in list(movie.cast):  # Używamy list() aby utworzyć kopię przed modyfikacją
                if hasattr(actor, 'movies_acted') and movie in actor.movies_acted:
                    actor.movies_acted.remove(movie)
                if actor in movie.cast:
                    movie.cast.remove(actor)

        # Usuń z list gatunków
        print(f"Usuwanie z gatunków...")
        if hasattr(movie, 'genres'):
            for genre in list(movie.genres):  # Używamy list() aby utworzyć kopię przed modyfikacją
                if hasattr(genre, 'movies') and movie in genre.movies:
                    genre.movies.remove(movie)
                if genre in movie.genres:
                    movie.genres.remove(genre)

        # Usuń film
        del self.root.movies[title]

        # Zatwierdź zmiany
        self.db.commit()
        print(f"Film {title} został usunięty")

        # Pakowanie bazy danych, aby usunąć stare wersje obiektów
        try:
            self.db.pack()
            print("Baza danych została spakowana")
        except:
            print("Pakowanie bazy danych nie powiodło się, ale film został usunięty")

        return True

    def list_movies(self, limit=None, sort_by=None, watched_only=False, with_rating_only=False):
        """
        Zwraca listę filmów z opcjonalnym filtrowaniem i sortowaniem.
        """
        movies_list = list(self.root.movies.values())

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
        """
        results = []
        query_lower = query.lower()

        for movie in self.root.movies.values():
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
        if year not in self.root.movies_by_year:
            return []
        return list(self.root.movies_by_year[year].values())

    def get_movies_by_director(self, director_name):
        """Zwraca wszystkie filmy danego reżysera."""
        if director_name not in self.root.movies_by_director:
            return []
        return list(self.root.movies_by_director[director_name].values())

    def get_movies_by_genre(self, genre_name):
        """Zwraca wszystkie filmy w danym gatunku."""
        if genre_name not in self.root.movies_by_genre:
            return []
        return list(self.root.movies_by_genre[genre_name].values())

    # ----- Operacje na osobach -----
    def get_or_create_person(self, name):
        """
        Zwraca osobę o podanym imieniu i nazwisku lub tworzy nową.
        """
        if name in self.root.persons:
            return self.root.persons[name]
        else:
            person = Person(name)
            self.root.persons[name] = person
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
        return list(self.root.persons.values())

    def get_directors(self):
        """Zwraca osoby, które są reżyserami."""
        return [p for p in self.root.persons.values() if p.movies_directed]

    def get_actors(self):
        """Zwraca osoby, które są aktorami."""
        return [p for p in self.root.persons.values() if p.movies_acted]

    def delete_person(self, name):
        """Usuwa osobę z bazy danych."""
        print(f"MovieManager: Próba usunięcia osoby {name}")  # Debug log
        print(f"Dostępne osoby: {list(self.root.persons.keys())}")  # Debug log

        if name not in self.root.persons:
            print(f"Osoba {name} nie istnieje w bazie")  # Debug log
            return False

        person = self.root.persons[name]

        # Sprawdź powiązania
        if person.movies_directed or person.movies_acted:
            print(f"Osoba {name} ma powiązane filmy")  # Debug log
            return False

        # Usuń osobę
        del self.root.persons[name]
        self.db.commit()

        print(f"Osoba {name} została usunięta")  # Debug log
        return True

    # ----- Operacje na gatunkach -----
    def add_genre(self, name):
        """
        Dodaje nowy gatunek.
        
        Args:
            name: Nazwa gatunku
            
        Returns:
            Obiekt Genre lub False jeśli gatunek już istnieje
        """
        if name in self.root.genres:
            return self.root.genres[name]

        genre = Genre(name)
        self.root.genres[name] = genre

        # Utwórz indeks dla tego gatunku
        if name not in self.root.movies_by_genre:
            self.root.movies_by_genre[name] = OOBTree()

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
        if genre_name not in self.root.movies_by_genre:
            self.root.movies_by_genre[genre_name] = OOBTree()
        self.root.movies_by_genre[genre_name][movie_title] = movie

        self.db.commit()
        return True

    def get_all_genres(self):
        """Zwraca wszystkie gatunki."""
        return list(self.root.genres.values())
