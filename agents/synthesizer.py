"""
Synthesizer

Combines findings from all agents, resolves conflicts, and generates unified report.
This is the critical component that makes multi-agent collaboration effective.
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from .base_agent import AgentResponse, Finding, Severity


logger = logging.getLogger(__name__)


@dataclass
class Conflict:
    """
    Represents a conflict between agent recommendations
    
    Example: Security wants more validation, Performance wants less overhead
    """
    agents: List[str]
    issue_type: str
    descriptions: List[str]
    resolution: str
    rationale: str


@dataclass
class SynthesizedReport:
    """
    Final unified report combining all agent findings
    
    This is what gets presented to the user.
    """
    pr_id: int
    pr_title: str
    overall_assessment: Dict[str, Any]
    priority_issues: List[Dict[str, Any]]
    all_findings: List[Finding]
    conflicts_resolved: List[Conflict]
    agent_summaries: Dict[str, str]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "pr_id": self.pr_id,
            "pr_title": self.pr_title,
            "overall_assessment": self.overall_assessment,
            "priority_issues": self.priority_issues,
            "all_findings": [f.to_dict() for f in self.all_findings],
            "conflicts_resolved": [
                {
                    "agents": c.agents,
                    "issue_type": c.issue_type,
                    "descriptions": c.descriptions,
                    "resolution": c.resolution,
                    "rationale": c.rationale
                }
                for c in self.conflicts_resolved
            ],
            "agent_summaries": self.agent_summaries,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


class Synthesizer:
    """
    Synthesizes findings from multiple agents into unified report
    
    Responsibilities:
    1. Merge findings from all agents
    2. Detect and resolve conflicts
    3. Prioritize issues by severity and impact
    4. Generate overall assessment
    5. Produce final unified report
    """
    
    def __init__(self):
        """Initialize synthesizer"""
        logger.info("Initialized Synthesizer")
    
    def synthesize(self, 
                   security_response: AgentResponse,
                   performance_response: AgentResponse,
                   architecture_response: AgentResponse,
                   pr_data: Dict[str, Any]) -> SynthesizedReport:
        """
        Synthesize findings from all agents
        
        Args:
            security_response: Security agent findings
            performance_response: Performance agent findings
            architecture_response: Architecture agent findings
            pr_data: Original PR data
            
        Returns:
            SynthesizedReport with unified findings
        """
        import time
        start_time = time.time()
        
        logger.info("Starting synthesis of multi-agent findings")
        
        # Collect all findings
        all_findings = []
        all_findings.extend(security_response.findings)
        all_findings.extend(performance_response.findings)
        all_findings.extend(architecture_response.findings)
        
        logger.info(f"Total findings: {len(all_findings)} "
                   f"(Security: {len(security_response.findings)}, "
                   f"Performance: {len(performance_response.findings)}, "
                   f"Architecture: {len(architecture_response.findings)})")
        
        # Detect conflicts
        conflicts = self._detect_conflicts(
            security_response,
            performance_response,
            architecture_response
        )
        
        logger.info(f"Detected {len(conflicts)} conflicts between agents")
        
        # Prioritize issues
        priority_issues = self._prioritize_issues(all_findings)
        
        # Generate overall assessment
        overall_assessment = self._assess_overall(
            security_response,
            performance_response,
            architecture_response,
            all_findings
        )
        
        # Create agent summaries
        agent_summaries = {
            "security": security_response.summary,
            "performance": performance_response.summary,
            "architecture": architecture_response.summary
        }
        
        execution_time = time.time() - start_time
        
        report = SynthesizedReport(
            pr_id=pr_data.get('id', 0),
            pr_title=pr_data.get('title', ''),
            overall_assessment=overall_assessment,
            priority_issues=priority_issues,
            all_findings=all_findings,
            conflicts_resolved=conflicts,
            agent_summaries=agent_summaries,
            execution_time=execution_time,
            metadata={
                "total_findings": len(all_findings),
                "conflicts_resolved": len(conflicts),
                "agents_used": ["security", "performance", "architecture"]
            }
        )
        
        logger.info(f"Synthesis complete in {execution_time:.2f}s")
        logger.info(f"Overall assessment: {overall_assessment['risk_level']} risk, "
                   f"{overall_assessment['readiness']}")
        
        return report
    
    def _detect_conflicts(self,
                          security: AgentResponse,
                          performance: AgentResponse,
                          architecture: AgentResponse) -> List[Conflict]:
        """
        Detect conflicts between agent recommendations
        
        Example conflicts:
        - Security wants input validation, Performance says it's too slow
        - Performance wants caching, Architecture says it violates SRP
        - Architecture wants abstraction, Performance says it adds overhead
        
        Args:
            security: Security agent response
            performance: Performance agent response
            architecture: Architecture agent response
            
        Returns:
            List of detected conflicts with resolutions
        """
        conflicts = []
        
        # Strategy 1: Check for overlapping files with contradicting recommendations
        security_files = {f.file: f for f in security.findings}
        performance_files = {f.file: f for f in performance.findings}
        architecture_files = {f.file: f for f in architecture.findings}
        
        # Find common files
        common_files = set(security_files.keys()) & set(performance_files.keys())
        
        for file in common_files:
            sec_finding = security_files[file]
            perf_finding = performance_files[file]
            
            # Check if recommendations conflict
            # Example: Security wants more checks, Performance wants less
            if self._recommendations_conflict(sec_finding, perf_finding):
                conflict = self._resolve_conflict(
                    [sec_finding, perf_finding],
                    ['security', 'performance']
                )
                if conflict:
                    conflicts.append(conflict)
        
        # Strategy 2: Detect philosophical conflicts
        # Security vs Performance trade-offs
        if security.findings and performance.findings:
            # Check for validation vs efficiency
            validation_findings = [f for f in security.findings 
                                  if 'validation' in f.description.lower() or 'check' in f.description.lower()]
            efficiency_findings = [f for f in performance.findings
                                  if 'slow' in f.description.lower() or 'overhead' in f.description.lower()]
            
            if validation_findings and efficiency_findings:
                conflict = Conflict(
                    agents=['security', 'performance'],
                    issue_type='validation_vs_efficiency',
                    descriptions=[
                        f"Security: {validation_findings[0].description[:100]}",
                        f"Performance: {efficiency_findings[0].description[:100]}"
                    ],
                    resolution="Implement efficient validation using pre-compiled patterns",
                    rationale="Security takes priority, but we can optimize validation methods"
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _recommendations_conflict(self, finding1: Finding, finding2: Finding) -> bool:
        """
        Check if two findings have conflicting recommendations
        
        Args:
            finding1: First finding
            finding2: Second finding
            
        Returns:
            True if recommendations conflict
        """
        # Simple heuristic: check for opposing keywords
        rec1 = finding1.recommendation.lower()
        rec2 = finding2.recommendation.lower()
        
        # Conflicting pairs
        conflicts = [
            (['add', 'implement', 'include'], ['remove', 'delete', 'eliminate']),
            (['more', 'additional', 'extra'], ['less', 'fewer', 'reduce']),
            (['complex', 'detailed'], ['simple', 'minimal']),
        ]
        
        for positive_words, negative_words in conflicts:
            has_positive = any(word in rec1 for word in positive_words)
            has_negative = any(word in rec2 for word in negative_words)
            
            if has_positive and has_negative:
                return True
        
        return False
    
    def _resolve_conflict(self, findings: List[Finding], agents: List[str]) -> Conflict:
        """
        Resolve conflict between findings
        
        Resolution strategy:
        1. Security > Performance (security always wins)
        2. Critical > Low severity (urgent issues first)
        3. High confidence > Low confidence (trust reliable findings)
        
        Args:
            findings: Conflicting findings
            agents: Agent names involved
            
        Returns:
            Conflict with resolution
        """
        # Priority order: security > performance > architecture
        agent_priority = {'security': 3, 'performance': 2, 'architecture': 1}
        
        # Sort by agent priority and severity
        sorted_findings = sorted(
            findings,
            key=lambda f: (
                agent_priority.get(f.context.get('agent', ''), 0),
                self._severity_score(f.severity),
                f.confidence
            ),
            reverse=True
        )
        
        winning_finding = sorted_findings[0]
        losing_finding = sorted_findings[1] if len(sorted_findings) > 1 else None
        
        # Generate resolution
        resolution = self._generate_resolution(winning_finding, losing_finding)
        rationale = self._generate_rationale(winning_finding, losing_finding)
        
        return Conflict(
            agents=agents,
            issue_type=winning_finding.type,
            descriptions=[f.description for f in findings],
            resolution=resolution,
            rationale=rationale
        )
    
    def _severity_score(self, severity: Severity) -> int:
        """Convert severity to numeric score"""
        scores = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        return scores.get(severity, 0)
    
    def _generate_resolution(self, winning: Finding, losing: Finding = None) -> str:
        """
        Generate resolution text
        
        Args:
            winning: Finding that takes priority
            losing: Finding that is overridden
            
        Returns:
            Resolution text
        """
        if not losing:
            return winning.recommendation
        
        # Try to find middle ground
        winning_agent = winning.context.get('agent', 'unknown')
        losing_agent = losing.context.get('agent', 'unknown')
        
        if winning_agent == 'security' and losing_agent == 'performance':
            return f"{winning.recommendation}. Optimize implementation for performance where possible."
        elif winning_agent == 'performance' and losing_agent == 'architecture':
            return f"{winning.recommendation}. Maintain code readability with clear comments."
        else:
            return winning.recommendation
    
    def _generate_rationale(self, winning: Finding, losing: Finding = None) -> str:
        """Generate rationale for resolution"""
        winning_agent = winning.context.get('agent', 'unknown')
        
        if winning_agent == 'security':
            return "Security takes priority to prevent vulnerabilities"
        elif winning.severity in [Severity.CRITICAL, Severity.HIGH]:
            return f"{winning.severity.value.capitalize()} severity issue requires immediate attention"
        elif winning.confidence > 0.8:
            return "High confidence in this finding justifies prioritization"
        else:
            return "Prioritized based on overall impact"
    
    def _prioritize_issues(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """
        Prioritize and rank all issues
        
        Ranking factors:
        1. Severity (Critical > High > Medium > Low)
        2. Agent type (Security > Performance > Architecture)
        3. Confidence (Higher confidence first)
        
        Args:
            findings: All findings from all agents
            
        Returns:
            Sorted list of priority issues
        """
        agent_priority = {'security': 3, 'performance': 2, 'architecture': 1}
        
        # Sort findings
        sorted_findings = sorted(
            findings,
            key=lambda f: (
                self._severity_score(f.severity),
                agent_priority.get(f.context.get('agent', ''), 0),
                f.confidence
            ),
            reverse=True
        )
        
        # Convert to priority issue format
        priority_issues = []
        for i, finding in enumerate(sorted_findings[:20], 1):  # Top 20 issues
            action = self._determine_action(finding)
            
            priority_issues.append({
                "priority": i,
                "severity": finding.severity.value,
                "agent": finding.context.get('agent', 'unknown'),
                "type": finding.type,
                "file": finding.file,
                "line": finding.line,
                "description": finding.description,
                "recommendation": finding.recommendation,
                "action": action,
                "confidence": finding.confidence
            })
        
        return priority_issues
    
    def _determine_action(self, finding: Finding) -> str:
        """Determine action required for finding"""
        if finding.severity == Severity.CRITICAL:
            return "MUST FIX before merge"
        elif finding.severity == Severity.HIGH:
            return "Should fix before merge"
        elif finding.severity == Severity.MEDIUM:
            return "Fix soon, can merge with tracking issue"
        else:
            return "Consider addressing in future PR"
    
    def _assess_overall(self,
                       security: AgentResponse,
                       performance: AgentResponse,
                       architecture: AgentResponse,
                       all_findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate overall assessment of the PR
        
        Args:
            security: Security agent response
            performance: Performance agent response
            architecture: Architecture agent response
            all_findings: All findings combined
            
        Returns:
            Overall assessment dictionary
        """
        # Count by severity
        critical_count = sum(1 for f in all_findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in all_findings if f.severity == Severity.HIGH)
        medium_count = sum(1 for f in all_findings if f.severity == Severity.MEDIUM)
        
        # Determine risk level (prioritize security)
        if security.risk_level in ['critical', 'high']:
            risk_level = security.risk_level
        elif critical_count > 0:
            risk_level = 'critical'
        elif high_count >= 3:
            risk_level = 'high'
        elif high_count >= 1 or medium_count >= 5:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Determine readiness
        if risk_level in ['critical', 'high']:
            readiness = 'needs_changes'
        elif risk_level == 'medium':
            readiness = 'needs_review'
        else:
            readiness = 'ready_to_merge'
        
        # Determine recommendation
        if readiness == 'needs_changes':
            recommendation = 'Request changes before merge'
        elif readiness == 'needs_review':
            recommendation = 'Approve with minor comments'
        else:
            recommendation = 'Approve'
        
        # Calculate overall confidence (weighted average)
        weights = {'security': 0.4, 'performance': 0.3, 'architecture': 0.3}
        overall_confidence = (
            security.confidence * weights['security'] +
            performance.confidence * weights['performance'] +
            architecture.confidence * weights['architecture']
        )
        
        return {
            "risk_level": risk_level,
            "readiness": readiness,
            "recommendation": recommendation,
            "confidence": round(overall_confidence, 2),
            "total_findings": len(all_findings),
            "critical_findings": critical_count,
            "high_findings": high_count,
            "medium_findings": medium_count,
            "agents_consensus": self._check_consensus(security, performance, architecture)
        }
    
    def _check_consensus(self,
                        security: AgentResponse,
                        performance: AgentResponse,
                        architecture: AgentResponse) -> str:
        """
        Check if agents agree on overall assessment
        
        Args:
            security: Security response
            performance: Performance response
            architecture: Architecture response
            
        Returns:
            Consensus status
        """
        risk_levels = [security.risk_level, performance.risk_level, architecture.risk_level]
        
        if len(set(risk_levels)) == 1:
            return "full_agreement"
        elif risk_levels.count(risk_levels[0]) >= 2:
            return "majority_agreement"
        else:
            return "divergent_views"
