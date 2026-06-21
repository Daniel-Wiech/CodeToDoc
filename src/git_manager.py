import os
import shutil
import stat
from pathlib import Path
from git import Repo

class GitManager:
    def __init__(self, temp_dir: str = "temp_repos"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    def _remove_readonly(self, func, path, excinfo):
        """Pomocnicza funkcja zmieniająca uprawnienia pliku na zapisywalny w razie błędu."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

# git_manager.py - clone_repository przyjmuje token
    def clone_repository(self, repo_url: str, repo_name: str, token: str | None = None) -> Path:
        target_path = self.temp_dir / repo_name

        if target_path.exists():
            print(f"Folder {target_path} istnieje. Usuwanie starej wersji...")
            shutil.rmtree(target_path, onerror=self._remove_readonly)

        # Wstrzykujemy token do URL: https://TOKEN@github.com/user/repo
        clone_url = repo_url
        if token and repo_url.startswith("https://"):
            clone_url = repo_url.replace("https://", f"https://{token}@")

        print(f"Klonowanie repozytorium: {repo_url}...")  # logujemy oryginalny URL bez tokena
        Repo.clone_from(clone_url, target_path)
        print("Klonowanie zakończone sukcesem.")
        return target_path

    def find_db_files(self, repo_path: Path) -> list[Path]:
        """Przeszukuje folder repozytorium w poszukiwaniu plików .db."""
        print(f"Szukanie plików bazy danych w {repo_path}...")
        found_files = []
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                if file.endswith('.db'):
                    full_path = Path(root) / file
                    found_files.append(full_path)
                    
        return found_files