"""
Advanced Scoring System for Multi-Agent Findings

Implements a sophisticated scoring mechanism that considers multiple factors:
- Severity of the finding
- Agent type (security, performance, architecture)
- Confidence level
- Estimated impact
- Code complexity
- File criticality
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import Finding, Severity


logger = logging.getLogger(__name__)


@dataclass
class WeightProfile:
    """
    Weight configuration for scoring formula
    
    Each weight determines how much a factor influences the final score.
    Default weights are balanced, but can be customized per use case.
    """
    # Core weights
    severity_weight: float = 10.0      # Base severity importance (0-10 scale)
    agent_weight: float = 5.0          # Agent type importance
    confidence_weight: float = 3.0     # How much to trust confidence scores
    impact_weight: float = 7.0         # Estimated business/technical impact
    
    # Additional factors
    complexity_weight: float = 2.0     # Code complexity factor
    criticality_weight: float = 4.0    # File/component criticality
    urgency_weight: float = 3.0        # Time sensitivity
    
    # Agent-specific multipliers
    agent_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'security': 1.0,
        'performance': 1.0,
        'architecture': 1.0
    })
    
    # Severity multipliers (can boost/reduce specific severities)
    severity_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'critical': 1.0,
        'high': 1.0,
        'medium': 1.0,
        'low': 1.0,
        'info': 1.0
    })
    
    def __post_init__(self):
        """Validate weights"""
        weights = [
            self.severity_weight, self.agent_weight, self.confidence_weight,
            self.impact_weight, self.complexity_weight, self.criticality_weight,
            self.urgency_weight
        ]
        
        if any(w < 0 for w in weights):
            raise ValueError("All weights must be non-negative")
        
        logger.info(f"Initialized WeightProfile: "
                   f"severity={self.severity_weight}, agent={self.agent_weight}, "
                   f"confidence={self.confidence_weight}, impact={self.impact_weight}")


class WeightPresets:
    """Predefined weight profiles for common use cases"""
    
    @staticmethod
    def balanced() -> WeightProfile:
        """Balanced weights - default configuration"""
        return WeightProfile()
    
    @staticmethod
    def security_critical() -> WeightProfile:
        """
        Security-critical projects (e.g., banking, healthcare, auth systems)
        Heavily prioritizes security findings
        """
        return WeightProfile(
            severity_weight=12.0,      # High severity importance
            agent_weight=8.0,          # Agent type very important
            confidence_weight=4.0,
            impact_weight=10.0,        # Security impact critical
            complexity_weight=1.0,     # Less concerned with complexity
            criticality_weight=6.0,
            urgency_weight=5.0,        # Security issues are urgent
            agent_multipliers={
                'security': 2.5,       # 2.5x multiplier for security
                'performance': 0.7,    # Lower priority
                'architecture': 0.6
            },
            severity_multipliers={
                'critical': 1.5,       # Boost critical issues
                'high': 1.3,
                'medium': 1.0,
                'low': 0.8,
                'info': 0.5
            }
        )
    
    @staticmethod
    def performance_critical() -> WeightProfile:
        """
        Performance-critical projects (e.g., real-time systems, high-traffic APIs)
        Prioritizes performance and efficiency
        """
        return WeightProfile(
            severity_weight=8.0,
            agent_weight=7.0,
            confidence_weight=3.0,
            impact_weight=10.0,        # Performance impact matters most
            complexity_weight=4.0,     # Complexity affects performance
            criticality_weight=5.0,
            urgency_weight=4.0,
            agent_multipliers={
                'security': 0.8,
                'performance': 2.5,    # 2.5x multiplier for performance
                'architecture': 1.0
            },
            severity_multipliers={
                'critical': 1.4,
                'high': 1.2,
                'medium': 1.0,
                'low': 0.7,
                'info': 0.4
            }
        )
    
    @staticmethod
    def architecture_focused() -> WeightProfile:
        """
        Architecture/maintainability focused (e.g., large codebases, long-term projects)
        Emphasizes code quality and maintainability
        """
        return WeightProfile(
            severity_weight=7.0,
            agent_weight=6.0,
            confidence_weight=3.0,
            impact_weight=6.0,
            complexity_weight=5.0,     # Complexity very important
            criticality_weight=4.0,
            urgency_weight=2.0,        # Less time pressure
            agent_multipliers={
                'security': 1.0,
                'performance': 0.9,
                'architecture': 2.0    # 2x multiplier for architecture
            },
            severity_multipliers={
                'critical': 1.2,
                'high': 1.1,
                'medium': 1.0,
                'low': 0.9,
                'info': 0.8
            }
        )
    
    @staticmethod
    def startup_mvp() -> WeightProfile:
        """
        Startup/MVP projects - balance speed with critical issues
        Focus on critical bugs, less on architecture
        """
        return WeightProfile(
            severity_weight=12.0,      # Fix critical bugs
            agent_weight=4.0,
            confidence_weight=2.0,
            impact_weight=8.0,
            complexity_weight=1.0,     # Don't worry about complexity
            criticality_weight=3.0,
            urgency_weight=6.0,        # Ship fast
            agent_multipliers={
                'security': 1.5,       # Security matters
                'performance': 1.2,    # Performance matters
                'architecture': 0.5    # Architecture can wait
            },
            severity_multipliers={
                'critical': 2.0,       # MUST fix critical
                'high': 1.5,           # Should fix high
                'medium': 0.8,
                'low': 0.3,            # Low priority for MVP
                'info': 0.1
            }
        )


@dataclass
class ImpactEstimate:
    """
    Estimated impact of a finding
    
    Impact considers multiple dimensions:
    - Technical impact (how much code is affected)
    - Business impact (user-facing, revenue, security)
    - Maintenance impact (future development burden)
    """
    technical_impact: float = 0.5      # 0.0-1.0: How much code is affected
    business_impact: float = 0.5       # 0.0-1.0: User/business consequence
    maintenance_impact: float = 0.5    # 0.0-1.0: Future maintenance burden
    
    @property
    def overall_impact(self) -> float:
        """
        Calculate overall impact score (0.0-1.0)
        Weighted average of all impact dimensions
        """
        return (
            self.technical_impact * 0.3 +
            self.business_impact * 0.5 +
            self.maintenance_impact * 0.2
        )
    
    def __repr__(self) -> str:
        return (f"ImpactEstimate(overall={self.overall_impact:.2f}, "
                f"technical={self.technical_impact:.2f}, "
                f"business={self.business_impact:.2f}, "
                f"maintenance={self.maintenance_impact:.2f})")


class AdvancedScorer:
    """
    Advanced scoring system for findings
    
    Calculates comprehensive scores based on multiple weighted factors.
    Can be configured with different weight profiles for different project types.
    """
    
    def __init__(self, weight_profile: Optional[WeightProfile] = None):
        """
        Initialize scorer with weight profile
        
        Args:
            weight_profile: Custom weight configuration (defaults to balanced)
        """
        self.weights = weight_profile or WeightPresets.balanced()
        logger.info(f"Initialized AdvancedScorer with profile: {self.weights}")
    
    def score_finding(self, 
                     finding: Finding,
                     file_criticality: Optional[float] = None,
                     code_complexity: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a finding
        
        Args:
            finding: The finding to score
            file_criticality: Optional criticality score for the file (0.0-1.0)
            code_complexity: Optional complexity score (0.0-1.0)
            
        Returns:
            Dictionary with score breakdown
        """
        # Extract basic info
        agent = finding.context.get('agent', 'unknown')
        severity = finding.severity
        confidence = finding.confidence
        
        # Estimate impact
        impact = self._estimate_impact(finding)
        
        # Use provided or default values
        criticality = file_criticality if file_criticality is not None else self._default_criticality(finding)
        complexity = code_complexity if code_complexity is not None else self._default_complexity(finding)
        
        # Calculate urgency
        urgency = self._calculate_urgency(finding, impact)
        
        # Calculate component scores
        severity_score = self._score_severity(severity) * self.weights.severity_weight
        agent_score = self._score_agent(agent) * self.weights.agent_weight
        confidence_score = confidence * self.weights.confidence_weight
        impact_score = impact.overall_impact * self.weights.impact_weight
        complexity_score = complexity * self.weights.complexity_weight
        criticality_score = criticality * self.weights.criticality_weight
        urgency_score = urgency * self.weights.urgency_weight
        
        # Apply multipliers
        severity_multiplier = self.weights.severity_multipliers.get(
            severity.value, 1.0
        )
        agent_multiplier = self.weights.agent_multipliers.get(agent, 1.0)
        
        # Calculate final score
        base_score = (
            severity_score +
            agent_score +
            confidence_score +
            impact_score +
            complexity_score +
            criticality_score +
            urgency_score
        )
        
        final_score = base_score * severity_multiplier * agent_multiplier
        
        # Normalize to 0-100 scale for easier interpretation
        # Max possible score with default weights ≈ 44, so normalize
        max_possible = 50.0  # Rough estimate
        normalized_score = min(100.0, (final_score / max_possible) * 100.0)
        
        return {
            'final_score': final_score,
            'normalized_score': normalized_score,
            'breakdown': {
                'severity_score': severity_score,
                'agent_score': agent_score,
                'confidence_score': confidence_score,
                'impact_score': impact_score,
                'complexity_score': complexity_score,
                'criticality_score': criticality_score,
                'urgency_score': urgency_score
            },
            'multipliers': {
                'severity_multiplier': severity_multiplier,
                'agent_multiplier': agent_multiplier
            },
            'factors': {
                'severity': severity.value,
                'agent': agent,
                'confidence': confidence,
                'impact': impact.overall_impact,
                'complexity': complexity,
                'criticality': criticality,
                'urgency': urgency
            }
        }
    
    def score_findings(self, 
                      findings: List[Finding],
                      file_criticality_map: Optional[Dict[str, float]] = None,
                      code_complexity_map: Optional[Dict[str, float]] = None) -> List[tuple]:
        """
        Score multiple findings and return sorted list
        
        Args:
            findings: List of findings to score
            file_criticality_map: Optional map of file -> criticality score
            code_complexity_map: Optional map of file -> complexity score
            
        Returns:
            List of (finding, score_dict) tuples sorted by score (highest first)
        """
        file_crit = file_criticality_map or {}
        code_comp = code_complexity_map or {}
        
        scored_findings = []
        for finding in findings:
            score_dict = self.score_finding(
                finding,
                file_criticality=file_crit.get(finding.file),
                code_complexity=code_comp.get(finding.file)
            )
            scored_findings.append((finding, score_dict))
        
        # Sort by final score (descending)
        scored_findings.sort(key=lambda x: x[1]['final_score'], reverse=True)
        
        logger.info(f"Scored {len(findings)} findings. "
                   f"Top score: {scored_findings[0][1]['normalized_score']:.1f}/100")
        
        return scored_findings
    
    def _score_severity(self, severity: Severity) -> float:
        """Convert severity to numeric score (0-1 scale)"""
        scores = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.75,
            Severity.MEDIUM: 0.5,
            Severity.LOW: 0.25,
            Severity.INFO: 0.1
        }
        return scores.get(severity, 0.5)
    
    def _score_agent(self, agent: str) -> float:
        """
        Score based on agent type (0-1 scale)
        
        Base priorities (modified by agent_multipliers):
        - Security: 1.0
        - Performance: 0.8
        - Architecture: 0.6
        """
        base_scores = {
            'security': 1.0,
            'performance': 0.8,
            'architecture': 0.6
        }
        return base_scores.get(agent, 0.5)
    
    def _estimate_impact(self, finding: Finding) -> ImpactEstimate:
        """
        Estimate the impact of a finding
        
        Based on:
        - Finding type
        - Severity
        - File type
        - Description keywords
        """
        agent = finding.context.get('agent', '')
        severity = finding.severity
        description = finding.description.lower()
        file = finding.file.lower()
        
        # Technical impact
        technical = 0.5
        if severity in [Severity.CRITICAL, Severity.HIGH]:
            technical += 0.3
        if any(word in description for word in ['all', 'entire', 'system-wide', 'global']):
            technical += 0.2
        technical = min(1.0, technical)
        
        # Business impact
        business = 0.5
        if agent == 'security':
            business += 0.3  # Security issues have high business impact
        if any(word in description for word in ['data loss', 'breach', 'leak', 'vulnerability']):
            business += 0.4
        if any(word in description for word in ['user', 'customer', 'production']):
            business += 0.2
        if severity == Severity.CRITICAL:
            business += 0.2
        business = min(1.0, business)
        
        # Maintenance impact
        maintenance = 0.5
        if agent == 'architecture':
            maintenance += 0.2  # Architecture issues affect maintainability
        if any(word in description for word in ['duplicate', 'complexity', 'technical debt']):
            maintenance += 0.3
        if any(word in file for word in ['core', 'base', 'util', 'common']):
            maintenance += 0.2  # Core files affect more maintenance
        maintenance = min(1.0, maintenance)
        
        return ImpactEstimate(
            technical_impact=technical,
            business_impact=business,
            maintenance_impact=maintenance
        )
    
    def _default_criticality(self, finding: Finding) -> float:
        """
        Estimate file criticality based on filename and context
        
        Returns:
            Criticality score (0.0-1.0)
        """
        file = finding.file.lower()
        
        # High criticality files
        critical_patterns = [
            'auth', 'security', 'payment', 'billing', 'database', 'db',
            'user', 'account', 'admin', 'core', 'main', 'api'
        ]
        
        # Medium criticality
        medium_patterns = ['service', 'controller', 'model', 'handler']
        
        # Low criticality
        low_patterns = ['test', 'mock', 'demo', 'example', 'util', 'helper']
        
        if any(pattern in file for pattern in critical_patterns):
            return 0.9
        elif any(pattern in file for pattern in medium_patterns):
            return 0.6
        elif any(pattern in file for pattern in low_patterns):
            return 0.3
        else:
            return 0.5  # Default medium criticality
    
    def _default_complexity(self, finding: Finding) -> float:
        """
        Estimate code complexity based on finding context
        
        Returns:
            Complexity score (0.0-1.0)
        """
        description = finding.description.lower()
        
        # Indicators of high complexity
        if any(word in description for word in ['complex', 'nested', 'multiple', 'many']):
            return 0.8
        elif any(word in description for word in ['simple', 'straightforward', 'basic']):
            return 0.3
        else:
            return 0.5  # Default medium complexity
    
    def _calculate_urgency(self, finding: Finding, impact: ImpactEstimate) -> float:
        """
        Calculate urgency score (0.0-1.0)
        
        Urgency based on:
        - Severity
        - Impact
        - Finding type
        """
        severity = finding.severity
        agent = finding.context.get('agent', '')
        
        # Base urgency from severity
        urgency = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.8,
            Severity.MEDIUM: 0.5,
            Severity.LOW: 0.3,
            Severity.INFO: 0.1
        }.get(severity, 0.5)
        
        # Boost for security issues
        if agent == 'security' and severity in [Severity.CRITICAL, Severity.HIGH]:
            urgency = min(1.0, urgency + 0.2)
        
        # Boost for high business impact
        if impact.business_impact > 0.7:
            urgency = min(1.0, urgency + 0.1)
        
        return urgency


def create_scorer(preset: str = 'balanced') -> AdvancedScorer:
    """
    Factory function to create scorer with preset profile
    
    Args:
        preset: One of 'balanced', 'security_critical', 'performance_critical',
                'architecture_focused', 'startup_mvp'
                
    Returns:
        AdvancedScorer configured with preset
    """
    presets = {
        'balanced': WeightPresets.balanced,
        'security_critical': WeightPresets.security_critical,
        'performance_critical': WeightPresets.performance_critical,
        'architecture_focused': WeightPresets.architecture_focused,
        'startup_mvp': WeightPresets.startup_mvp
    }
    
    if preset not in presets:
        logger.warning(f"Unknown preset '{preset}', using 'balanced'")
        preset = 'balanced'
    
    profile = presets[preset]()
    return AdvancedScorer(weight_profile=profile)
