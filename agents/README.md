# Multi-Agent PR Analysis System

This directory contains the multi-agent system for collaborative code review of GitHub Pull Requests.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent Orchestrator                   │
│                                                         │
│  ┌────────────────────┬────────────────────┬─────────┐ │
│  │                    │                    │         │ │
│  ▼                    ▼                    ▼         │ │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐    │ │
│  │ Security │   │Performance│   │ Architecture │    │ │
│  │  Agent   │   │  Agent    │   │    Agent     │    │ │
│  └────┬─────┘   └────┬──────┘   └──────┬───────┘    │ │
│       │              │                  │            │ │
│       └──────────────┼──────────────────┘            │ │
│                      ▼                                │ │
│              ┌──────────────┐                         │ │
│              │ Synthesizer  │ (Conflict Resolution)   │ │
│              └──────┬───────┘                         │ │
│                     │                                 │ │
│                     ▼                                 │ │
│            Unified Report (JSON)                      │ │
└───────────────────────────────────────────────────────┘
```

## Components

### 1. Base Agent (`base_agent.py`)

Abstract base class that all specialized agents inherit from.

**Key Classes:**
- `BaseAgent`: Abstract base with common analysis logic
- `Finding`: Represents a single issue found
- `Severity`: Enum for issue severity (Critical, High, Medium, Low, Info)
- `AgentResponse`: Standardized response format

**Key Methods:**
- `analyze(pr_data)`: Main entry point for analysis
- `_create_system_prompt()`: Agent-specific instructions (abstract)
- `_create_analysis_prompt(pr_data)`: Format PR data for analysis (abstract)
- `_parse_llm_response(response)`: Parse LLM output to findings (abstract)

### 2. Security Agent (`security_agent.py`)

Specializes in detecting security vulnerabilities.

**Focus Areas:**
- SQL Injection
- Cross-Site Scripting (XSS)
- Authentication/Authorization flaws
- Hardcoded secrets and credentials
- Insecure dependencies
- Cryptographic issues
- Data exposure risks

**Configuration:**
- Temperature: 0.2 (low for deterministic security checks)
- Max tokens: 6000
- Automatic pattern detection for common vulnerabilities

**Output Example:**
```json
{
  "type": "sql_injection",
  "severity": "high",
  "confidence": 0.92,
  "file": "api/users.py",
  "line": 45,
  "description": "Unsanitized user input in SQL query",
  "recommendation": "Use parameterized queries",
  "context": {
    "attack_scenario": "Attacker could inject SQL to access all user data"
  }
}
```

### 3. Performance Agent (`performance_agent.py`)

Specializes in detecting performance issues and optimization opportunities.

**Focus Areas:**
- Algorithmic complexity (O(n²) → O(n))
- Memory leaks and resource management
- Inefficient loops and redundant operations
- Database query optimization (N+1 queries)
- Synchronous I/O in hot paths
- Missing caching opportunities
- Inefficient data structures

**Configuration:**
- Temperature: 0.3 (medium-low for consistent analysis)
- Max tokens: 6000
- Complexity analysis with Big O notation

**Output Example:**
```json
{
  "type": "inefficient_algorithm",
  "severity": "medium",
  "confidence": 0.88,
  "file": "utils/search.py",
  "line": 23,
  "description": "Nested loop can be optimized",
  "recommendation": "Use dictionary for O(1) lookups",
  "context": {
    "current_complexity": "O(n²)",
    "optimal_complexity": "O(n)",
    "estimated_improvement": "10x faster for n>100"
  }
}
```

### 4. Architecture Agent (`architecture_agent.py`)

Specializes in code quality and maintainability.

**Focus Areas:**
- SOLID principle violations
- Design pattern issues
- Code smells (long methods, god classes, duplicated code)
- Naming conventions
- Separation of concerns
- Test coverage gaps
- Documentation issues

**Configuration:**
- Temperature: 0.5 (medium for balanced suggestions)
- Max tokens: 6000
- Considers project coding standards if available

**Output Example:**
```json
{
  "type": "solid_violation",
  "severity": "low",
  "confidence": 0.75,
  "file": "services/user_service.py",
  "description": "Class handles both business logic and database operations",
  "recommendation": "Split into UserService and UserRepository",
  "context": {
    "principle_violated": "Single Responsibility Principle",
    "maintainability_impact": "high"
  }
}
```

### 5. Synthesizer (`synthesizer.py`)

Combines findings from all agents and resolves conflicts.

**Responsibilities:**
1. **Merge Findings**: Combine results from all agents
2. **Detect Conflicts**: Identify contradicting recommendations
3. **Resolve Conflicts**: Apply priority rules to conflicts
4. **Prioritize Issues**: Rank findings by severity and impact
5. **Generate Report**: Create unified assessment

**Conflict Resolution Strategy:**
```
Priority Order:
1. Security > Performance > Architecture
2. Critical > High > Medium > Low severity
3. High confidence > Low confidence
```

**Output Example:**
```json
{
  "overall_assessment": {
    "risk_level": "high",
    "readiness": "needs_changes",
    "recommendation": "Request changes before merge",
    "confidence": 0.87
  },
  "priority_issues": [
    {
      "priority": 1,
      "severity": "high",
      "agent": "security",
      "description": "SQL injection vulnerability",
      "action": "MUST FIX before merge"
    }
  ],
  "conflicts_resolved": [
    {
      "agents": ["security", "performance"],
      "issue_type": "validation_vs_efficiency",
      "resolution": "Implement efficient validation using pre-compiled patterns",
      "rationale": "Security takes priority, but optimize implementation"
    }
  ]
}
```

### 6. Orchestrator (`orchestrator.py`)

Coordinates execution of all agents and synthesizer.

**Features:**
- **Parallel Execution**: Runs all 3 agents simultaneously (default)
- **Sequential Execution**: Runs agents one-by-one (for debugging)
- **Error Handling**: Gracefully handles agent failures
- **Timing**: Tracks execution time for each component

**Usage:**
```python
from agents import MultiAgentOrchestrator
from crawler.llm_integration import LLMIntegrator

llm_client = LLMIntegrator(model="gpt-3.5-turbo")
orchestrator = MultiAgentOrchestrator(
    llm_client=llm_client,
    model="gpt-3.5-turbo",
    parallel=True
)

report = orchestrator.analyze_pr(pr_data)
```

## Usage Examples

### Basic Usage

```python
from agents import MultiAgentOrchestrator
from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator

# Crawl PR
crawler = PRCrawler()
pr_data = crawler.crawl_pr("owner/repo", pr_number=123)

# Initialize multi-agent system
llm_client = LLMIntegrator(model="gpt-3.5-turbo")
orchestrator = MultiAgentOrchestrator(llm_client, parallel=True)

# Analyze PR
report = orchestrator.analyze_pr(pr_data)

# Access results
print(f"Risk Level: {report.overall_assessment['risk_level']}")
print(f"Total Findings: {len(report.all_findings)}")

for issue in report.priority_issues[:5]:
    print(f"{issue['severity']}: {issue['description']}")
```

### Quick Analysis

```python
from agents import quick_multi_agent_analysis
from crawler.llm_integration import LLMIntegrator

llm_client = LLMIntegrator()
report = quick_multi_agent_analysis(
    llm_client,
    pr_data,
    model="gpt-3.5-turbo",
    parallel=True
)
```

### Individual Agent Usage

```python
from agents import SecurityAgent
from crawler.llm_integration import LLMIntegrator

llm_client = LLMIntegrator()
security_agent = SecurityAgent(llm_client, model="gpt-4")

response = security_agent.analyze(pr_data)

for finding in response.findings:
    if finding.severity == Severity.CRITICAL:
        print(f"Critical: {finding.description}")
```

## Testing

### Run Multi-Agent Test

```bash
python test_multi_agent.py
```

This will:
1. Crawl a test PR
2. Run all 3 agents in parallel
3. Synthesize results
4. Display summary
5. Save full report as JSON

### Expected Output

```
============================================================
TESTING MULTI-AGENT PR ANALYSIS SYSTEM
============================================================

Test Configuration:
  Repository: tiangolo/fastapi
  PR Number: 1
  Model: gpt-3.5-turbo

STEP 1: Crawling PR data
✓ PR crawled successfully

STEP 2: Initializing Multi-Agent System
✓ Orchestrator initialized

STEP 3: Running Multi-Agent Analysis
(analyzing...)

📊 Overall Assessment:
  Risk Level: MEDIUM
  Readiness: needs_review
  Recommendation: Approve with minor comments
  Confidence: 78%
  Total Findings: 12

🤖 Agent Summaries:
  Security: Found 3 issues (1 high, 2 medium)
  Performance: Found 5 issues (2 medium, 3 low)
  Architecture: Found 4 issues (all low)

✅ MULTI-AGENT SYSTEM TEST PASSED
```

## Configuration

### Agent Temperature Settings

Different agents use different temperatures for optimal results:

| Agent | Temperature | Reason |
|-------|-------------|---------|
| **Security** | 0.2 | Low for deterministic security checks |
| **Performance** | 0.3 | Medium-low for consistent analysis |
| **Architecture** | 0.5 | Medium for creative suggestions |

### Model Recommendations

| Model | Cost per PR | Quality | Speed | Recommended For |
|-------|-------------|---------|-------|----------------|
| **GPT-3.5-turbo** | ~$1-2 | Good | Fast | Development, testing |
| **GPT-4** | ~$7-10 | Excellent | Slow | Production, evaluation |
| **GPT-4-turbo** | ~$3-5 | Excellent | Medium | Best balance |
| **Claude 3 Sonnet** | ~$3-5 | Excellent | Fast | Alternative to GPT-4 |

### Performance

| Configuration | Time per PR | Findings Quality |
|---------------|-------------|------------------|
| **Parallel (3 agents)** | 15-30s | High |
| **Sequential (3 agents)** | 45-90s | High |
| **Single agent** | 10-15s | Medium (baseline) |

## Output Format

### SynthesizedReport Structure

```python
{
    "pr_id": 123,
    "pr_title": "Add user authentication",
    "overall_assessment": {
        "risk_level": "high|medium|low|none",
        "readiness": "ready_to_merge|needs_review|needs_changes",
        "recommendation": "Approve|Request changes|etc",
        "confidence": 0.0-1.0,
        "total_findings": int,
        "critical_findings": int,
        "high_findings": int,
        "medium_findings": int,
        "agents_consensus": "full_agreement|majority_agreement|divergent_views"
    },
    "priority_issues": [
        {
            "priority": 1,
            "severity": "critical|high|medium|low",
            "agent": "security|performance|architecture",
            "type": "sql_injection|memory_leak|solid_violation|etc",
            "file": "path/to/file.py",
            "line": 42,
            "description": "Clear description",
            "recommendation": "Specific fix",
            "action": "MUST FIX|Should fix|Consider addressing",
            "confidence": 0.0-1.0
        }
    ],
    "all_findings": [...],  # All findings from all agents
    "conflicts_resolved": [...],  # Conflicts between agents
    "agent_summaries": {
        "security": "Found X issues...",
        "performance": "Found Y issues...",
        "architecture": "Found Z issues..."
    },
    "execution_time": 15.2,  # seconds
    "metadata": {...}
}
```

## Development

### Adding a New Agent

1. Create new file `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement abstract methods:
   - `_create_system_prompt()`
   - `_create_analysis_prompt(pr_data)`
   - `_parse_llm_response(response, pr_data)`
4. Update `orchestrator.py` to include new agent
5. Update `synthesizer.py` conflict resolution logic if needed

### Testing Individual Components

```python
# Test base agent functionality
from agents.base_agent import BaseAgent, Finding, Severity

# Test synthesizer
from agents.synthesizer import Synthesizer

# Test orchestrator
from agents.orchestrator import MultiAgentOrchestrator
```

## Troubleshooting

### Common Issues

**Issue: "Module 'litellm' not found"**
```bash
pip install litellm
```

**Issue: "LLM API rate limit exceeded"**
- Wait 60 seconds and retry
- Use lower rate (sequential instead of parallel)
- Upgrade API plan

**Issue: "Agent response not JSON"**
- Check LLM model supports JSON
- Agent falls back to text parsing automatically
- Lower confidence in text-parsed findings

**Issue: "Analysis too slow"**
- Use parallel execution (default)
- Use faster model (gpt-3.5-turbo)
- Reduce max_tokens setting

## Performance Optimization

### Tips for Faster Analysis

1. **Use Parallel Execution** (default)
2. **Use GPT-3.5-turbo** for development
3. **Limit PR size** (crawler truncates at 100 files)
4. **Cache PR data** to avoid re-crawling
5. **Batch multiple PRs** if analyzing many

### Cost Optimization

1. **Use GPT-3.5-turbo** ($1-2 per PR vs $7-10 for GPT-4)
2. **Reduce max_tokens** if acceptable
3. **Filter small/trivial PRs** before analysis
4. **Cache results** for repeated analysis

## Research Contribution

This multi-agent architecture is the **core contribution** of the thesis:

**Hypothesis:** Multi-agent collaboration with specialized roles produces higher-quality code reviews than single general-purpose agent.

**Expected Results:**
- +15-20% improvement in F1 score
- Reduced false positives through conflict resolution
- Better coverage across different issue types

**Evaluation Metrics:**
- Precision: % of flagged issues that are real
- Recall: % of real issues that are flagged
- F1 Score: Harmonic mean of precision and recall
- Inter-agent agreement: How often agents agree
- Synthesis quality: How well conflicts are resolved

---

**Version:** 1.0.0  
**Last Updated:** May 16, 2026  
**Status:** ✅ Implemented and Ready for Testing
