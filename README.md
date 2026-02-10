# Multi-Agent System 🤖

Ein intelligentes Multi-Agent-System für Software-Entwicklung mit CrewAI. Verschiedene spezialisierte KI-Agenten arbeiten zusammen, um komplexe Entwicklungsaufgaben zu lösen.

## 🎯 Features

- **Orchestrator** (Claude Sonnet 3.5): Plant und koordiniert Aufgaben
- **Developer** (DeepSeek Coder): Schreibt hochwertigen Code
- **Tester** (GPT-4o Mini): Erstellt umfassende Tests
- **Documenter** (Gemini Flash): Schreibt klare Dokumentation

## 📋 Voraussetzungen

- Python 3.8 oder höher
- OpenRouter API Key ([hier registrieren](https://openrouter.ai/keys))

## 🚀 Installation

1. **Repository klonen**
   ```bash
   git clone https://github.com/DEIN-USERNAME/DEIN-REPO-NAME.git
   cd DEIN-REPO-NAME
   ```

2. **Paket installieren**
   ```bash
   pip install -e .
   ```

3. **Umgebungsvariablen konfigurieren**
   
   Kopiere die Template-Datei:
   ```bash
   cp .env.template .env
   ```
   
   Öffne `.env` und füge deinen OpenRouter API Key ein:
   ```
   OPENROUTER_API_KEY=dein-api-key-hier
   ```

## 💡 Verwendung

Starte das Multi-Agent-System mit einer Aufgabe:

```bash
agents "Erstelle eine Python-Funktion für Fibonacci-Zahlen"
```

### Beispiele

```bash
# Web-Scraper entwickeln
agents "Entwickle einen Web-Scraper für News-Artikel"

# API erstellen
agents "Erstelle eine REST API mit FastAPI für User-Management"

# Datenanalyse
agents "Analysiere CSV-Daten und erstelle Visualisierungen"
```

## 📁 Projektstruktur

```
.
├── my_agents/          # Agent-Implementierungen
├── setup.py            # Paket-Konfiguration
├── .env.template       # Umgebungsvariablen-Vorlage
├── .gitignore          # Git-Ausschlüsse
└── README.md           # Diese Datei
```

## 🔧 Entwicklung

### Tests ausführen

```bash
python -m pytest test_math_operations.py
```

### Eigene Agenten hinzufügen

Erweitere das System durch neue Agenten im `my_agents/` Verzeichnis.

## 📝 Lizenz

Dieses Projekt ist Open Source. Siehe LICENSE-Datei für Details.

## 🤝 Beitragen

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## ⚠️ Hinweise

- **Niemals** deinen API Key committen
- Die `.env` Datei ist in `.gitignore` und wird nicht hochgeladen
- Verwende `.env.template` als Vorlage für andere Nutzer