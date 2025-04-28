from web import create_app
import sys
import atexit
import os
import signal

# Funkcja do obsługi zamykania aplikacji
def cleanup():
    from app.crud import MovieManager
    print("Zamykanie aplikacji, zapisywanie danych...")
    try:
        manager = MovieManager()
        manager.close()
    except Exception as e:
        print(f"Błąd podczas zamykania bazy danych: {e}")
    print("Aplikacja została zamknięta.")

# Rejestracja funkcji czyszczenia
atexit.register(cleanup)

# Obsługa sygnału SIGTERM
def handle_sigterm(*args):
    print("Otrzymano sygnał zamknięcia...")
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
            cleanup()
