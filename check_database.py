
"""
check_database.py - skrypt sprawdzający stan bazy danych ZODB
Udostępnia jedną funkcje check_database(path), która sprawdza stan bazy danych ZODB
i wypisuje jej zawartość.
"""

import os
from ZODB import FileStorage, DB
import transaction

def check_database(path="db/movies.fs"):
    """
    Sprawdza stan bazy danych ZODB i wypisuje jej zawartość.
    """
    print(f"\n--- SPRAWDZANIE BAZY DANYCH ---")
    print(f"Ścieżka: {path}")

    if not os.path.exists(path):
        print(f"Plik bazy danych NIE ISTNIEJE")
        return

    print(f"Plik bazy danych ISTNIEJE, rozmiar: {os.path.getsize(path)} bajtów")

    try:
        storage = FileStorage.FileStorage(path, read_only=True)
        db = DB(storage)
        connection = db.open()
        root = connection.root()

        if hasattr(root, "movies"):
            print(f"Znaleziono {len(root.movies)} filmów w bazie:")
            for title in root.movies.keys():
                print(f"  - {title}")
        else:
            print("Brak kolekcji filmów w bazie")

        if hasattr(root, "persons"):
            print(f"Znaleziono {len(root.persons)} osób w bazie")
        else:
            print("Brak kolekcji osób w bazie")

        if hasattr(root, "genres"):
            print(f"Znaleziono {len(root.genres)} gatunków w bazie")
        else:
            print("Brak kolekcji gatunków w bazie")

        connection.close()
        db.close()
        storage.close()
        print("Baza danych sprawdzona pomyślnie")

    except Exception as e:
        print(f"Błąd podczas sprawdzania bazy danych: {e}")

    print("--- KONIEC SPRAWDZANIA ---\n")

if __name__ == "__main__":
    check_database()
