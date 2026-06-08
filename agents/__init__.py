"""
Multi-Agent System for PR Code Review

This package contains specialized agents for analyzing pull requests:
- SecurityAgent: Focuses on security vulnerabilities
- PerformanceAgent: Focuses on performance issues
- ArchitectureAgent: Focuses on code quality and maintainability
- Synthesizer: Combines and resolves findings from all agents
- MultiAgentOrchestrator: Coordinates all agents
- Scoring: Advanced scoring system for prioritizing findings

Usage:
    from agents import MultiAgentOrchestrator
    from crawler.llm_integration import LLMIntegrator
    
    llm_client = LLMIntegrator()
    orchestrator = MultiAgentOrchestrator(llm_client, model="gpt-3.5-turbo")
    report = orchestrator.analyze_pr(pr_data)
    
    # With advanced scoring:
    orchestrator = MultiAgentOrchestrator(
        llm_client,
        use_advanced_scoring=True,
        scoring_preset='security_critical'
    )
"""

from .base_agent import BaseAgent, Finding, Severity, AgentResponse
from .security_agent import SecurityAgent
from .performance_agent import PerformanceAgent
from .architecture_agent import ArchitectureAgent
from .synthesizer import Synthesizer, SynthesizedReport, Conflict
from .orchestrator import MultiAgentOrchestrator, quick_multi_agent_analysis
from .scoring import (
    AdvancedScorer,
    WeightProfile,
    WeightPresets,
    ImpactEstimate,
    create_scorer
)

from .single_agent import (
    SingleAgent,
    SingleAgentReport
)

__all__ = [
    # Base classes
    'BaseAgent',
    'Finding',
    'Severity',
    'AgentResponse',
    
    # Specialized agents
    'SecurityAgent',
    'PerformanceAgent',
    'ArchitectureAgent',
    
    # Single agent (baseline)
    'SingleAgent',
    'SingleAgentReport',
    
    # Synthesis
    'Synthesizer',
    'SynthesizedReport',
    'Conflict',
    
    # Orchestration
    'MultiAgentOrchestrator',
    'quick_multi_agent_analysis',
    
    # Scoring system
    'AdvancedScorer',
    'WeightProfile',
    'WeightPresets',
    'ImpactEstimate',
    'create_scorer',
]

__version__ = '1.0.0'
