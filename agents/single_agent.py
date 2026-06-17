"""
Single Agent Baseline

A single powerful agent that performs comprehensive code review.
Used as a baseline to compare against the multi-agent system.

This agent attempts to cover all aspects (security, performance, architecture)
in a single analysis, representing the traditional approach.
"""

import logging
import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import Finding, Severity, AgentResponse


logger = logging.getLogger(__name__)


@dataclass
class SingleAgentReport:
    """Report from single agent analysis"""
    pr_id: int
    pr_title: str
    findings: List[Finding]
    summary: str
    risk_level: str
    confidence: float
    execution_time: float
    quality_score: float
    quality_grade: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "pr_id": self.pr_id,
            "pr_title": self.pr_title,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "quality_score": self.quality_score,
            "quality_grade": self.quality_grade,
            "metadata": self.metadata
        }


class SingleAgent:
    """
    Single powerful agent for comprehensive code review
    
    Attempts to cover security, performance, and architecture in one pass.
    This represents the traditional single-agent approach.
    """
    
    def __init__(self, llm_client, model: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize single agent
        
        Args:
            llm_client: LLM integration client
            model: Model to use (recommend GPT-4 or Claude for best baseline)
            temperature: Temperature for generation (0.3 for balanced)
        """
        self.llm_client = llm_client
        self.model = model
        self.temperature = temperature
        
        logger.info(f"Initialized SingleAgent with model {model}")
    
    def analyze(self, pr_data: Dict[str, Any]) -> SingleAgentReport:
        """
        Analyze PR with single comprehensive review
        
        Args:
            pr_data: Pull request data from crawler
            
        Returns:
            SingleAgentReport with findings
        """
        pr_id = pr_data.get('id', 'unknown')
        pr_title = pr_data.get('title', '')
        
        logger.info(f"Single agent starting comprehensive analysis of PR #{pr_id}")
        start_time = time.time()
        
        try:
            # Build comprehensive prompt
            user_prompt = self._build_comprehensive_prompt(pr_data)
            
            # Build full prompt with system instructions
            system_prompt = self._get_system_prompt()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Call LLM directly
            logger.info(f"Calling {self.model} for comprehensive review...")
            response = self.llm_client._call_llm(full_prompt)
            
            # Parse response
            findings = self._parse_response(response)
            
            # Calculate metrics
            execution_time = time.time() - start_time
            risk_level = self._calculate_risk_level(findings)
            confidence = self._calculate_confidence(findings)
            summary = self._generate_summary(findings, risk_level)
            quality_score = self._calculate_quality_score(findings, risk_level)
            quality_grade = self._score_to_grade(quality_score)
            
            logger.info(f"Single agent found {len(findings)} issues in {execution_time:.2f}s")
            
            return SingleAgentReport(
                pr_id=pr_id,
                pr_title=pr_title,
                findings=findings,
                summary=summary,
                risk_level=risk_level,
                confidence=confidence,
                execution_time=execution_time,
                quality_score=quality_score,
                quality_grade=quality_grade,
                metadata={
                    "model": self.model,
                    "temperature": self.temperature,
                    "approach": "single_agent_comprehensive"
                }
            )
            
        except Exception as e:
            logger.error(f"Single agent analysis failed: {e}", exc_info=True)
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for comprehensive review"""
        return """You are an expert code reviewer with deep knowledge of:
- Security vulnerabilities and best practices
- Performance optimization and scalability
- Software architecture and design patterns
- Code quality and maintainability

Perform a comprehensive code review covering ALL aspects:
- Security issues (injection, auth, data leaks, etc.)
- Performance problems (inefficient algorithms, bottlenecks, etc.)
- Architecture concerns (design patterns, SOLID principles, etc.)
- Code quality (readability, maintainability, testing, etc.)

Be thorough and identify ALL issues, not just the most obvious ones."""
    
    def _build_comprehensive_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt"""
        
        # Format files
        files_info = []
        for file in pr_data.get('files', []):
            files_info.append(f"File: {file['filename']}")
            files_info.append(f"Status: {file['status']}")
            files_info.append(f"Changes: +{file.get('additions', 0)} -{file.get('deletions', 0)}")
            if 'patch' in file:
                files_info.append(f"Diff:\n{file['patch']}")
            files_info.append("")
        
        files_text = "\n".join(files_info)
        
        prompt = f"""Perform a comprehensive code review of this Pull Request.

PR Information:
- Title: {pr_data.get('title', 'N/A')}
- Description: {pr_data.get('body', 'N/A')}
- Author: {pr_data.get('author', 'N/A')}
- Files changed: {len(pr_data.get('files', []))}

Files and Changes:
{files_text}

Please analyze this PR and identify ALL issues in these categories:

1. **Security Issues**: Vulnerabilities, injection risks, authentication problems, data exposure
2. **Performance Issues**: Inefficient algorithms, bottlenecks, scalability concerns
3. **Architecture Issues**: Design patterns, SOLID violations, code organization
4. **Code Quality**: Readability, maintainability, testing, documentation

For EACH issue you find, provide:
- type: Issue type (e.g., "sql_injection", "n_plus_one_query", "solid_violation")
- severity: "critical", "high", "medium", or "low"
- confidence: Your confidence level (0.0-1.0)
- file: Which file has the issue
- line: Line number (if applicable, otherwise 0)
- description: Clear description of the problem
- recommendation: How to fix it

Return your findings as a JSON array:
{{
  "findings": [
    {{
      "type": "issue_type",
      "severity": "high",
      "confidence": 0.9,
      "file": "path/to/file.py",
      "line": 42,
      "description": "Description of the issue",
      "recommendation": "How to fix it"
    }}
  ]
}}

Be COMPREHENSIVE. This is a single-pass review, so catch everything now."""
        
        return prompt
    
    def _parse_response(self, response: str) -> List[Finding]:
        """Parse LLM response into findings"""
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in response")
                return []
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            findings = []
            for item in data.get('findings', []):
                # Map severity string to enum
                severity_map = {
                    'critical': Severity.CRITICAL,
                    'high': Severity.HIGH,
                    'medium': Severity.MEDIUM,
                    'low': Severity.LOW,
                    'info': Severity.INFO
                }
                
                severity = severity_map.get(
                    item.get('severity', 'medium').lower(),
                    Severity.MEDIUM
                )
                
                finding = Finding(
                    type=item.get('type', 'unknown'),
                    severity=severity,
                    confidence=float(item.get('confidence', 0.5)),
                    file=item.get('file', 'unknown'),
                    line=item.get('line', 0),
                    description=item.get('description', ''),
                    recommendation=item.get('recommendation', ''),
                    context={'agent': 'single_agent', 'category': self._categorize(item.get('type', ''))}
                )
                
                findings.append(finding)
            
            return findings
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return []
    
    def _categorize(self, issue_type: str) -> str:
        """Categorize issue type"""
        security_keywords = ['injection', 'auth', 'security', 'xss', 'csrf', 'leak', 'vulnerability']
        performance_keywords = ['slow', 'inefficient', 'bottleneck', 'n+1', 'query', 'memory']
        architecture_keywords = ['solid', 'pattern', 'design', 'architecture', 'coupling', 'cohesion']
        
        issue_lower = issue_type.lower()
        
        if any(kw in issue_lower for kw in security_keywords):
            return 'security'
        elif any(kw in issue_lower for kw in performance_keywords):
            return 'performance'
        elif any(kw in issue_lower for kw in architecture_keywords):
            return 'architecture'
        else:
            return 'quality'
    
    def _calculate_risk_level(self, findings: List[Finding]) -> str:
        """Calculate overall risk level"""
        if not findings:
            return 'low'
        
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
        
        if critical_count > 0:
            return 'critical'
        elif high_count >= 3:
            return 'high'
        elif high_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self, findings: List[Finding]) -> float:
        """Calculate average confidence"""
        if not findings:
            return 0.0
        return sum(f.confidence for f in findings) / len(findings)
    
    def _generate_summary(self, findings: List[Finding], risk_level: str) -> str:
        """Generate summary of findings"""
        if not findings:
            return "No issues found. PR looks good."
        
        by_category = {}
        for f in findings:
            category = f.context.get('category', 'other')
            by_category[category] = by_category.get(category, 0) + 1
        
        summary_parts = [f"Found {len(findings)} issues across categories:"]
        for category, count in sorted(by_category.items()):
            summary_parts.append(f"- {category.capitalize()}: {count}")
        
        summary_parts.append(f"Overall risk level: {risk_level}")
        
        return " ".join(summary_parts)
    
    def _calculate_quality_score(self, findings: List[Finding], risk_level: str) -> float:
        """Calculate quality score (same formula as multi-agent)"""
        score = 100.0
        
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium_count = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        
        score -= critical_count * 25.0
        score -= high_count * 10.0
        score -= medium_count * 3.0
        score -= (len(findings) - critical_count - high_count - medium_count) * 0.5
        
        risk_penalties = {
            'critical': -15.0,
            'high': -10.0,
            'medium': -5.0,
            'low': 0.0
        }
        score += risk_penalties.get(risk_level, 0.0)
        
        # Bonus for clean PR
        if critical_count == 0 and high_count == 0:
            score += 5.0
        
        return max(0.0, min(100.0, score))
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 97:
            return 'A+'
        elif score >= 93:
            return 'A'
        elif score >= 90:
            return 'A-'
        elif score >= 87:
            return 'B+'
        elif score >= 83:
            return 'B'
        elif score >= 80:
            return 'B-'
        elif score >= 77:
            return 'C+'
        elif score >= 73:
            return 'C'
        elif score >= 70:
            return 'C-'
        elif score >= 67:
            return 'D+'
        elif score >= 63:
            return 'D'
        elif score >= 60:
            return 'D-'
        else:
            return 'F'
