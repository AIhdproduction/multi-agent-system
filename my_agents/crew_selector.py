"""Intelligente Crew-Auswahl basierend auf Task-Beschreibung mit LLM-Router"""

import re
from typing import Tuple
from crewai import Crew, Agent, Task
import os
from my_agents.llm_config import get_orchestrator_llm

def select_crew_with_llm(task_description: str, work_dir: str) -> Tuple[Crew, str]:
    """
    Nutze ein LLM als Router-Agent zur intelligenten Team-Auswahl.
    
    Returns:
        (crew, crew_name)
    """
    
    # Router-Agent: Nur für Team-Auswahl zuständig
    router_agent = Agent(
        role="Team Router & Task Analyzer",
        goal="Analysiere die Aufgabe und wähle das optimale Team",
        backstory="""Du bist ein Experte darin, Aufgaben zu analysieren und das beste Team auszuwählen.
        
        Verfügbare Teams:
        
        1. **small** - 2 Agents (Dev + Test)
           Für: Bug-Fixes, einfache Scripts, kleine Änderungen, Quick-Fixes
           Kosten: ~$0.03 (sehr günstig)
        
        2. **standard** - 4 Agents (Orchestrator + Dev + Test + Docs)
           Für: Normale Projekte, neue Features, Module, Standard-Entwicklung
           Kosten: ~$0.10 (balanced)
        
        3. **fullstack** - 8 Agents (Orchestrator + Architect + Backend + Frontend + DB + Test + DevOps + Docs)
           Für: Komplette Web-Anwendungen, APIs mit Frontend, Microservices, Full-Stack Projekte
           Kosten: ~$0.50 (teuer aber komplett)
        
        4. **security** - 5 Agents (Security Expert + Code Reviewer + Pentester + Dev + Docs)
           Für: Security Audits, Penetration Testing, Vulnerability Scans, Security-Fixes
           Kosten: ~$0.30 (spezialisiert)
        
        5. **refactoring** - 4 Agents (Code Reviewer + Refactoring Expert + Tester + Docs)
           Für: Code-Qualität verbessern, Legacy Code modernisieren, Clean Code, Technical Debt
           Kosten: ~$0.20 (fokussiert)
        
        6. **performance** - 3 Agents (Performance Expert + Dev + Tester)
           Für: Performance-Optimierung, Bottlenecks fixen, Speed-Ups, Benchmarks
           Kosten: ~$0.15 (effizient)
        
        Deine Aufgabe: Analysiere die User-Anfrage und wähle DAS BESTE Team.
        
        Antwort-Format (nur der Team-Name, nichts anderes):
        small
        ODER
        standard
        ODER
        fullstack
        ODER
        security
        ODER
        refactoring
        ODER
        performance
        """,
        verbose=False,
        allow_delegation=False,
        llm=get_orchestrator_llm(),
    )
    
    # Routing-Task
    routing_task = Task(
        description=f"""Analysiere diese Aufgabe und wähle das beste Team:

"{task_description}"

Überlege:
- Wie komplex ist die Aufgabe?
- Welche Skills werden benötigt?
- Ist es eine Web-App (fullstack)?
- Geht es um Security (security)?
- Soll Code verbessert werden (refactoring)?
- Geht es um Performance (performance)?
- Ist es klein/einfach (small)?
- Oder normal (standard)?

Antworte NUR mit dem Team-Namen (ein Wort): small, standard, fullstack, security, refactoring oder performance
""",
        expected_output="Ein einzelnes Wort: Der Name des besten Teams (small/standard/fullstack/security/refactoring/performance)",
        agent=router_agent,
    )
    
    # Führe Routing durch
    from crewai import Crew, Process
    routing_crew = Crew(
        agents=[router_agent],
        tasks=[routing_task],
        process=Process.sequential,
        verbose=False,
    )
    
    try:
        result = routing_crew.kickoff()
        team_name = str(result).strip().lower()
        
        # Bereinige Output (falls das LLM mehr schreibt)
        valid_teams = ['small', 'standard', 'fullstack', 'security', 'refactoring', 'performance']
        for valid_team in valid_teams:
            if valid_team in team_name:
                team_name = valid_team
                break
        
        # Fallback wenn kein gültiges Team
        if team_name not in valid_teams:
            print(f"⚠️  Router-Agent antwortete: '{team_name}' - Nutze Standard-Team")
            team_name = 'standard'
        
        # Lade gewähltes Team
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
            from my_agents.crews.standard_crew import get_crew
            team_name = 'standard'
        
        return get_crew(work_dir), team_name
        
    except Exception as e:
        print(f"⚠️  Router-Agent Fehler: {e} - Nutze Standard-Team")
        from my_agents.crews.standard_crew import get_crew
        return get_crew(work_dir), "standard"


def select_crew_with_keywords(task_description: str, work_dir: str) -> Tuple[Crew, str]:
    """
    Keyword-basierte Team-Auswahl (Fallback-Methode).
    
    Returns:
        (crew, crew_name)
    """
    
    task_lower = task_description.lower()
    
    # Keywords für jedes Team
    SECURITY_KEYWORDS = [
        'security', 'vulnerability', 'penetration', 'audit', 'exploit',
        'xss', 'sql injection', 'csrf', 'authentication', 'authorization',
        'secure', 'hack', 'breach', 'owasp'
    ]
    
    REFACTORING_KEYWORDS = [
        'refactor', 'clean up', 'improve code', 'legacy', 'modernize',
        'optimize code', 'code smell', 'technical debt', 'restructure',
        'clean code', 'dry', 'solid'
    ]
    
    PERFORMANCE_KEYWORDS = [
        'performance', 'optimize', 'speed up', 'slow', 'faster',
        'bottleneck', 'profiling', 'benchmark', 'efficiency',
        'memory', 'cpu', 'latency', 'throughput'
    ]
    
    FULLSTACK_KEYWORDS = [
        'web app', 'fullstack', 'full stack', 'frontend', 'backend',
        'database', 'react', 'vue', 'api', 'rest api', 'graphql',
        'microservice', 'web application', 'spa', 'ssr'
    ]
    
    SMALL_KEYWORDS = [
        'fix bug', 'small', 'quick', 'simple', 'script', 'utility',
        'helper', 'one function', 'bug fix', 'hotfix', 'patch'
    ]
    
    # Zähle Matches
    security_score = sum(1 for kw in SECURITY_KEYWORDS if kw in task_lower)
    refactoring_score = sum(1 for kw in REFACTORING_KEYWORDS if kw in task_lower)
    performance_score = sum(1 for kw in PERFORMANCE_KEYWORDS if kw in task_lower)
    fullstack_score = sum(1 for kw in FULLSTACK_KEYWORDS if kw in task_lower)
    small_score = sum(1 for kw in SMALL_KEYWORDS if kw in task_lower)
    
    # Wähle Team mit höchstem Score
    scores = {
        'security': security_score,
        'refactoring': refactoring_score,
        'performance': performance_score,
        'fullstack': fullstack_score,
        'small': small_score,
    }
    
    max_score = max(scores.values())
    
    # Wenn kein klarer Gewinner oder alle Scores niedrig → Standard
    if max_score == 0 or list(scores.values()).count(max_score) > 1:
        from my_agents.crews.standard_crew import get_crew
        return get_crew(work_dir), "standard"
    
    # Wähle Team basierend auf höchstem Score
    if security_score == max_score:
        from my_agents.crews.security_crew import get_crew
        return get_crew(work_dir), "security"
    
    elif refactoring_score == max_score:
        from my_agents.crews.refactoring_crew import get_crew
        return get_crew(work_dir), "refactoring"
    
    elif performance_score == max_score:
        from my_agents.crews.performance_crew import get_crew
        return get_crew(work_dir), "performance"
    
    elif fullstack_score == max_score:
        from my_agents.crews.fullstack_crew import get_crew
        return get_crew(work_dir), "fullstack"
    
    elif small_score == max_score:
        from my_agents.crews.small_task_crew import get_crew
        return get_crew(work_dir), "small"
    
    # Fallback
    from my_agents.crews.standard_crew import get_crew
    return get_crew(work_dir), "standard"


def select_crew(task_description: str, work_dir: str) -> Tuple[Crew, str]:
    """
    Intelligente Team-Auswahl (Standard: LLM-Router, Fallback: Keywords).
    
    Umgebungsvariable USE_KEYWORD_ROUTER=1 für Keyword-Modus.
    
    Returns:
        (crew, crew_name)
    """
    
    # Prüfe welcher Modus
    use_keywords = os.getenv('USE_KEYWORD_ROUTER', '0') == '1'
    
    if use_keywords:
        # Keyword-basierte Auswahl (schnell, offline)
        return select_crew_with_keywords(task_description, work_dir)
    else:
        # LLM-basierte Auswahl (intelligent, benötigt API-Call)
        return select_crew_with_llm(task_description, work_dir)


def get_crew_description(crew_name: str) -> str:
    """Hole Beschreibung für Crew"""
    descriptions = {
        "small": "⚡ Small Task Crew (2 Agents: Dev + Test) - Schnell & günstig",
        "standard": "📋 Standard Crew (4 Agents: Orchestrator + Dev + Test + Docs) - Balanced",
        "fullstack": "🌐 Full-Stack Crew (8 Agents) - Komplette Web-Anwendung",
        "security": "🔒 Security Crew (5 Agents) - Security Audit & Penetration Testing",
        "refactoring": "🔧 Refactoring Crew (4 Agents) - Code-Qualität & Legacy Modernisierung",
        "performance": "⚡ Performance Crew (3 Agents) - Performance-Optimierung & Benchmarks",
    }
    return descriptions.get(crew_name, "📋 Standard Crew")
