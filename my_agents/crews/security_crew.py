"""Security Crew - Für Security Audits & Penetration Testing"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import (get_security_llm, get_reviewer_llm, 
                                   get_developer_llm, get_documenter_llm,
                                   get_summarizer_llm)
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """5 Agents: Security-Focused"""
    
    package_dir = Path(__file__).parent.parent
    
    with open(package_dir / 'config' / 'agents.yaml', 'r') as f:
        agents_config = yaml.safe_load(f)
    
    with open(package_dir / 'config' / 'tasks.yaml', 'r') as f:
        tasks_config = yaml.safe_load(f)
    
    tools = [
        DirectoryReadTool(directory=work_dir),
        FileReadTool(),
        WriteFileTool(work_dir=work_dir),
        DeleteFileTool(work_dir=work_dir),
    ]
    
    # Erstelle Zusammenfassung für mittlere Projekte
    project_size = get_project_size_category(work_dir)
    project_summary = None
    
    if project_size == 'small':
        print("✅ Kleines Projekt - Direkte Verarbeitung")
    elif project_size == 'medium':
        print("📄 Mittleres Projekt (100-400k tokens) - Erstelle Zusammenfassung mit Gemini...")
        try:
            summarizer_llm = get_summarizer_llm()
            project_summary = summarize_project_with_gemini(work_dir, summarizer_llm)
            print("✅ Zusammenfassung erstellt - Agents erhalten kompakte Übersicht")
        except Exception as e:
            print(f"⚠️ Zusammenfassung fehlgeschlagen: {e}")
            project_summary = None
    else:  # large
        print("📊 Großes Projekt (>400k tokens) erkannt")
    
    # Security Expert (mit optionaler Projekt-Zusammenfassung)
    security_backstory = agents_config['security_expert']['backstory']
    if project_summary:
        security_backstory = f"{security_backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    security = Agent(
        role=agents_config['security_expert']['role'],
        goal=agents_config['security_expert']['goal'],
        backstory=security_backstory,
        verbose=True,
        tools=tools,
        llm=get_security_llm(),
    )
    
    # Code Reviewer
    reviewer = Agent(
        role=agents_config['code_reviewer']['role'],
        goal=agents_config['code_reviewer']['goal'],
        backstory=agents_config['code_reviewer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_reviewer_llm(),
    )
    
    # Penetration Tester
    pentester = Agent(
        role=agents_config['tester']['role'],
        goal="Finde Sicherheitslücken durch Penetration Testing",
        backstory=agents_config['tester']['backstory'] + "\n\nSpezialisiert auf Security Testing.",
        verbose=True,
        tools=tools,
        llm=get_developer_llm(),  # Using tester LLM for pentesting
    )
    
    # Developer (für Fixes)
    developer = Agent(
        role=agents_config['developer']['role'],
        goal="Implementiere Security-Fixes",
        backstory=agents_config['developer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_developer_llm(),
    )
    
    # Documenter
    documenter = Agent(
        role=agents_config['documenter']['role'],
        goal=agents_config['documenter']['goal'],
        backstory=agents_config['documenter']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_documenter_llm(),
    )
    
    # Tasks
    tasks = [
        Task(
            description=tasks_config['security_audit_task']['description'],
            expected_output=tasks_config['security_audit_task']['expected_output'],
            agent=security,
        ),
        Task(
            description=tasks_config['code_review_task']['description'],
            expected_output=tasks_config['code_review_task']['expected_output'],
            agent=reviewer,
        ),
        Task(
            description="Führe Penetration Tests durch. Teste auf: SQL Injection, XSS, CSRF, Authentication Bypass, Authorization Issues, Input Validation. Dokumentiere alle Findings mit PoC.",
            expected_output="Penetration Test Report mit Findings & Proof of Concepts",
            agent=pentester,
        ),
        Task(
            description="Implementiere Fixes für alle gefundenen Security-Issues. Priorisiere Critical/High Findings.",
            expected_output="Gesicherter Code mit allen Fixes implementiert",
            agent=developer,
        ),
        Task(
            description="Dokumentiere alle Security-Findings, Fixes und Best Practices für zukünftige Entwicklung.",
            expected_output="Security Documentation & Best Practices Guide",
            agent=documenter,
        ),
    ]
    
    return Crew(
        agents=[security, reviewer, pentester, developer, documenter],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
