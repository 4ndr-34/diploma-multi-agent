"""
Security Agent

Specializes in detecting security vulnerabilities in code changes.
Focuses on: SQL injection, XSS, authentication issues, hardcoded secrets, etc.
"""

import logging
import re
import json
from typing import Dict, List, Any

from .base_agent import BaseAgent, Finding, Severity


logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Security-focused code review agent
    
    Specializes in identifying:
    - SQL Injection vulnerabilities
    - Cross-Site Scripting (XSS)
    - Authentication and authorization flaws
    - Hardcoded secrets and credentials
    - Insecure dependencies
    - Cryptographic issues
    - Data exposure risks
    """
    
    def __init__(self, llm_client, model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        """
        Initialize Security Agent
        
        Args:
            llm_client: LLM integration client
            model: LLM model to use
            temperature: Low temperature for consistent security analysis
        """
        super().__init__(
            llm_client=llm_client,
            agent_name="security",
            model=model,
            temperature=temperature,  # Low temp for deterministic security checks
            max_tokens=4000  # Max tokens for GPT-3.5-turbo compatibility
        )
        
        # Security patterns to check
        self.dangerous_patterns = {
            'sql_injection': [
                r'execute\s*\(',
                r'raw\s*\(',
                r'\.query\s*\(',
                r'SELECT.*FROM.*WHERE.*\+',
                r'INSERT.*INTO.*VALUES.*\+',
            ],
            'hardcoded_secrets': [
                r'(api[_-]?key|password|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
                r'(AWS|AZURE|GITHUB)_[A-Z_]+\s*=\s*["\']',
            ],
            'xss': [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'\.html\s*\(',
            ],
            'eval_usage': [
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__\s*\(',
            ]
        }
    
    def _create_system_prompt(self) -> str:
        """Create security-focused system prompt"""
        return """You are a senior security engineer specializing in application security and vulnerability assessment.

Your expertise includes:
- OWASP Top 10 vulnerabilities
- Secure coding practices
- Authentication and authorization
- Cryptography and data protection
- Input validation and sanitization
- Secure API design

When reviewing code changes, you must:
1. Identify security vulnerabilities with high confidence
2. Explain the potential impact and attack vectors
3. Provide specific, actionable remediation steps
4. Rate severity based on CVSS methodology (Critical, High, Medium, Low)
5. Consider the broader security context of the application

Be thorough but avoid false positives. Only flag genuine security concerns.

Respond in the following JSON format:
{
  "findings": [
    {
      "type": "sql_injection|xss|auth_bypass|hardcoded_secret|insecure_dependency|crypto_issue|data_exposure|other",
      "severity": "critical|high|medium|low",
      "confidence": 0.0-1.0,
      "file": "path/to/file.py",
      "line": 42,
      "description": "Clear description of the vulnerability",
      "recommendation": "Specific fix recommendation",
      "code_snippet": "Relevant code excerpt",
      "attack_scenario": "How an attacker could exploit this"
    }
  ]
}
"""
    
    def _create_analysis_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Create security analysis prompt from PR data"""
        
        pr_id = pr_data.get('id', 'unknown')
        pr_title = pr_data.get('title', '')
        files = pr_data.get('files', [])
        
        # Build prompt
        prompt_parts = []
        
        prompt_parts.append(f"""# Security Review Request

## Pull Request Information
- **PR #{pr_id}:** {pr_title}
- **Repository:** {pr_data.get('repo', 'unknown')}
- **Files Changed:** {len(files)}

## Your Task
Perform a security-focused code review of the following changes. Identify any security vulnerabilities, insecure practices, or potential attack vectors.

## Changed Files
""")
        
        # Add each file
        for i, file in enumerate(files[:10], 1):  # Limit to 10 files
            filename = file.get('filename', 'unknown')
            patch = file.get('patch', '')
            status = file.get('status', 'modified')
            
            prompt_parts.append(f"\n### File {i}: `{filename}` ({status})")
            
            # Check for suspicious patterns
            suspicious = self._check_patterns(patch)
            if suspicious:
                prompt_parts.append(f"\n**⚠️ Automatic Detection:** {', '.join(suspicious)}")
            
            # Add full content if available
            full_context = file.get('full_context', {})
            if full_context and full_context.get('after'):
                content = full_context['after'].get('content', '')
                if content and len(content) < 5000:  # Include full file if reasonable size
                    prompt_parts.append(f"\n**Full File Content:**\n```python\n{content}\n```")
            
            # Add patch
            if patch:
                prompt_parts.append(f"\n**Changes (diff):**\n```diff\n{patch}\n```")
        
        if len(files) > 10:
            prompt_parts.append(f"\n\n*... and {len(files) - 10} more files (focusing on first 10 for detailed analysis)*")
        
        prompt_parts.append("""

## Focus Areas

1. **Input Validation:** Are user inputs properly validated and sanitized?
2. **SQL Injection:** Are database queries parameterized?
3. **XSS:** Is output properly escaped?
4. **Authentication:** Are authentication mechanisms secure?
5. **Authorization:** Are access controls properly implemented?
6. **Secrets:** Are there any hardcoded credentials or API keys?
7. **Dependencies:** Are new dependencies from trusted sources?
8. **Cryptography:** Is encryption properly implemented?
9. **Data Exposure:** Could sensitive data be leaked?
10. **Error Handling:** Do error messages expose sensitive information?

## Response Format

Respond with a JSON object containing all security findings. For each finding, include:
- type (specific vulnerability type)
- severity (critical/high/medium/low)
- confidence (0.0-1.0, your confidence in this finding)
- file and line number
- clear description
- actionable recommendation
- code snippet showing the issue
- attack scenario (how it could be exploited)

If no security issues are found, return an empty findings array.
""")
        
        return "\n".join(prompt_parts)
    
    def _check_patterns(self, code: str) -> List[str]:
        """
        Check code for suspicious patterns
        
        Args:
            code: Code to check
            
        Returns:
            List of detected patterns
        """
        detected = []
        
        for pattern_type, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    detected.append(pattern_type)
                    break  # Only add each type once
        
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
            # Try to parse as JSON
            # First, try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Try to find JSON object
            json_match = re.search(r'\{.*"findings".*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            
            # Extract findings
            for finding_data in data.get('findings', []):
                try:
                    # Map severity string to Severity enum
                    severity_str = finding_data.get('severity', 'medium').lower()
                    severity_map = {
                        'critical': Severity.CRITICAL,
                        'high': Severity.HIGH,
                        'medium': Severity.MEDIUM,
                        'low': Severity.LOW,
                        'info': Severity.INFO
                    }
                    severity = severity_map.get(severity_str, Severity.MEDIUM)
                    
                    finding = Finding(
                        type=finding_data.get('type', 'security_issue'),
                        severity=severity,
                        confidence=float(finding_data.get('confidence', 0.7)),
                        file=finding_data.get('file', 'unknown'),
                        line=finding_data.get('line'),
                        description=finding_data.get('description', ''),
                        recommendation=finding_data.get('recommendation', ''),
                        code_snippet=finding_data.get('code_snippet'),
                        context={
                            'attack_scenario': finding_data.get('attack_scenario', ''),
                            'agent': 'security'
                        }
                    )
                    
                    findings.append(finding)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse individual finding: {e}")
                    continue
        
        except json.JSONDecodeError:
            logger.warning("LLM response is not valid JSON, attempting text parsing")
            
            # Fallback: Try to parse text response
            findings = self._parse_text_response(response, pr_data)
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        
        return findings
    
    def _parse_text_response(self, response: str, pr_data: Dict[str, Any]) -> List[Finding]:
        """
        Fallback parser for non-JSON responses
        
        Args:
            response: Text response
            pr_data: PR data for context
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        # Look for severity indicators
        lines = response.split('\n')
        
        current_issue = {}
        for line in lines:
            line = line.strip()
            
            # Detect severity mentions
            if any(word in line.lower() for word in ['critical', 'severe', 'dangerous']):
                if 'sql' in line.lower() or 'injection' in line.lower():
                    current_issue['type'] = 'sql_injection'
                    current_issue['severity'] = Severity.CRITICAL
                elif 'xss' in line.lower() or 'script' in line.lower():
                    current_issue['type'] = 'xss'
                    current_issue['severity'] = Severity.HIGH
                elif 'secret' in line.lower() or 'password' in line.lower() or 'key' in line.lower():
                    current_issue['type'] = 'hardcoded_secret'
                    current_issue['severity'] = Severity.HIGH
                
                current_issue['description'] = line
        
        # Create finding from accumulated data
        if current_issue:
            finding = Finding(
                type=current_issue.get('type', 'security_issue'),
                severity=current_issue.get('severity', Severity.MEDIUM),
                confidence=0.6,  # Lower confidence for text parsing
                file=pr_data.get('files', [{}])[0].get('filename', 'unknown'),
                description=current_issue.get('description', 'Security concern detected'),
                recommendation="Please review this code for security issues",
                context={'parsed_from_text': True}
            )
            findings.append(finding)
        
        return findings
