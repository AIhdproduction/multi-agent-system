"""Schätzt Context-Größe eines Projekts"""

import os
from pathlib import Path


def estimate_project_context_size(work_dir: str) -> int:
    """
    Schätzt die Context-Größe eines Projekts in Tokens.
    
    Grobe Schätzung: 1 Token ≈ 4 Zeichen
    
    Args:
        work_dir: Arbeitsverzeichnis
        
    Returns:
        Geschätzte Context-Größe in Tokens
    """
    try:
        total_chars = 0
        file_count = 0
        
        work_path = Path(work_dir)
        
        # Ignoriere bestimmte Ordner
        ignore_dirs = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv', 
            'dist', 'build', '.cache', '.pytest_cache', 'env'
        }
        
        # Relevante Dateiendungen
        relevant_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', 
            '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift',
            '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', 
            '.css', '.scss', '.sql'
        }
        
        # Durchsuche Verzeichnis
        for root, dirs, files in os.walk(work_path):
            # Filtere ignorierte Ordner
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Prüfe Dateiendung
                if file_path.suffix.lower() in relevant_extensions:
                    try:
                        # Lese Datei und zähle Zeichen
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        total_chars += len(content)
                        file_count += 1
                    except Exception:
                        # Ignoriere Dateien die nicht gelesen werden können
                        pass
        
        # Schätze Tokens (1 Token ≈ 4 Zeichen)
        estimated_tokens = total_chars // 4
        
        return estimated_tokens
        
    except Exception:
        # Bei Fehler: Annahme kleines Projekt
        return 0


def needs_large_context(work_dir: str, threshold: int = 100_000) -> bool:
    """
    Prüft ob ein Projekt ein großes Context-Window benötigt.
    
    Args:
        work_dir: Arbeitsverzeichnis
        threshold: Schwellwert in Tokens (Standard: 100k)
        
    Returns:
        True wenn großes Context-Window benötigt wird
    """
    estimated = estimate_project_context_size(work_dir)
    return estimated > threshold


def get_project_size_category(work_dir: str) -> str:
    """
    Kategorisiert die Projektgröße.
    
    Args:
        work_dir: Arbeitsverzeichnis
        
    Returns:
        'small' (<100k tokens), 'medium' (100-400k), oder 'large' (>400k)
    """
    estimated = estimate_project_context_size(work_dir)
    
    if estimated < 100_000:
        return 'small'
    elif estimated < 400_000:
        return 'medium'
    else:
        return 'large'
