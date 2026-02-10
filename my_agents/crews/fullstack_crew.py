"""Full-Stack Crew - Für komplette Web-Anwendungen"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import (get_orchestrator_llm, get_large_context_orchestrator_llm,
                                   get_architect_llm, get_backend_llm, get_developer_llm, 
                                   get_tester_llm, get_documenter_llm, get_devops_llm,
                                   get_summarizer_llm)
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """8 Agents: Full Web Development Stack"""
    
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
        orchestrator_llm = get_orchestrator_llm()
        print("\u2705 Kleines Projekt - Nutze gpt-5-nano")
    elif project_size == 'medium':
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
        orchestrator_llm = get_large_context_orchestrator_llm()
        print("\ud83d\udcca Großes Projekt (>400k tokens) - Nutze kimi-k2.5 (200k+ context)")
    
    # Orchestrator (mit optionaler Projekt-Zusammenfassung)
    backstory = agents_config['orchestrator']['backstory']
    if project_summary:
        backstory = f"{backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    orchestrator = Agent(
        role=agents_config['orchestrator']['role'],
        goal=agents_config['orchestrator']['goal'],
        backstory=backstory,
        verbose=True,
        allow_delegation=True,
        tools=tools,
        llm=orchestrator_llm,
    )
    
    # Architect
    architect = Agent(
        role=agents_config['architect']['role'],
        goal=agents_config['architect']['goal'],
        backstory=agents_config['architect']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_architect_llm(),
    )
    
    # Backend Developer
    backend_dev = Agent(
        role=agents_config['backend_developer']['role'],
        goal=agents_config['backend_developer']['goal'],
        backstory=agents_config['backend_developer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_backend_llm(),
    )
    
    # Frontend Developer
    frontend_dev = Agent(
        role=agents_config['frontend_developer']['role'],
        goal=agents_config['frontend_developer']['goal'],
        backstory=agents_config['frontend_developer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_developer_llm(),
    )
    
    # Database Expert
    db_expert = Agent(
        role=agents_config['database_expert']['role'],
        goal=agents_config['database_expert']['goal'],
        backstory=agents_config['database_expert']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_architect_llm(),
    )
    
    # Tester
    tester = Agent(
        role=agents_config['tester']['role'],
        goal=agents_config['tester']['goal'],
        backstory=agents_config['tester']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_tester_llm(),
    )
    
    # DevOps
    devops = Agent(
        role=agents_config['devops_engineer']['role'],
        goal=agents_config['devops_engineer']['goal'],
        backstory=agents_config['devops_engineer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_devops_llm(),
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
            description=tasks_config['planning_task']['description'],
            expected_output=tasks_config['planning_task']['expected_output'],
            agent=orchestrator,
        ),
        Task(
            description=tasks_config['architecture_task']['description'],
            expected_output=tasks_config['architecture_task']['expected_output'],
            agent=architect,
        ),
        Task(
            description=tasks_config['database_design_task']['description'],
            expected_output=tasks_config['database_design_task']['expected_output'],
            agent=db_expert,
        ),
        Task(
            description=tasks_config['backend_task']['description'],
            expected_output=tasks_config['backend_task']['expected_output'],
            agent=backend_dev,
        ),
        Task(
            description=tasks_config['frontend_task']['description'],
            expected_output=tasks_config['frontend_task']['expected_output'],
            agent=frontend_dev,
        ),
        Task(
            description=tasks_config['testing_task']['description'],
            expected_output=tasks_config['testing_task']['expected_output'],
            agent=tester,
        ),
        Task(
            description=tasks_config['devops_task']['description'],
            expected_output=tasks_config['devops_task']['expected_output'],
            agent=devops,
        ),
        Task(
            description=tasks_config['documentation_task']['description'],
            expected_output=tasks_config['documentation_task']['expected_output'],
            agent=documenter,
        ),
    ]
    
    return Crew(
        agents=[orchestrator, architect, db_expert, backend_dev, frontend_dev, tester, devops, documenter],
        tasks=tasks,
        process=Process.hierarchical,
        manager_llm=orchestrator_llm,  # Nutze das gleiche LLM wie der Orchestrator-Agent
        verbose=True,
    )
