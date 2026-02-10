from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from pathlib import Path
import yaml

@CrewBase
class MyAgentsCrew():
    """Globales Multi-Agent System"""
    
    def __init__(self):
        # Package-Verzeichnis
        self.package_dir = Path(__file__).parent
        
        # Arbeitsverzeichnis (wo User das Kommando ausführt)
        self.work_dir = os.getcwd()
        
        # Lade Konfigurationen
        with open(self.package_dir / 'config' / 'agents.yaml', 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
        
        with open(self.package_dir / 'config' / 'tasks.yaml', 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)
        
        # OpenRouter Base URL
        self.openrouter_base = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv('OPENROUTER_API_KEY')
    
    def _create_llm_config(self, model):
        """Erstelle LLM-Config für OpenRouter"""
        return {
            "model": model,
            "api_key": self.api_key,
            "base_url": self.openrouter_base,
        }
    
    @agent
    def orchestrator(self) -> Agent:
        config = self.agents_config['orchestrator']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', True),
            tools=[
                DirectoryReadTool(directory=self.work_dir),
                FileReadTool(),
            ],
            llm="anthropic/claude-3.5-sonnet",
        )
    
    @agent
    def developer(self) -> Agent:
        config = self.agents_config['developer']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            tools=[
                DirectoryReadTool(directory=self.work_dir),
                FileReadTool(),
            ],
            llm="deepseek/deepseek-coder",
        )
    
    @agent
    def tester(self) -> Agent:
        config = self.agents_config['tester']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            tools=[
                DirectoryReadTool(directory=self.work_dir),
                FileReadTool(),
            ],
            llm="openai/gpt-4o-mini",
        )
    
    @agent
    def documenter(self) -> Agent:
        config = self.agents_config['documenter']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            tools=[
                DirectoryReadTool(directory=self.work_dir),
                FileReadTool(),
            ],
            llm="google/gemini-flash-1.5",
        )
    
    @task
    def planning_task(self) -> Task:
        config = self.tasks_config['planning_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.orchestrator(),
        )
    
    @task
    def coding_task(self) -> Task:
        config = self.tasks_config['coding_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.developer(),
        )
    
    @task
    def testing_task(self) -> Task:
        config = self.tasks_config['testing_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.tester(),
        )
    
    @task
    def documentation_task(self) -> Task:
        config = self.tasks_config['documentation_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.documenter(),
        )
    
    @crew
    def crew(self) -> Crew:
        """Erstelle die Crew mit hierarchischem Prozess"""
        return Crew(
            agents=[
                self.orchestrator(),
                self.developer(),
                self.tester(),
                self.documenter(),
            ],
            tasks=[
                self.planning_task(),
                self.coding_task(),
                self.testing_task(),
                self.documentation_task(),
            ],
            process=Process.hierarchical,
            manager_llm="anthropic/claude-3.5-sonnet",
            verbose=True,
        )