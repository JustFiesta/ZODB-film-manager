# 1. Całkowicie poprawiony database.py z zachowaną metodą _migrate_schema()

"""
Oto kompletna wersja pliku database.py z poprawkami do persystencji danych.
Proszę zastąpić cały plik tym kodem.
"""

from ZODB import FileStorage, DB
import transaction
from BTrees.OOBTree import OOBTree
import os
import datetime
from persistent.list import PersistentList

class DatabaseManager:
    """
    Zarządza połączeniem z bazą danych ZODB i zapewnia podstawowe operacje.
    
    Klasa inicjalizuje ZODB, tworzy potrzebne kolekcje dla filmów, osób i gatunków,
    oraz zapewnia metody do zarządzania transakcjami i migracji schematu.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, db_path="db/movies.fs"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path="db/movies.fs"):
        if not DatabaseManager._initialized:
            print(f"Inicjalizacja bazy danych: {db_path}")  # Debug
            try:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                # Sprawdź czy istnieje plik blokujący i usuń go, jeśli istnieje
                lock_path = db_path + '.lock'
                if os.path.exists(lock_path):
                    print(f"Usuwanie starego pliku blokującego: {lock_path}")
                    os.remove(lock_path)
                
                # Inicjalizuj storage z opcją 'read-only=False'
                self.storage = FileStorage.FileStorage(db_path, read_only=False)
                self.db = DB(self.storage)
                self.connection = self.db.open()
                self.root = self.connection.root()
                
                # Inicjalizacja struktur danych, jeśli nie istnieją
                if not hasattr(self.root, "movies"):
                    print("Tworzenie nowego słownika filmów")  # Debug
                    self.root.movies = OOBTree()
                    
                if not hasattr(self.root, "persons"):
                    self.root.persons = OOBTree()
                    
                if not hasattr(self.root, "genres"):
                    self.root.genres = OOBTree()
                    
                # Tworzenie indeksów dla efektywnego wyszukiwania
                if not hasattr(self.root, "movies_by_year"):
                    self.root.movies_by_year = OOBTree()
                    
                if not hasattr(self.root, "movies_by_genre"):
                    self.root.movies_by_genre = OOBTree()
                    
                if not hasattr(self.root, "movies_by_director"):
                    self.root.movies_by_director = OOBTree()
                
                # Migracja schematu przy starcie
                self._migrate_schema()
                
                # Commitujemy inicjalizację
                transaction.commit()
                DatabaseManager._initialized = True
            except Exception as e:
                print(f"Błąd podczas inicjalizacji bazy danych: {e}")
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.close()
                    except:
                        pass
                if hasattr(self, 'db') and self.db:
                    try:
                        self.db.close()
                    except:
                        pass
                raise

    def get_root(self):
        """Zwraca obiekt root bazy danych."""
        return self.root
    
    def commit(self):
        """Zatwierdza zmiany w bazie danych."""
        print("Zatwierdzanie transakcji...")
        transaction.commit()
        print(f"Filmy po zatwierdzeniu: {list(self.root.movies.keys())}")
    
    def abort(self):
        """Anuluje bieżące zmiany."""
        transaction.abort()

    def close(self):
        """Zamyka połączenie z bazą danych."""
        try:
            # Upewnij się, że wszystkie zmiany są zatwierdzone przed zamknięciem
            transaction.commit()
            
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
            if hasattr(self, 'db') and self.db:
                self.db.close()
            if hasattr(self, 'storage') and self.storage:
                self.storage.close()
                
            print("Baza danych została zamknięta.")
        except Exception as e:
            print(f"Błąd podczas zamykania bazy: {e}")
    
    def pack(self):
        """Pakuje bazę danych aby zaoszczędzić miejsce."""
        self.db.pack()
    
    def _migrate_schema(self):
        """
        Aktualizuje istniejące obiekty o brakujące atrybuty.
        
        Ta metoda zapewnia kompatybilność wsteczną przy zmianach schematu.
        """
        updated = False
        
        # Migracja obiektów Movie
        for movie in self.root.movies.values():
            if not hasattr(movie, 'date_added'):
                movie.date_added = datetime.datetime.now()
                updated = True
                
            if not hasattr(movie, 'genres'):
                movie.genres = PersistentList()
                updated = True
                
            if not hasattr(movie, 'cast'):
                movie.cast = PersistentList()
                updated = True
                
            if not hasattr(movie, 'date_watched'):
                movie.date_watched = None
                updated = True
                
            if not hasattr(movie, 'rating'):
                movie.rating = None
                updated = True
                
            if not hasattr(movie, 'comment'):
                movie.comment = ""
                updated = True
        
        # Migracja obiektów Person
        if hasattr(self.root, "persons"):
            for person in self.root.persons.values():
                if not hasattr(person, 'movies_directed'):
                    person.movies_directed = PersistentList()
                    updated = True
                
                if not hasattr(person, 'movies_acted'):
                    person.movies_acted = PersistentList()
                    updated = True
        
        # Zapisanie zmian jeśli były jakieś aktualizacje
        if updated:
            transaction.commit()
    
    def update_indexes(self, movie):
        """
        Aktualizuje indeksy dla danego filmu.
        
        Args:
            movie: Obiekt filmu do indeksowania
        """
        # Indeks po roku
        if movie.year not in self.root.movies_by_year:
            self.root.movies_by_year[movie.year] = OOBTree()
        self.root.movies_by_year[movie.year][movie.title] = movie
        
        # Indeks po reżyserze
        director_name = movie.director.name
        if director_name not in self.root.movies_by_director:
            self.root.movies_by_director[director_name] = OOBTree()
        self.root.movies_by_director[director_name][movie.title] = movie
        
        # Indeks po gatunkach
        for genre in movie.genres:
            genre_name = genre.name
            if genre_name not in self.root.movies_by_genre:
                self.root.movies_by_genre[genre_name] = OOBTree()
            self.root.movies_by_genre[genre_name][movie.title] = movie
    
    def remove_from_indexes(self, movie):
        """
        Usuwa film z indeksów.
        
        Args:
            movie: Obiekt filmu do usunięcia z indeksów
        """
        # Usunięcie z indeksu po roku
        if movie.year in self.root.movies_by_year:
            if movie.title in self.root.movies_by_year[movie.year]:
                del self.root.movies_by_year[movie.year][movie.title]
        
        # Usunięcie z indeksu po reżyserze
        director_name = movie.director.name
        if director_name in self.root.movies_by_director:
            if movie.title in self.root.movies_by_director[director_name]:
                del self.root.movies_by_director[director_name][movie.title]
        
        # Usunięcie z indeksu po gatunkach
        for genre in movie.genres:
            genre_name = genre.name
            if genre_name in self.root.movies_by_genre:
                if movie.title in self.root.movies_by_genre[genre_name]:
                    del self.root.movies_by_genre[genre_name][movie.title]
