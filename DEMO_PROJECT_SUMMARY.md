# Demo Project with GitHub Actions - Complete Setup

## 🎯 What Was Created

A complete **dummy project** with **automated PR review** using GitHub Actions and your multi-agent system.

## 📁 Project Structure

```
demo-project/
├── README.md                         # Project overview
├── CONTRIBUTING.md                   # Contribution guidelines
├── requirements.txt                  # Python dependencies
├── setup_demo.sh                     # Linux/Mac setup script
├── setup_demo.ps1                    # Windows setup script
│
├── .github/
│   ├── workflows/
│   │   └── pr-review.yml            # GitHub Actions workflow
│   └── PULL_REQUEST_TEMPLATE.md     # PR template
│
├── src/
│   ├── api/
│   │   └── users.py                 # User API (with security issues)
│   ├── models/
│   │   └── user.py                  # User model (with arch issues)
│   └── utils/
│       └── data_processor.py        # Data utils (with perf issues)
│
└── .github/scripts/
    └── run_review.py                # Review runner script
```

## 🐛 Intentional Issues in Demo Code

### Security Issues (`src/api/users.py`):
1. **SQL Injection** (Line 30): `query = f"SELECT * FROM users WHERE id = {user_id}"`
2. **SQL Injection** (Line 56): Unparameterized query in `search_users()`
3. **Plain text password** (Line 97): Storing passwords without hashing
4. **No input validation** (Line 85): Missing validation in `create_user()`

### Performance Issues:
1. **N+1 Query** (`users.py:114`): Fetching comments individually in loop
2. **No pagination** (`users.py:43`): Loading all users at once
3. **O(n²) algorithm** (`data_processor.py:22`): Inefficient nested loops

### Architecture Issues:
1. **Large if-else chain** (`data_processor.py:38`): Should use strategy pattern
2. **Code duplication** (`data_processor.py:65`): Repeated merge logic
3. **Business logic in model** (`user.py:33`): `send_welcome_email()` in model class
4. **Weak validation** (`user.py:39`): Password length only

## 🚀 Quick Start

### 1. Setup Demo Repository

```powershell
# Windows
cd demo-project
.\setup_demo.ps1

# Linux/Mac
cd demo-project
chmod +x setup_demo.sh
./setup_demo.sh
```

### 2. Create GitHub Repository

**Option A: Using GitHub CLI**
```bash
cd demo-project
gh repo create demo-pr-review --public --source=. --remote=origin --push
```

**Option B: Manual**
1. Go to https://github.com/new
2. Repository name: `demo-pr-review`
3. Public
4. Don't initialize with README
5. Create repository
6. Follow push instructions:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/demo-pr-review.git
   git branch -M main
   git push -u origin main
   ```

### 3. Add API Key Secret

1. Go to repository Settings
2. Secrets and variables → Actions
3. New repository secret:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-...` (your key)

### 4. Enable Workflow Permissions

1. Settings → Actions → General
2. Workflow permissions:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests
3. Save

### 5. Create Test PR

```bash
# Fix SQL injection issue
git checkout -b fix/sql-injection

# Edit src/api/users.py line 30-31:
# FROM: query = f"SELECT * FROM users WHERE id = {user_id}"
#       cursor.execute(query)
# TO:   query = "SELECT * FROM users WHERE id = ?"
#       cursor.execute(query, (user_id,))

git add src/api/users.py
git commit -m "Fix: SQL injection vulnerability in get_user_by_id"
git push -u origin fix/sql-injection
```

6. Go to GitHub and create Pull Request
7. Wait ~60 seconds
8. See automated review comment! 🎉

## 📊 Expected Review Output

```markdown
## 🤖 Multi-Agent PR Review

### Overall Assessment

- **Quality Score:** 78.5% (Grade: C+)
- **Risk Level:** MEDIUM
- **Recommendation:** Approve with minor comments
- **Total Findings:** 7

### Findings by Category

**Security:** Found 2 remaining input validation issues
**Performance:** Identified 2 optimization opportunities
**Architecture:** Detected 3 code quality improvements

### Top Priority Issues

1. **[HIGH]** sql_injection
   - File: `src/api/users.py`
   - SQL injection in search_users function (line 56)
   - **Action:** Should fix before merge

2. **[MEDIUM]** n_plus_one_query
   - File: `src/api/users.py`
   - N+1 query pattern in get_user_posts
   - **Action:** Fix soon, can merge with tracking issue

---
*Analysis completed in 32.5s*
*Agent consensus: majority_agreement*
```

## 🧪 Test Scenarios

### Scenario 1: Fix Security Issue (Expected: Positive Review)
```bash
git checkout -b fix/sql-injection
# Fix SQL injection in get_user_by_id
git commit -am "Fix SQL injection"
git push origin fix/sql-injection
```

**Expected:**
- ✅ Security agent approves fix
- Quality score: 75% → 82%
- Remaining issues: 6

### Scenario 2: Add Performance Optimization (Expected: Partial Approval)
```bash
git checkout -b perf/add-pagination
# Add pagination to get_all_users
git commit -am "Add pagination to user listing"
git push origin perf/add-pagination
```

**Expected:**
- ✅ Performance agent highlights improvement
- Still flags other perf issues
- Quality score: 75% → 78%

### Scenario 3: Introduce New Bug (Expected: Failure)
```bash
git checkout -b bug/new-vulnerability
# Add code with XSS vulnerability
git commit -am "Add search feature (with XSS bug)"
git push origin bug/new-vulnerability
```

**Expected:**
- ❌ Security agent flags XSS
- Quality score: 75% → 65%
- Workflow fails (< 70% threshold)

### Scenario 4: Clean PR (Expected: Full Approval)
```bash
git checkout -b fix/all-issues
# Fix all security, performance, and architecture issues
git commit -am "Fix all identified issues"
git push origin fix/all-issues
```

**Expected:**
- ✅ All agents approve
- Quality score: 75% → 92%
- Grade: C → A-

## 🔧 Customization

### Change Quality Threshold

Edit `.github/workflows/pr-review.yml` line 85:

```javascript
if (results.quality_score < 80) {  // Change from 70 to 80
  state = 'failure';
}
```

### Use Different Model

Edit `.github/scripts/run_review.py` line 31:

```python
parser.add_argument('--model', default='gpt-4', help='LLM model')  # Use GPT-4
```

### Enable Advanced Scoring

Edit `.github/scripts/run_review.py` line 52:

```python
orchestrator = MultiAgentOrchestrator(
    llm_client=llm_client,
    model=args.model,
    parallel=True,
    use_advanced_scoring=True,           # Enable
    scoring_preset='security_critical'   # Use preset
)
```

### Add Comparison with Single Agent

Edit `.github/scripts/run_review.py` after line 50:

```python
# Also run single agent
from agents import SingleAgent
single_agent = SingleAgent(llm_client=llm_client, model=args.model)
single_report = single_agent.analyze(pr_data)

# Add comparison to results
results['comparison'] = {
    'single_findings': len(single_report.findings),
    'multi_findings': len(report.all_findings),
    'advantage': len(report.all_findings) - len(single_report.findings)
}
```

## 📈 For Your Thesis

### Data Collection

1. **Create 20 diverse PRs:**
   - 5 security fixes
   - 5 performance improvements
   - 5 architecture refactorings
   - 5 bug introductions

2. **Collect metrics:**
   - Quality scores
   - Findings count
   - Category coverage
   - Execution time
   - Review accuracy

3. **Compare approaches:**
   - Multi-agent vs single-agent
   - Different weight profiles
   - Model variations (GPT-3.5 vs GPT-4)

### Demonstration

**During thesis defense:**

1. Show live repository
2. Create PR with known issue
3. Wait for automated review
4. Explain results
5. Show how agents collaborated
6. Discuss findings

**Key talking points:**
- "Here's a real deployment scenario"
- "The system caught X issues automatically"
- "Security agent specialized in finding Y"
- "This runs on every PR, providing continuous quality checks"

## 💰 Cost Estimates

**Per PR review (GPT-3.5-turbo):**
- Multi-agent: ~$0.10
- With advanced scoring: ~$0.12

**For thesis evaluation (30 PRs):**
- Total cost: ~$3-4
- Very affordable!

**For production use (100 PRs/month):**
- Monthly cost: ~$10-15
- Comparable to code review tools

## 🎓 Academic Value

This demo provides:

1. **Real-world deployment** - Not just a prototype
2. **Reproducible results** - Anyone can fork and test
3. **Practical validation** - Shows system works in practice
4. **Cost analysis** - Demonstrates feasibility
5. **Scalability proof** - CI/CD integration
6. **User experience** - Actual PR review workflow

## 📚 Documentation

- **`GITHUB_ACTIONS_SETUP.md`** - Complete setup guide
- **`COMPARISON_GUIDE.md`** - Single vs multi-agent comparison
- **`demo-project/README.md`** - Project overview
- **`demo-project/CONTRIBUTING.md`** - How to contribute test PRs

## ✅ Success Criteria

Your demo is working when:

1. ✅ PR creation triggers workflow
2. ✅ Analysis completes within 60s
3. ✅ Review comment appears on PR
4. ✅ Quality score is calculated
5. ✅ All 3 agents contribute findings
6. ✅ PR status is set (pass/fail)

## 🐛 Troubleshooting

**Workflow not running?**
- Check `.github/workflows/` path
- Verify Actions are enabled
- Check workflow permissions

**No comment posted?**
- Verify `GITHUB_TOKEN` permissions
- Check Actions logs
- Ensure workflow has `pull-requests: write`

**Analysis fails?**
- Check `OPENAI_API_KEY` secret
- Verify API key is valid
- Check rate limits

## 🎉 You're Ready!

You now have a complete demo project that:
- ✅ Automatically reviews PRs
- ✅ Uses your multi-agent system
- ✅ Posts results as comments
- ✅ Demonstrates thesis hypothesis
- ✅ Ready for evaluation and demonstration

Good luck with your thesis! 🚀
