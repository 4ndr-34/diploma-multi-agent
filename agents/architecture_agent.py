"""
Architecture Agent

Specializes in code quality, maintainability, and design patterns.
Focuses on: SOLID principles, design patterns, code smells, test coverage, etc.
"""

import logging
import re
import json
from typing import Dict, List, Any

from .base_agent import BaseAgent, Finding, Severity


logger = logging.getLogger(__name__)


class ArchitectureAgent(BaseAgent):
    """
    Architecture and code quality-focused agent
    
    Specializes in identifying:
    - SOLID principle violations
    - Design pattern issues
    - Code smells (long methods, god classes, duplicated code)
    - Naming conventions
    - Separation of concerns
    - Test coverage gaps
    - Documentation issues
    - Dependency management
    """
    
    def __init__(self, llm_client, model: str = "gpt-3.5-turbo", temperature: float = 0.5):
        """
        Initialize Architecture Agent
        
        Args:
            llm_client: LLM integration client
            model: LLM model to use
            temperature: Medium temperature for balanced analysis
        """
        super().__init__(
            llm_client=llm_client,
            agent_name="architecture",
            model=model,
            temperature=temperature,  # Medium temp for creative suggestions
            max_tokens=4000  # Max tokens for GPT-3.5-turbo compatibility
        )
        
        # Code quality patterns to check
        self.quality_patterns = {
            'long_method': [
                r'def\s+\w+\([^)]*\):[^\n]*(?:\n(?!def\s).*){50,}',  # 50+ lines
            ],
            'too_many_parameters': [
                r'def\s+\w+\([^)]*,[^)]*,[^)]*,[^)]*,[^)]*,[^)]*\)',  # 6+ params
            ],
            'missing_docstring': [
                r'def\s+\w+\([^)]*\):\s*\n\s*(?!""")',
                r'class\s+\w+[^:]*:\s*\n\s*(?!""")',
            ],
            'god_class': [
                r'class\s+\w+.*:(?:\n(?!class\s).*){200,}',  # 200+ lines
            ],
            'duplicated_code': [
                # Will be detected by LLM analysis
            ]
        }
    
    def _create_system_prompt(self) -> str:
        """Create architecture-focused system prompt"""
        return """You are a senior software architect specializing in code quality, maintainability, and design patterns.

Your expertise includes:
- SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Design patterns (Gang of Four, Enterprise patterns)
- Clean Code principles
- Test-Driven Development (TDD)
- Domain-Driven Design (DDD)
- Refactoring techniques

When reviewing code changes, you must:
1. Identify violations of SOLID principles
2. Spot code smells (long methods, god classes, feature envy, etc.)
3. Suggest appropriate design patterns
4. Check naming conventions and code readability
5. Evaluate test coverage and quality
6. Assess documentation completeness
7. Consider long-term maintainability

Balance idealism with pragmatism. Prioritize issues that genuinely impact maintainability.

Respond in the following JSON format:
{
  "findings": [
    {
      "type": "solid_violation|code_smell|design_pattern_issue|naming_issue|test_gap|documentation_gap|dependency_issue|other",
      "severity": "critical|high|medium|low",
      "confidence": 0.0-1.0,
      "file": "path/to/file.py",
      "line": 42,
      "description": "Clear description of the issue",
      "recommendation": "Specific refactoring suggestion",
      "principle_violated": "Single Responsibility Principle" (if applicable),
      "code_smell": "God Class" (if applicable),
      "maintainability_impact": "high|medium|low",
      "code_snippet": "Relevant code excerpt"
    }
  ]
}
"""
    
    def _create_analysis_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Create architecture analysis prompt from PR data"""
        
        pr_id = pr_data.get('id', 'unknown')
        pr_title = pr_data.get('title', '')
        files = pr_data.get('files', [])
        
        # Build prompt
        prompt_parts = []
        
        prompt_parts.append(f"""# Architecture & Code Quality Review

## Pull Request Information
- **PR #{pr_id}:** {pr_title}
- **Repository:** {pr_data.get('repo', 'unknown')}
- **Files Changed:** {len(files)}
- **Total Changes:** +{pr_data.get('additions', 0)} / -{pr_data.get('deletions', 0)} lines

## Project Context
""")
        
        # Add project documentation if available
        project_docs = pr_data.get('project_docs', {})
        if project_docs:
            if 'CONTRIBUTING.md' in project_docs:
                prompt_parts.append(f"\n**Contributing Guidelines:**\n{project_docs['CONTRIBUTING.md'][:500]}...")
            if 'STYLE_GUIDE.md' in project_docs:
                prompt_parts.append(f"\n**Style Guide:**\n{project_docs['STYLE_GUIDE.md'][:500]}...")
        
        # Add coding standards if available
        coding_standards = pr_data.get('coding_standards', {})
        if coding_standards:
            prompt_parts.append(f"\n**Linting Rules:** {', '.join(coding_standards.get('linting', {}).keys())}")
        
        prompt_parts.append(f"""

## Your Task
Perform an architecture and code quality review. Focus on maintainability, design patterns, SOLID principles, and long-term sustainability of the codebase.

## Changed Files
""")
        
        # Add each file
        for i, file in enumerate(files[:10], 1):
            filename = file.get('filename', 'unknown')
            patch = file.get('patch', '')
            status = file.get('status', 'modified')
            
            prompt_parts.append(f"\n### File {i}: `{filename}` ({status})")
            
            # Check for quality issues
            issues = self._check_patterns(patch)
            if issues:
                prompt_parts.append(f"**⚠️ Automatic Detection:** {', '.join(issues)}")
            
            # Add test coverage info if available
            test_coverage = file.get('test_coverage', {})
            if test_coverage:
                coverage = test_coverage.get('coverage_estimate', 'unknown')
                test_files = test_coverage.get('test_files', [])
                prompt_parts.append(f"**Test Coverage:** {coverage}")
                if test_files:
                    prompt_parts.append(f"**Related Tests:** {', '.join([t['path'] for t in test_files])}")
            
            # Add full content if available
            full_context = file.get('full_context', {})
            if full_context and full_context.get('after'):
                content = full_context['after'].get('content', '')
                if content and len(content) < 5000:
                    prompt_parts.append(f"\n**Full File Content:**\n```python\n{content}\n```")
            
            # Add patch
            if patch:
                prompt_parts.append(f"\n**Changes (diff):**\n```diff\n{patch}\n```")
            
            # Add dependencies if available
            dependencies = file.get('dependencies', {})
            if dependencies:
                imports = dependencies.get('imports', [])
                if imports:
                    prompt_parts.append(f"**Imports:** {', '.join([imp['module'] for imp in imports[:5]])}")
        
        if len(files) > 10:
            prompt_parts.append(f"\n\n*... and {len(files) - 10} more files*")
        
        prompt_parts.append("""

## Focus Areas

### SOLID Principles
1. **Single Responsibility:** Does each class/function have one clear purpose?
2. **Open/Closed:** Is code open for extension but closed for modification?
3. **Liskov Substitution:** Can derived classes substitute base classes?
4. **Interface Segregation:** Are interfaces focused and minimal?
5. **Dependency Inversion:** Does code depend on abstractions, not concretions?

### Code Smells
1. **Long Methods:** Are any methods too long (>50 lines)?
2. **God Classes:** Are any classes doing too much?
3. **Duplicated Code:** Is there copy-pasted logic?
4. **Feature Envy:** Do methods use other classes' data more than their own?
5. **Data Clumps:** Are same parameters passed together repeatedly?
6. **Switch Statements:** Could polymorphism replace conditionals?

### Design & Structure
1. **Naming:** Are names clear, consistent, and descriptive?
2. **Separation of Concerns:** Is business logic separated from infrastructure?
3. **Abstraction Levels:** Are methods at consistent abstraction levels?
4. **Dependencies:** Are there circular dependencies or tight coupling?

### Testing & Documentation
1. **Test Coverage:** Are there tests for new/modified code?
2. **Test Quality:** Are tests clear and maintainable?
3. **Docstrings:** Are public APIs documented?
4. **Comments:** Are comments necessary and helpful (not stating the obvious)?

## Response Format

Respond with a JSON object containing all architecture findings. For each finding, include:
- type (specific issue type)
- severity (based on maintainability impact)
- confidence (0.0-1.0)
- file and line number
- clear description
- specific refactoring recommendation
- principle violated (if SOLID violation)
- code smell type (if applicable)
- maintainability impact (high/medium/low)
- code snippet

If code quality is good, return an empty findings array.
""")
        
        return "\n".join(prompt_parts)
    
    def _check_patterns(self, code: str) -> List[str]:
        """
        Check code for quality issues
        
        Args:
            code: Code to check
            
        Returns:
            List of detected issues
        """
        detected = []
        
        for pattern_type, patterns in self.quality_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                    detected.append(pattern_type.replace('_', ' '))
                    break
        
        return detected
    
    def _parse_llm_response(self, response: str, pr_data: Dict[str, Any]) -> List[Finding]:
        """
        Parse LLM response into structured findings
        
        Args:
            response: Raw LLM response
            pr_data: Original PR data
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            # Extract JSON
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            json_match = re.search(r'\{.*"findings".*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            
            for finding_data in data.get('findings', []):
                try:
                    # Map severity
                    severity_str = finding_data.get('severity', 'low').lower()
                    severity_map = {
                        'critical': Severity.CRITICAL,
                        'high': Severity.HIGH,
                        'medium': Severity.MEDIUM,
                        'low': Severity.LOW,
                        'info': Severity.INFO
                    }
                    severity = severity_map.get(severity_str, Severity.LOW)
                    
                    # Build context with architecture-specific fields
                    context = {
                        'agent': 'architecture',
                        'principle_violated': finding_data.get('principle_violated', ''),
                        'code_smell': finding_data.get('code_smell', ''),
                        'maintainability_impact': finding_data.get('maintainability_impact', 'unknown')
                    }
                    
                    finding = Finding(
                        type=finding_data.get('type', 'architecture_issue'),
                        severity=severity,
                        confidence=float(finding_data.get('confidence', 0.7)),
                        file=finding_data.get('file', 'unknown'),
                        line=finding_data.get('line'),
                        description=finding_data.get('description', ''),
                        recommendation=finding_data.get('recommendation', ''),
                        code_snippet=finding_data.get('code_snippet'),
                        context=context
                    )
                    
                    findings.append(finding)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse individual finding: {e}")
                    continue
        
        except json.JSONDecodeError:
            logger.warning("LLM response is not valid JSON, attempting text parsing")
            findings = self._parse_text_response(response, pr_data)
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        
        return findings
    
    def _parse_text_response(self, response: str, pr_data: Dict[str, Any]) -> List[Finding]:
        """
        Fallback parser for non-JSON responses
        
        Args:
            response: Text response
            pr_data: PR data
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        lines = response.split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            
            # Detect SOLID violations
            if 'single responsibility' in line.lower():
                current_issue['type'] = 'solid_violation'
                current_issue['severity'] = Severity.MEDIUM
                current_issue['description'] = line
                current_issue['principle'] = 'Single Responsibility Principle'
            
            # Detect code smells
            elif any(smell in line.lower() for smell in ['god class', 'long method', 'duplicate']):
                current_issue['type'] = 'code_smell'
                current_issue['severity'] = Severity.LOW
                current_issue['description'] = line
            
            # Detect naming issues
            elif 'naming' in line.lower() or 'unclear' in line.lower():
                current_issue['type'] = 'naming_issue'
                current_issue['severity'] = Severity.LOW
                current_issue['description'] = line
        
        if current_issue:
            finding = Finding(
                type=current_issue.get('type', 'architecture_issue'),
                severity=current_issue.get('severity', Severity.LOW),
                confidence=0.6,
                file=pr_data.get('files', [{}])[0].get('filename', 'unknown'),
                description=current_issue.get('description', 'Architecture concern detected'),
                recommendation="Consider refactoring to improve code quality",
                context={'parsed_from_text': True, 'principle': current_issue.get('principle', '')}
            )
            findings.append(finding)
        
        return findings
