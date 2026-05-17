"""
Base Agent Class

Provides the foundation for all specialized agents in the multi-agent system.
Each agent inherits from this class and implements specialized analysis logic.
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """
    Represents a single issue found by an agent
    
    Attributes:
        type: Type of issue (e.g., 'sql_injection', 'memory_leak')
        severity: How serious is this issue
        confidence: Agent's confidence in this finding (0.0-1.0)
        file: File where issue was found
        line: Line number (if applicable)
        description: Human-readable description
        recommendation: Suggested fix
        code_snippet: Relevant code excerpt (optional)
        context: Additional context (optional)
    """
    type: str
    severity: Severity
    confidence: float
    file: str
    description: str
    recommendation: str
    line: Optional[int] = None
    code_snippet: Optional[str] = None
    context: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "type": self.type,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "recommendation": self.recommendation,
            "code_snippet": self.code_snippet,
            "context": self.context
        }


@dataclass
class AgentResponse:
    """
    Standardized response from an agent
    
    Attributes:
        agent_name: Name of the agent (e.g., 'security', 'performance')
        findings: List of issues found
        summary: Brief summary of analysis
        risk_level: Overall risk assessment
        confidence: Overall confidence in analysis (0.0-1.0)
        execution_time: Time taken for analysis (seconds)
        metadata: Additional information
    """
    agent_name: str
    findings: List[Finding]
    summary: str
    risk_level: str
    confidence: float
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "agent_name": self.agent_name,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }
    
    @property
    def findings_count(self) -> int:
        """Total number of findings"""
        return len(self.findings)
    
    @property
    def critical_findings(self) -> List[Finding]:
        """Get critical severity findings"""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]
    
    @property
    def high_findings(self) -> List[Finding]:
        """Get high severity findings"""
        return [f for f in self.findings if f.severity == Severity.HIGH]


class BaseAgent(ABC):
    """
    Abstract base class for all PR review agents
    
    Each specialized agent must implement:
    - analyze(): Core analysis logic
    - _create_system_prompt(): Agent-specific instructions
    - _parse_llm_response(): Convert LLM output to structured findings
    """
    
    def __init__(self, llm_client, agent_name: str, model: str = "gpt-3.5-turbo", 
                 temperature: float = 0.3, max_tokens: int = 3000):
        """
        Initialize base agent
        
        Args:
            llm_client: LLM integration client
            agent_name: Name of this agent (e.g., 'security')
            model: LLM model to use
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response (GPT-3.5-turbo max: 4096)
        """
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"Initialized {agent_name} agent with model {model}")
    
    @abstractmethod
    def _create_system_prompt(self) -> str:
        """
        Create agent-specific system prompt
        
        Each agent defines its own expertise and focus areas.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def _create_analysis_prompt(self, pr_data: Dict[str, Any]) -> str:
        """
        Create analysis prompt from PR data
        
        Args:
            pr_data: Pull request data with files, diffs, metadata
            
        Returns:
            Formatted prompt for analysis
        """
        pass
    
    @abstractmethod
    def _parse_llm_response(self, response: str, pr_data: Dict[str, Any]) -> List[Finding]:
        """
        Parse LLM response into structured findings
        
        Args:
            response: Raw text response from LLM
            pr_data: Original PR data for context
            
        Returns:
            List of Finding objects
        """
        pass
    
    def analyze(self, pr_data: Dict[str, Any]) -> AgentResponse:
        """
        Analyze PR and return structured findings
        
        This is the main entry point for agent analysis.
        
        Args:
            pr_data: Dictionary containing PR information:
                - id: PR number
                - title: PR title
                - files: List of changed files with diffs
                - repository_context: Project information
                - etc.
        
        Returns:
            AgentResponse with findings and metadata
        """
        import time
        
        start_time = time.time()
        
        try:
            logger.info(f"{self.agent_name} agent starting analysis of PR #{pr_data.get('id', 'unknown')}")
            
            # Create prompts
            system_prompt = self._create_system_prompt()
            analysis_prompt = self._create_analysis_prompt(pr_data)
            
            # Call LLM
            logger.debug(f"{self.agent_name}: Calling LLM with {len(analysis_prompt)} chars prompt")
            llm_response = self._call_llm(system_prompt, analysis_prompt)
            
            # Parse response into structured findings
            findings = self._parse_llm_response(llm_response, pr_data)
            
            # Calculate metrics
            execution_time = time.time() - start_time
            risk_level = self._assess_risk_level(findings)
            confidence = self._calculate_confidence(findings)
            summary = self._generate_summary(findings)
            
            logger.info(f"{self.agent_name}: Found {len(findings)} issues in {execution_time:.2f}s")
            
            return AgentResponse(
                agent_name=self.agent_name,
                findings=findings,
                summary=summary,
                risk_level=risk_level,
                confidence=confidence,
                execution_time=execution_time,
                metadata={
                    "model": self.model,
                    "temperature": self.temperature,
                    "pr_id": pr_data.get('id')
                }
            )
            
        except Exception as e:
            logger.error(f"{self.agent_name} agent failed: {e}", exc_info=True)
            
            # Return error response
            execution_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.agent_name,
                findings=[],
                summary=f"Analysis failed: {str(e)}",
                risk_level="unknown",
                confidence=0.0,
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call LLM with prompts
        
        Args:
            system_prompt: System instructions
            user_prompt: Analysis request
            
        Returns:
            LLM response text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        from litellm import completion
        
        response = completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def _assess_risk_level(self, findings: List[Finding]) -> str:
        """
        Assess overall risk level based on findings
        
        Args:
            findings: List of findings
            
        Returns:
            Risk level: 'critical', 'high', 'medium', 'low', or 'none'
        """
        if not findings:
            return "none"
        
        # Count by severity
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium_count = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        
        if critical_count > 0:
            return "critical"
        elif high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, findings: List[Finding]) -> float:
        """
        Calculate average confidence across all findings
        
        Args:
            findings: List of findings
            
        Returns:
            Average confidence (0.0-1.0)
        """
        if not findings:
            return 1.0  # High confidence in "no issues found"
        
        total_confidence = sum(f.confidence for f in findings)
        return total_confidence / len(findings)
    
    def _generate_summary(self, findings: List[Finding]) -> str:
        """
        Generate human-readable summary of findings
        
        Args:
            findings: List of findings
            
        Returns:
            Summary string
        """
        if not findings:
            return f"{self.agent_name.capitalize()} analysis: No issues found."
        
        # Count by severity
        severity_counts = {}
        for finding in findings:
            severity = finding.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Build summary
        parts = []
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                parts.append(f"{count} {severity}")
        
        return f"{self.agent_name.capitalize()} analysis: Found {len(findings)} issues ({', '.join(parts)})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model}, temperature={self.temperature})"
