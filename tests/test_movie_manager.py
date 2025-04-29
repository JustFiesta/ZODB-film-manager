import unittest
from datetime import datetime
import os
import transaction
from app.crud import MovieManager

class TestMovieManager(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        # Utworzenie katalogu data w folderze testów jeśli nie istnieje
        test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Pełna ścieżka do pliku bazy testowej
        self.test_db_path = os.path.join(test_data_dir, 'test_movies.fs')
        self.manager = MovieManager(self.test_db_path)

    def tearDown(self):
        """Czyszczenie po każdym teście"""
        self.manager.close()
        # Usuń plik bazy danych
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        # Usuń katalog data jeśli jest pusty
        test_data_dir = os.path.dirname(self.test_db_path)
        if os.path.exists(test_data_dir) and not os.listdir(test_data_dir):
            os.rmdir(test_data_dir)

    def test_add_simple_movie(self):
        """Test dodawania podstawowego filmu"""
        movie = self.manager.add_movie(
            title="Test Movie",
            director_name="Test Director",
            year=2023
        )

        self.assertIsNotNone(movie)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.director.name, "Test Director")
        self.assertEqual(movie.year, 2023)

        # Sprawdź czy film jest w bazie
        saved_movie = self.manager.get_movie("Test Movie")
        self.assertIsNotNone(saved_movie)

    def test_add_full_movie(self):
        """Test dodawania filmu ze wszystkimi opcjonalnymi polami"""
        actors = ["Actor 1", "Actor 2"]
        genres = ["Action", "Drama"]
        date_watched = datetime.now()

        movie = self.manager.add_movie(
            title="Full Test Movie",
            director_name="Full Test Director",
            year=2023,
            actors=actors,
            genres=genres,
            rating=8,
            comment="Test comment",
            date_watched=date_watched
        )

        self.assertIsNotNone(movie)
        saved_movie = self.manager.get_movie("Full Test Movie")

        # Sprawdź wszystkie pola
        self.assertEqual(len(saved_movie.cast), 2)
        self.assertEqual(len(saved_movie.genres), 2)
        self.assertEqual(saved_movie.rating, 8)
        self.assertEqual(saved_movie.comment, "Test comment")
        self.assertEqual(saved_movie.date_watched, date_watched)

    def test_duplicate_movie(self):
        """Test próby dodania filmu o istniejącym tytule"""
        # Dodaj pierwszy film
        self.manager.add_movie("Duplicate Movie", "Director", 2023)

        # Próba dodania drugiego filmu o tym samym tytule
        result = self.manager.add_movie("Duplicate Movie", "Other Director", 2024)
        self.assertFalse(result)

    def test_persistence(self):
        """Test czy film pozostaje w bazie po ponownym otwarciu"""
        # Dodaj film
        self.manager.add_movie("Persistent Movie", "Director", 2023)
        self.manager.db.close()

        # Otwórz nowe połączenie
        new_manager = MovieManager(self.test_db_path)
        saved_movie = new_manager.get_movie("Persistent Movie")

        self.assertIsNotNone(saved_movie)
        self.assertEqual(saved_movie.title, "Persistent Movie")
        self.manager.db.close()
