from setuptools import setup, find_packages

setup(
    name="my-agents",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.28.0",
        "crewai-tools>=0.2.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'agents=my_agents.cli:main',
        ],
    },
    author="Your Name",
    description="Multi-Agent System für VS Code",
)