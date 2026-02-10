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

## �️ Technologie-Stack

Dieses Projekt basiert auf folgenden Open-Source-Technologien und AI-Modellen:

### Framework
- **[CrewAI](https://github.com/joaomdmoura/crewAI)** - Multi-Agent Orchestration Framework
- **[CrewAI Tools](https://github.com/joaomdmoura/crewai-tools)** - Werkzeuge für Agenten
- **Python 3.8+** - Programmiersprache
- **python-dotenv** - Umgebungsvariablen-Management

### AI-Modelle (via OpenRouter)

Das System nutzt verschiedene spezialisierte AI-Modelle über [OpenRouter](https://openrouter.ai):

| Rolle | Modell | Anbieter |
|-------|--------|----------|
| Orchestrator | GPT-5-Nano | OpenAI |
| Orchestrator (Large Context) | Kimi K2.5 | Moonshot AI |
| Developer (Frontend) | Qwen3-Coder | Alibaba |
| Developer (Backend) | Codestral-2508 | Mistral AI |
| Architect | DeepSeek-V3.2 | DeepSeek |
| Security Expert | DeepSeek-V3.2 | DeepSeek |
| Code Reviewer | DeepSeek-V3.2 | DeepSeek |
| Tester | Gemini 2.5 Flash Lite | Google |
| Documenter | Gemini 2.5 Flash Lite | Google |
| Performance Expert | GPT-5-Mini | OpenAI |
| DevOps Specialist | Codestral-2508 | Mistral AI |

> **Hinweis:** Die Modellauswahl kann in `my_agents/llm_config.py` angepasst werden.

## �📝 Lizenz

Dieses Projekt ist Open Source. Siehe LICENSE-Datei für Details.

## 🤝 Beitragen

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## ⚠️ Hinweise

- **Niemals** deinen API Key committen
- Die `.env` Datei ist in `.gitignore` und wird nicht hochgeladen
- Verwende `.env.template` als Vorlage für andere Nutzer