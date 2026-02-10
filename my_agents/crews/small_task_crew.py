"""Small Task Crew - Schnell & Günstig für einfache Aufgaben"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import get_developer_llm, get_tester_llm, get_summarizer_llm
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """2 Agents: Developer + Tester"""
    
    package_dir = Path(__file__).parent.parent
    
    with open(package_dir / 'config' / 'agents.yaml', 'r', encoding='utf-8') as f:
        agents_config = yaml.safe_load(f)
    
    with open(package_dir / 'config' / 'tasks.yaml', 'r', encoding='utf-8') as f:
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
    
    # Developer (mit optionaler Projekt-Zusammenfassung)
    dev_config = agents_config['developer']
    dev_backstory = dev_config['backstory']
    if project_summary:
        dev_backstory = f"{dev_backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    developer = Agent(
        role=dev_config['role'],
        goal=dev_config['goal'],
        backstory=dev_backstory,
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
    
    # Tasks
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
    
    return Crew(
        agents=[developer, tester],
        tasks=[coding, testing],
        process=Process.sequential,
        verbose=True,
    )
