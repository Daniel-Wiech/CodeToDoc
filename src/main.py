from pathlib import Path
from src.git_manager import GitManager
from src.db_analyzer import DBAnalyzer

def main():
    REPO_URL = "https://github.com/Daniel-Wiech/MCPNorthwind"
    REPO_NAME = "test_project"

    # __file__ to: Projekty\CodeToDoc\src\main.py
    # .resolve().parent to: Projekty\CodeToDoc\src
    # .parent.parent to: Projekty\CodeToDoc
    base_dir = Path(__file__).resolve().parent.parent
    temp_dir = base_dir / "temp_repos"

    print(f"Folder na tymczasowe repozytoria: {temp_dir}")

    git_mgr = GitManager(temp_dir=temp_dir)
    
    try:
        # 1. Klonowanie repozytorium do Projekty\CodeToDoc\temp_repos
        repo_path = git_mgr.clone_repository(REPO_URL, REPO_NAME)
        
        # 2. Szukanie plików bazy danych
        db_files = git_mgr.find_db_files(repo_path)
        
        if not db_files:
            print("W repozytorium nie znaleziono żadnego pliku .db.")
            return
            
        print(f"Znaleziono pliki bazy danych ({len(db_files)}):")
        for db in db_files:
            print(f" - {db.relative_to(repo_path)}")
            
            # 3. Analiza struktury pliku .db
            analyzer = DBAnalyzer(db)
            schema = analyzer.extract_schema()
            
            print(f"\nWykryto {len(schema)} tabel w bazie {db.name}:")
            for table_name, create_sql in schema.items():
                print(f"\n--- Tabela: {table_name} ---")
                # Wyciągamy pierwsze 3 linijki, żeby sprawdzić czy działa
                short_sql = "\n".join(create_sql.split("\n")[:3])
                print(f"{short_sql}\n  ...")
            
    except Exception as e:
        print(f"Wystąpił błąd podczas wykonywania programu: {e}")

if __name__ == "__main__":
    main()