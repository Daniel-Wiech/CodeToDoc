import sqlite3
from pathlib import Path

class DBAnalyzer:
    def __init__(self, db_type: str, connection_string: str | Path):
        """
        db_type: 'sqlite', 'postgres', 'oracle', 'mongodb'
        connection_string: ścieżka do pliku (dla sqlite) lub url połączenia (dla innych)
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string

    def extract_schema(self) -> dict[str, str]:
        """Główna metoda, która decyduje, który silnik bazy danych uruchomić."""
        if self.db_type == "sqlite":
            return self._extract_sqlite()
        elif self.db_type == "postgres":
            return self._extract_postgres()
        elif self.db_type == "oracle":
            return self._extract_oracle()
        elif self.db_type == "mongodb":
            return self._extract_mongodb()
        else:
            print(f"Typ bazy '{self.db_type}' nie jest jeszcze obsługiwany.")
            return {}

    def _extract_sqlite(self) -> dict[str, str]:
        """Logika dedykowana dla SQLite"""
        schema_info = {}
        db_path = Path(self.connection_string)
        
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, sql 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """)
            for table_name, create_sql in cursor.fetchall():
                if create_sql:
                    schema_info[table_name] = create_sql
            conn.close()
        except sqlite3.Error as e:
            print(f"Błąd SQLite ({db_path.name}): {e}")
            
        return schema_info

    def _extract_postgres(self) -> dict[str, str]:
        """Logika dedykowana dla PostgreSQL (szablon pod przyszłość)"""
        schema_info = {}
        print(f"Łączenie z PostgreSQL przez: {self.connection_string}...")
        # W przyszłości: 
        # import psycopg2
        # conn = psycopg2.connect(self.connection_string)
        # ... odpytanie information_schema ...
        return schema_info

    def _extract_oracle(self) -> dict[str, str]:
        """Logika dedykowana dla Oracle (szablon pod przyszłość)"""
        schema_info = {}
        print(f"Łączenie z Oracle przez: {self.connection_string}...")
        return schema_info
    def _extract_mongodb(self) -> dict[str, str]:
        """Logika próbkowania schematu dla MongoDB"""
        schema_info = {}
        print(f"Próbkowanie kolekcji MongoDB przez URI: {self.connection_string}...")
        
        # W przyszłości: poetry add pymongo
        # z powodu braku biblioteki w tym kroku, pokazujemy strukturę algorytmu:
        try:
            # import pymongo
            # client = pymongo.MongoClient(self.connection_string)
            # db = client.get_default_database() # Pobiera bazę wskazaną w URI lub konfiguracji
            
            # Dla celów demonstracyjnych/szablonu symulujemy wyciąg z kolekcji:
            mock_collections = ["users", "orders", "products"]
            
            for col_name in mock_collections:
                # doc = db[col_name].find_one() # Pobieramy jeden, przykładowy dokument
                # Wytwarzamy pseudo-DDL na podstawie kluczy z JSON dla LLM:
                if col_name == "users":
                    schema_info[col_name] = "Collection 'users' sample fields:\n - _id (ObjectId)\n - username (String)\n - email (String)"
                elif col_name == "orders":
                    schema_info[col_name] = "Collection 'orders' sample fields:\n - _id (ObjectId)\n - user_id (ObjectId)\n - total_amount (Double)\n - items (Array)"
                else:
                    schema_info[col_name] = f"Collection '{col_name}' sample document fields analyzed successfully."
                    
        except Exception as e:
            print(f"Błąd podczas łączenia z MongoDB: {e}")
            
        return schema_info