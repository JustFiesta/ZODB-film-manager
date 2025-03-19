from app.crud import MovieManager

# Ten plik powinien służyć do uruchamiania całej apki
# Obecnie służy jako przykład do uruchomienia bazy i movie managera

# Inicjalizacja
manager = MovieManager()

# Dodajemy filmy
manager.add_movie("Inception", "Christopher Nolan", 2010)
manager.add_movie("The Matrix", "Wachowski Sisters", 1999)

# Pobieramy filmy
print(manager.get_movie("Inception"))

# Aktualizujemy film
manager.update_movie("The Matrix", new_year=2000)

# Lista filmów
print(manager.list_movies())

# Usuwamy film
manager.delete_movie("Inception")

# Sprawdzamy listę po usunięciu
print(manager.list_movies())

# Zamykamy bazę
manager.close()
