"""Standard Crew - Balanced für normale Projekte"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import (get_orchestrator_llm, get_developer_llm, get_tester_llm, 
                                   get_documenter_llm, get_summarizer_llm, 
                                   get_large_context_orchestrator_llm)
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """4 Agents: Orchestrator + Developer + Tester + Documenter"""
    
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
    
    # Intelligente LLM-Auswahl basierend auf Projektgröße
    project_size = get_project_size_category(work_dir)
    project_summary = None
    
    if project_size == 'small':
        # Klein (<100k): Nutze gpt-5-nano direkt
        orchestrator_llm = get_orchestrator_llm()
        print("\u2705 Kleines Projekt - Nutze gpt-5-nano")
    
    elif project_size == 'medium':
        # Mittel (100-400k): Erstelle Zusammenfassung mit Gemini, dann gpt-5-nano
        print("\ud83d\udcc4 Mittleres Projekt (100-400k tokens) - Erstelle Zusammenfassung mit Gemini...")
        try:
            summarizer_llm = get_summarizer_llm()
            project_summary = summarize_project_with_gemini(work_dir, summarizer_llm)
            print("\u2705 Zusammenfassung erstellt - Nutze gpt-5-nano mit kompakter Übersicht")
        except Exception as e:
            print(f"\u26a0\ufe0f  Zusammenfassung fehlgeschlagen: {e} - Nutze kimi-k2.5")
            project_summary = None
        orchestrator_llm = get_orchestrator_llm()
    
    else:  # large
        # Groß (>400k): Nutze kimi-k2.5 direkt (großes Context-Window)
        orchestrator_llm = get_large_context_orchestrator_llm()
        print("\ud83d\udcca Großes Projekt (>400k tokens) - Nutze kimi-k2.5 (200k+ context)")
    
    # Orchestrator (mit optionaler Projekt-Zusammenfassung)
    orch_config = agents_config['orchestrator']
    
    # Füge Projekt-Zusammenfassung zum Backstory hinzu wenn vorhanden
    backstory = orch_config['backstory']
    if project_summary:
        backstory = f"{backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    orchestrator = Agent(
        role=orch_config['role'],
        goal=orch_config['goal'],
        backstory=backstory,
        verbose=True,
        allow_delegation=True,
        tools=tools,
        llm=orchestrator_llm,
    )
    
    # Developer
    dev_config = agents_config['developer']
    developer = Agent(
        role=dev_config['role'],
        goal=dev_config['goal'],
        backstory=dev_config['backstory'],
        verbose=True,
        tools=tools,
        llm=get_developer_llm(),
    )
    
    # Tester
    test_config = agents_config['tester']
    tester = Agent(
        role=test_config['role'],
        goal=test_config['goal'],
        backstory=test_config['backstory'],
        verbose=True,
        tools=tools,
        llm=get_tester_llm(),
    )
    
    # Documenter
    doc_config = agents_config['documenter']
    documenter = Agent(
        role=doc_config['role'],
        goal=doc_config['goal'],
        backstory=doc_config['backstory'],
        verbose=True,
        tools=tools,
        llm=get_documenter_llm(),
    )
    
    # Tasks
    planning = Task(
        description=tasks_config['planning_task']['description'],
        expected_output=tasks_config['planning_task']['expected_output'],
        agent=orchestrator,
    )
    
    coding = Task(
        description=tasks_config['coding_task']['description'],
        expected_output=tasks_config['coding_task']['expected_output'],
        agent=developer,
    )
    
    testing = Task(
        description=tasks_config['testing_task']['description'],
        expected_output=tasks_config['testing_task']['expected_output'],
        agent=tester,
    )
    
    documentation = Task(
        description=tasks_config['documentation_task']['description'],
        expected_output=tasks_config['documentation_task']['expected_output'],
        agent=documenter,
    )
    
    return Crew(
        agents=[orchestrator, developer, tester, documenter],
        tasks=[planning, coding, testing, documentation],
        process=Process.hierarchical,
        manager_llm=orchestrator_llm,  # Nutze das gleiche LLM wie der Orchestrator-Agent
        verbose=True,
    )
