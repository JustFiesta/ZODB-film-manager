from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.crud import MovieManager
import os
import datetime
import pprint
import json
from flask import jsonify

main = Blueprint('main', __name__)
manager = MovieManager(os.environ.get('DB_PATH', 'db/movies.fs'))

# ------ Strony główne ------

@main.route('/')
def index():
    """Strona główna z listą ostatnio dodanych filmów."""
    movies = manager.list_movies(limit=6, sort_by="date_added")
    return render_template('index.html', movies=movies)

# ------ Zarządzanie filmami ------

@main.route('/movies')
def list_movies():
    """Lista wszystkich filmów z opcjami sortowania."""
    sort_by = request.args.get('sort', 'title')
    watched_only = request.args.get('watched_only') == '1'
    with_rating_only = request.args.get('with_rating_only') == '1'
    
    movies = manager.list_movies(
        sort_by=sort_by, 
        watched_only=watched_only, 
        with_rating_only=with_rating_only
    )
    
    return render_template(
        'movie_list.html', 
        movies=movies, 
        sort_by=sort_by,
        watched_only=watched_only,
        with_rating_only=with_rating_only
    )

@main.route('/movie/<title>')
def movie_detail(title):
    """Szczegóły filmu."""
    movie = manager.get_movie(title)
    if not movie:
        abort(404)
    return render_template('movie_detail.html', movie=movie)

@main.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """Dodawanie nowego filmu."""
    if request.method == 'POST':
        print("Dodawanie filmu...")
        title = request.form.get('title')
        director = request.form.get('director')
        year = int(request.form.get('year', 0))
        
        # Pola opcjonalne
        actors = request.form.get('actors', '').split(',')
        actors = [a.strip() for a in actors if a.strip()]
        
        genres = request.form.getlist('genres')
        new_genres = request.form.get('new_genres', '').split(',')
        new_genres = [g.strip() for g in new_genres if g.strip()]
        genres.extend(new_genres)
        
        rating = request.form.get('rating')
        if rating and rating.isdigit():
            rating = int(rating)
        else:
            rating = None
            
        comment = request.form.get('comment', '')
        
        date_watched_str = request.form.get('date_watched')
        date_watched = None
        if date_watched_str:
            try:
                date_watched = datetime.datetime.strptime(date_watched_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Walidacja
        if not title or not director or year < 1900:
            flash('Wymagane pola: tytuł, reżyser i rok (min. 1900)')
            # Przygotowanie danych do formularza
            all_directors = manager.get_directors()
            all_actors = manager.get_actors()
            all_genres = manager.get_all_genres()
            return render_template(
                'add_movie.html',
                all_directors=all_directors,
                all_actors=all_actors,
                all_genres=all_genres
            )
        
        # Zapisz film
        movie = manager.add_movie(
            title=title,
            director_name=director,
            year=year,
            actors=actors,
            genres=genres,
            rating=rating,
            comment=comment,
            date_watched=date_watched
        )

        print(f"Wynik dodawania: {movie}")
        print(f"Filmy w bazie: {list(manager.root.movies.keys())}")
        
        if movie:
            # Upewnij się, że zmiany zostały zapisane
            manager.db.commit()
            flash(f'Film "{title}" został dodany')
            
            # Double-check that movie exists before redirecting
            test_movie = manager.get_movie(title)
            if test_movie:
                print(f"Film {title} istnieje w bazie przed przekierowaniem")
                return redirect(url_for('main.movie_detail', title=title))
            else:
                print(f"UWAGA: Film {title} NIE istnieje w bazie mimo dodania")
                flash(f'Wystąpił błąd przy dodawaniu filmu "{title}"')
                return redirect(url_for('main.list_movies'))
        else:
            flash(f'Film "{title}" już istnieje')
    
    # Dane do formularza
    all_directors = manager.get_directors()
    all_actors = manager.get_actors()
    all_genres = manager.get_all_genres()
    
    return render_template(
        'add_movie.html',
        all_directors=all_directors,
        all_actors=all_actors,
        all_genres=all_genres
    )

@main.route('/edit_movie/<title>', methods=['GET', 'POST'])
def edit_movie(title):
    """Edycja istniejącego filmu."""
    movie = manager.get_movie(title)
    if not movie:
        abort(404)
        
    if request.method == 'POST':
        new_director = request.form.get('director')
        new_year = int(request.form.get('year', 0))
        
        # Pola opcjonalne
        new_rating = request.form.get('rating')
        if new_rating and new_rating.isdigit():
            new_rating = int(new_rating)
        else:
            new_rating = None
            
        new_comment = request.form.get('comment', '')
        
        new_date_watched_str = request.form.get('date_watched')
        new_date_watched = None
        if new_date_watched_str:
            try:
                new_date_watched = datetime.datetime.strptime(new_date_watched_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Walidacja
        if not new_director or new_year < 1900:
            flash('Wymagane pola: reżyser i rok (min. 1900)')
            # Przygotowanie danych do formularza
            all_directors = manager.get_directors()
            return render_template(
                'edit_movie.html',
                movie=movie,
                all_directors=all_directors
            )
        
        # Aktualizacja podstawowych danych
        success = manager.update_movie(
            title=title,
            new_director=new_director,
            new_year=new_year,
            new_rating=new_rating,
            new_comment=new_comment,
            new_date_watched=new_date_watched
        )
        
        # Aktualizacja aktorów - najpierw usuwamy istniejących, potem dodajemy nowych
        # To uproszczone podejście - w rzeczywistości moglibyśmy porównywać listy
        actors = request.form.get('actors', '').split(',')
        actors = [a.strip() for a in actors if a.strip()]
        
        for actor in list(movie.cast):
            movie.cast.remove(actor)
            if actor in actor.movies_acted:
                actor.movies_acted.remove(movie)
        
        for actor_name in actors:
            manager.add_actor_to_movie(title, actor_name)
        
        # Aktualizacja gatunków
        genres = request.form.getlist('genres')
        new_genres = request.form.get('new_genres', '').split(',')
        new_genres = [g.strip() for g in new_genres if g.strip()]
        genres.extend(new_genres)
        
        # Usuwamy stare gatunki
        for genre in list(movie.genres):
            movie.genres.remove(genre)
            if movie in genre.movies:
                genre.movies.remove(movie)
        
        # Dodajemy nowe gatunki
        for genre_name in genres:
            if genre_name:
                manager.add_genre_to_movie(title, genre_name)
        
        # Zatwierdzamy zmiany
        manager.db.commit()
        
        if success:
            flash(f'Film "{title}" został zaktualizowany')
            return redirect(url_for('main.movie_detail', title=title))
        else:
            flash(f'Błąd podczas aktualizacji filmu "{title}"')
            
    # Dane do formularza
    all_directors = manager.get_directors()
    all_actors = manager.get_actors()
    all_genres = manager.get_all_genres()
    
    # Przygotowujemy aktualną listę aktorów jako string
    current_actors = ", ".join([actor.name for actor in movie.cast]) if movie.cast else ""
    
    return render_template(
        'edit_movie.html',
        movie=movie,
        all_directors=all_directors,
        all_actors=all_actors,
        all_genres=all_genres,
        current_actors=current_actors
    )

@main.route('/delete_movie/<title>', methods=['POST'])
def delete_movie(title):
    """Usuwanie filmu."""
    success = manager.delete_movie(title)
    
    if success:
        flash(f'Film "{title}" został usunięty')
    else:
        flash(f'Błąd podczas usuwania filmu "{title}"')
        
    return redirect(url_for('main.list_movies'))

@main.route('/rate_movie/<title>', methods=['POST'])
def rate_movie(title):
    """Ocenianie filmu."""
    movie = manager.get_movie(title)
    if not movie:
        abort(404)
        
    try:
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '')
        
        if 1 <= rating <= 10:
            # Ustaw ocenę filmu
            movie.rating = rating
            movie.comment = comment
            
            # Data obejrzenia - jeśli nie ustawiona, ustaw na dziś
            if not movie.date_watched:
                movie.date_watched = datetime.datetime.now()
                
            # Zatwierdź zmiany
            manager.db.commit()
            
            flash(f'Ocena filmu "{title}" została zapisana')
        else:
            flash('Ocena musi być w zakresie 1-10')
    except (ValueError, TypeError):
        flash('Nieprawidłowa ocena')
        
    return redirect(url_for('main.movie_detail', title=title))

@main.route('/search')
def search():
    """Wyszukiwanie filmów."""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.list_movies'))
        
    results = manager.search_movies(query)
    return render_template('search_results.html', query=query, movies=results)

@main.route('/movies/year/<int:year>')
def movies_by_year(year):
    """Wyświetla filmy z danego roku."""
    movies = manager.get_movies_by_year(year)
    return render_template('movies_list.html', 
                         movies=movies, 
                         title=f'Filmy z roku {year}')

@main.route('/movies/director/<director_name>')
def movies_by_director(director_name):
    """Wyświetla filmy danego reżysera."""
    movies = manager.get_movies_by_director(director_name)
    return render_template('movies_list.html', 
                         movies=movies, 
                         title=f'Filmy reżysera: {director_name}')

# ------ Zarządzanie gatunkami ------

@main.route('/genres')
def list_genres():
    """Lista wszystkich gatunków."""
    genres = manager.get_all_genres()
    return render_template('genre_list.html', genres=genres)

@main.route('/genre/<name>')
def genre_detail(name):
    """Filmy w danym gatunku."""
    genre = manager.root.genres.get(name)
    if not genre:
        abort(404)
        
    movies = manager.get_movies_by_genre(name)
    return render_template('genre_detail.html', genre=genre, movies=movies)

@main.route('/add_genre', methods=['GET', 'POST'])
def add_genre():
    """Dodawanie nowego gatunku."""
    if request.method == 'POST':
        name = request.form.get('name')
        
        if not name:
            flash('Nazwa gatunku jest wymagana')
            return render_template('add_genre.html')
            
        genre = manager.add_genre(name)
        
        if genre:
            flash(f'Gatunek "{name}" został dodany')
            return redirect(url_for('main.list_genres'))
        else:
            flash(f'Gatunek "{name}" już istnieje')
            
    return render_template('add_genre.html')

@main.route('/edit_genre/<name>', methods=['GET', 'POST'])
def edit_genre(name):
    """Edycja istniejącego gatunku."""
    genre = manager.root.genres.get(name)
    if not genre:
        abort(404)
        
    if request.method == 'POST':
        new_name = request.form.get('name')
        
        if not new_name:
            flash('Nazwa gatunku jest wymagana')
            return render_template('edit_genre.html', genre=genre)
            
        # Jeśli nazwa się nie zmieniła, nic nie robimy
        if new_name == name:
            flash(f'Gatunek "{name}" nie został zmieniony')
            return redirect(url_for('main.genre_detail', name=name))
            
        # Sprawdź czy nowa nazwa nie istnieje już w bazie
        if new_name in manager.root.genres and new_name != name:
            flash(f'Gatunek "{new_name}" już istnieje')
            return render_template('edit_genre.html', genre=genre)
            
        # Tworzenie nowego gatunku
        new_genre = manager.add_genre(new_name)
        
        # Przeniesienie filmów ze starego do nowego gatunku
        if hasattr(genre, 'movies'):
            for movie in list(genre.movies):
                # Usuń stary gatunek z filmu
                if genre in movie.genres:
                    movie.genres.remove(genre)
                # Dodaj nowy gatunek do filmu
                movie.add_genre(new_genre)
                # Aktualizuj indeks gatunków
                if name in manager.root.movies_by_genre and movie.title in manager.root.movies_by_genre[name]:
                    del manager.root.movies_by_genre[name][movie.title]
                if new_name not in manager.root.movies_by_genre:
                    manager.root.movies_by_genre[new_name] = OOBTree()
                manager.root.movies_by_genre[new_name][movie.title] = movie
        
        # Usuń stary gatunek
        del manager.root.genres[name]
        if name in manager.root.movies_by_genre:
            del manager.root.movies_by_genre[name]
            
        # Zatwierdź zmiany
        manager.db.commit()
        
        flash(f'Gatunek "{name}" został zaktualizowany na "{new_name}"')
        return redirect(url_for('main.genre_detail', name=new_name))
            
    return render_template('edit_genre.html', genre=genre)

@main.route('/delete_genre/<name>', methods=['POST'])
def delete_genre(name):
    """Usuwanie gatunku."""
    genre = manager.root.genres.get(name)
    if not genre:
        abort(404)
        
    # Usuń gatunek z wszystkich powiązanych filmów
    if hasattr(genre, 'movies'):
        for movie in list(genre.movies):
            if genre in movie.genres:
                movie.genres.remove(genre)
    
    # Usuń gatunek z kolekcji i indeksu
    del manager.root.genres[name]
    if name in manager.root.movies_by_genre:
        del manager.root.movies_by_genre[name]
        
    # Zatwierdź zmiany
    manager.db.commit()
    
    flash(f'Gatunek "{name}" został usunięty')
    return redirect(url_for('main.list_genres'))

# ------ Zarządzanie osobami ------

@main.route('/persons')
def list_persons():
    persons = manager.get_all_persons()
    return render_template('person_list.html', persons=persons)

@main.route('/directors')
def list_directors():
    """Lista reżyserów."""
    directors = manager.get_directors()
    return render_template('director_list.html', directors=directors)

@main.route('/actors')
def list_actors():
    """Lista aktorów."""
    actors = manager.get_actors()
    return render_template('actor_list.html', actors=actors)

@main.route('/person/<name>')
def person_detail(name):
    """Szczegóły osoby (reżysera/aktora)."""
    person = manager.root.persons.get(name)
    if not person:
        abort(404)
    
    directed_movies = list(person.movies_directed)
    acted_movies = list(person.movies_acted)
    
    return render_template(
        'person_detail.html', 
        person=person,
        directed_movies=directed_movies,
        acted_movies=acted_movies
    )

@main.route('/person/<name>/delete', methods=['POST'])
def delete_person(name):
    print(f"Próba usunięcia osoby: {name}")  # Debug log
    try:
        if manager.delete_person(name):
            flash(f'Osoba {name} została usunięta pomyślnie.', 'success')
        else:
            flash(f'Nie można usunąć osoby {name}.', 'error')
    except Exception as e:
        print(f"Błąd podczas usuwania: {str(e)}")  # Debug log
        flash(f'Wystąpił błąd podczas usuwania osoby: {str(e)}', 'error')
    
    return redirect(url_for('main.list_persons'))

@main.route('/edit_person/<name>', methods=['GET', 'POST'])
def edit_person(name):
    """Edycja istniejącej osoby."""
    person = manager.root.persons.get(name)
    if not person:
        abort(404)
        
    if request.method == 'POST':
        new_name = request.form.get('name')
        
        if not new_name:
            flash('Imię i nazwisko są wymagane')
            return render_template('edit_person.html', person=person)
            
        # Jeśli nazwa się nie zmieniła, nic nie robimy
        if new_name == name:
            flash(f'Osoba "{name}" nie została zmieniona')
            return redirect(url_for('main.person_detail', name=name))
            
        # Sprawdź czy nowa nazwa nie istnieje już w bazie
        if new_name in manager.root.persons and new_name != name:
            flash(f'Osoba "{new_name}" już istnieje')
            return render_template('edit_person.html', person=person)
            
        # Tworzymy nową osobę
        new_person = manager.get_or_create_person(new_name)
        
        # Przenosimy filmy wyreżyserowane
        for movie in list(person.movies_directed):
            # Zmień reżysera filmu
            movie.director = new_person
            # Usuń film z listy starej osoby
            if movie in person.movies_directed:
                person.movies_directed.remove(movie)
            # Dodaj film do listy nowej osoby
            if movie not in new_person.movies_directed:
                new_person.movies_directed.append(movie)
            
            # Aktualizuj indeks reżyserów
            if name in manager.root.movies_by_director and movie.title in manager.root.movies_by_director[name]:
                del manager.root.movies_by_director[name][movie.title]
            if new_name not in manager.root.movies_by_director:
                manager.root.movies_by_director[new_name] = OOBTree()
            manager.root.movies_by_director[new_name][movie.title] = movie
        
        # Przenosimy filmy, w których osoba grała
        for movie in list(person.movies_acted):
            # Usuń osobę z obsady filmu
            if person in movie.cast:
                movie.cast.remove(person)
            # Dodaj nową osobę do obsady filmu
            if new_person not in movie.cast:
                movie.cast.append(new_person)
            # Usuń film z listy starej osoby
            if movie in person.movies_acted:
                person.movies_acted.remove(movie)
            # Dodaj film do listy nowej osoby
            if movie not in new_person.movies_acted:
                new_person.movies_acted.append(movie)
        
        # Usuń starą osobę jeśli nie ma już powiązań z filmami
        if not person.movies_directed and not person.movies_acted:
            del manager.root.persons[name]
            
        # Zatwierdź zmiany
        manager.db.commit()
        
        flash(f'Osoba "{name}" została zaktualizowana na "{new_name}"')
        return redirect(url_for('main.person_detail', name=new_name))
            
    return render_template('edit_person.html', person=person)

# ------ Obsługa błędów ------

@main.errorhandler(404)
def page_not_found(e):
    """Obsługa błędu 404."""
    return render_template('404.html'), 404

def init_app(app):
    """Inicjalizuje aplikację Flask routingiem."""
    app.register_blueprint(main)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
        
    return app

# ------ Debug ------

@main.route('/database_debug')
def database_debug():
    """Widok debugowania zawartości bazy danych ZODB."""
    # Pobranie danych z głównych kolekcji
    collections = {
        'movies': len(manager.movies),
        'persons': len(manager.root.persons),
        'genres': len(manager.root.genres),
        'movies_by_year': len(manager.movies_by_year),
        'movies_by_genre': len(manager.root.movies_by_genre),
        'movies_by_director': len(manager.root.movies_by_director)
    }
    
    # Przykładowe obiekty do inspekcji
    sample_objects = {
        'movies': list(manager.movies.values())[:5] if manager.movies else [],
        'persons': list(manager.root.persons.values())[:5] if manager.root.persons else [],
        'genres': list(manager.root.genres.values())[:5] if manager.root.genres else []
    }
    
    # Przygotowanie danych o indeksach w formie słowników
    years_data = {}
    for year in manager.movies_by_year.keys():
        years_data[year] = len(manager.movies_by_year[year])
    
    genres_data = {}
    for genre in manager.root.movies_by_genre.keys():
        genres_data[genre] = len(manager.root.movies_by_genre[genre])
    
    directors_data = {}
    for director in manager.root.movies_by_director.keys():
        directors_data[director] = len(manager.root.movies_by_director[director])
    
    # Indeksy jako pojedyncze słowniki zamiast list
    indexes = {
        'years': years_data,
        'genres': genres_data,
        'directors': directors_data
    }
    
    return render_template('database_debug.html', 
                           collections=collections,
                           sample_objects=sample_objects,
                           indexes=indexes)
