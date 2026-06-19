import sqlite3
from pathlib import Path

class DBAnalyzer:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def extract_schema(self) -> dict[str, str]:
        """
        Łączy się z bazą SQLite i wyciąga strukturę (DDL) wszystkich tabel użytkownika.
        Zwraca słownik: {nazwa_tabeli: "CREATE TABLE ..."}
        """
        schema_info = {}
        
        try:
            # Łączymy się z bazą w trybie tylko do odczytu (mode=ro) dla pełnego bezpieczeństwa
            # Używamy URI=True, aby SQLite poprawnie zinterpretował parametry połączenia
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            
            # Pobieramy nazwy tabel oraz zapytania SQL, które je utworzyły.
            # Warunek NOT LIKE 'sqlite_%' odrzuca wewnętrzne tabele systemowe SQLite.
            cursor.execute("""
                SELECT name, sql 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """)
            
            tables = cursor.fetchall()
            
            for table_name, create_sql in tables:
                if create_sql:  # Upewniamy się, że kod SQL nie jest pusty
                    schema_info[table_name] = create_sql
                    
            conn.close()
        except sqlite3.Error as e:
            print(f"Błąd podczas odczytu bazy danych {self.db_path.name}: {e}")
            
        return schema_info