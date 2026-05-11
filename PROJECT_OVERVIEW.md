# Multi-Agent PR Analyzer

## Overview

A Python-based system that crawls public GitHub pull requests and analyzes them using multiple specialized AI agents. The system simulates a human code review process by having different agents focus on security, performance, and code quality, then synthesizing their findings into a unified report.

## Core Components

### 1. PR Crawler (`pr_crawler.py`)
- Fetches PR data from public GitHub repositories using the GitHub API
- Handles rate limiting with automatic retries
- Supports batch processing with configurable concurrency
- Implements LRU caching to avoid redundant API calls
- Manages large PRs through size-based truncation (file count, patch size)

### 2. LLM Formatter (`llm_formatter.py`)
- Converts raw PR data into structured prompts for LLM analysis
- Provides different output formats (summary, full analysis with/without diffs)
- Handles truncation notifications for oversized PRs

### 3. LLM Integrator (`llm_integration.py`)
- Unified interface for multiple LLM providers (OpenAI, Anthropic, etc.) via LiteLLM
- Manages API calls with retry logic
- Supports configurable models and token limits

## Multi-Agent Architecture

| Agent | Focus Area | Key Checks |
|-------|------------|-------------|
| Security Auditor | Vulnerabilities | Injection flaws, hardcoded secrets, auth issues |
| Performance Engineer | Efficiency | Time complexity, memory leaks, resource usage |
| Code Architect | Maintainability | SOLID principles, design patterns, code smells |

A **synthesizer agent** resolves conflicting opinions and formats the final output.

## Data Flow
