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

# 2. Poprawiony run.py

"""
Oto kompletna wersja pliku run.py z poprawkami do persystencji danych.
Proszę zastąpić cały plik tym kodem.
"""

from web import create_app
import sys
import atexit
import os
import signal
import transaction

# Funkcja do obsługi zamykania aplikacji

def cleanup():
    from app.crud import MovieManager
    print("\nZamykanie aplikacji, zapisywanie danych...")
    try:
        # Upewnij się, że wszystkie transakcje są zatwierdzone
        try:
            transaction.commit()
            print("Główna transakcja zatwierdzona")
        except Exception as e:
            print(f"Błąd podczas zatwierdzania głównej transakcji: {e}")
        
        # Zamknij menedżera filmów
        try:
            manager = MovieManager()
            if hasattr(manager, 'db'):
                print("Zamykanie bazy danych przez MovieManager")
                if hasattr(manager.db, 'commit'):
                    manager.db.commit()
                
                # Sprawdź czy MovieManager ma metodę close
                if hasattr(manager, 'close'):
                    manager.close()
                else:
                    print("MovieManager nie ma metody close, zamykanie przez DatabaseManager")
                    manager.db.close()
            else:
                print("MovieManager nie ma obiektu db")
        except Exception as e:
            print(f"Błąd podczas zamykania bazy danych: {e}")
    except Exception as e:
        print(f"Błąd podczas zamykania aplikacji: {e}")
    print("Aplikacja została zamknięta.")

# Rejestracja funkcji czyszczenia
atexit.register(cleanup)

# Obsługa sygnału SIGTERM
def handle_sigterm(*args):
    print("Otrzymano sygnał zamknięcia...")
    # Upewnij się, że transakcje są zatwierdzone
    transaction.commit()
    # Wykonaj czyszczenie
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

if __name__ == "__main__":
    app = create_app()
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run tests
        import unittest
        from tests.test_crud import TestMovieManager
        from tests.test_routes import TestFlaskRoutes
        
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(TestMovieManager))
        test_suite.addTest(unittest.makeSuite(TestFlaskRoutes))
        
        runner = unittest.TextTestRunner()
        runner.run(test_suite)
    else:
        # Run web app
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("Przerwanie przez użytkownika, zamykanie aplikacji...")
            # Upewnij się, że transakcje są zatwierdzone
            transaction.commit()
            cleanup()
