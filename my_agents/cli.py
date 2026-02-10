#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Lade .env aus Package-Verzeichnis
package_dir = Path(__file__).parent.parent
env_file = package_dir / '.env'
load_dotenv(env_file)

def print_help():
    """Zeige Hilfe"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║         🤖 Multi-Agent System v2.0                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("📋 Verwendung:")
    print("   agents \"Deine Aufgabe\"          → 🤖 LLM-Router wählt Team")
    print("   agents --team small \"Aufgabe\"   → Manuell Team wählen")
    print("   agents --list                    → Zeige alle Teams")
    print()
    print("💡 Beispiele:")
    print("   agents \"Erstelle eine FastAPI Todo-App\"")
    print("   agents \"Finde Security-Lücken in meinem Code\"")
    print("   agents \"Refactor main.py nach Clean Code\"")
    print("   agents \"Optimiere Performance von slow_function()\"")
    print()
    print("🎯 Verfügbare Teams (--team):")
    print("   small       → Schnell & günstig (Dev + Test)")
    print("   standard    → Balanced (Orchestrator + Dev + Test + Docs)")
    print("   fullstack   → Web-Apps (8 Agents)")
    print("   security    → Security Audits (5 Agents)")
    print("   refactoring → Code-Qualität (4 Agents)")
    print("   performance → Performance (3 Agents)")
    print()
    print(f"📂 Aktuelles Verzeichnis: {os.getcwd()}")

def list_teams():
    """Liste alle verfügbaren Teams"""
    from my_agents.crew_selector import get_crew_description
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║         📋 Verfügbare Teams                           ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    teams = ["small", "standard", "fullstack", "security", "refactoring", "performance"]
    
    for team in teams:
        desc = get_crew_description(team)
        print(f"  {desc}")
    
    print()
    print("💡 Verwendung: agents --team <name> \"Deine Aufgabe\"")

def main():
    # Prüfe ob OpenRouter API Key gesetzt ist
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ FEHLER: OPENROUTER_API_KEY nicht gesetzt!")
        print(f"📝 Bitte erstelle: {env_file}")
        print("   Und füge hinzu: OPENROUTER_API_KEY=dein-key-hier")
        sys.exit(1)
    
    # Hole aktuelles Arbeitsverzeichnis
    work_dir = os.getcwd()
    
    # Parse Arguments
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
    
    if args[0] in ['-l', '--list', 'list']:
        list_teams()
        sys.exit(0)
    
    # Manuelle Team-Auswahl?
    manual_team = None
    task_start_idx = 0
    
    if len(args) >= 2 and args[0] in ['-t', '--team']:
        manual_team = args[1]
        task_start_idx = 2
    
    if len(args) <= task_start_idx:
        print("❌ Keine Aufgabe angegeben!")
        print("💡 Verwendung: agents \"Deine Aufgabe\"")
        sys.exit(1)
    
    task = " ".join(args[task_start_idx:])
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║         🤖 Starte Multi-Agent System                  ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"📂 Arbeitsverzeichnis: {work_dir}")
    print(f"📋 Aufgabe: {task}")
    print("─" * 60)
    
    # Crew auswählen
    from my_agents.crew_selector import select_crew, get_crew_description
    
    if manual_team:
        # Manuell gewähltes Team
        team_name = manual_team.lower()
        print(f"👤 Manuell gewählt: {get_crew_description(team_name)}")
        
        try:
            if team_name == 'small':
                from my_agents.crews.small_task_crew import get_crew
            elif team_name == 'standard':
                from my_agents.crews.standard_crew import get_crew
            elif team_name == 'fullstack':
                from my_agents.crews.fullstack_crew import get_crew
            elif team_name == 'security':
                from my_agents.crews.security_crew import get_crew
            elif team_name == 'refactoring':
                from my_agents.crews.refactoring_crew import get_crew
            elif team_name == 'performance':
                from my_agents.crews.performance_crew import get_crew
            else:
                print(f"❌ Unbekanntes Team: {team_name}")
                print("💡 Nutze: agents --list")
                sys.exit(1)
            
            crew = get_crew(work_dir)
        except ImportError as e:
            print(f"❌ Fehler beim Laden des Teams: {e}")
            sys.exit(1)
    else:
        # Auto-Auswahl mit LLM-Router
        print("🤖 Router-Agent analysiert Aufgabe für beste Team-Auswahl...")
        crew, team_name = select_crew(task, work_dir)
        print(f"🎯 Router wählt: {get_crew_description(team_name)}")
    
    print("─" * 60)
    print()
    
    # Wechsle zum Arbeitsverzeichnis
    os.chdir(work_dir)
    
    # Starte Crew
    try:
        result = crew.kickoff(inputs={'topic': task})
        
        print()
        print("─" * 60)
        print("✅ FERTIG!")
        print("─" * 60)
        print(result)
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()