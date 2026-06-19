# Complete PR Review Testing Setup Guide

Step-by-step guide to create a GitHub Actions workflow for automated PR reviews, starting from scratch.

## Table of Contents
1. [Understanding GitHub Actions](#understanding-github-actions)
2. [Creating the Demo Project](#creating-the-demo-project)
3. [Setting Up GitHub Actions Workflow](#setting-up-github-actions-workflow)
4. [Creating the Runner Script](#creating-the-runner-script)
5. [Deploying to GitHub](#deploying-to-github)
6. [Running Your First Test](#running-your-first-test)
7. [Complete Test Suite](#complete-test-suite)

---

## Understanding GitHub Actions

### What is GitHub Actions?

GitHub Actions is a CI/CD (Continuous Integration/Continuous Deployment) platform that automates workflows directly in your repository.

**Key Concepts:**
- **Workflow:** Automated process defined in YAML file (e.g., `pr-review.yml`)
- **Trigger:** Events that start workflows (e.g., pull request opened)
- **Job:** Set of steps that execute on the same runner
- **Step:** Individual task (run a script, checkout code, etc.)
- **Runner:** Server that executes your workflow (GitHub-hosted or self-hosted)

### How Our System Will Work

```
┌─────────────────────────────────────────────────────────────┐
│  Developer creates Pull Request                             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions Trigger (on: pull_request)                  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Workflow Steps:                                            │
│  1. Checkout demo-pr-review code                           │
│  2. Checkout diploma-multi-agent (agent system)            │
│  3. Install Python dependencies                            │
│  4. Run run_review.py script                               │
│  5. Post results as PR comment                             │
│  6. Set PR status (✅ pass or ❌ fail)                     │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Developer sees automated review in ~60 seconds             │
└─────────────────────────────────────────────────────────────┘
```

---

## Creating the Demo Project

We'll create a **separate repository** for the demo project. This simulates a real-world scenario where the review system is used in a different project.

### Step 1: Create Demo Project Directory

```powershell
# Navigate to your Msc2 folder
cd C:\Users\andre\Desktop\Uni\Msc2\

# Create new directory for demo project
New-Item -ItemType Directory -Path "demo-pr-review"
cd demo-pr-review
```

### Step 2: Create Project Structure

```powershell
# Create directory structure
New-Item -ItemType Directory -Path "src\api"
New-Item -ItemType Directory -Path "src\models"
New-Item -ItemType Directory -Path "src\utils"
New-Item -ItemType Directory -Path ".github\workflows"
```

Your structure should look like:
```
demo-pr-review/
├── .github/
│   └── workflows/
├── src/
│   ├── api/
│   ├── models/
│   └── utils/
└── README.md (we'll create this)
```

### Step 3: Create Demo Files with Intentional Issues

**Create `README.md`:**

```powershell
@"
# Demo PR Review Project

This project is designed to test the multi-agent PR review system.

## Purpose

Contains intentional code issues to validate that the review system can detect:
- Security vulnerabilities (SQL injection, XSS, weak passwords)
- Performance issues (N+1 queries, O(n²) algorithms)
- Architecture smells (god classes, code duplication, SOLID violations)

## Usage

1. Create a branch
2. Make changes
3. Open a Pull Request
4. Automated review runs via GitHub Actions
5. Results posted as PR comment

## Testing Scenarios

- Fix security issues → See quality score improve
- Add performance optimization → Verify detection
- Refactor architecture → Check pattern recognition
- Submit clean code → Confirm positive feedback
"@ | Out-File -FilePath "README.md" -Encoding utf8
```

**Create `src/api/users.py`:**

```powershell
@"
`# -*- coding: utf-8 -*-
`"""
User API Module

Handles user-related operations.
Contains intentional issues for testing.
`"""

import sqlite3
from typing import List, Optional


class UserAPI:
    `"""User API with intentional security and performance issues`"""
    
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        `"""
        Get user by ID
        
        SECURITY ISSUE: SQL Injection vulnerability
        `"""
        cursor = self.connection.cursor()
        # SECURITY ISSUE: SQL Injection vulnerability
        query = f`"SELECT * FROM users WHERE id = {user_id}`"
        cursor.execute(query)
        
        row = cursor.fetchone()
        if row:
            return {
                `"id`": row[0],
                `"username`": row[1],
                `"email`": row[2],
                `"created_at`": row[3]
            }
        return None
    
    def get_all_users(self) -> List[dict]:
        `"""
        Get all users
        
        PERFORMANCE ISSUE: No pagination
        `"""
        cursor = self.connection.cursor()
        cursor.execute(`"SELECT * FROM users`")
        
        users = []
        # PERFORMANCE ISSUE: Loading all users without pagination
        for row in cursor.fetchall():
            users.append({
                `"id`": row[0],
                `"username`": row[1],
                `"email`": row[2],
                `"created_at`": row[3]
            })
        
        return users
    
    def get_user_posts(self, user_id: int) -> List[dict]:
        `"""
        Get all posts for a user
        
        PERFORMANCE ISSUE: N+1 query problem
        `"""
        cursor = self.connection.cursor()
        
        # Get user
        cursor.execute(f`"SELECT * FROM users WHERE id = {user_id}`")
        user = cursor.fetchone()
        
        if not user:
            return []
        
        # PERFORMANCE ISSUE: N+1 queries
        cursor.execute(`"SELECT id FROM posts WHERE user_id = ?`", (user_id,))
        post_ids = cursor.fetchall()
        
        posts = []
        for post_id in post_ids:
            # Separate query for each post (N+1 problem)
            cursor.execute(`"SELECT * FROM posts WHERE id = ?`", (post_id[0],))
            post = cursor.fetchone()
            posts.append({
                `"id`": post[0],
                `"title`": post[1],
                `"content`": post[2]
            })
        
        return posts
    
    def search_users(self, query: str) -> List[dict]:
        `"""
        Search users by username
        
        SECURITY ISSUE: SQL Injection in search
        `"""
        cursor = self.connection.cursor()
        # SECURITY ISSUE: SQL Injection in LIKE clause
        sql = f`"SELECT * FROM users WHERE username LIKE '%{query}%'`"
        cursor.execute(sql)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                `"id`": row[0],
                `"username`": row[1],
                `"email`": row[2]
            })
        
        return users
    
    def create_user(self, username: str, email: str, password: str) -> int:
        `"""
        Create new user
        
        SECURITY ISSUE: Plain text password storage
        `"""
        cursor = self.connection.cursor()
        
        # SECURITY ISSUE: Storing password in plain text
        cursor.execute(
            `"INSERT INTO users (username, email, password) VALUES (?, ?, ?)`",
            (username, email, password)  # Plain text password!
        )
        
        self.connection.commit()
        return cursor.lastrowid
"@ | Out-File -FilePath "src\api\users.py" -Encoding utf8
```

**Create `src/utils/data_processor.py`:**

```powershell
@"
`# -*- coding: utf-8 -*-
`"""
Data Processing Utilities

Contains intentional performance and architecture issues.
`"""

from typing import List, Any
import json


class DataProcessor:
    `"""Data processor with intentional issues`"""
    
    def process_items(self, items: List[dict]) -> List[dict]:
        `"""
        Process list of items
        
        PERFORMANCE ISSUE: O(n²) complexity
        `"""
        processed = []
        
        # PERFORMANCE ISSUE: Nested loops creating O(n²) complexity
        for item in items:
            duplicates = []
            for other_item in items:
                if item['id'] == other_item['id']:
                    duplicates.append(other_item)
            
            item['duplicate_count'] = len(duplicates)
            processed.append(item)
        
        return processed
    
    def transform_data(self, data: Any, format: str) -> str:
        `"""
        Transform data to different formats
        
        ARCHITECTURE ISSUE: Large if-else chain (should use Strategy pattern)
        `"""
        # ARCHITECTURE ISSUE: Long if-else chain
        if format == 'json':
            return json.dumps(data)
        elif format == 'csv':
            # Simplified CSV conversion
            return `"csv_data`"
        elif format == 'xml':
            return `"<data></data>`"
        elif format == 'yaml':
            return `"yaml_data`"
        elif format == 'text':
            return str(data)
        else:
            return str(data)
    
    def calculate_metrics(self, data: List[dict]) -> dict:
        `"""
        Calculate metrics from data
        
        ARCHITECTURE ISSUE: Code duplication
        `"""
        total = 0
        # ARCHITECTURE ISSUE: Code duplication
        for item in data:
            total += item.get('value', 0)
        
        average = 0
        for item in data:
            average += item.get('value', 0)
        average = average / len(data) if data else 0
        
        maximum = 0
        for item in data:
            val = item.get('value', 0)
            if val > maximum:
                maximum = val
        
        minimum = float('inf')
        for item in data:
            val = item.get('value', 0)
            if val < minimum:
                minimum = val
        
        return {
            'total': total,
            'average': average,
            'max': maximum,
            'min': minimum if minimum != float('inf') else 0
        }
"@ | Out-File -FilePath "src\utils\data_processor.py" -Encoding utf8
```

**Create `src/models/user.py`:**

```powershell
@"
`# -*- coding: utf-8 -*-
`"""
User Model

Contains intentional architecture issues.
`"""

from datetime import datetime
from typing import Optional


class User:
    `"""
    User model
    
    ARCHITECTURE ISSUE: Business logic in model (god class pattern)
    `"""
    
    def __init__(self, id: int, username: str, email: str, password: str):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.now()
    
    def validate_password(self, password: str) -> bool:
        `"""
        Validate password strength
        
        SECURITY ISSUE: Weak password validation
        `"""
        # SECURITY ISSUE: Very weak password validation
        return len(password) >= 6  # Should be much stronger!
    
    def send_welcome_email(self):
        `"""
        Send welcome email
        
        ARCHITECTURE ISSUE: Model should not handle email sending
        `"""
        # ARCHITECTURE ISSUE: Business logic in model
        print(f`"Sending welcome email to {self.email}`")
    
    def log_login(self):
        `"""
        Log user login
        
        ARCHITECTURE ISSUE: Model handling logging
        `"""
        # ARCHITECTURE ISSUE: Model should not handle logging
        print(f`"User {self.username} logged in at {datetime.now()}`")
    
    def calculate_reputation(self) -> int:
        `"""
        Calculate user reputation
        
        ARCHITECTURE ISSUE: Complex business logic in model
        `"""
        # ARCHITECTURE ISSUE: Business logic should be in service layer
        days_since_creation = (datetime.now() - self.created_at).days
        return days_since_creation * 10
    
    def to_dict(self) -> dict:
        `"""Convert user to dictionary`"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
"@ | Out-File -FilePath "src\models\user.py" -Encoding utf8
```

**Create `requirements.txt`:**

```powershell
@"
# Demo project dependencies (minimal)
python-dotenv==1.0.0
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8
```

---

## Setting Up GitHub Actions Workflow

Now we'll create the GitHub Actions workflow file that will automatically review PRs.

### Step 1: Create Workflow File

```powershell
# Create the workflow YAML file
@"
name: Multi-Agent PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      # Step 1: Checkout the demo PR code
      - name: Checkout PR Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better context
      
      # Step 2: Checkout the review system (your diploma project)
      - name: Checkout Review System
        uses: actions/checkout@v4
        with:
          repository: 4ndr-34/diploma-multi-agent
          path: review-system
          token: `${{ secrets.GITHUB_TOKEN }}
      
      # Step 3: Set up Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      # Step 4: Install dependencies
      - name: Install Dependencies
        run: |
          cd review-system
          pip install -r requirements.txt
      
      # Step 5: Run the multi-agent review
      - name: Run Multi-Agent Review
        id: review
        env:
          OPENAI_API_KEY: `${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: `${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/scripts/run_review.py \
            --repo `${{ github.repository }} \
            --pr `${{ github.event.pull_request.number }} \
            --output review_results.json
        working-directory: review-system
        continue-on-error: true
      
      # Step 6: Read review results
      - name: Read Review Results
        id: read_results
        if: always()
        run: |
          if [ -f review-system/review_results.json ]; then
            echo `"results_exist=true`" >> `$GITHUB_OUTPUT
          else
            echo `"results_exist=false`" >> `$GITHUB_OUTPUT
          fi
      
      # Step 7: Post review comment on PR
      - name: Post Review Comment
        if: steps.read_results.outputs.results_exist == 'true'
        uses: actions/github-script@v7
        with:
          github-token: `${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('review-system/review_results.json', 'utf8'));
            
            // Build comment markdown
            let comment = `### 🤖 Multi-Agent PR Review Results\n\n`;
            
            // Overall assessment
            comment += `#### 📊 Overall Quality\n\n`;
            comment += `| Metric | Value |\n`;
            comment += `|--------|-------|\n`;
            comment += `| **Quality Score** | ${results.quality_score}% (Grade ${results.quality_grade}) |\n`;
            comment += `| **Risk Level** | ${results.risk_level} |\n`;
            comment += `| **Recommendation** | ${results.recommendation} |\n`;
            comment += `| **Confidence** | ${results.confidence}% |\n`;
            comment += `| **Total Findings** | ${results.total_findings} |\n`;
            comment += `| **Execution Time** | ${results.execution_time.toFixed(1)}s |\n\n`;
            
            // Findings breakdown
            comment += `#### 🔍 Findings Breakdown\n\n`;
            comment += `| Severity | Count |\n`;
            comment += `|----------|-------|\n`;
            comment += `| 🔴 Critical | ${results.critical_findings} |\n`;
            comment += `| 🟠 High | ${results.high_findings} |\n`;
            comment += `| 🟡 Medium | ${results.medium_findings} |\n\n`;
            
            // Agent summaries
            comment += `#### 🎯 Agent Analysis\n\n`;
            for (const [agent, summary] of Object.entries(results.agent_summaries)) {
              const icon = agent.includes('Security') ? '🔒' : 
                          agent.includes('Performance') ? '⚡' : '🏗️';
              comment += `**${icon} ${agent}**\n`;
              comment += `- Issues: ${summary.issues_found}\n`;
              comment += `- Status: ${summary.status}\n`;
              comment += `- Summary: ${summary.summary}\n\n`;
            }
            
            // Priority issues
            if (results.priority_issues && results.priority_issues.length > 0) {
              comment += `#### ⚠️ Top Priority Issues\n\n`;
              results.priority_issues.slice(0, 5).forEach((issue, idx) => {
                comment += `${idx + 1}. **[${issue.severity}]** ${issue.title}\n`;
                comment += `   - Category: ${issue.category}\n`;
                comment += `   - Location: \`${issue.location}\`\n`;
                comment += `   - ${issue.description}\n\n`;
              });
            }
            
            comment += `---\n`;
            comment += `*Agents Consensus: ${results.agents_consensus}% | Model: gpt-3.5-turbo*\n`;
            
            // Post the comment
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.pull_request.number,
              body: comment
            });
      
      # Step 8: Set PR status based on results
      - name: Check Review Status
        if: steps.read_results.outputs.results_exist == 'true'
        run: |
          QUALITY=`$(jq -r '.quality_score' review-system/review_results.json)
          CRITICAL=`$(jq -r '.critical_findings' review-system/review_results.json)
          
          echo `"Quality Score: `$QUALITY%`"
          echo `"Critical Findings: `$CRITICAL`"
          
          if [ `$CRITICAL -gt 0 ]; then
            echo `"❌ Review failed: Critical issues found`"
            exit 1
          elif (( `$(echo `"`$QUALITY < 70`" | bc -l) )); then
            echo `"❌ Review failed: Quality score below threshold`"
            exit 1
          else
            echo `"✅ Review passed`"
            exit 0
          fi
"@ | Out-File -FilePath ".github\workflows\pr-review.yml" -Encoding utf8
```

### Step 2: Understand the Workflow

Let's break down what this workflow does:

**Triggers:**
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```
- Runs when a PR is opened, updated (synchronize), or reopened

**Jobs:**
```yaml
jobs:
  review:
    runs-on: ubuntu-latest  # Uses GitHub's Ubuntu runner
```

**Key Steps:**
1. **Checkout PR Code** - Gets the code from your PR
2. **Checkout Review System** - Clones your main diploma project (where agents live)
3. **Setup Python** - Installs Python 3.11
4. **Install Dependencies** - Installs required packages from `requirements.txt`
5. **Run Review** - Executes `run_review.py` with PR data
6. **Post Comment** - Formats and posts results as a PR comment
7. **Set Status** - Marks PR as passing (✅) or failing (❌)

---

## Creating the Runner Script

Now we need to create the script that GitHub Actions will run. This goes in your **main diploma repository**, not the demo project.

### Step 1: Create Scripts Directory

```powershell
# Navigate to your main diploma project
cd C:\Users\andre\Desktop\Uni\Msc2\Diploma

# Create scripts directory
New-Item -ItemType Directory -Path ".github\scripts" -Force
```

### Step 2: Create run_review.py

```powershell
# The run_review.py script already exists at .github/scripts/run_review.py
# Let's verify it exists
Test-Path ".github\scripts\run_review.py"
```

If it doesn't exist, let's create it now (I'll use the improved version with comparison support):

**The script is already in your project at** `.github\scripts\run_review.py` - this is the runner that GitHub Actions calls.

### Step 3: Test the Script Locally (Optional)

Before deploying to GitHub, you can test locally:

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\Diploma
.venv\Scripts\activate

# Test on a real PR (e.g., FastAPI PR #1)
python .github\scripts\run_review.py `
  --repo tiangolo/fastapi `
  --pr 1 `
  --output test_results.json

# Check the output
Get-Content test_results.json | ConvertFrom-Json | Format-List
```

---

## Deploying to GitHub

Now we'll push everything to GitHub and configure the secrets.

### Step 1: Initialize Demo Project Git Repository

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review

# Initialize git
git init
git add .
git commit -m "Initial commit: Demo project with intentional issues for testing

- Added UserAPI with SQL injection vulnerabilities
- Added DataProcessor with O(n²) complexity
- Added User model with architecture issues
- Configured GitHub Actions workflow for automated review"
```

### Step 2: Create GitHub Repository

1. **Go to GitHub:** https://github.com/new
2. **Fill in details:**
   - **Repository name:** `demo-pr-review`
   - **Description:** "Demo project for testing multi-agent PR review system (MSc Thesis)"
   - **Visibility:** Public
   - **DO NOT** check "Initialize with README" (we already have one)
3. **Click:** "Create repository"

### Step 3: Push to GitHub

GitHub will show you commands. Run them:

```powershell
# Add remote (replace YOUR_USERNAME with your actual username)
git remote add origin https://github.com/4ndr-34/demo-pr-review.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 4: Add OpenAI API Key Secret

This is **critical** - without it, the workflow can't call OpenAI.

1. **Go to your demo repository settings:**
   ```
   https://github.com/4ndr-34/demo-pr-review/settings/secrets/actions
   ```

2. **Click:** "New repository secret"

3. **Add secret:**
   - **Name:** `OPENAI_API_KEY` (must be exactly this)
   - **Secret:** Your OpenAI API key (starts with `sk-...`)
   
   **Where to find your API key:**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy it immediately (you won't see it again!)

4. **Click:** "Add secret"

### Step 5: Configure Workflow Permissions

1. **Go to Actions settings:**
   ```
   https://github.com/4ndr-34/demo-pr-review/settings/actions
   ```

2. **Under "Workflow permissions":**
   - ✅ Select: **"Read and write permissions"**
   - ✅ Check: **"Allow GitHub Actions to create and approve pull requests"**

3. **Click:** "Save"

### Step 6: Enable GitHub Actions

1. **Go to Actions tab:**
   ```
   https://github.com/4ndr-34/demo-pr-review/actions
   ```

2. **If prompted:** Click "I understand my workflows, go ahead and enable them"

3. **You should see:** "No workflow runs yet" (this is correct - workflows run when PRs are created)

### Step 7: Verify Your Main Diploma Repository

The workflow needs to access your main diploma repository. Make sure it's pushed to GitHub:

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\Diploma

# Check remote
git remote -v

# If no remote, add one:
# git remote add origin https://github.com/4ndr-34/diploma-multi-agent.git

# Push your code (including .github/scripts/run_review.py)
git add .
git commit -m "Add GitHub Actions runner script"
git push
```

---

## Running Your First Test

Everything is set up! Now let's create your first automated PR review.

### Step 1: Create a Test Branch

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review

# Make sure you're on main
git checkout main
git pull

# Create a test branch
git checkout -b test/first-automated-review
```

### Step 2: Make a Simple Change

Let's add a simple comment to trigger the workflow:

```powershell
# Add a test comment to README
Add-Content -Path "README.md" -Value "`n## First Test`nTesting automated PR review system.`n"

# Commit the change
git add README.md
git commit -m "Test: First automated review

This PR tests if the GitHub Actions workflow runs correctly.
Expected: Automated review comment should appear within 60 seconds."

# Push the branch
git push -u origin test/first-automated-review
```

### Step 3: Create Pull Request on GitHub

1. **Go to your repository:**
   ```
   https://github.com/4ndr-34/demo-pr-review
   ```

2. **You'll see a notification:**
   ```
   test/first-automated-review had recent pushes (less than a minute ago)
   [Compare & pull request]
   ```

3. **Click:** "Compare & pull request"

4. **Fill in PR details:**
   - **Title:** `Test: First automated review`
   - **Description:**
     ```
     Testing the automated PR review system.
     
     **Expected:**
     - Workflow runs automatically
     - Review comment appears
     - PR status shows pass/fail
     
     **Test scenario:**
     - Simple README change
     - Should detect existing issues in codebase
     - Quality score should be ~75-80%
     ```

5. **Click:** "Create pull request"

### Step 4: Watch the Magic Happen! ✨

**Immediately (within 5 seconds):**
- You'll see a yellow dot (🟡) next to "Some checks haven't completed yet"
- Click on "Details" to watch the workflow run live

**What you'll see in the workflow:**
```
Run Checkout PR Code
✅ Checkout PR code (2s)

Run Checkout Review System  
✅ Checkout review system (3s)

Run Set up Python
✅ Set up Python 3.11 (8s)

Run Install Dependencies
✅ pip install -r requirements.txt (15s)

Run Multi-Agent Review
🔄 Running analysis... (30-45s)
  ├─ Fetching PR data
  ├─ Security Agent analyzing...
  ├─ Performance Agent analyzing...
  ├─ Architecture Agent analyzing...
  └─ Synthesizing results...
✅ Review complete

Run Post Review Comment
✅ Comment posted

Run Check Review Status
✅ or ❌ Depending on quality score
```

**After ~60 seconds total:**
- Go back to the "Conversation" tab of your PR
- You should see a comment from `github-actions[bot]`
- The comment contains the full review results!

### Step 5: Interpret the Results

Your automated comment should look like this:

```markdown
### 🤖 Multi-Agent PR Review Results

#### 📊 Overall Quality

| Metric | Value |
|--------|-------|
| **Quality Score** | 76% (Grade C+) |
| **Risk Level** | MEDIUM |
| **Recommendation** | Request changes - address key issues before merging |
| **Confidence** | 85% |
| **Total Findings** | 8 |
| **Execution Time** | 42.3s |

#### 🔍 Findings Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | 0 |
| 🟠 High | 3 |
| 🟡 Medium | 5 |

#### 🎯 Agent Analysis

**🔒 Security Agent**
- Issues: 3
- Status: Issues found
- Summary: Detected SQL injection vulnerabilities in user queries

**⚡ Performance Agent**
- Issues: 2
- Status: Issues found
- Summary: Found N+1 query problem and missing pagination

**🏗️ Architecture Agent**
- Issues: 3
- Status: Issues found
- Summary: Identified god class pattern and code duplication

#### ⚠️ Top Priority Issues

1. **[HIGH]** SQL Injection in get_user_by_id
   - Category: Security
   - Location: `src/api/users.py:30`
   - Using string interpolation in SQL query allows injection attacks

2. **[HIGH]** SQL Injection in search_users
   - Category: Security
   - Location: `src/api/users.py:78`
   - LIKE clause vulnerable to SQL injection

3. **[MEDIUM]** N+1 Query Problem
   - Category: Performance
   - Location: `src/api/users.py:55`
   - Multiple database queries in loop impacts performance

---
*Agents Consensus: 87% | Model: gpt-3.5-turbo*
```

### Step 6: Check PR Status

- At the bottom of the PR, you'll see the status check:
  - ✅ **"Multi-Agent Review / review — succeeded"** (if quality > 70%)
  - ❌ **"Multi-Agent Review / review — failed"** (if quality < 70% or critical issues)

---

## Complete Test Suite

Now that basic testing works, let's run comprehensive tests.

### Test 2: Fix a Security Issue

**Goal:** Verify that fixing a security issue improves the score.

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review
git checkout main
git pull
git checkout -b fix/sql-injection-user-id
```

**Edit `src/api/users.py` line 30:**

Before:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

After:
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

```powershell
git add src\api\users.py
git commit -m "Fix: SQL injection vulnerability in get_user_by_id

- Replaced string interpolation with parameterized query
- Prevents SQL injection attacks
- Follows OWASP security guidelines"

git push -u origin fix/sql-injection-user-id
```

**Create PR** and watch the results. **Expected:** Quality score improves by 3-5%.

### Test 3: Add Performance Optimization

```powershell
git checkout main
git pull
git checkout -b perf/add-pagination
```

**Edit `src/api/users.py` - Update `get_all_users` method:**

```python
def get_all_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
    """Get all users with pagination"""
    cursor = self.connection.cursor()
    query = "SELECT * FROM users LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))
    # ... rest of method
```

```powershell
git add src\api\users.py
git commit -m "Perf: Add pagination to get_all_users

- Added limit and offset parameters
- Prevents loading all records at once
- Improves scalability"

git push -u origin perf/add-pagination
```

**Expected:** Performance agent recognizes improvement.

### Test 4: Submit Clean Code

```powershell
git checkout main
git pull
git checkout -b feat/add-helper-function
```

**Create `src/utils/helpers.py`:**

```python
# -*- coding: utf-8 -*-
"""
Helper Utilities

Well-written helper functions following best practices.
"""

from typing import List, Optional


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """
    Safely divide two numbers
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        
    Returns:
        Result of division or None if denominator is zero
    """
    if denominator == 0:
        return None
    return numerator / denominator


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunked lists
        
    Example:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
```

```powershell
New-Item -ItemType File -Path "src\utils\helpers.py"
# Copy the code above into the file

git add src\utils\helpers.py
git commit -m "Feat: Add utility helper functions

- Added safe_divide with zero division handling
- Added chunk_list for list processing
- Well-documented with examples
- Follows Python best practices"

git push -u origin feat/add-helper-function
```

**Expected:** Quality score 90-95%, minimal issues, positive feedback.

---

## Troubleshooting

### Workflow Doesn't Run

**Symptoms:** No yellow dot appears when you create PR.

**Solutions:**
1. Check Actions are enabled: `Settings` → `Actions` → `General`
2. Verify workflow file is in `.github/workflows/pr-review.yml`
3. Check YAML syntax: https://www.yamllint.com/

### "Resource not accessible by integration" Error

**Symptoms:** Workflow fails with permission error.

**Solutions:**
1. Go to `Settings` → `Actions` → `General`
2. Select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"
4. Save and re-run workflow

### "Authentication failed" or OpenAI API Error

**Symptoms:** Review step fails, logs show API error.

**Solutions:**
1. Verify secret name is exactly `OPENAI_API_KEY`
2. Check API key is valid: https://platform.openai.com/api-keys
3. Ensure you have API credits available
4. Check key has proper permissions

### Comment Not Posted

**Symptoms:** Workflow succeeds but no comment appears.

**Solutions:**
1. Check workflow permissions (step above)
2. Look at workflow logs - any errors in "Post Review Comment" step?
3. Verify `review_results.json` was created (check logs)

### Review Seems Inaccurate

**Symptoms:** Agents miss obvious issues or flag false positives.

**Solutions:**
1. Review the PR changes - are they clear enough?
2. Check model temperature (in `run_review.py`)
3. Try with a better model (e.g., `gpt-4` instead of `gpt-3.5-turbo`)
4. Increase agent token limits

---

## Success Checklist

✅ Demo project created with intentional issues  
✅ GitHub Actions workflow file created  
✅ Runner script exists in main repo  
✅ Demo repository pushed to GitHub  
✅ `OPENAI_API_KEY` secret added  
✅ Workflow permissions configured  
✅ First test PR created  
✅ Automated review comment appears  
✅ PR status check shows (pass/fail)  
✅ Security fix test completed  
✅ Performance optimization test completed  
✅ Clean code test completed  

---

## Next Steps

1. **Run Complete Test Suite** (15-20 PRs with different scenarios)
2. **Enable Comparison Mode** (add `--compare` flag)
3. **Collect Data for Thesis** (quality scores, findings, execution time)
4. **Analyze Results** (calculate averages, improvements, statistical significance)
5. **Document Findings** (tables, charts, conclusions)

---

## Cost Tracking

**Per PR (gpt-3.5-turbo):**
- Multi-agent only: ~$0.08-0.12
- With comparison: ~$0.12-0.18

**Total for 20 test PRs:**
- Approximately: $2-4
- Very affordable for a thesis project!

---

Good luck with your testing! 🚀

**Pro Tip:** Create a spreadsheet to track results:
```
PR# | Type | Quality | Findings | Time | Notes
1   | test | 76%     | 8        | 42s  | Baseline
2   | fix  | 81%     | 7        | 45s  | SQL injection fixed
...
```

This data will be invaluable for your thesis results chapter!
