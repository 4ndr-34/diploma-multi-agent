# Multi-Agent PR Analyzer

**A specialized multi-agent system for automated code review of GitHub Pull Requests**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)](https://github.com/4ndr-34/diploma-multi-agent)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Development Status](#development-status)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

A Python-based research project (MSc thesis) that uses **multiple specialized AI agents** to analyze GitHub pull requests. Unlike traditional single-agent code review tools, this system employs three specialized agents (Security, Performance, Architecture) that collaborate through a synthesizer to provide comprehensive, conflict-resolved code reviews.

### Research Contribution

The **core novelty** of this thesis is demonstrating that multi-agent collaboration with specialized roles produces higher-quality code reviews than a single general-purpose agent.

### Key Innovation

- **Specialization:** Each agent focuses on a specific aspect (security, performance, architecture)
- **Collaboration:** Agents work independently then combine findings
- **Conflict Resolution:** Synthesizer resolves contradicting recommendations
- **Context-Aware:** Provides full file context, not just diffs

---

## ✨ Key Features

### Implemented Features

- ✅ **PR Crawler**: Fetch complete PR data from GitHub (metadata, files, diffs)
- ✅ **LLM Integration**: Support for multiple LLM providers (OpenAI, Anthropic) via LiteLLM
- ✅ **Multi-Agent System**: Three specialized agents + synthesizer for conflict resolution
- ✅ **Structured Output**: JSON-formatted findings with severity levels
- ✅ **Logging System**: Comprehensive logging for debugging and monitoring
- ✅ **Parallel Execution**: Run multiple agents concurrently for faster analysis

### Specialized Agents

1. **Security Agent** (`agents/security_agent.py`)
   - Input validation vulnerabilities
   - Authentication/authorization issues
   - Sensitive data exposure
   - Cryptography problems
   - Injection attacks

2. **Performance Agent** (`agents/performance_agent.py`)
   - Algorithmic complexity
   - Database query optimization
   - Memory management
   - Network efficiency
   - Caching opportunities

3. **Architecture Agent** (`agents/architecture_agent.py`)
   - Code organization & structure
   - Design patterns & SOLID principles
   - Code duplication
   - Maintainability concerns
   - API design

4. **Synthesizer** (`agents/synthesizer.py`)
   - Combines findings from all agents
   - Detects and resolves conflicts
   - Prioritizes issues
   - Generates unified reports

---

## 🏗️ Architecture

### Multi-Agent System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub API                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  PR Crawler │  (Fetches PR data + full context)
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Orchestrator│  (Coordinates agents)
                  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Security │    │Performance│   │Architecture│
  │  Agent   │    │  Agent    │   │   Agent   │
  └────┬─────┘    └─────┬─────┘   └─────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Synthesizer │  (Resolves conflicts)
                  └──────┬──────┘
                         │
                         ▼
                Unified JSON Report
                (Prioritized findings)
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Git
- GitHub Personal Access Token (for API access)
- OpenAI API Key (for GPT models) or Anthropic API Key (for Claude models)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/4ndr-34/diploma-multi-agent.git
   cd diploma-multi-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys:
   # GITHUB_PAT=your_github_token
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key (optional)
   ```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# GitHub API (required)
GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxx

# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

### Getting API Keys

- **GitHub PAT**: Settings → Developer settings → Personal access tokens → Generate new token (Classic)
  - Required scopes: `repo`, `read:org`
  
- **OpenAI API**: https://platform.openai.com/api-keys
  
- **Anthropic API**: https://console.anthropic.com/settings/keys

---

## 💻 Usage

### Quick Start - Single PR Analysis

```bash
# Analyze a specific PR
python main.py tiangolo/fastapi --pr 1

# Analyze with a specific model
python main.py owner/repo --pr 123 --model gpt-4

# Analyze recent PRs
python main.py owner/repo --recent 5 --state open
```

### Multi-Agent Analysis

```python
from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator
from agents import MultiAgentOrchestrator

# Initialize components
crawler = PRCrawler()
llm_client = LLMIntegrator(model="gpt-3.5-turbo")
orchestrator = MultiAgentOrchestrator(
    llm_client=llm_client,
    model="gpt-3.5-turbo",
    parallel=True
)

# Crawl PR
pr_data = crawler.crawl_pr("owner/repo", pr_number=123)

# Run multi-agent analysis
report = orchestrator.analyze_pr(pr_data)

# Access results
print(f"Risk Level: {report.overall_assessment['risk_level']}")
print(f"Total Findings: {report.overall_assessment['total_findings']}")
print(f"Priority Issues: {len(report.priority_issues)}")
```

### Command Line Options

```bash
python main.py <repo> [options]

Required:
  repo                   Repository in format 'owner/name'

Options:
  --pr NUMBER           Analyze specific PR number
  --recent N            Analyze N most recent PRs
  --state STATE         PR state: open, closed, all (default: open)
  --model MODEL         LLM model to use (default: gpt-3.5-turbo)
  --no-diff             Exclude full diff from analysis
  --output FILE         Save results to JSON file
```

---

## 🧪 Testing

### Run All Tests

```bash
# Quick test (no API calls)
python tests/test_quick.py

# Multi-agent mock test (no API calls)
python tests/test_multi_agent_mock.py

# Full multi-agent test (requires API keys, costs ~$1-2)
python tests/test_multi_agent.py
```

### Test Coverage

- **test_quick.py**: Tests imports, GitHub connection, crawler, formatter, LLM setup
- **test_multi_agent_mock.py**: Tests multi-agent architecture without real LLM calls
- **test_multi_agent.py**: Full integration test with real LLM analysis

---

## 📁 Project Structure

```
diploma-multi-agent/
├── agents/                      # Multi-agent system
│   ├── __init__.py             # Package exports
│   ├── base_agent.py           # Abstract base agent class
│   ├── security_agent.py       # Security specialist
│   ├── performance_agent.py    # Performance specialist
│   ├── architecture_agent.py   # Architecture specialist
│   ├── synthesizer.py          # Conflict resolver
│   ├── orchestrator.py         # Agent coordinator
│   └── README.md               # Agent documentation
│
├── crawler/                     # PR data fetching
│   ├── __init__.py
│   ├── crawler.py              # GitHub API client
│   ├── llm_formatter.py        # Format PR for LLMs
│   └── llm_integration.py      # LLM API wrapper
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_quick.py           # Quick integration tests
│   ├── test_multi_agent.py     # Full multi-agent test
│   └── test_multi_agent_mock.py # Mock agent tests
│
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── PROJECT_OVERVIEW.md          # Detailed project documentation
└── LIMITATIONS_AND_IMPROVEMENTS.md  # Known issues & roadmap
```

---

## 📊 Development Status

**Current Completion: ~70%**

| Component | Status | Notes |
|-----------|--------|-------|
| PR Crawler | ✅ Complete | Fetches PR metadata, files, diffs |
| LLM Integration | ✅ Complete | Supports OpenAI, Anthropic via LiteLLM |
| Multi-Agent System | ✅ Complete | 3 agents + synthesizer + orchestrator |
| Logging System | ✅ Complete | Structured logging throughout |
| Basic Tests | ✅ Complete | Quick, mock, and integration tests |
| Evaluation Framework | ❌ Not started | 🔴 CRITICAL for thesis |
| Web Interface | ❌ Not started | Low priority |
| Comprehensive Tests | ⚠️ Partial | Need more coverage |

### Next Steps

1. ✅ ~~Implement multi-agent architecture~~ (DONE)
2. 🔄 Build evaluation framework (compare multi-agent vs single-agent)
3. 🔄 Conduct experiments on real PRs
4. 🔄 Write thesis chapters
5. 🔄 Create result visualizations

---

## 📚 Documentation

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**: Comprehensive project documentation
- **[agents/README.md](agents/README.md)**: Multi-agent system details
- **[LIMITATIONS_AND_IMPROVEMENTS.md](LIMITATIONS_AND_IMPROVEMENTS.md)**: Known issues and roadmap
- **[.env.example](.env.example)**: Environment configuration template

---

## 🤝 Contributing

This is a thesis project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 👤 Author

**Andre** (4ndr-34)
- GitHub: [@4ndr-34](https://github.com/4ndr-34)
- Project: MSc Thesis - Multi-Agent Code Review System

---

## 🙏 Acknowledgments

- **LiteLLM**: For unified LLM API interface
- **PyGithub**: For GitHub API integration
- **FastAPI Team**: For providing excellent example PRs for testing

---

## 📝 Citation

If you use this work in your research, please cite:

```bibtex
@mastersthesis{andre2026multiagent,
  author  = {Andre},
  title   = {Multi-Agent Code Review: A Specialized Approach to Automated Pull Request Analysis},
  school  = {[Your University]},
  year    = {2026},
  type    = {MSc Thesis}
}
```

---

**Status**: Active Development | **Last Updated**: May 2026
