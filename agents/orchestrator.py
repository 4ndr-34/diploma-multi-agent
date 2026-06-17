"""
Multi-Agent Orchestrator

Coordinates the execution of all specialized agents and synthesizer.
This is the main entry point for multi-agent PR analysis.
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional
import time

from .security_agent import SecurityAgent
from .performance_agent import PerformanceAgent
from .architecture_agent import ArchitectureAgent
from .synthesizer import Synthesizer, SynthesizedReport
from .scoring import WeightProfile


logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent PR analysis
    
    Responsibilities:
    1. Initialize all specialized agents
    2. Run agents in parallel for efficiency
    3. Collect and combine results
    4. Invoke synthesizer for final report
    """
    
    def __init__(self, 
                 llm_client, 
                 model: str = "gpt-3.5-turbo", 
                 parallel: bool = True,
                 use_advanced_scoring: bool = False,
                 weight_profile: Optional[WeightProfile] = None,
                 scoring_preset: Optional[str] = None):
        """
        Initialize orchestrator with agents
        
        Args:
            llm_client: LLM integration client
            model: Default model for all agents
            parallel: Whether to run agents in parallel (True) or sequential (False)
            use_advanced_scoring: Use advanced scoring system for prioritization
            weight_profile: Custom weight profile for advanced scoring
            scoring_preset: Preset name for advanced scoring ('balanced', 'security_critical', etc.)
        """
        self.llm_client = llm_client
        self.model = model
        self.parallel = parallel
        self.use_advanced_scoring = use_advanced_scoring
        
        logger.info(f"Initializing Multi-Agent Orchestrator (parallel={parallel}, "
                   f"advanced_scoring={use_advanced_scoring})")
        
        # Initialize agents with specialized configurations
        self.security_agent = SecurityAgent(
            llm_client=llm_client,
            model=model,
            temperature=0.2  # Low for deterministic security
        )
        
        self.performance_agent = PerformanceAgent(
            llm_client=llm_client,
            model=model,
            temperature=0.3  # Medium-low for consistent performance analysis
        )
        
        self.architecture_agent = ArchitectureAgent(
            llm_client=llm_client,
            model=model,
            temperature=0.5  # Medium for balanced architecture suggestions
        )
        
        # Initialize synthesizer with scoring configuration
        self.synthesizer = Synthesizer(
            use_advanced_scoring=use_advanced_scoring,
            weight_profile=weight_profile,
            scoring_preset=scoring_preset
        )
        
        logger.info("All agents initialized successfully")
    
    def analyze_pr(self, pr_data: Dict[str, Any]) -> SynthesizedReport:
        """
        Analyze PR using all agents and synthesize results
        
        This is the main entry point for multi-agent analysis.
        
        Args:
            pr_data: Pull request data from crawler
            
        Returns:
            SynthesizedReport with combined findings
        """
        pr_id = pr_data.get('id', 'unknown')
        pr_title = pr_data.get('title', '')
        
        logger.info(f"=" * 80)
        logger.info(f"Starting multi-agent analysis of PR #{pr_id}: {pr_title}")
        logger.info(f"=" * 80)
        
        start_time = time.time()
        
        try:
            # Run agents (parallel or sequential)
            if self.parallel:
                logger.info("Running agents in parallel...")
                agent_responses = self._run_agents_parallel(pr_data)
            else:
                logger.info("Running agents sequentially...")
                agent_responses = self._run_agents_sequential(pr_data)
            
            security_response = agent_responses['security']
            performance_response = agent_responses['performance']
            architecture_response = agent_responses['architecture']
            
            # Synthesize results
            logger.info("Synthesizing results from all agents...")
            report = self.synthesizer.synthesize(
                security_response,
                performance_response,
                architecture_response,
                pr_data
            )
            
            total_time = time.time() - start_time
            report.execution_time = total_time  # Set the actual total execution time
            
            logger.info(f"=" * 80)
            logger.info(f"Multi-agent analysis complete in {total_time:.2f}s")
            logger.info(f"Total findings: {len(report.all_findings)}")
            logger.info(f"Risk level: {report.overall_assessment['risk_level']}")
            logger.info(f"Recommendation: {report.overall_assessment['recommendation']}")
            logger.info(f"=" * 80)
            
            return report
            
        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {e}", exc_info=True)
            raise
    
    def _run_agents_parallel(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents in parallel using ThreadPoolExecutor
        
        Args:
            pr_data: PR data
            
        Returns:
            Dictionary with agent responses
        """
        responses = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all agent tasks
            futures = {
                executor.submit(self.security_agent.analyze, pr_data): 'security',
                executor.submit(self.performance_agent.analyze, pr_data): 'performance',
                executor.submit(self.architecture_agent.analyze, pr_data): 'architecture'
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    response = future.result()
                    responses[agent_name] = response
                    logger.info(f"{agent_name.capitalize()} agent completed: "
                              f"{len(response.findings)} findings in {response.execution_time:.2f}s")
                except Exception as e:
                    logger.error(f"{agent_name.capitalize()} agent failed: {e}")
                    # Create empty response for failed agent
                    from .base_agent import AgentResponse
                    responses[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        findings=[],
                        summary=f"Analysis failed: {str(e)}",
                        risk_level="unknown",
                        confidence=0.0,
                        execution_time=0.0,
                        metadata={"error": str(e)}
                    )
        
        return responses
    
    def _run_agents_sequential(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents sequentially (one after another)
        
        Args:
            pr_data: PR data
            
        Returns:
            Dictionary with agent responses
        """
        responses = {}
        
        # Run security agent
        logger.info("Running Security Agent...")
        responses['security'] = self.security_agent.analyze(pr_data)
        logger.info(f"Security agent: {len(responses['security'].findings)} findings")
        
        # Run performance agent
        logger.info("Running Performance Agent...")
        responses['performance'] = self.performance_agent.analyze(pr_data)
        logger.info(f"Performance agent: {len(responses['performance'].findings)} findings")
        
        # Run architecture agent
        logger.info("Running Architecture Agent...")
        responses['architecture'] = self.architecture_agent.analyze(pr_data)
        logger.info(f"Architecture agent: {len(responses['architecture'].findings)} findings")
        
        return responses
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents
        
        Returns:
            Status dictionary
        """
        return {
            "security": {
                "name": self.security_agent.agent_name,
                "model": self.security_agent.model,
                "temperature": self.security_agent.temperature
            },
            "performance": {
                "name": self.performance_agent.agent_name,
                "model": self.performance_agent.model,
                "temperature": self.performance_agent.temperature
            },
            "architecture": {
                "name": self.architecture_agent.agent_name,
                "model": self.architecture_agent.model,
                "temperature": self.architecture_agent.temperature
            },
            "parallel_execution": self.parallel
        }
    
    def __repr__(self) -> str:
        return (f"MultiAgentOrchestrator(model={self.model}, "
                f"parallel={self.parallel}, "
                f"agents=3)")


# Convenience function for quick analysis
def quick_multi_agent_analysis(llm_client, pr_data: Dict[str, Any], 
                               model: str = "gpt-3.5-turbo",
                               parallel: bool = True) -> SynthesizedReport:
    """
    Quick wrapper for multi-agent PR analysis
    
    Args:
        llm_client: LLM client
        pr_data: PR data from crawler
        model: LLM model to use
        parallel: Run agents in parallel
        
    Returns:
        SynthesizedReport with findings
    """
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model=model,
        parallel=parallel
    )
    
    return orchestrator.analyze_pr(pr_data)
