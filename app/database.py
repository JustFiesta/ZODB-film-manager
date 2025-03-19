from ZODB import FileStorage, DB
import transaction

class DatabaseManager:
    def __init__(self, db_path="db/movies.fs"):
        self.storage = FileStorage.FileStorage(db_path)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        if not hasattr(self.root, "movies"):
            self.root.movies = {}

    def get_root(self):
        return self.root

    def commit(self):
        transaction.commit()

    def close(self):
        self.connection.close()
        self.db.close()
