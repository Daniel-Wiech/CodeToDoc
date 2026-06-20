from pathlib import Path
from src.git_manager import GitManager
from src.db_analyzer import DBAnalyzer
from src.code_analyzer import CodeAnalyzer
from src.doc_generator import DocGenerator

def main():
    REPO_URL = "https://github.com/Daniel-Wiech/MCPNorthwind"
    REPO_NAME = "test_project"
    MODEL_NAME = "llama3"  # Jeśli pobrałeś inny model, wpisz tutaj jego nazwę (np. qwen2.5:7b)

    base_dir = Path(__file__).resolve().parents[1]
    temp_dir = base_dir / "temp_repos"
    output_doc_path = base_dir / "fullstack_documentation.md"  # Nazwa pliku wynikowego

    print(f"Folder na tymczasowe repozytoria: {temp_dir}")

    git_mgr = GitManager(temp_dir=temp_dir)
    doc_gen = DocGenerator(model_name=MODEL_NAME)
    
    try:
        # 1. Klonowanie repozytorium
        repo_path = git_mgr.clone_repository(REPO_URL, REPO_NAME)
        
        # Inicjalizacja analizatora kodu z pełną, zwalidowaną ścieżką lokalną
        code_analyzer = CodeAnalyzer(repo_path=repo_path.resolve())

        # KROK 1: Generowanie rzeczywistego drzewa plików ASCII
        print("\n📁 Krok 1: Generowanie drzewa katalogów projektu...")
        file_tree = code_analyzer.generate_ascii_tree()
        print(f"\n{file_tree}\n")

        # KROK 2: Szukanie i analiza plików bazy danych
        print("📊 Krok 2: Pobieranie schematu bazy danych...")
        db_files = git_mgr.find_db_files(repo_path)
        schema = {}  # Inicjalizujemy pusty słownik na wypadek braku bazy danych
        
        if db_files:
            print(f"Znaleziono pliki bazy danych ({len(db_files)}):")
            for db in db_files:
                print(f" - {db.relative_to(repo_path)}")
            
            # Analizujemy pierwszą znalezioną bazę danych
            primary_db = db_files[0]
            print(f"\nAnaliza struktury pliku bazy: {primary_db.name}...")
            analyzer = DBAnalyzer(db_type="sqlite", connection_string=primary_db)
            schema = analyzer.extract_schema()
            print(f"-> Wykryto {len(schema)} tabel.")
        else:
            print("-> W repozytorium nie znaleziono żadnego pliku bazy danych (.db).")

        # KROK 3: Analiza kodu źródłowego (Plik po pliku)
        print("\n💻 Krok 3: Analiza plików źródłowych (plik po pliku)...")
        code_files = code_analyzer.extract_source_code()
        print(f"Przeskanowano pliki kodu źródłowego. Znaleziono {len(code_files)} plików do analizy.")
        
        if len(code_files) == 0:
            print("⚠️ OSTRZEŻENIE: Brak plików do przeanalizowania przez LLM. Upewnij się, że klasa CodeAnalyzer poprawnie odrzuca ignorowane foldery na poziomie ścieżki względnej!")
        
        analyzed_modules_list = []
        for file_name, file_content in code_files.items():
            print(f"  └─ Analizowanie pliku przez LLM: {file_name}")
            single_analysis = doc_gen.analyze_single_file(file_name, file_content)
            
            # Formatuje analizę jednostkową dla każdego modułu
            module_doc = f"### Moduł: {file_name}\n{single_analysis}\n\n---\n"
            analyzed_modules_list.append(module_doc)
            
        # Łączymy wszystkie analizy cząstkowe w jeden uporządkowany ciąg tekstowy
        all_modules_summary = "\n".join(analyzed_modules_list)
        
        # KROK 4: Kompilacja i generowanie dokumentacji Fullstack przez Ollama
        print("\n🤖 Krok 4: Kompilowanie dokumentacji końcowej i generowanie diagramów przez AI...")
        documentation = doc_gen.compile_fullstack_documentation(
            file_tree=file_tree,
            schema_info=schema,
            analyzed_modules_summary=all_modules_summary
        )
        
        if documentation:
            # 5. Zapis wyniku do pliku
            doc_gen.save_to_file(documentation, output_doc_path)
            print("\n🚀 Sukces! Wygenerowano kompletną i stabilną dokumentację projektową.")
        else:
            print("❌ Nie udało się wygenerować dokumentacji przez model AI.")
            
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas wykonywania programu: {e}")

if __name__ == "__main__":
    main()