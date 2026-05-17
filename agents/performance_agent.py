"""
Performance Agent

Specializes in detecting performance issues and optimization opportunities.
Focuses on: algorithmic complexity, memory usage, inefficient patterns, etc.
"""

import logging
import re
import json
from typing import Dict, List, Any

from .base_agent import BaseAgent, Finding, Severity


logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Performance-focused code review agent
    
    Specializes in identifying:
    - Inefficient algorithms (O(n²) where O(n) possible)
    - Memory leaks and resource management issues
    - Unnecessary loops and redundant operations
    - Database query optimization (N+1 queries)
    - Synchronous I/O in hot paths
    - Missing caching opportunities
    - Inefficient data structures
    """
    
    def __init__(self, llm_client, model: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """
        Initialize Performance Agent
        
        Args:
            llm_client: LLM integration client
            model: LLM model to use
            temperature: Medium-low temperature for consistent analysis
        """
        super().__init__(
            llm_client=llm_client,
            agent_name="performance",
            model=model,
            temperature=temperature,
            max_tokens=4000  # Max tokens for GPT-3.5-turbo compatibility
        )
        
        # Performance anti-patterns to check
        self.performance_patterns = {
            'nested_loops': [
                r'for\s+\w+\s+in.*:\s*\n.*for\s+\w+\s+in',
                r'while.*:\s*\n.*while',
            ],
            'database_in_loop': [
                r'for\s+\w+\s+in.*:.*\.query\(',
                r'for\s+\w+\s+in.*:.*\.execute\(',
                r'for\s+\w+\s+in.*:.*\.get\(',
            ],
            'inefficient_operations': [
                r'\+\s*=.*\[.*\]',  # String concatenation in loop
                r'\.append\(.*\).*for.*in',  # List append in loop (could be list comp)
            ],
            'missing_caching': [
                r'def\s+\w+\(.*\):.*return.*\(.*\)',  # Function that could be cached
            ]
        }
    
    def _create_system_prompt(self) -> str:
        """Create performance-focused system prompt"""
        return """You are a senior performance engineer specializing in code optimization and efficient algorithm design.

Your expertise includes:
- Algorithmic complexity analysis (Big O notation)
- Memory profiling and optimization
- Database query optimization
- Caching strategies
- Parallel processing opportunities
- Resource management (connections, files, memory)

When reviewing code changes, you must:
1. Identify performance bottlenecks and inefficiencies
2. Analyze algorithmic complexity (current vs optimal)
3. Suggest concrete optimization strategies
4. Estimate performance impact (e.g., "10x faster for n>100")
5. Consider trade-offs between performance and readability

Focus on issues that have measurable impact. Avoid micro-optimizations unless in hot paths.

Respond in the following JSON format:
{
  "findings": [
    {
      "type": "inefficient_algorithm|memory_leak|database_issue|io_bottleneck|caching_opportunity|resource_leak|other",
      "severity": "critical|high|medium|low",
      "confidence": 0.0-1.0,
      "file": "path/to/file.py",
      "line": 42,
      "description": "Clear description of the performance issue",
      "recommendation": "Specific optimization suggestion",
      "current_complexity": "O(n²)" or "Blocking I/O" etc,
      "optimal_complexity": "O(n)" or "Async I/O" etc,
      "estimated_improvement": "10x faster for n>100",
      "code_snippet": "Relevant code excerpt"
    }
  ]
}
"""
    
    def _create_analysis_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Create performance analysis prompt from PR data"""
        
        pr_id = pr_data.get('id', 'unknown')
        pr_title = pr_data.get('title', '')
        files = pr_data.get('files', [])
        
        # Build prompt
        prompt_parts = []
        
        prompt_parts.append(f"""# Performance Review Request

## Pull Request Information
- **PR #{pr_id}:** {pr_title}
- **Repository:** {pr_data.get('repo', 'unknown')}
- **Files Changed:** {len(files)}
- **Total Changes:** +{pr_data.get('additions', 0)} / -{pr_data.get('deletions', 0)} lines

## Your Task
Perform a performance-focused code review. Identify inefficiencies, bottlenecks, and optimization opportunities. Consider algorithmic complexity, memory usage, and resource management.

## Changed Files
""")
        
        # Add each file
        for i, file in enumerate(files[:10], 1):
            filename = file.get('filename', 'unknown')
            patch = file.get('patch', '')
            status = file.get('status', 'modified')
            additions = file.get('additions', 0)
            deletions = file.get('deletions', 0)
            
            prompt_parts.append(f"\n### File {i}: `{filename}` ({status})")
            prompt_parts.append(f"**Changes:** +{additions} / -{deletions} lines")
            
            # Check for performance anti-patterns
            issues = self._check_patterns(patch)
            if issues:
                prompt_parts.append(f"**⚠️ Automatic Detection:** {', '.join(issues)}")
            
            # Add full content if available
            full_context = file.get('full_context', {})
            if full_context and full_context.get('after'):
                content = full_context['after'].get('content', '')
                if content and len(content) < 5000:
                    prompt_parts.append(f"\n**Full File Content:**\n```python\n{content}\n```")
            
            # Add patch
            if patch:
                prompt_parts.append(f"\n**Changes (diff):**\n```diff\n{patch}\n```")
        
        if len(files) > 10:
            prompt_parts.append(f"\n\n*... and {len(files) - 10} more files*")
        
        prompt_parts.append("""

## Focus Areas

1. **Algorithmic Complexity:** Are there nested loops that could be optimized?
2. **Database Queries:** Are there N+1 query problems? Are queries efficient?
3. **Memory Usage:** Are there memory leaks? Unnecessary data copies?
4. **I/O Operations:** Is I/O blocking hot paths? Should it be async?
5. **Data Structures:** Are appropriate data structures used? (dict vs list for lookups)
6. **Caching:** Are there opportunities for memoization or caching?
7. **Resource Management:** Are connections/files properly closed?
8. **Loops:** Can loops be avoided with vectorization or list comprehensions?
9. **String Operations:** Is string concatenation done efficiently?
10. **Redundant Operations:** Are there calculations done multiple times unnecessarily?

## Response Format

Respond with a JSON object containing all performance findings. For each finding, include:
- type (specific performance issue type)
- severity (critical/high/medium/low based on impact)
- confidence (0.0-1.0)
- file and line number
- clear description
- specific optimization recommendation
- current complexity / approach
- optimal complexity / approach
- estimated improvement (e.g., "10x faster", "reduces memory by 50%")
- code snippet

If no performance issues are found, return an empty findings array.
""")
        
        return "\n".join(prompt_parts)
    
    def _check_patterns(self, code: str) -> List[str]:
        """
        Check code for performance anti-patterns
        
        Args:
            code: Code to check
            
        Returns:
            List of detected issues
        """
        detected = []
        
        for pattern_type, patterns in self.performance_patterns.items():
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
            # Extract JSON from response
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
                    severity_str = finding_data.get('severity', 'medium').lower()
                    severity_map = {
                        'critical': Severity.CRITICAL,
                        'high': Severity.HIGH,
                        'medium': Severity.MEDIUM,
                        'low': Severity.LOW,
                        'info': Severity.INFO
                    }
                    severity = severity_map.get(severity_str, Severity.MEDIUM)
                    
                    # Build context with performance-specific fields
                    context = {
                        'agent': 'performance',
                        'current_complexity': finding_data.get('current_complexity', 'unknown'),
                        'optimal_complexity': finding_data.get('optimal_complexity', 'unknown'),
                        'estimated_improvement': finding_data.get('estimated_improvement', 'unknown')
                    }
                    
                    finding = Finding(
                        type=finding_data.get('type', 'performance_issue'),
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
            
            # Detect complexity mentions
            if 'o(n' in line.lower() or 'complexity' in line.lower():
                if 'nested' in line.lower() or 'n²' in line or 'n^2' in line:
                    current_issue['type'] = 'inefficient_algorithm'
                    current_issue['severity'] = Severity.HIGH
                    current_issue['description'] = line
            
            # Detect database issues
            elif 'database' in line.lower() or 'query' in line.lower():
                if 'loop' in line.lower() or 'n+1' in line.lower():
                    current_issue['type'] = 'database_issue'
                    current_issue['severity'] = Severity.HIGH
                    current_issue['description'] = line
            
            # Detect memory issues
            elif 'memory' in line.lower() or 'leak' in line.lower():
                current_issue['type'] = 'memory_leak'
                current_issue['severity'] = Severity.MEDIUM
                current_issue['description'] = line
        
        if current_issue:
            finding = Finding(
                type=current_issue.get('type', 'performance_issue'),
                severity=current_issue.get('severity', Severity.MEDIUM),
                confidence=0.6,
                file=pr_data.get('files', [{}])[0].get('filename', 'unknown'),
                description=current_issue.get('description', 'Performance concern detected'),
                recommendation="Consider optimizing this code for better performance",
                context={'parsed_from_text': True}
            )
            findings.append(finding)
        
        return findings
