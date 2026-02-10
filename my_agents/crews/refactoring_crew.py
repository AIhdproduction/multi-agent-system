"""Refactoring Crew - Für Code-Qualität & Legacy Code"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import (get_reviewer_llm, get_refactoring_llm, 
                                   get_tester_llm, get_documenter_llm,
                                   get_summarizer_llm)
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """4 Agents: Code Quality Improvement"""
    
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
    
    # Code Reviewer (mit optionaler Projekt-Zusammenfassung)
    reviewer_backstory = agents_config['code_reviewer']['backstory']
    if project_summary:
        reviewer_backstory = f"{reviewer_backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    reviewer = Agent(
        role=agents_config['code_reviewer']['role'],
        goal=agents_config['code_reviewer']['goal'],
        backstory=reviewer_backstory,
        verbose=True,
        tools=tools,
        llm=get_reviewer_llm(),
    )
    
    # Refactoring Expert
    refactorer = Agent(
        role=agents_config['refactoring_expert']['role'],
        goal=agents_config['refactoring_expert']['goal'],
        backstory=agents_config['refactoring_expert']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_refactoring_llm(),
    )
    
    # Tester
    tester = Agent(
        role=agents_config['tester']['role'],
        goal="Erstelle Regression Tests um sicherzustellen dass Refactoring nichts kaputt macht",
        backstory=agents_config['tester']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_tester_llm(),
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
            description=tasks_config['code_review_task']['description'],
            expected_output=tasks_config['code_review_task']['expected_output'],
            agent=reviewer,
        ),
        Task(
            description=tasks_config['refactoring_task']['description'],
            expected_output=tasks_config['refactoring_task']['expected_output'],
            agent=refactorer,
        ),
        Task(
            description="Erstelle Regression Tests um sicherzustellen, dass der refactored Code die gleiche Funktionalität hat. Teste alle Edge Cases.",
            expected_output="Regression Test Suite",
            agent=tester,
        ),
        Task(
            description="Update Dokumentation basierend auf Refactoring. Erkläre Verbesserungen.",
            expected_output="Updated Documentation",
            agent=documenter,
        ),
    ]
    
    return Crew(
        agents=[reviewer, refactorer, tester, documenter],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
