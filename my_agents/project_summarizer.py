"""Erstellt strukturierte Zusammenfassungen großer Projekte"""

import os
from pathlib import Path
from typing import Dict, List
from crewai import LLM


def scan_project_files(work_dir: str) -> Dict[str, List[str]]:
    """
    Scannt alle relevanten Dateien im Projekt.
    
    Args:
        work_dir: Arbeitsverzeichnis
        
    Returns:
        Dictionary mit Dateistruktur
    """
    work_path = Path(work_dir)
    
    # Ignoriere bestimmte Ordner
    ignore_dirs = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv', 
        'dist', 'build', '.cache', '.pytest_cache', 'env',
        '.next', 'coverage', '.nyc_output'
    }
    
    # Relevante Dateiendungen
    relevant_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', 
        '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift',
        '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', 
        '.css', '.scss', '.sql', '.sh', '.bat', '.ps1'
    }
    
    project_structure = {
        'code_files': [],
        'config_files': [],
        'docs': [],
        'tests': [],
        'other': []
    }
    
    for root, dirs, files in os.walk(work_path):
        # Filtere ignorierte Ordner
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = Path(root) / file
            rel_path = str(file_path.relative_to(work_path))
            
            if file_path.suffix.lower() not in relevant_extensions:
                continue
            
            # Kategorisiere Dateien
            if file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']:
                if 'test' in file.lower() or 'spec' in file.lower():
                    project_structure['tests'].append(rel_path)
                else:
                    project_structure['code_files'].append(rel_path)
            elif file_path.suffix in ['.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.env']:
                project_structure['config_files'].append(rel_path)
            elif file_path.suffix in ['.md', '.txt', '.rst']:
                project_structure['docs'].append(rel_path)
            else:
                project_structure['other'].append(rel_path)
    
    return project_structure


def read_file_safe(file_path: Path, max_size: int = 50000) -> str:
    """
    Liest eine Datei sicher (begrenzt auf max_size Zeichen).
    
    Args:
        file_path: Pfad zur Datei
        max_size: Maximale Anzahl Zeichen
        
    Returns:
        Dateiinhalt (gekürzt wenn nötig)
    """
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        if len(content) > max_size:
            return content[:max_size] + f"\n\n... [gekürzt, noch {len(content) - max_size} Zeichen]"
        return content
    except Exception:
        return f"[Fehler beim Lesen der Datei]"


def summarize_project_with_gemini(work_dir: str, llm: LLM) -> str:
    """
    Erstellt eine strukturierte Zusammenfassung des Projekts mit Gemini.
    
    Args:
        work_dir: Arbeitsverzeichnis
        llm: LLM-Instanz (Gemini)
        
    Returns:
        Kompakte Projekt-Zusammenfassung
    """
    work_path = Path(work_dir)
    
    # Scanne Projekt-Struktur
    structure = scan_project_files(work_dir)
    
    # Erstelle strukturierte Übersicht
    overview = "# PROJEKT-STRUKTUR\n\n"
    overview += f"**Code-Dateien ({len(structure['code_files'])}):**\n"
    for f in structure['code_files'][:20]:  # Erste 20
        overview += f"- {f}\n"
    if len(structure['code_files']) > 20:
        overview += f"... und {len(structure['code_files']) - 20} weitere\n"
    
    overview += f"\n**Test-Dateien ({len(structure['tests'])}):**\n"
    for f in structure['tests'][:10]:
        overview += f"- {f}\n"
    if len(structure['tests']) > 10:
        overview += f"... und {len(structure['tests']) - 10} weitere\n"
    
    overview += f"\n**Konfiguration ({len(structure['config_files'])}):**\n"
    for f in structure['config_files'][:10]:
        overview += f"- {f}\n"
    
    overview += f"\n**Dokumentation ({len(structure['docs'])}):**\n"
    for f in structure['docs'][:5]:
        overview += f"- {f}\n"
    
    # Lese wichtigste Dateien
    overview += "\n\n# DATEI-INHALTE (Auswahl)\n\n"
    
    # README
    for readme in ['README.md', 'readme.md', 'README.txt']:
        readme_path = work_path / readme
        if readme_path.exists():
            overview += f"## {readme}\n```\n{read_file_safe(readme_path, 10000)}\n```\n\n"
            break
    
    # Haupt-Code-Dateien (erste 5)
    for code_file in structure['code_files'][:5]:
        file_path = work_path / code_file
        if file_path.exists():
            overview += f"## {code_file}\n```\n{read_file_safe(file_path, 5000)}\n```\n\n"
    
    # Package-Info
    for pkg_file in ['package.json', 'setup.py', 'pyproject.toml', 'Cargo.toml']:
        pkg_path = work_path / pkg_file
        if pkg_path.exists():
            overview += f"## {pkg_file}\n```\n{read_file_safe(pkg_path, 3000)}\n```\n\n"
            break
    
    # Erstelle Zusammenfassungs-Prompt
    prompt = f"""Du bist ein Projekt-Analyst. Analysiere dieses Projekt und erstelle eine KOMPAKTE, STRUKTURIERTE Zusammenfassung.

{overview}

Erstelle eine Zusammenfassung mit folgenden Abschnitten:

1. **PROJEKT-TYP**: (Web-App, CLI-Tool, Library, API, etc.)
2. **TECHNOLOGIE-STACK**: (Sprachen, Frameworks, wichtigste Dependencies)
3. **ARCHITEKTUR**: (Ordner-Struktur, Haupt-Komponenten, Design-Pattern)
4. **KERN-FEATURES**: (Die 3-5 wichtigsten Features/Funktionen)
5. **ENTRY-POINTS**: (Wo startet die Anwendung? Haupt-Dateien?)
6. **ABHÄNGIGKEITEN**: (Externe Libraries, APIs, Datenbanken)
7. **TESTING**: (Test-Framework, Coverage, wichtige Test-Dateien)
8. **BESONDERHEITEN**: (Spezielle Konfiguration, Deployment, etc.)

WICHTIG: Halte die Zusammenfassung KOMPAKT (max 2000 Tokens). Fokus auf das Wichtigste!
"""
    
    try:
        # Nutze LLM für Zusammenfassung
        messages = [{"role": "user", "content": prompt}]
        response = llm.call(messages)
        
        # Extrahiere Text aus Response
        if hasattr(response, 'content'):
            summary = response.content
        elif isinstance(response, str):
            summary = response
        else:
            summary = str(response)
        
        return summary
        
    except Exception as e:
        # Fallback: Gebe strukturierte Übersicht zurück
        return f"# PROJEKT-ÜBERSICHT\n\n{overview}\n\n[Automatische Zusammenfassung fehlgeschlagen: {str(e)}]"
