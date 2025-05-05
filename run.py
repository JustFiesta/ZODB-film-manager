"""
Punkt wejścia aplikacji webowej opartej na ZODB.
- Obsługuje zamykanie aplikacji (cleanup) i sygnały SIGTERM/SIGINT.
- Uruchamia aplikację na hoście `0.0.0.0` i porcie `5000`.
"""
import sys
import atexit
import signal
from web import create_app
import transaction

# Funkcja do obsługi zamykania aplikacji
def cleanup():
    """
    Funkcja czyszcząca, która jest wywoływana przy zamykaniu aplikacji.
    Zatwierdza transakcje i zamyka połączenia z bazą danych.
    """
    from app.crud import MovieManager
    print("\nZamykanie aplikacji, zapisywanie danych...")
    try:
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

    # Run web app
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Przerwanie przez użytkownika, zamykanie aplikacji...")
        # Upewnij się, że transakcje są zatwierdzone
        transaction.commit()
        cleanup()
