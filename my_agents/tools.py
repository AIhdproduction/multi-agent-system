"""Custom Tools für die Agents"""

import os
from pathlib import Path
from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field


class WriteFileInput(BaseModel):
    """Input für WriteFileTool"""
    filename: str = Field(..., description="Dateiname (relativ zum Arbeitsverzeichnis)")
    content: str = Field(..., description="Dateiinhalt")


class WriteFileTool(BaseTool):
    name: str = "Write File"
    description: str = (
        "Schreibt eine Datei im Arbeitsverzeichnis (auch in Unterordnern). "
        "Input: filename (z.B. 'script.py' oder 'src/utils.py') und content. "
        "Unterordner werden automatisch erstellt. "
        "Überschreibt existierende Dateien."
    )
    args_schema: Type[BaseModel] = WriteFileInput
    work_dir: str = Field(description="Working directory path")
    
    def _run(self, filename: str, content: str) -> str:
        """Schreibt eine Datei im Arbeitsverzeichnis"""
        try:
            work_dir_path = Path(self.work_dir).resolve()
            # Sicherheit: Nur Dateien im work_dir erlauben
            file_path = (work_dir_path / filename).resolve()
            
            # Prüfe ob Pfad innerhalb work_dir liegt
            if not str(file_path).startswith(str(work_dir_path)):
                return f"❌ Fehler: Dateien dürfen nur im Arbeitsverzeichnis erstellt werden: {work_dir_path}"
            
            # Prüfe ob Unterordner erstellt werden müssen
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Schreibe Datei
            file_path.write_text(content, encoding='utf-8')
            
            return f"✅ Datei erfolgreich gespeichert: {file_path.relative_to(work_dir_path)}"
            
        except Exception as e:
            return f"❌ Fehler beim Schreiben der Datei: {str(e)}"


class DeleteFileInput(BaseModel):
    """Input für DeleteFileTool"""
    filename: str = Field(..., description="Dateiname (relativ zum Arbeitsverzeichnis)")


class DeleteFileTool(BaseTool):
    name: str = "Delete File"
    description: str = (
        "Löscht eine Datei im Arbeitsverzeichnis (auch in Unterordnern). "
        "Input: filename (z.B. 'old_file.py' oder 'src/old.py')."
    )
    args_schema: Type[BaseModel] = DeleteFileInput
    work_dir: str = Field(description="Working directory path")
    
    def _run(self, filename: str) -> str:
        """Löscht eine Datei im Arbeitsverzeichnis"""
        try:
            work_dir_path = Path(self.work_dir).resolve()
            # Sicherheit: Nur Dateien im work_dir erlauben
            file_path = (work_dir_path / filename).resolve()
            
            # Prüfe ob Pfad innerhalb work_dir liegt
            if not str(file_path).startswith(str(work_dir_path)):
                return f"❌ Fehler: Dateien dürfen nur im Arbeitsverzeichnis gelöscht werden: {work_dir_path}"
            
            # Prüfe ob Datei existiert
            if not file_path.exists():
                return f"⚠️  Datei existiert nicht: {file_path.relative_to(work_dir_path)}"
            
            # Lösche Datei
            file_path.unlink()
            
            return f"✅ Datei erfolgreich gelöscht: {file_path.relative_to(work_dir_path)}"
            
        except Exception as e:
            return f"❌ Fehler beim Löschen der Datei: {str(e)}"
