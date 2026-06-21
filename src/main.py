from pathlib import Path
from git_manager import GitManager
from db_analyzer import DBAnalyzer
from code_analyzer import CodeAnalyzer
from doc_generator import DocGenerator
import argparse
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generator dokumentacji technicznej projektu.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "source",
        help=(
            "Źródło projektu:\n"
            "  URL GitHub:     https://github.com/user/repo\n"
            "  Ścieżka lokalna: /home/user/projekty/moj_projekt"
        ),
    )
    parser.add_argument(
        "--model",
        default="llama3",
        help="Nazwa modelu Ollama (domyślnie: llama3)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Ścieżka wynikowego pliku .md (domyślnie: obok skryptu)",
    )
    parser.add_argument(
    "--token",
    default=None,
    help="Token GitHub dla prywatnych repozytoriów (lub ustaw GITHUB_TOKEN w env)",
    )
    return parser.parse_args()


def resolve_repo(source: str, temp_dir: Path, git_mgr: GitManager, token: str | None = None) -> tuple[Path, str]:
    """
    Zwraca (repo_path, repo_name).
    Jeśli source to URL – klonuje. Jeśli ścieżka lokalna – używa jej bezpośrednio.
    """
    is_url = source.startswith("http://") or source.startswith("https://") or source.startswith("git@")

    if is_url:
        repo_name = Path(source.rstrip("/")).stem  # obcina .git jeśli jest
        print(f"Tryb GitHub – klonowanie: {source}")
        repo_path = git_mgr.clone_repository(source, repo_name, token=token)
    else:
        local_path = Path(source).resolve()
        if not local_path.exists():
            print(f"Podana ścieżka nie istnieje: {local_path}")
            sys.exit(1)
        if not local_path.is_dir():
            print(f"Podana ścieżka nie jest katalogiem: {local_path}")
            sys.exit(1)
        repo_name = local_path.name
        repo_path = local_path
        print(f"Tryb lokalny – używam: {repo_path}")

    return repo_path, repo_name


def main():
    args = parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    temp_dir = base_dir / "temp_repos"
    token = args.token or os.environ.get("GITHUB_TOKEN")
    git_mgr = GitManager(temp_dir=temp_dir)
    doc_gen = DocGenerator(model_name=args.model)

    repo_path, repo_name = resolve_repo(args.source, temp_dir, git_mgr, token=token)

    output_doc_path = Path(args.output) if args.output else base_dir / f"{repo_name}_documentation.md"

    try:
        code_analyzer = CodeAnalyzer(repo_path=repo_path.resolve())

        print("\nKrok 1: Generowanie drzewa katalogów projektu...")
        file_tree = code_analyzer.generate_ascii_tree()
        print(f"\n{file_tree}\n")

        print("Krok 2: Pobieranie schematu bazy danych...")
        db_files = git_mgr.find_db_files(repo_path)
        schema = {}

        if db_files:
            print(f"Znaleziono pliki bazy danych ({len(db_files)}):")
            for db in db_files:
                print(f" - {db.relative_to(repo_path)}")
            primary_db = db_files[0]
            print(f"\nAnaliza struktury pliku bazy: {primary_db.name}...")
            analyzer = DBAnalyzer(db_type="sqlite", connection_string=primary_db)
            schema = analyzer.extract_schema()
            print(f"-> Wykryto {len(schema)} tabel.")
        else:
            print("-> Nie znaleziono żadnego pliku bazy danych (.db).")

        print("\nKrok 3: Analiza plików źródłowych (plik po pliku)...")
        code_files = code_analyzer.extract_source_code()
        print(f"Znaleziono {len(code_files)} plików do analizy.")

        if len(code_files) == 0:
            print("Brak plików do przeanalizowania. Sprawdź konfigurację CodeAnalyzer.")

        analyzed_modules_list = []
        for file_name, file_content in code_files.items():
            print(f"  └─ Analizowanie: {file_name}")
            single_analysis = doc_gen.analyze_single_file(file_name, file_content)
            analyzed_modules_list.append(f"### Moduł: {file_name}\n{single_analysis}\n\n---\n")

        all_modules_summary = "\n".join(analyzed_modules_list)

        print("\nKrok 4: Generowanie dokumentacji przez AI...")
        documentation = doc_gen.compile_fullstack_documentation(
            file_tree=file_tree,
            schema_info=schema,
            analyzed_modules_summary=all_modules_summary,
        )

        if documentation:
            doc_gen.save_to_file(documentation, output_doc_path)
            print(f"\nGotowe! Dokumentacja zapisana w: {output_doc_path}")
        else:
            print("Nie udało się wygenerować dokumentacji.")

    except Exception as e:
        print(f"Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()