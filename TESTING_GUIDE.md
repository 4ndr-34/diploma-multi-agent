# PR Review Testing Guide

Complete step-by-step guide for testing the multi-agent PR review system.

## Table of Contents
1. [Setup Demo Repository](#setup-demo-repository)
2. [Test 1: Basic Functionality](#test-1-basic-functionality)
3. [Test 2: Security Issue Detection](#test-2-security-issue-detection)
4. [Test 3: Performance Issue Detection](#test-3-performance-issue-detection)
5. [Test 4: Architecture Issue Detection](#test-4-architecture-issue-detection)
6. [Test 5: Clean Code (Positive Test)](#test-5-clean-code-positive-test)
7. [Test 6: Single vs Multi-Agent Comparison](#test-6-single-vs-multi-agent-comparison)
8. [Data Collection for Thesis](#data-collection-for-thesis)

---

## Setup Demo Repository

### Step 1: Move Demo Project

```powershell
# Navigate to parent directory
cd C:\Users\andre\Desktop\Uni\Msc2\

# Move demo-project outside main repo (if not already done)
# It should be at: C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review\
```

### Step 2: Initialize Git Repository

```powershell
cd demo-pr-review

# Initialize git
git init
git add .
git commit -m "Initial commit: Demo project for multi-agent review"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `demo-pr-review`
3. Description: "Demo project for testing multi-agent PR review system"
4. Public repository
5. **Don't** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 4: Push to GitHub

```powershell
git remote add origin https://github.com/4ndr-34/demo-pr-review.git
git branch -M main
git push -u origin main
```

### Step 5: Add API Key Secret

1. Go to: https://github.com/4ndr-34/demo-pr-review/settings/secrets/actions
2. Click "New repository secret"
3. Add secret:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (starts with `sk-...`)
4. Click "Add secret"

### Step 6: Enable Workflow Permissions

1. Go to: https://github.com/4ndr-34/demo-pr-review/settings/actions
2. Under "Workflow permissions":
   - Select ✅ "Read and write permissions"
   - Check ✅ "Allow GitHub Actions to create and approve pull requests"
3. Click "Save"

### Step 7: Verify Setup

1. Go to: https://github.com/4ndr-34/demo-pr-review/actions
2. You should see "No workflow runs yet" (this is correct)
3. Workflow will trigger when you create a PR

---

## Test 1: Basic Functionality

**Goal:** Verify the automated review system works end-to-end.

### Step 1: Create Test Branch

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review

git checkout -b test/basic-functionality
```

### Step 2: Make a Simple Change

```powershell
# Add a comment to README
echo "`n## Testing`nThis is a test of the automated review system." >> README.md

git add README.md
git commit -m "Test: Basic functionality check"
git push -u origin test/basic-functionality
```

### Step 3: Create Pull Request

1. Go to: https://github.com/4ndr-34/demo-pr-review
2. Click "Compare & pull request" button
3. Title: "Test: Basic functionality"
4. Description: "Testing if automated review works"
5. Click "Create pull request"

### Step 4: Watch the Review

1. **Immediately:** You should see a yellow dot (workflow running)
2. **After ~60 seconds:** 
   - Review comment appears
   - Status check shows (green ✅ or red ❌)
3. Click on "Details" next to status check to see logs

### Step 5: Verify Results

Check that the PR comment contains:
- ✅ Quality score (e.g., 85% / Grade B)
- ✅ Risk level
- ✅ Findings by category (Security, Performance, Architecture)
- ✅ Top priority issues (if any)
- ✅ Execution time

### Expected Result:
- **Quality Score:** ~85-95% (Grade A-/B+)
- **Findings:** 5-10 (existing issues in demo code)
- **Status:** ✅ Pass (quality > 70%)

---

## Test 2: Security Issue Detection

**Goal:** Verify security agent catches SQL injection vulnerability fix.

### Step 1: Create Fix Branch

```powershell
git checkout main
git pull
git checkout -b fix/sql-injection
```

### Step 2: Fix SQL Injection in users.py

Open `src/api/users.py` and find line 30:

**Before (line 29-31):**
```python
# SECURITY ISSUE: SQL Injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**After:**
```python
# Fixed: Using parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Step 3: Commit and Push

```powershell
git add src/api/users.py
git commit -m "Fix: SQL injection vulnerability in get_user_by_id

- Changed from string interpolation to parameterized query
- Prevents SQL injection attacks
- Follows OWASP security best practices"

git push -u origin fix/sql-injection
```

### Step 4: Create Pull Request

1. Create PR: "Fix: SQL injection vulnerability"
2. Description: "Fixes SQL injection in get_user_by_id method using parameterized queries"
3. Wait for review

### Expected Results:
- ✅ **Security Agent:** Should recognize the fix
- ✅ **Quality Score:** Should improve (e.g., 78% → 82%)
- ✅ **Remaining Issues:** Still flags other security issues (search_users, create_user)
- ✅ **Status:** Pass

### Verify:
- Security findings count should decrease by 1
- Comment should mention the improvement

---

## Test 3: Performance Issue Detection

**Goal:** Test if performance agent detects optimization.

### Step 1: Add Pagination

```powershell
git checkout main
git pull
git checkout -b perf/add-pagination
```

### Step 2: Modify get_all_users Method

Open `src/api/users.py` and find the `get_all_users` method (around line 43):

**Before:**
```python
def get_all_users(self) -> List[dict]:
    """
    Get all users
    
    Returns:
        List of all users
    """
    cursor = self.connection.cursor()
    cursor.execute("SELECT * FROM users")
    
    users = []
    # PERFORMANCE ISSUE: Loading all users without pagination
    for row in cursor.fetchall():
        users.append({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "created_at": row[3]
        })
    
    return users
```

**After:**
```python
def get_all_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
    """
    Get all users with pagination
    
    Args:
        limit: Maximum number of users to return (default 100)
        offset: Number of users to skip (default 0)
    
    Returns:
        List of users (paginated)
    """
    cursor = self.connection.cursor()
    query = "SELECT * FROM users LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))
    
    users = []
    for row in cursor.fetchall():
        users.append({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "created_at": row[3]
        })
    
    return users
```

### Step 3: Commit and Push

```powershell
git add src/api/users.py
git commit -m "Perf: Add pagination to get_all_users

- Added limit and offset parameters
- Prevents loading all users at once
- Improves scalability for large datasets"

git push -u origin perf/add-pagination
```

### Step 4: Create PR

Title: "Performance: Add pagination to user listing"

### Expected Results:
- ✅ **Performance Agent:** Should recognize the improvement
- ✅ **Quality Score:** Should improve slightly
- ✅ **Still flags:** N+1 query issue in get_user_posts
- ✅ **Status:** Pass

---

## Test 4: Architecture Issue Detection

**Goal:** Test architecture agent's pattern recognition.

### Step 1: Refactor to Strategy Pattern

```powershell
git checkout main
git pull
git checkout -b refactor/strategy-pattern
```

### Step 2: Create New File - Format Strategies

Create `src/utils/formatters.py`:

```python
"""
Format strategies for data transformation

Implements Strategy pattern to replace large if-else chain.
"""

from abc import ABC, abstractmethod
import json
from typing import Any


class DataFormatter(ABC):
    """Abstract formatter interface"""
    
    @abstractmethod
    def format(self, data: Any) -> str:
        """Format data to string"""
        pass


class JsonFormatter(DataFormatter):
    """JSON formatter"""
    
    def format(self, data: Any) -> str:
        return json.dumps(data)


class CsvFormatter(DataFormatter):
    """CSV formatter"""
    
    def format(self, data: Any) -> str:
        # Simplified implementation
        return "csv_data"


class XmlFormatter(DataFormatter):
    """XML formatter"""
    
    def format(self, data: Any) -> str:
        return "<data></data>"


class YamlFormatter(DataFormatter):
    """YAML formatter"""
    
    def format(self, data: Any) -> str:
        return "yaml_data"


class TextFormatter(DataFormatter):
    """Plain text formatter"""
    
    def format(self, data: Any) -> str:
        return str(data)


class FormatterFactory:
    """Factory for creating formatters"""
    
    _formatters = {
        'json': JsonFormatter,
        'csv': CsvFormatter,
        'xml': XmlFormatter,
        'yaml': YamlFormatter,
        'text': TextFormatter
    }
    
    @classmethod
    def get_formatter(cls, format_type: str) -> DataFormatter:
        """Get formatter for specified type"""
        formatter_class = cls._formatters.get(format_type, TextFormatter)
        return formatter_class()
```

### Step 3: Update DataProcessor

Open `src/utils/data_processor.py` and replace `transform_data` method:

**After:**
```python
from .formatters import FormatterFactory

def transform_data(self, data: Any, format: str) -> str:
    """
    Transform data to specified format using Strategy pattern
    
    Args:
        data: Data to transform
        format: Output format
        
    Returns:
        Transformed data as string
    """
    formatter = FormatterFactory.get_formatter(format)
    return formatter.format(data)
```

### Step 4: Commit and Push

```powershell
git add src/utils/formatters.py src/utils/data_processor.py
git commit -m "Refactor: Implement Strategy pattern for data transformation

- Created DataFormatter interface and implementations
- Replaced large if-else chain with strategy pattern
- Follows Open/Closed Principle (SOLID)
- Easier to extend with new formats"

git push -u origin refactor/strategy-pattern
```

### Step 5: Create PR

Title: "Refactor: Replace if-else chain with Strategy pattern"

### Expected Results:
- ✅ **Architecture Agent:** Should recognize the improvement
- ✅ **Quality Score:** Should improve (e.g., 78% → 85%)
- ✅ **Comments:** May praise SOLID principles
- ✅ **Status:** Pass

---

## Test 5: Clean Code (Positive Test)

**Goal:** Verify system recognizes good code.

### Step 1: Create Clean Feature

```powershell
git checkout main
git pull
git checkout -b feat/user-validation
```

### Step 2: Add Well-Written Validator

Create `src/utils/validators.py`:

```python
"""
User input validators

Provides secure and efficient validation for user data.
"""

import re
from typing import Tuple, Optional


class UserValidator:
    """Validates user input according to security best practices"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    PASSWORD_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
    )
    
    # Email validation
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > 254:
            return False, "Email is too long"
        
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength
        
        Requirements:
        - At least 12 characters
        - Contains uppercase and lowercase
        - Contains digits
        - Contains special characters
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letters"
        
        if not re.search(r'\d', password):
            return False, "Password must contain digits"
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain special characters"
        
        return True, None
    
    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        if not username.isalnum():
            return False, "Username must contain only letters and numbers"
        
        return True, None
```

### Step 3: Commit and Push

```powershell
git add src/utils/validators.py
git commit -m "Feat: Add comprehensive user input validation

- Implements strong password requirements (12+ chars, complexity)
- Email validation with RFC-compliant regex
- Username validation with length constraints
- Returns clear error messages
- Well-documented and tested patterns
- Follows security best practices"

git push -u origin feat/user-validation
```

### Step 4: Create PR

Title: "Feature: Add user input validators"

### Expected Results:
- ✅ **Quality Score:** High (90-95% / Grade A)
- ✅ **All Agents:** Minimal or no issues found
- ✅ **Comments:** Positive feedback on code quality
- ✅ **Status:** Pass
- ✅ **Recommendation:** "Approve - looks good"

---

## Test 6: Single vs Multi-Agent Comparison

**Goal:** Compare single agent vs multi-agent system.

### Option A: Local Comparison (Recommended for Thesis)

```powershell
cd C:\Users\andre\Desktop\Uni\Msc2\Diploma

# Activate virtual environment
.venv\Scripts\activate

# Run comparison script
python compare_single_vs_multi.py
```

This will:
1. Fetch PR #1 from tiangolo/fastapi
2. Run single agent analysis (~30s)
3. Run multi-agent analysis (~45s)
4. Generate comparison report
5. Save 3 JSON files:
   - `comparison_single_agent.json`
   - `comparison_multi_agent.json`
   - `comparison_results.json`

### Option B: GitHub Actions Comparison

1. In your demo-pr-review repo, edit `.github/workflows/pr-review.yml`
2. Find line with `run_review.py` command (around line 38)
3. Add `--compare` flag:
   ```yaml
   --output review_results.json \
   --compare
   ```
4. Commit and push this change
5. Next PR will run both single and multi-agent

### Expected Comparison Results:

**Metrics to observe:**
- **Findings:** Multi should find 20-50% more issues
- **Coverage:** Multi should cover all 3 categories better
- **Quality Score:** Similar, but multi may be stricter
- **Time:** Multi takes ~50% longer
- **Comprehensiveness:** Multi scores 10-20 points higher

---

## Data Collection for Thesis

### Phase 1: Create Diverse Test PRs (15-20 PRs)

Create PRs with different characteristics:

**Security PRs (5):**
1. Fix SQL injection ✅ (already done)
2. Fix XSS vulnerability
3. Add authentication
4. Fix insecure password storage
5. Add input sanitization

**Performance PRs (5):**
1. Add pagination ✅ (already done)
2. Fix N+1 queries
3. Add caching layer
4. Optimize algorithm (O(n²) → O(n log n))
5. Add database indexes

**Architecture PRs (5):**
1. Strategy pattern ✅ (already done)
2. Extract service layer
3. Apply dependency injection
4. Refactor god class
5. Remove code duplication

**Mixed/Regression PRs (5):**
1. Feature with bugs
2. Performance fix that breaks security
3. Clean refactoring
4. Breaking changes
5. Large feature with multiple issues

### Phase 2: Collect Data

For each PR, record:

```json
{
  "pr_number": 1,
  "pr_title": "Fix SQL injection",
  "pr_type": "security_fix",
  "lines_changed": 5,
  "files_changed": 1,
  
  "single_agent": {
    "quality_score": 75,
    "findings_count": 6,
    "execution_time": 28.5,
    "categories": {"security": 2, "performance": 2, "architecture": 2}
  },
  
  "multi_agent": {
    "quality_score": 78,
    "findings_count": 9,
    "execution_time": 45.2,
    "categories": {"security": 3, "performance": 2, "architecture": 4}
  },
  
  "comparison": {
    "findings_advantage": 3,
    "quality_difference": 3.0,
    "time_overhead": 16.7,
    "unique_multi_findings": ["n_plus_one", "solid_violation", "test_gap"]
  }
}
```

### Phase 3: Analyze Results

Run analysis on collected data:

```powershell
# Create analysis script
python analyze_thesis_data.py
```

Calculate:
- Average improvement metrics
- Statistical significance
- Category coverage comparison
- Cost-benefit analysis
- False positive/negative rates

### Phase 4: Document Findings

Create thesis tables and charts:

**Table 1: Overall Comparison**
| Metric | Single Agent | Multi-Agent | Improvement |
|--------|--------------|-------------|-------------|
| Avg Findings | 6.2 | 9.1 | +46.8% |
| Avg Quality | 76.3% | 78.9% | +3.4% |
| Category Coverage | 65% | 87% | +33.8% |
| Comprehensiveness | 68/100 | 82/100 | +20.6% |

**Chart 1:** Findings count per PR (bar chart)
**Chart 2:** Category coverage (radar chart)
**Chart 3:** Quality score distribution (histogram)

---

## Troubleshooting

### Workflow Not Running

**Check:**
1. Go to Actions tab - any errors?
2. Workflow file in `.github/workflows/`?
3. Actions enabled in Settings?
4. Permissions set to "Read and write"?

### No Comment Posted

**Check:**
1. Review the Actions logs (click on failed job)
2. API key correct? (OPENAI_API_KEY in secrets)
3. Workflow has `pull-requests: write` permission?

### Analysis Fails

**Common issues:**
1. **API key invalid:** Check secret value
2. **Rate limit:** Wait and retry
3. **Model not available:** Try different model
4. **Timeout:** Increase workflow timeout

### Review Seems Wrong

**Validate:**
1. Check the PR changes - are they clear?
2. Look at agent logs in Actions
3. Try running locally: `python main.py owner/repo --pr X`
4. Compare with manual review

---

## Success Checklist

✅ Demo repository created and pushed to GitHub  
✅ API key added as repository secret  
✅ Workflow permissions configured  
✅ Test PR #1 created and reviewed automatically  
✅ Security fix PR tested  
✅ Performance optimization PR tested  
✅ Architecture refactoring PR tested  
✅ Clean code PR tested  
✅ Single vs multi comparison completed  
✅ Data collected from 15+ diverse PRs  
✅ Comparison metrics documented  
✅ Results analyzed for thesis  

---

## Next Steps After Testing

1. **Write thesis chapter** with findings
2. **Create visualizations** of results
3. **Prepare defense demo** (live PR creation)
4. **Document limitations** encountered
5. **Suggest future improvements**

---

## Cost Tracking

Keep track of API costs:

**Per PR:**
- Multi-agent only: ~$0.10
- With comparison: ~$0.15

**For 20 test PRs:**
- Total: ~$2-3
- Very affordable for thesis!

**Production estimate (100 PRs/month):**
- Cost: ~$10-15/month
- Compare to: GitHub Copilot ($10/month), CodeClimate ($hundreds)

---

## Tips for Thesis

1. **Screenshot everything:** Capture PR comments, workflows, results
2. **Save all JSON outputs:** Evidence for methodology
3. **Document edge cases:** When system fails or succeeds unexpectedly
4. **Compare manually:** Verify some findings yourself
5. **Note surprises:** Multi-agent catching things you missed

Good luck with your testing! 🚀
