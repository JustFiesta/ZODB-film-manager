# ZODB Movie Manager

ZODB Movie Manager is a demonstration application showcasing the capabilities of the ZODB (Zope Object Database), an object-oriented database for Python. The app allows users to manage a collection of movies, directors, actors, and genres while leveraging ZODB's transparent persistence and object relationships.

## Features

- Add, edit, and delete movies, directors, actors, and genres.
- Rate and review movies.
- Organize movies by genres and maintain bidirectional relationships.
- Search movies by title, director, actor, or genre.
- Efficient indexing using ZODB's `OOBTree` for fast lookups.
- Transparent object persistence without the need for an ORM or SQL.

## How ZODB Works

ZODB is an object-oriented database that allows Python objects to be stored directly in the database without the need for serialization or mapping to relational tables. Key advantages of ZODB include:

- **Transparent Persistence**: Python objects are automatically saved and loaded without explicit database queries.
- **Bidirectional Relationships**: Objects can reference each other directly, and changes to one object are reflected in related objects.
- **No Schema**: ZODB does not require a predefined schema, making it flexible and easy to evolve.
- **Efficient Indexing**: ZODB uses `OOBTree` for indexing, enabling fast lookups and sorting.
- **ACID Transactions**: All changes are wrapped in transactions, ensuring data consistency.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Virtual environment (`venv`) module
- Required Python dependencies (listed in `requirements.txt`)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/JustFiesta/ZODB-film-manager
    cd project
    ```

2. Create and activate a virtual environment

    On Linux:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    On Windows:

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database

    ```bash
    python -m app.database
    ```

## Running the application

On Linux:

```bash
export FLASK_APP=web
export FLASK_ENV=development
flask run
```

On Windows:

```bash
set FLASK_APP=web
set FLASK_ENV=development
flask run
```  

The application will be available at [http://127.0.0.1:5000].

## Usage

1. Open the application in your web browser.
2. Use the navigation bar to explore movies, directors, actors, and genres.
3. Add new movies, edit existing ones, or delete entries as needed.
4. Search for movies using the search bar.
5. View detailed relationships between objects, such as movies and their genres or actors.

## Advantages of ZODB in ZODB-film-manager

1. Simplified Data Managament
No need to write SQL queries or manage complex ORM mappings.

2. Natural Object Relationships
Objects like movies, directors, and genres maintain direct references to each other.

3. Scalability
Efficient indexing with OOBTree ensures fast lookups even with large datasets
  
4. Flexibility
Schema-less design allows for easy modifications and additions to the data model.

5. Consistency
ACID transactions ensure that all changes are applied atomically.

## Troubleshooting

- If the application fails to start, ensure that the database file (movies.fs) is initialized and accessible.
- For issues with dependencies, verify that all packages in requirements.txt are installed.
