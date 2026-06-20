from pathlib import Path

class CodeAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        # Wspierane rozszerzenia plików dla backendu i frontendu
        self.supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.vue', '.html', '.css', '.toml', '.yml', '.yaml'}
        # Katalogi, które bezwzględnie ignorujemy, aby nie analizować zbędnych zależności
        self.ignored_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.git', 
            '__pycache__', 'dist', 'build', '.idea', '.vscode',
            'temp_repos', 'migrations'
        }

    def extract_source_code(self) -> dict[str, str]:
        """
        Przeszukuje repozytorium i wyciąga kod źródłowy z plików backendu oraz frontendu.
        Zwraca słownik: {względna_ścieżka_pliku: "zawartość kodu"}
        """
        code_structure = {}
        print(f"🔍 Skanowanie plików kodu źródłowego w {self.repo_path}...")
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                # Otrzymujemy ścieżkę względną do sklonowanego projektu (np. "agent.py", "server.py")
                relative_path = file_path.relative_to(self.repo_path)
                
                # POPRAWKA: Filtrujemy tylko na podstawie części ścieżki względnej,
                # aby nadrzędne katalogi takie jak "temp_repos" nie odrzucały wszystkich plików.
                if any(ignored in relative_path.parts for ignored in self.ignored_dirs):
                    continue
                
                try:
                    relative_name = str(relative_path)
                    # Odczytujemy zawartość pliku z kodowaniem UTF-8
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Ograniczamy rozmiar pojedynczego pliku do analizy jednostkowej
                    code_structure[relative_name] = content[:4000]
                except Exception as e:
                    continue
                    
        return code_structure

    def generate_ascii_tree(self) -> str:
        """
        Generuje rzeczywiste, czyste drzewo katalogów i plików (ASCII Tree) dla projektu,
        pomijając ignorowane foldery.
        """
        tree_lines = []
        
        def _build_tree(dir_path: Path, prefix: str = ""):
            # Pobieramy elementy i filtrujemy ignorowane foldery
            items = sorted(
                [x for x in dir_path.iterdir() if x.name not in self.ignored_dirs],
                key=lambda x: (x.is_file(), x.name.lower())
            )
            
            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                connector = "└── " if is_last else "├── "
                
                # Dodajemy plik lub folder do drzewa
                tree_lines.append(f"{prefix}{connector}{item.name}")
                
                if item.is_dir():
                    # Rekurencyjne zagłębianie się w foldery
                    extension = "    " if is_last else "│   "
                    _build_tree(item, prefix + extension)

        # Uruchamiamy budowanie od głównego katalogu repozytorium
        tree_lines.append(self.repo_path.name)
        _build_tree(self.repo_path)
        return "\n".join(tree_lines)