import ollama
from pathlib import Path

class DocGenerator:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        # Biblioteka ollama domyślnie komunikuje się z http://localhost:11434 (port kontenera)

    def analyze_single_file(self, file_path: str, code_content: str) -> str:
        """
        KROK 3: Analizuje pojedynczy plik kodu źródłowego.
        Wyciąga zwięzły opis pliku oraz kompletną listę funkcji wraz z ich parametrami.
        """
        system_prompt = (
            "Jesteś precyzyjnym analitykiem kodu źródłowego.\n"
            "Twoim jedynym zadaniem jest przeczytanie przesłanego pliku i zwrócenie:\n"
            "1. Krótkiego podsumowania roli tego pliku w projekcie.\n"
            "2. Spisu zaimplementowanych w nim funkcji wraz z ich parametrami i krótkim przeznaczeniem.\n\n"
            "PISZ WYŁĄCZNIE W JĘZYKU POLSKIM. Nie twórz żadnych wstępów grzecznościowych typu 'Oto analiza...', "
            "zwróć od razu czyste, techniczne podsumowanie sformatowane w Markdown."
        )

        user_prompt = f"""
Przeanalizuj poniższy plik o ścieżce: **{file_path}**

Napisz po polsku:
1. Krótki opis (1-2 zdania): Do czego służy ten plik.
2. Wykaz funkcji/metod zaimplementowanych w tym pliku wraz z parametrami wejściowymi i ich rolą.

Oto kod źródłowy pliku:
```python
{code_content}
```
"""
        try:
            # Używamy interfejsu ollama.chat dla pełnego rygoru językowego i strukturalnego
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.1}  # Bardzo niska temperatura zapobiega halucynacjom
            )
            return response['message']['content']
        except Exception as e:
            return f"❌ Błąd podczas analizy pliku {file_path}: {e}"

    def compile_fullstack_documentation(self, file_tree: str, schema_info: dict[str, str], analyzed_modules_summary: str) -> str:
        """
        KROK 4: Kompiluje i konsoliduje wszystkie zebrane uprzednio informacje strukturalne
        w jeden profesjonalny plik dokumentacji technicznej Markdown z diagramami.
        """
        
        # Przygotowanie struktury bazy danych do końcowego raportu
        formatted_db = ""
        if schema_info:
            for table_name, sql_code in schema_info.items():
                formatted_db += f"### Tabela: {table_name}\n```sql\n{sql_code}\n```\n\n"
        else:
            formatted_db = "Brak wykrytych tabel bazy danych.\n"

        system_prompt = (
            "Jesteś wybitnym polskim Architektem Oprogramowania Fullstack.\n"
            "Twoim zadaniem jest ułożenie spójnej, czysto technicznej dokumentacji projektu (w stylu profesjonalnego README) "
            "na podstawie dostarczonych, przeanalizowanych w poprzednich krokach faktów.\n\n"
            "BEZWZGLĘDNE REGUŁY:\n"
            "1. ODPOWIADAJ WYŁĄCZNIE W JĘZYKU POLSKIM.\n"
            "2. Absolutny zakaz lania wody, marketingu i korporacyjnych ogólników. Skup się wyłącznie na konkretach technicznych.\n"
            "3. Narysuj piękny, czytelny diagram struktury warstw systemu w formacie tekstowym ASCII.\n"
            "4. Stwórz poprawny graficznie diagram przepływu Mermaid (```mermaid) rygorystycznie unikając błędów składniowych."
        )

        user_prompt = f"""
Wygeneruj kompletną dokumentację techniczną projektu na podstawie poniższych, zweryfikowanych kroków analizy.

DOKUMENTACJA MUSI ZAWIERAĆ DOKŁADNIE PONIŻSZE SEKCJE W PODANEJ KOLEJNOŚCI:

# 📘 Dokumentacja Techniczna Projektu

## 1. OPIS PROJEKTU I DIAGRAM ARCHITEKTURY
- Krótki, precyzyjny opis w języku polskim: co to za projekt, do czego służy, jakie ma zadanie i jak ogólnie działa (na podstawie dostarczonych modułów).
- Narysuj czytelny, graficzny diagram warstw systemu w formacie tekstowym ASCII block art (pokazujący przepływ danych, komunikację, serwery itp. za pomocą ramek i strzałek). Przykład struktury do odzwierciedlenia i rozbudowania:
```text
┌──────────┐          MCP           ┌───────────┐         SQLite         ┌───────────────┐
│ agent.py │ ─────────────────────> │ server.py │ ─────────────────────> │ northwind.db  │
└──────────┘                        └───────────┘                        └───────────────┘
```

## 2. STRUKTURA PLIKÓW I FOLDERÓW W PROJEKCIE
- Przedstaw poniższe rzeczywiste drzewo katalogów (ASCII Tree).
- Pod drzewem krótko (jednym zdaniem) wyjaśnij techniczną rolę każdego pliku i folderu na podstawie zebranych analiz plików.

[RZECZYWISTE DRZEWO PLIKÓW]:
```text
{file_tree}
```

## 3. OPIS DZIAŁANIA MODUŁÓW I ICH FUNKCJI
- Wykorzystując poniższe analizy jednostkowe plików, przedstaw uporządkowany opis każdego modułu/pliku oraz wylistuj jego kluczowe funkcje wraz z ich przeznaczeniem i parametrami.

[ZEBRANE ANALIZY PLIKÓW I FUNKCJI]:
{analyzed_modules_summary}

## 4. UŻYTE BIBLIOTEKI I TECHNOLOGIE
- Wypisz technologie i biblioteki zaimportowane w projekcie (np. langchain_ollama, mcp, sqlite3, asyncio itp.) wraz z wyjaśnieniem ich roli w tym konkretnym rozwiązaniu.

## 5. KONTENERYZACJA (DOCKER)
- Na podstawie analizy plików opisz jak użyto kontenera Docker (np. co odpala, konfiguracja portów, wolumeny, zmienne środowiskowe). Jeśli w kodzie nie ma konfiguracji Dockera, po prostu pomiń tę sekcję.

## 6. STRUKTURA BAZY DANYCH (SCHEMAT RELACYJNY)
- Przedstaw poniższy schemat tabel bazy danych w postaci czytelnych tabel Markdown zawierających kolumny, typy danych oraz relacje.

[SCHEMAT BAZY DANYCH]:
{formatted_db}

## 7. PRZEPŁYW DZIAŁANIA I DIAGRAM MERMAID
- Przedstaw krok po kroku sekwencyjny przepływ działania programu (Krok 1, Krok 2...).
- Wygeneruj poprawny graficznie diagram Mermaid.js (```mermaid) obrazujący architekturę i relacje komponentów.
⚠️ BEZWZGLĘDNE REGUŁY MERMAID (ZAKAZ BŁĘDÓW SKŁADNIYCH):
- Używaj wyłącznie strzałek typu `NodeA -->|Opis relacji| NodeB`.
- Zakaz stosowania znaków `>` bezpośrednio po pionowych kreskach (NIGDY nie pisz `-->|opis|>`).
- Wykorzystaj subgrafy (`subgraph`) do przejrzystego wydzielenia warstw logicznych (np. Warstwa Agenta, Warstwa Serwera MCP, Warstwa Danych).

Wygeneruj profesjonalną, czysto techniczną dokumentację po polsku spełniającą powyższe kryteria:
"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            return f"❌ Błąd podczas generowania dokumentacji końcowej: {e}"

    def save_to_file(self, content: str, output_path: Path):
        """Zapisuje wygenerowaną dokumentację do pliku Markdown na dysku."""
        try:
            output_path.write_text(content, encoding="utf-8")
            print(f"💾 Dokumentacja została pomyślnie zapisana w pliku: {output_path.resolve()}")
        except Exception as e:
            print(f"❌ Błąd podczas zapisu pliku: {e}")