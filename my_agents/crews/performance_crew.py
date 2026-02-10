"""Performance Crew - Für Performance-Optimierung"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml
from my_agents.llm_config import (get_performance_llm, get_developer_llm, get_tester_llm,
                                   get_summarizer_llm)
from my_agents.tools import WriteFileTool, DeleteFileTool
from my_agents.context_estimator import get_project_size_category
from my_agents.project_summarizer import summarize_project_with_gemini

def get_crew(work_dir: str):
    """3 Agents: Performance Optimization"""
    
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
    
    # Performance Expert (mit optionaler Projekt-Zusammenfassung)
    perf_backstory = agents_config['performance_expert']['backstory']
    if project_summary:
        perf_backstory = f"{perf_backstory}\n\n# PROJEKT-ZUSAMMENFASSUNG\n{project_summary}"
    
    perf_expert = Agent(
        role=agents_config['performance_expert']['role'],
        goal=agents_config['performance_expert']['goal'],
        backstory=perf_backstory,
        verbose=True,
        tools=tools,
        llm=get_performance_llm(),
    )
    
    # Developer
    developer = Agent(
        role=agents_config['developer']['role'],
        goal="Implementiere Performance-Optimierungen",
        backstory=agents_config['developer']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_developer_llm(),
    )
    
    # Tester
    tester = Agent(
        role=agents_config['tester']['role'],
        goal="Benchmark vorher/nachher und stelle sicher dass Funktionalität erhalten bleibt",
        backstory=agents_config['tester']['backstory'],
        verbose=True,
        tools=tools,
        llm=get_tester_llm(),
    )
    
    # Tasks
    tasks = [
        Task(
            description=tasks_config['performance_optimization_task']['description'],
            expected_output=tasks_config['performance_optimization_task']['expected_output'],
            agent=perf_expert,
        ),
        Task(
            description="Implementiere die vorgeschlagenen Performance-Optimierungen. Behalte Lesbarkeit bei.",
            expected_output="Optimierter Code",
            agent=developer,
        ),
        Task(
            description="Benchmark vorher/nachher. Erstelle Performance-Tests. Stelle sicher dass nichts kaputt ist.",
            expected_output="Performance Report mit Benchmarks & Tests",
            agent=tester,
        ),
    ]
    
    return Crew(
        agents=[perf_expert, developer, tester],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
