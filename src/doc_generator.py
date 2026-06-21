import ollama
from pathlib import Path


class DocGenerator:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.project_context: dict = {}  # ustawiane przez set_context()

    def set_context(
        self,
        file_tree: str,
        analyzed_modules: str,
        schema: dict[str, str],
        dependencies: list[str],
    ) -> None:
        """
        Zapisuje kontekst projektu – wywoływany raz przed generowaniem rozdziałów.
        Każde wywołanie LLM automatycznie dostaje te dane w system promptcie.
        """
        self.project_context = {
            "tree":         file_tree,
            "modules":      analyzed_modules,
            "db_schema":    schema,
            "dependencies": dependencies,
        }

    # ─────────────────────────────────────────────
    # KROK 3 – analiza pojedynczego pliku
    # ─────────────────────────────────────────────

    def analyze_single_file(self, file_path: str, code_content: str) -> str:
        system_prompt = (
            "Jesteś precyzyjnym analitykiem kodu źródłowego.\n"
            "Twoim jedynym zadaniem jest przeczytanie przesłanego pliku i zwrócenie:\n"
            "1. Krótkiego podsumowania roli tego pliku w projekcie.\n"
            "2. Spisu zaimplementowanych w nim funkcji wraz z ich parametrami i krótkim przeznaczeniem.\n\n"
            "PISZ WYŁĄCZNIE W JĘZYKU POLSKIM. Bez wstępów grzecznościowych – "
            "zwróć od razu czyste, techniczne podsumowanie w Markdown."
        )
        user_prompt = f"""
Przeanalizuj poniższy plik o ścieżce: **{file_path}**

1. Krótki opis (1-2 zdania): Do czego służy ten plik.
2. Wykaz funkcji/metod wraz z parametrami wejściowymi i ich rolą.

```python
{code_content}
```
"""
        return self._chat(system_prompt, user_prompt, context=f"analiza pliku {file_path}")

    # ─────────────────────────────────────────────
    # KROK 4 – rozdziały dokumentacji
    # ─────────────────────────────────────────────

    def generate_chapter_1(self) -> str:
        """Rozdział 1: Opis projektu + diagram architektury Mermaid."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 1. OPIS PROJEKTU I DIAGRAM ARCHITEKTURY

Zawrzyj:
- Krótki (2-3 zdania) opis: czym jest projekt, co robi, jaki problem rozwiązuje.
- Diagram architektury w bloku ```mermaid``` (flowchart TD lub graph LR).
  Uwzględnij TYLKO komponenty, które rzeczywiście istnieją w kodzie.
  Grupuj je w `subgraph`. Używaj wyłącznie strzałek `-->|opis|`.
"""
        return self._chat(self._system("architekta oprogramowania"), user_prompt, context="rozdział 1")

    def generate_chapter_2(self) -> str:
        """Rozdział 2: Struktura plików i folderów."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 2. STRUKTURA PLIKÓW I FOLDERÓW W PROJEKCIE

- Przedstaw drzewo katalogów z kontekstu jako blok ASCII (```text```).
- Pod drzewem, dla każdego pliku/folderu napisz jednym zdaniem jego techniczną rolę.
"""
        return self._chat(self._system("technicznego pisarza dokumentacji"), user_prompt, context="rozdział 2")

    def generate_chapter_3(self) -> str:
        """Rozdział 3: Opis działania modułów i ich funkcji."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 3. OPIS DZIAŁANIA MODUŁÓW I ICH FUNKCJI

Dla każdego modułu/pliku:
- Nagłówek `###` z nazwą pliku.
- 1-2 zdania opisu modułu.
- Lista kluczowych funkcji z parametrami i przeznaczeniem (format Markdown).
"""
        return self._chat(self._system("analityka kodu piszącego referencję API"), user_prompt, context="rozdział 3")

    def generate_chapter_4(self) -> str:
        """Rozdział 4: Użyte biblioteki i technologie."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 4. UŻYTE BIBLIOTEKI I TECHNOLOGIE

Na podstawie listy zależności z kontekstu projektu:
- Tabela Markdown: Biblioteka | Rola w projekcie.
- Opisz rolę każdej biblioteki w tym konkretnym projekcie, nie ogólnie.
"""
        return self._chat(self._system("inżyniera DevOps opisującego stos technologiczny"), user_prompt, context="rozdział 4")

    def generate_chapter_5(self) -> str:
        """Rozdział 5: Konteneryzacja Docker."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 5. KONTENERYZACJA (DOCKER)

Jeśli w analizach modułów widać konfigurację Dockera (Dockerfile, docker-compose itp.):
- Opisz: co odpala kontener, porty, wolumeny, zmienne środowiskowe.

Jeśli NIE ma żadnej konfiguracji Dockera, napisz tylko:
`> Projekt nie zawiera konfiguracji Docker.`
"""
        return self._chat(self._system("inżyniera DevOps specjalizującego się w Dockerze"), user_prompt, context="rozdział 5")

    def generate_chapter_6(self) -> str:
        """Rozdział 6: Struktura bazy danych."""
        schema = self.project_context.get("db_schema", {})
        if not schema:
            return "## 6. STRUKTURA BAZY DANYCH\n\n> Brak wykrytych tabel bazy danych.\n"

        user_prompt = """
Wygeneruj TYLKO sekcję:

## 6. STRUKTURA BAZY DANYCH (SCHEMAT RELACYJNY)

Na podstawie schematu SQL z kontekstu projektu:
- Dla każdej tabeli: tabela Markdown z kolumnami: Kolumna | Typ | Opis/Rola.
- Na końcu opisz relacje między tabelami (klucze obce, jeśli istnieją).
"""
        return self._chat(self._system("architekta baz danych"), user_prompt, context="rozdział 6")

    def generate_chapter_7(self) -> str:
        """Rozdział 7: Przepływ działania + diagram sekwencyjny Mermaid."""
        user_prompt = """
Wygeneruj TYLKO sekcję:

## 7. PRZEPŁYW DZIAŁANIA I DIAGRAM MERMAID

- Opisz krok po kroku sekwencję działania programu (Krok 1, Krok 2...).
- Wygeneruj diagram w bloku ```mermaid``` (sequenceDiagram lub flowchart TD).

REGUŁY MERMAID:
- Używaj wyłącznie strzałek `NodeA -->|Opis| NodeB`.
- Zakaz `>` bezpośrednio po `|`.
- Grupuj warstwy logiczne w `subgraph`.
"""
        return self._chat(self._system("architekta oprogramowania opisującego przepływ systemu"), user_prompt, context="rozdział 7")

    # ─────────────────────────────────────────────
    # Orkiestrator
    # ─────────────────────────────────────────────

    def compile_fullstack_documentation(
        self,
        file_tree: str,
        schema_info: dict[str, str],
        analyzed_modules_summary: str,
        dependencies: list[str] | None = None,
    ) -> str:
        self.set_context(
            file_tree=file_tree,
            analyzed_modules=analyzed_modules_summary,
            schema=schema_info,
            dependencies=dependencies or [],
        )

        chapters = [
            ("1. Opis projektu",      self.generate_chapter_1()),
            ("2. Struktura plików",   self.generate_chapter_2()),
            ("3. Moduły i funkcje",   self.generate_chapter_3()),
            ("4. Biblioteki",         self.generate_chapter_4()),
            ("5. Docker",             self.generate_chapter_5()),
            ("6. Baza danych",        self.generate_chapter_6()),
            ("7. Przepływ działania", self.generate_chapter_7()),
        ]

        parts = ["# 📘 Dokumentacja Techniczna Projektu\n"]
        for label, content in chapters:
            print(f"  ✅ Wygenerowano: {label}")
            parts.append(content)

        return "\n\n---\n\n".join(parts)

    # ─────────────────────────────────────────────
    # Helpery
    # ─────────────────────────────────────────────

    def _build_context_block(self) -> str:
        """Serializuje project_context do bloku tekstowego wstrzykiwanego w system prompt."""
        ctx = self.project_context
        schema_text = "\n".join(
            f"  ### {name}\n  ```sql\n  {sql}\n  ```"
            for name, sql in ctx.get("db_schema", {}).items()
        ) or "  Brak tabel."

        deps = "\n".join(f"  - {d}" for d in ctx.get("dependencies", [])) or "  Brak."

        return f"""
=== KONTEKST PROJEKTU (używaj jako źródło prawdy) ===

[DRZEWO PLIKÓW]:
{ctx.get("tree", "Brak.")}

[ANALIZY MODUŁÓW]:
{ctx.get("modules", "Brak.")}

[SCHEMAT BAZY DANYCH]:
{schema_text}

[ZALEŻNOŚCI / BIBLIOTEKI]:
{deps}

======================================================
"""

    def _system(self, rola: str) -> str:
        return (
            f"Jesteś doświadczonym {rola}.\n"
            "BEZWZGLĘDNE ZASADY:\n"
            "1. Odpowiadaj WYŁĄCZNIE po polsku.\n"
            "2. Pisz tylko tę sekcję, którą masz wygenerować – bez wstępów i podsumowań.\n"
            "3. Konkretne fakty techniczne, zero marketingu.\n"
            "4. Wszelkie informacje o projekcie czerp WYŁĄCZNIE z sekcji KONTEKST PROJEKTU poniżej.\n"
            + self._build_context_block()
        )

    def _chat(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                options={"temperature": 0.1},
            )
            return response["message"]["content"]
        except Exception as e:
            return f"❌ Błąd podczas generowania ({context}): {e}"

    def save_to_file(self, content: str, output_path: Path) -> None:
        try:
            output_path.write_text(content, encoding="utf-8")
            print(f"💾 Dokumentacja zapisana: {output_path.resolve()}")
        except Exception as e:
            print(f"❌ Błąd zapisu: {e}")