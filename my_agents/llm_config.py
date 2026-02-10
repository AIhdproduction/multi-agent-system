"""Zentrale LLM-Konfiguration für alle Crews"""

import os
from crewai import LLM

def get_llm(model_name: str) -> LLM:
    """
    Erstelle eine LLM-Instanz mit OpenRouter-Konfiguration.
    
    Args:
        model_name: Der Modellname (z.B. "deepseek/deepseek-v3.2")
    
    Returns:
        Konfigurierte LLM-Instanz
    """
    # Füge openrouter/ prefix hinzu, falls nicht vorhanden
    if not model_name.startswith("openrouter/"):
        model_name = f"openrouter/{model_name}"
    
    return LLM(
        model=model_name,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )


# Vorkonfigurierte LLMs für verschiedene Rollen
def get_orchestrator_llm() -> LLM:
    """LLM für Orchestrator/Manager (gpt-5-nano)"""
    return get_llm("openai/gpt-5-nano")


def get_large_context_orchestrator_llm() -> LLM:
    """LLM für Orchestrator bei großen Projekten (kimi-k2.5 - 200k+ context)"""
    return get_llm("moonshotai/kimi-k2.5")


def get_summarizer_llm() -> LLM:
    """LLM für Projekt-Zusammenfassung (gemini-2.5-flash-lite)"""
    return get_llm("google/gemini-2.5-flash-lite")


def get_developer_llm() -> LLM:
    """LLM für Developer Frontend/Komplex (qwen3-coder)"""
    return get_llm("qwen/qwen3-coder")


def get_backend_llm() -> LLM:
    """LLM für Backend Developer (codestral-2508)"""
    return get_llm("mistralai/codestral-2508")


def get_tester_llm() -> LLM:
    """LLM für Tester (gemini-2.5-flash-lite)"""
    return get_llm("google/gemini-2.5-flash-lite")


def get_documenter_llm() -> LLM:
    """LLM für Documenter (gemini-2.5-flash-lite)"""
    return get_llm("google/gemini-2.5-flash-lite")


def get_refactoring_llm() -> LLM:
    """LLM für Refactoring Expert (kimi-k2.5 - großer Context)"""
    return get_llm("moonshotai/kimi-k2.5")


def get_architect_llm() -> LLM:
    """LLM für Architect (deepseek-v3.2)"""
    return get_llm("deepseek/deepseek-v3.2")


def get_security_llm() -> LLM:
    """LLM für Security Expert (deepseek-v3.2)"""
    return get_llm("deepseek/deepseek-v3.2")


def get_reviewer_llm() -> LLM:
    """LLM für Code Reviewer (deepseek-v3.2)"""
    return get_llm("deepseek/deepseek-v3.2")


def get_performance_llm() -> LLM:
    """LLM für Performance Expert (gpt-5-mini)"""
    return get_llm("openai/gpt-5-mini")


def get_devops_llm() -> LLM:
    """LLM für DevOps Specialist (codestral-2508)"""
    return get_llm("mistralai/codestral-2508")
