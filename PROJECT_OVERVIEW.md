# Multi-Agent PR Analyzer

**A specialized multi-agent system for automated code review of GitHub Pull Requests**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)](https://github.com/4ndr-34/diploma-multi-agent)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Status](#project-status)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Multi-Agent System](#multi-agent-system)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Installation & Usage](#installation--usage)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Documentation](#documentation)

---

## 🎯 Overview

A Python-based research project that uses **multiple specialized AI agents** to analyze GitHub pull requests. Unlike traditional single-agent code review tools, this system employs three specialized agents (Security, Performance, Architecture) that collaborate through a synthesizer to provide comprehensive, conflict-resolved code reviews.

### Research Contribution

The **core novelty** of this thesis is demonstrating that multi-agent collaboration with specialized roles produces higher-quality code reviews than a single general-purpose agent.

### Key Innovation

- **Specialization:** Each agent focuses on a specific aspect (security, performance, architecture)
- **Collaboration:** Agents work independently then combine findings
- **Conflict Resolution:** Synthesizer resolves contradicting recommendations
- **Context-Aware:** Provides full file context, not just diffs

---

## 📊 Project Status

**Current Completion: ~85%**

| Component | Status | Priority |
|-----------|--------|----------|
| **PR Crawler** | ✅ Complete | - |
| **LLM Formatter** | ✅ Complete | - |
| **LLM Integration** | ✅ Complete | - |
| **Logging System** | ✅ Complete | - |
| **Multi-Agent System** | ✅ Complete | - |
| **Evaluation Framework** | ✅ Complete | - |
| **GitHub Actions Integration** | ✅ Complete | - |
| **Test Suite** | ⚠️ Basic only | Medium |
| **Web Interface** | ❌ Not implemented | Low |
| **Documentation** | ⚠️ In progress | High |

**Current Phase:** Data collection and analysis (ready for thesis evaluation)

---

## 🏗️ Architecture

### Current Architecture (Single-Agent)

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub API                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  PR Crawler │  (Fetches PR data)
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Formatter  │  (Structures for LLM)
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Generic LLM │  (Single agent)
                  └──────┬──────┘
                         │
                         ▼
                    Raw Text Output
```

### Target Architecture (Multi-Agent) - TO BE IMPLEMENTED

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub API                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  PR Crawler │  (Enhanced with full context)
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Formatter  │  (Context-aware prompts)
                  └──────┬──────┘
                         │
                         ▼
            ┌────────────┴────────────┐
            │   Multi-Agent           │
            │   Orchestrator          │
            └────────────┬────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Security │   │Performance│   │Architecture│
   │  Agent   │   │  Agent    │   │  Agent    │
   └────┬─────┘   └────┬──────┘   └────┬─────┘
        │              │               │
        └──────────────┼───────────────┘
                       │
                       ▼
                ┌─────────────┐
                │ Synthesizer │  (Resolves conflicts)
                └──────┬──────┘
                       │
                       ▼
              Structured JSON Output
              (Findings, Severity, Confidence)
```

---

## 🔧 Core Components

### 1. PR Crawler (`crawler/crawler.py`)

**Purpose:** Fetch PR data from GitHub with robust error handling

**Features:**
- GitHub API integration via PyGithub
- Automatic rate limiting with exponential backoff
- Batch processing with configurable concurrency (ThreadPoolExecutor)
- Size-based truncation for large PRs:
  - Max 100 files per PR (configurable)
  - Max 50,000 characters per patch (configurable)
- Comprehensive error handling (404, 403, rate limits)

**Key Methods:**
```python
crawl_pr(repo_full_name, pr_number)         # Fetch single PR
crawl_prs_batch(repo, pr_numbers)           # Fetch multiple PRs
get_recent_prs(repo, limit, state)          # Get recent PRs
```

**Output:** Dictionary with PR metadata, file changes, diffs, and statistics

---

### 2. LLM Formatter (`crawler/llm_formatter.py`)

**Purpose:** Convert PR data into structured prompts for LLM analysis

**Features:**
- Multiple output formats:
  - Summary (quick overview)
  - Full analysis with diffs
  - Metadata only
- Markdown-formatted prompts with:
  - File change summary tables
  - Code diffs with syntax highlighting
  - Analysis request templates
- Smart truncation for token limits
- Configurable detail levels

**Key Methods:**
```python
format_for_llm(pr_payload, include_full_diff)  # Main formatter
format_summary_for_llm(pr_payload)             # Quick summary
```

---

### 3. LLM Integration (`crawler/llm_integration.py`)

**Purpose:** Unified interface for multiple LLM providers

**Features:**
- Multi-provider support via LiteLLM:
  - OpenAI (GPT-3.5, GPT-4, GPT-4-turbo)
  - Anthropic (Claude 3 Opus, Sonnet, Haiku)
  - Other providers (Cohere, AI21, etc.)
- Automatic retry logic for rate limits
- Configurable model and token limits
- Temperature control
- Batch processing support

**Key Methods:**
```python
analyze_pr(pr_payload, formatter)              # Analyze single PR
analyze_pr_batch(pr_data_list, formatter)      # Batch analysis
get_pr_with_analysis(crawler, repo, pr_number) # Complete pipeline
```

---

### 4. Main Entry Point (`main.py`)

**Purpose:** CLI interface for PR analysis

**Features:**
- Command-line argument parsing
- Single PR analysis
- Batch PR analysis
- Recent PRs analysis
- JSON output saving
- Comprehensive logging
- Error handling with graceful degradation

**Usage Examples:**
```bash
# Analyze single PR
python main.py tiangolo/fastapi --pr 123

# Analyze multiple PRs
python main.py tiangolo/fastapi --prs 123 124 125 --save

# Analyze recent PRs
python main.py tiangolo/fastapi --recent 5 --model gpt-4
```

---

## 🤖 Multi-Agent System

### Planned Architecture (TO BE IMPLEMENTED)

The system will use **four specialized agents** working collaboratively:

### Agent 1: Security Auditor

**Specialization:** Security vulnerabilities and best practices

**Focus Areas:**
- SQL Injection vulnerabilities
- Cross-Site Scripting (XSS)
- Authentication & Authorization flaws
- Hardcoded secrets and credentials
- Insecure dependencies
- Data exposure risks
- Cryptographic issues

**Output:**
```json
{
  "agent": "security",
  "findings": [
    {
      "type": "sql_injection",
      "severity": "high",
      "confidence": 0.92,
      "file": "api/users.py",
      "line": 45,
      "description": "Unsanitized user input in SQL query",
      "recommendation": "Use parameterized queries or ORM",
      "code_snippet": "..."
    }
  ],
  "summary": "Found 3 security issues (2 high, 1 medium)",
  "risk_level": "high"
}
```

---

### Agent 2: Performance Engineer

**Specialization:** Performance bottlenecks and optimization

**Focus Areas:**
- Algorithmic complexity (O(n²) → O(n))
- Memory leaks and resource management
- Inefficient loops and redundant operations
- Database query optimization (N+1 queries)
- Synchronous I/O in hot paths
- Caching opportunities
- Unnecessary data copies

**Output:**
```json
{
  "agent": "performance",
  "findings": [
    {
      "type": "inefficient_algorithm",
      "severity": "medium",
      "confidence": 0.88,
      "file": "utils/search.py",
      "line": 23,
      "current_complexity": "O(n²)",
      "optimal_complexity": "O(n)",
      "description": "Nested loop can be optimized with hash map",
      "recommendation": "Use dictionary for O(1) lookups",
      "estimated_improvement": "10x faster for n>100"
    }
  ],
  "summary": "Found 2 performance issues",
  "impact": "medium"
}
```

---

### Agent 3: Code Architect

**Specialization:** Code quality and maintainability

**Focus Areas:**
- SOLID principles violations
- Design patterns (appropriate usage)
- Code smells (long methods, god classes)
- Naming conventions
- Code duplication (DRY violations)
- Separation of concerns
- Test coverage and quality
- Documentation completeness

**Output:**
```json
{
  "agent": "architecture",
  "findings": [
    {
      "type": "single_responsibility_violation",
      "severity": "low",
      "confidence": 0.75,
      "file": "services/user_service.py",
      "class": "UserService",
      "description": "Class handles both business logic and database operations",
      "recommendation": "Split into UserService and UserRepository",
      "maintainability_impact": "high"
    }
  ],
  "summary": "Found 4 architectural issues",
  "code_quality_score": 7.5
}
```

---

### Agent 4: Synthesizer

**Specialization:** Conflict resolution and report generation

**Responsibilities:**
1. **Combine Findings:** Merge results from all three agents
2. **Resolve Conflicts:** Handle contradicting recommendations
   - Example: Security wants more validation checks, Performance wants fewer operations
   - Resolution: Prioritize security, suggest efficient validation methods
3. **Prioritize Issues:** Rank findings by severity and impact
4. **Generate Report:** Create unified, actionable report

**Conflict Resolution Strategy:**
- **Security > Performance** (security issues take priority)
- **Critical > Low severity** (urgent issues first)
- **High confidence > Low confidence** (trust reliable findings)
- **Provide context** for trade-offs in final report

**Output:**
```json
{
  "pr_id": 123,
  "overall_assessment": {
    "risk_level": "high",
    "readiness": "needs_changes",
    "confidence": 0.87,
    "recommendation": "Request changes before merge"
  },
  "priority_issues": [
    {
      "priority": 1,
      "severity": "high",
      "agent": "security",
      "issue": "SQL injection in user authentication",
      "action": "MUST FIX before merge"
    },
    {
      "priority": 2,
      "severity": "medium",
      "agent": "performance",
      "issue": "Inefficient database query pattern",
      "action": "Should fix, impacts user experience"
    }
  ],
  "conflicts_resolved": [
    {
      "conflict": "Security recommends additional input validation (slower), Performance recommends fewer checks (faster)",
      "resolution": "Implement efficient validation using compiled regex",
      "rationale": "Security takes priority, but optimized implementation minimizes performance impact"
    }
  ],
  "agent_summaries": {
    "security": "3 issues found (2 high, 1 medium)",
    "performance": "2 issues found (both medium)",
    "architecture": "4 issues found (all low severity)"
  }
}
```

---

## 🔄 Data Flow

### Complete Analysis Pipeline

```
1. User Request
   └─> python main.py owner/repo --pr 123

2. PR Crawler
   ├─> Fetch PR metadata from GitHub API
   ├─> Download file changes and diffs
   ├─> Apply size limits and truncation
   └─> Output: PR data dictionary

3. Context Enhancement (PLANNED)
   ├─> Fetch full file contents (before/after)
   ├─> Extract dependencies and imports
   ├─> Find related files
   ├─> Get project documentation
   └─> Output: Enriched PR data

4. Formatter
   ├─> Convert to LLM-friendly prompts
   ├─> Add file summaries and diffs
   ├─> Include analysis instructions
   └─> Output: Structured prompts (one per agent)

5. Multi-Agent Analysis (PLANNED)
   ├─> Security Agent → Security findings
   ├─> Performance Agent → Performance findings
   ├─> Architecture Agent → Architecture findings
   └─> Run in parallel

6. Synthesizer (PLANNED)
   ├─> Combine all findings
   ├─> Resolve conflicts
   ├─> Prioritize issues
   └─> Output: Unified JSON report

7. Output
   ├─> Display in console
   ├─> Save to JSON file (optional)
   └─> Generate HTML report (FUTURE)
```

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.10+ | Main implementation |
| **GitHub API** | PyGithub | 2.1.0+ | PR data fetching |
| **LLM Integration** | LiteLLM | 1.0.0+ | Multi-provider LLM access |
| **Environment** | python-dotenv | 1.0.0+ | Configuration management |
| **Logging** | logging (built-in) | - | Structured logging |

### LLM Providers (via LiteLLM)

- **OpenAI:** GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Anthropic:** Claude 3 Opus, Claude 3 Sonnet
- **Others:** Cohere, AI21, local models

### Development Tools

- **Testing:** pytest, pytest-cov
- **Type Checking:** mypy
- **Linting:** flake8, black
- **Code Quality:** isort

---

## 📦 Installation & Usage

### Prerequisites

- Python 3.10 or higher
- GitHub Personal Access Token
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone repository
git clone https://github.com/4ndr-34/diploma-multi-agent.git
cd diploma-multi-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   GITHUB_PAT=your_github_token
#   OPENAI_API_KEY=your_openai_key
```

### Usage Examples

```bash
# Quick test to verify setup
python test_quick.py

# Analyze a single PR
python main.py tiangolo/fastapi --pr 1 --model gpt-3.5-turbo

# Analyze multiple specific PRs
python main.py facebook/react --prs 100 101 102 --save

# Analyze 5 most recent PRs
python main.py microsoft/vscode --recent 5 --model gpt-4

# Save results to file
python main.py django/django --pr 15234 --save

# Demo: See what data is crawled
python demo_crawler_output.py
```

### Configuration

Edit `.env` file:

```bash
# GitHub API (Required)
GITHUB_PAT=ghp_your_token_here

# LLM Provider (Required - choose one or more)
OPENAI_API_KEY=sk-your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Optional: Model preferences
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=4000
TEMPERATURE=0.7
```

---

## 📁 Project Structure

```
diploma-multi-agent/
├── crawler/
│   ├── __init__.py              # Package initialization
│   ├── crawler.py               # PR fetching logic
│   ├── llm_formatter.py         # Prompt formatting
│   └── llm_integration.py       # LLM API interface
│
├── agents/                      # ✅ IMPLEMENTED
│   ├── __init__.py
│   ├── base_agent.py            # Base class for agents
│   ├── security_agent.py        # Security analysis
│   ├── performance_agent.py     # Performance analysis
│   ├── architecture_agent.py    # Code quality analysis
│   ├── single_agent.py          # Baseline single agent
│   ├── orchestrator.py          # Multi-agent orchestrator
│   └── synthesizer.py           # Conflict resolution
│
├── .github/                     # ✅ IMPLEMENTED
│   ├── workflows/
│   │   └── pr-review.yml        # GitHub Actions workflow (demo repo)
│   └── scripts/
│       └── run_review.py        # Evaluation runner script
│
├── evaluation/                  # ⚠️ PARTIAL
│   ├── generate_test_prs.py     # ✅ Test PR generator
│   └── analysis/                # 🔄 Statistical analysis (in progress)
│
├── tests/                       # ⚠️ BASIC ONLY
│   ├── test_crawler.py
│   ├── test_formatter.py
│   └── test_agents.py
│
├── docs/                        # Documentation
│   ├── LIMITATIONS_AND_IMPROVEMENTS.md
│   ├── LIMITATIONS_SUMMARY.md
│   └── CONTEXT_ENHANCEMENT_STRATEGIES.md
│
├── main.py                      # CLI entry point
├── test_quick.py                # Quick integration test
├── demo_crawler_output.py       # Demo script
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── PROJECT_OVERVIEW.md          # This file
```

---

## ✨ Key Features

### Currently Implemented ✅

1. **Robust PR Crawling**
   - Handles rate limits automatically
   - Batch processing with concurrency
   - Smart truncation for large PRs
   - Comprehensive error handling

2. **Flexible LLM Integration**
   - Multiple provider support (OpenAI, Anthropic, etc.)
   - Configurable models and parameters
   - Retry logic with exponential backoff

3. **Structured Prompts**
   - Markdown-formatted with syntax highlighting
   - File change summaries
   - Contextual analysis requests

4. **CLI Interface**
   - Easy-to-use commands
   - Multiple analysis modes
   - JSON output support

5. **Logging System**
   - Structured logging with timestamps
   - Different log levels (INFO, WARNING, ERROR)
   - Stack traces for debugging

### Recently Completed Features ✅

1. **Multi-Agent Collaboration**
   - 3 specialized agents (Security, Performance, Architecture) + synthesizer
   - Parallel execution support
   - Conflict resolution and consensus building
   - Structured JSON output with confidence scores

2. **Evaluation Framework**
   - Automated comparison (multi-agent vs single-agent)
   - GitHub Actions integration for continuous evaluation
   - Comprehensive metrics tracking
   - Test PR generation for diverse scenarios
   - Data collection and export for analysis

3. **GitHub Actions Integration**
   - Automated PR review workflow
   - Real-time review comments on PRs
   - Pass/fail status checks based on quality score
   - Configurable model selection

### Planned Features 🔄

1. **Context Enhancement**
   - Full file contents (not just diffs)
   - Dependency analysis
   - Project documentation integration
   - Related files discovery

2. **Statistical Analysis**
   - T-tests and p-values for significance testing
   - Precision, recall, F1 metrics
   - Results visualization (charts and tables)

3. **Web Interface** (Future)
   - Real-time analysis dashboard
   - Interactive results viewer
   - Historical comparison tools

---

## ⚠️ Current Limitations

### Technical Limitations

1. **Limited Context**
   - Only sees diffs, not full files
   - No project documentation awareness
   - Missing dependency information

2. **Statistical Analysis**
   - Data collection operational, but statistical validation in progress
   - Need larger sample size for robust conclusions
   - T-tests and significance testing not yet automated

3. **Performance Optimization**
   - API rate limits can affect batch processing
   - Token usage optimization could be improved
   - Caching not implemented for repeated analyses

### Scope Limitations

- **Language Support:** Python PRs only (currently)
- **Platform:** GitHub only (no GitLab, Bitbucket)
- **Visibility:** Public repositories only
- **File Types:** Text files only (no binary analysis)

For detailed limitations and improvement roadmap, see:
- `LIMITATIONS_AND_IMPROVEMENTS.md` (comprehensive)
- `LIMITATIONS_SUMMARY.md` (quick reference)

---

## 📊 Evaluation System

### Implementation Overview

The evaluation framework has been fully implemented to quantitatively validate the multi-agent approach. The system allows for systematic comparison between single-agent and multi-agent code review.

### Key Components

#### 1. GitHub Actions Integration (`.github/workflows/pr-review.yml`)

**Purpose:** Automated PR review in a separate demo repository

**Features:**
- Triggers automatically on PR open/update
- Runs multi-agent analysis on PR code
- Posts review results as PR comments
- Sets pass/fail status based on quality thresholds
- Supports comparison mode (optional single-agent baseline)

**Typical Runtime:** 40-60 seconds per PR

#### 2. Review Runner Script (`.github/scripts/run_review.py`)

**Purpose:** Orchestrates evaluation and comparison

**Key Features:**
```python
# Run multi-agent only
python run_review.py --repo owner/repo --pr 123 --output results.json

# Run with baseline comparison
python run_review.py --repo owner/repo --pr 123 --compare --output results.json
```

**Output Format:**
```json
{
  "pr_number": 123,
  "quality_score": 82,
  "quality_grade": "B",
  "risk_level": "MEDIUM",
  "total_findings": 12,
  "critical_findings": 1,
  "execution_time": 45.3,
  "comparison": {
    "single_agent": {...},
    "multi_agent": {...},
    "advantage": {
      "more_findings": 4,
      "quality_difference": 8
    }
  }
}
```

#### 3. Test PR Generator (`generate_test_prs.py`)

**Purpose:** Create diverse test scenarios for evaluation

**Test Categories (20 PRs total):**
- **Security Fixes (4 PRs):** SQL injection, XSS, password hashing, input validation
- **Performance Improvements (4 PRs):** Database optimization, caching, connection pooling, batch operations
- **Architecture Refactoring (4 PRs):** Design patterns, service layers, dependency injection, code duplication
- **Bug Fixes/Regressions (4 PRs):** Null handling, error handling, subtle bugs
- **Clean Code/Positive (4 PRs):** Documentation, tests, logging, monitoring

**Usage:**
```bash
python generate_test_prs.py
# Creates 20 branches in demo-pr-review repository
# Each branch contains specific code changes for testing
```

#### 4. Demo Repository

**Repository:** `demo-pr-review` (separate from main project)

**Purpose:** Isolated testing environment with intentional issues

**Contains:**
- Baseline codebase with known security vulnerabilities
- Performance bottlenecks (N+1 queries, O(n²) algorithms)
- Architecture smells (god classes, SOLID violations)
- GitHub Actions workflow for automated review

### Evaluation Metrics

The system tracks multiple metrics for comparison:

| Metric | Description | Purpose |
|--------|-------------|---------|
| **Quality Score** | 0-100% overall code quality | Primary comparison metric |
| **Findings Count** | Total issues detected | Coverage measurement |
| **Severity Breakdown** | Critical/High/Medium counts | Risk assessment |
| **Confidence** | Agent confidence in findings | Reliability indicator |
| **Execution Time** | Analysis duration | Performance overhead |
| **Agent Consensus** | Agreement between agents | Consistency measure |

### Comparison Methodology

**Baseline:** Single general-purpose agent
**Test:** Multi-agent system (3 specialized agents + synthesizer)
**Variables Controlled:**
- Same PR data input
- Same LLM model (configurable)
- Same context and prompts structure
- Same timeout and token limits

**Expected Advantages:**
- **Specialization:** Deeper analysis in specific domains
- **Coverage:** More comprehensive issue detection
- **False Positives:** Better filtering through consensus
- **Actionability:** More specific recommendations

### Data Collection Process

1. **Generate Test PRs** → Create 20 diverse test scenarios
2. **Automated Review** → GitHub Actions runs on each PR
3. **Comparison Mode** → Both single and multi-agent analyze same PR
4. **Data Export** → Results saved as JSON for analysis
5. **Statistical Analysis** → Calculate metrics, significance testing

### Current Status

✅ **Operational:**
- Automated review pipeline
- Comparison mode
- Metrics collection
- Test PR generation

🔄 **In Progress:**
- Statistical significance testing (t-tests, p-values)
- Results visualization (charts, tables)
- Large-scale evaluation (100+ PRs)

---

## 🗓️ Roadmap

### Phase 1: Multi-Agent Implementation (Week 1) ✅
**Priority: CRITICAL** - **STATUS: COMPLETE**

- [x] Design agent base class interface
- [x] Implement SecurityAgent with specialized prompts
- [x] Implement PerformanceAgent with specialized prompts
- [x] Implement ArchitectureAgent with specialized prompts
- [x] Implement Synthesizer for conflict resolution
- [x] Implement SingleAgent for baseline comparison
- [x] Create MultiAgentOrchestrator for coordination
- [x] Add parallel agent execution
- [x] Implement structured JSON output with Pydantic-like models

**Deliverable:** ✅ Working multi-agent system operational

---

### Phase 2: Context Enhancement (Week 2)
**Priority: HIGH**

- [ ] Fetch full file contents (before/after changes)
- [ ] Extract dependencies and imports
- [ ] Integrate project documentation (README, CONTRIBUTING)
- [ ] Analyze coding standards (.pylintrc, .flake8)
- [ ] Find related files
- [ ] Add file history and related PRs

**Deliverable:** Context-aware agents

---

### Phase 3: Evaluation Framework (Week 3) ✅
**Priority: CRITICAL** - **STATUS: COMPLETE**

- [x] Collect evaluation dataset (automated test PR generation)
- [x] Create baseline (single-agent) comparison
- [x] Implement comparison mode in run_review.py
- [x] Build GitHub Actions workflow for automated testing
- [x] Add metrics tracking (quality score, findings, execution time)
- [x] Create comprehensive testing setup guide
- [ ] Statistical analysis (t-test, p-values) - IN PROGRESS
- [ ] Generate final results tables and figures - IN PROGRESS

**Deliverable:** ✅ Quantitative validation framework operational

**Implemented Features:**
- **Automated PR Review System:** GitHub Actions workflow that automatically reviews PRs
- **Comparison Mode:** Side-by-side evaluation of single-agent vs multi-agent
- **Test PR Generator:** Script to create 20 diverse test PRs across 5 categories
- **Metrics Collection:** Quality scores, findings breakdown, execution time, confidence levels
- **Data Export:** JSON output for statistical analysis
- **Demo Repository:** Separate test repository (demo-pr-review) with intentional issues

---

### Phase 4: Documentation & Polish (Week 4)
**Priority: HIGH**

- [ ] Write comprehensive README.md
- [ ] Create ARCHITECTURE.md
- [ ] Add code examples and tutorials
- [ ] Write thesis chapter on implementation
- [ ] Create presentation slides for defense
- [ ] Record demo video
- [ ] Clean up code and fix linting issues

**Deliverable:** Thesis-ready project

---

### Future Enhancements (Post-Thesis)

- [ ] Web interface with FastAPI
- [ ] Database for historical analysis
- [ ] Webhook integration for automatic analysis
- [ ] Support for more languages (JavaScript, Java, Go)
- [ ] Support for more platforms (GitLab, Bitbucket)
- [ ] Cost optimization and caching
- [ ] Human-in-the-loop feedback
- [ ] Agent learning from feedback

---

## 📚 Documentation

### Primary Documents

| Document | Purpose | Size |
|----------|---------|------|
| **PROJECT_OVERVIEW.md** | This file - project introduction | Brief |
| **LIMITATIONS_SUMMARY.md** | Quick reference for issues and roadmap | 350 lines |
| **LIMITATIONS_AND_IMPROVEMENTS.md** | Comprehensive technical analysis | 1,715 lines |
| **CONTEXT_ENHANCEMENT_STRATEGIES.md** | Guide for improving agent context | 1,745 lines |

### Code Documentation

- All modules have comprehensive docstrings
- Type hints for better IDE support
- Inline comments for complex logic
- Examples in function docstrings

### Getting Help

- **Issues:** Check existing documentation first
- **Questions:** Open GitHub issue
- **Contributing:** See CONTRIBUTING.md (to be created)

---

## 🎓 Academic Context

### Thesis Information

- **Title:** Multi-Agent Collaborative System for Automated Code Review
- **Focus:** Demonstrating specialized agent collaboration > single agent
- **Expected Contribution:** Novel multi-agent architecture for code review
- **Metrics:** Precision, Recall, F1 Score, Inter-agent agreement

### Research Questions

1. Does multi-agent review provide better results than single-agent?
2. How do specialized agents contribute differently to code review?
3. What types of conflicts arise between agents and how can they be resolved?
4. What is the cost-accuracy trade-off of multi-agent systems?

### Expected Results

- **Hypothesis:** Multi-agent system achieves 15-20% higher F1 score
- **Secondary:** Reduced false positives through conflict resolution
- **Tertiary:** Different agents excel at different issue types

---

## 🤝 Contributing

This is a thesis project, but contributions and feedback are welcome!

**How to contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

**Areas needing help:**
- Multi-agent implementation
- Evaluation dataset creation
- Documentation improvements
- Bug fixes and optimizations

---

## 📄 License

MIT License - see LICENSE file for details

---

## 📧 Contact

- **Author:** André (4ndr-34)
- **Email:** andrearanxha@gmail.com
- **GitHub:** [@4ndr-34](https://github.com/4ndr-34)
- **Repository:** [diploma-multi-agent](https://github.com/4ndr-34/diploma-multi-agent)

---

## 🙏 Acknowledgments

- **PyGithub** - Python library for GitHub API
- **LiteLLM** - Unified LLM interface
- **OpenAI & Anthropic** - LLM providers
- **FastAPI** - Web framework (planned)
- **Open Source Community** - Inspiration and tools

---

**Last Updated:** June 19, 2026  
**Version:** 3.0  
**Status:** Evaluation Phase (85% complete)
