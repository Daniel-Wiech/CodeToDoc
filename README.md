# CodeToDoc

Narzędzie do automatycznego generowania technicznej dokumentacji Markdown z kodu źródłowego – lokalnego lub z GitHuba – przy użyciu lokalnego modelu LLM przez Ollama.

## Jak to działa

```
Kod źródłowy
     ↓
Analiza pliku po pliku (LLM)
     ↓
Generowanie 7 rozdziałów dokumentacji (osobne wywołanie LLM na każdy)
     ↓
Gotowy plik .md
```

Projekt stosuje zasadę **dziel i rządź** – każdy rozdział dokumentacji to osobne, krótkie wywołanie modelu, co pozwala na pracę z małymi lokalnymi LLM bez przepełnienia kontekstu.

## Wymagania

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- [Ollama](https://ollama.com/) z pobranym modelem (domyślnie `llama3`)

## Instalacja

```bash
git clone https://github.com/Daniel-Wiech/CodeToDoc.git
cd CodeToDoc
poetry install
```

## Docker (Ollama)

Projekt zawiera `docker-compose.yml`, który uruchamia Ollamę w kontenerze – nie musisz jej instalować lokalnie.

```bash
# Uruchom kontener z Ollamą w tle
docker compose up -d

# Pobierz model do kontenera
docker exec -it ollama_mcp ollama pull llama3
```

Ollama będzie dostępna pod `http://localhost:11434` – dokładnie tak samo jak instalacja lokalna, kod nie wymaga żadnych zmian.

Aby zatrzymać kontener:

```bash
docker compose down
```

## Użycie

```bash
# Repozytorium GitHub (publiczne)
poetry run python src/main.py https://github.com/user/repo

# Repozytorium GitHub (prywatne)
poetry run python src/main.py https://github.com/user/repo --token ghp_xxxxxxxxxxxx

# Projekt lokalny
poetry run python src/main.py /ścieżka/do/projektu

# Z własnym modelem i ścieżką wyjściową
poetry run python src/main.py https://github.com/user/repo --model qwen2.5:7b --output /tmp/docs.md
```

### Argumenty

| Argument | Opis | Domyślnie |
|----------|------|-----------|
| `source` | URL GitHub lub ścieżka lokalna | *(wymagany)* |
| `--model` | Nazwa modelu Ollama | `llama3` |
| `--output` | Ścieżka pliku wyjściowego `.md` | `<nazwa_projektu>_documentation.md` |
| `--token` | Token GitHub dla prywatnych repozytoriów | `$GITHUB_TOKEN` z env |

Token można też ustawić przez zmienną środowiskową (bezpieczniejsze – nie zostaje w historii terminala):

```bash
# Linux / macOS
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# PowerShell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

## Struktura projektu

```
CodeToDoc/
├── src/
│   ├── main.py            # Punkt wejścia, parsowanie argumentów, orkiestracja kroków
│   ├── doc_generator.py   # Generowanie dokumentacji rozdział po rozdziale (Ollama)
│   ├── code_analyzer.py   # Skanowanie plików źródłowych, generowanie drzewa katalogów
│   ├── db_analyzer.py     # Ekstrakcja schematu bazy danych SQLite
│   └── git_manager.py     # Klonowanie repozytoriów, wyszukiwanie plików .db
├── tests/
├── docker-compose.yml     # Kontener Ollama
├── pyproject.toml
└── README.md
```

## Wygenerowane dokumentacje (przykłady)

- [`MCPNorthwind_documentation.md`](MCPNorthwind_documentation.md) – agent SQL z bazą Northwind
- [`LLMGuard_documentation.md`](LLMGuard_documentation.md) – biblioteka do bezpieczeństwa LLM

## Zależności

| Biblioteka | Rola |
|------------|------|
| `ollama` | Komunikacja z lokalnym modelem LLM |
| `gitpython` | Klonowanie repozytoriów Git |
