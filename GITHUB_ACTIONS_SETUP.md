# GitHub Actions Setup Guide

## Overview

This guide shows you how to set up automated PR review using GitHub Actions and the multi-agent system.

## Architecture

```
┌─────────────┐
│   PR Open   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ GitHub Actions      │
│ Workflow Triggered  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Fetch PR Data       │
│ via GitHub API      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Run Multi-Agent     │
│ Analysis            │
│ (Security,          │
│  Performance,       │
│  Architecture)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Post Results as     │
│ PR Comment          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Set PR Status       │
│ (Pass/Fail)         │
└─────────────────────┘
```

## Setup Steps

### 1. Create Demo Project Repository

```bash
cd demo-project
git init
git add .
git commit -m "Initial commit: Demo project for multi-agent review"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/demo-pr-review.git
git push -u origin main
```

### 2. Add Repository Secrets

Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add:
- **Name:** `OPENAI_API_KEY`
- **Value:** Your OpenAI API key

(Note: `GITHUB_TOKEN` is automatically provided by GitHub Actions)

### 3. Enable GitHub Actions

1. Go to `Settings` → `Actions` → `General`
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Click "Save"

### 4. Push the Workflow

```bash
# Make sure .github/workflows/pr-review.yml is committed
git add .github/
git commit -m "Add PR review workflow"
git push
```

### 5. Create Your First PR

```bash
# Create a new branch
git checkout -b feature/add-validation

# Make some changes (e.g., fix a security issue)
# Edit demo-project/src/api/users.py

git add .
git commit -m "Add input validation"
git push -u origin feature/add-validation

# Create PR via GitHub UI
```

## Demo Project Structure

The demo project includes intentional issues:

### Security Issues
- **SQL Injection** in `src/api/users.py`
  - `get_user_by_id()` - String interpolation in SQL
  - `search_users()` - Unparameterized query
- **Plain text passwords** in `create_user()`
- **Weak validation** in `models/user.py`

### Performance Issues
- **N+1 Query** in `get_user_posts()`
- **No pagination** in `get_all_users()`
- **O(n²) algorithm** in `data_processor.py`

### Architecture Issues
- **Large if-else chain** in `transform_data()` (should use strategy pattern)
- **Code duplication** in `merge_data()`
- **Business logic in model** (`send_welcome_email()`)

## Creating Test PRs

### PR 1: Fix Security Issue

```bash
git checkout -b fix/sql-injection

# Edit src/api/users.py - Fix SQL injection
# Change line 30 from:
# query = f"SELECT * FROM users WHERE id = {user_id}"
# To:
# query = "SELECT * FROM users WHERE id = ?"
# cursor.execute(query, (user_id,))

git commit -am "Fix SQL injection in get_user_by_id"
git push origin fix/sql-injection
```

**Expected Review:**
- ✅ Security agent: Approves fix
- Quality score improvement
- Positive recommendation

### PR 2: Add Performance Optimization

```bash
git checkout -b feat/add-pagination

# Add pagination to get_all_users()
git commit -am "Add pagination to user listing"
git push origin feat/add-pagination
```

**Expected Review:**
- ✅ Performance agent: Highlights improvement
- May still flag other issues
- Better quality score

### PR 3: Refactor Architecture

```bash
git checkout -b refactor/strategy-pattern

# Refactor transform_data() to use strategy pattern
git commit -am "Implement strategy pattern for data transformation"
git push origin refactor/strategy-pattern
```

**Expected Review:**
- ✅ Architecture agent: Approves refactoring
- Improved maintainability score
- Positive consensus

### PR 4: Introduce New Bug

```bash
git checkout -b bug/broken-feature

# Add code with issues
git commit -am "Add feature (with bugs)"
git push origin bug/broken-feature
```

**Expected Review:**
- ❌ Multiple agents flag issues
- Low quality score (< 70%)
- Recommendation to request changes

## Workflow Configuration

### Basic Workflow (`.github/workflows/pr-review.yml`)

```yaml
name: Multi-Agent PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Run Review
        # ... (see full file)
```

### Advanced Options

**1. Compare Single vs Multi-Agent:**

Edit `.github/scripts/run_review.py`:

```python
# Run both analyses
single_report = single_agent.analyze(pr_data)
multi_report = orchestrator.analyze_pr(pr_data)

# Add comparison to results
results['comparison'] = compare_results(single_report, multi_report)
```

**2. Use Advanced Scoring:**

```python
orchestrator = MultiAgentOrchestrator(
    llm_client=llm_client,
    model=args.model,
    parallel=True,
    use_advanced_scoring=True,
    scoring_preset='security_critical'  # For security-focused projects
)
```

**3. Customize Quality Threshold:**

Edit workflow step "Set PR Status":

```yaml
if (results.quality_score < 80) {  # Stricter threshold
  state = 'failure';
}
```

**4. Add Cost Tracking:**

```python
# In run_review.py
results['cost_estimate'] = estimate_cost(
    model=args.model,
    agents=3,
    avg_response_tokens=500
)
```

## Example PR Review Comment

```markdown
## 🤖 Multi-Agent PR Review

### Overall Assessment

- **Quality Score:** 75% (Grade: C)
- **Risk Level:** MEDIUM
- **Recommendation:** Approve with minor comments
- **Total Findings:** 9

⚠️ **0 CRITICAL** issues found!

### Findings by Category

**Security:** Found 3 input validation issues that should be addressed

**Performance:** Identified 2 optimization opportunities for database queries

**Architecture:** Detected 4 code quality improvements to enhance maintainability

### Top Priority Issues

1. **[HIGH]** sql_injection
   - File: `src/api/users.py`
   - SQL injection vulnerability in search function
   - **Action:** Should fix before merge

2. **[MEDIUM]** n_plus_one_query
   - File: `src/api/users.py`
   - N+1 query pattern in get_user_posts
   - **Action:** Fix soon, can merge with tracking issue

3. **[MEDIUM]** code_smell
   - File: `src/utils/data_processor.py`
   - Large if-else chain violates Open/Closed principle
   - **Action:** Fix soon, can merge with tracking issue

---
*Analysis completed in 32.5s*
*Agent consensus: majority_agreement*
```

## Troubleshooting

### Workflow Not Running

**Problem:** Workflow doesn't trigger on PR creation

**Solutions:**
1. Check workflow file is in `.github/workflows/`
2. Verify file extension is `.yml` or `.yaml`
3. Check workflow permissions in Settings
4. Look at Actions tab for errors

### Authentication Failed

**Problem:** `Error: API key not found`

**Solutions:**
1. Verify `OPENAI_API_KEY` secret exists
2. Check secret name matches exactly (case-sensitive)
3. Re-save the secret if needed

### PR Comment Not Posted

**Problem:** Analysis runs but no comment appears

**Solutions:**
1. Check workflow permissions (need `pull-requests: write`)
2. Verify GITHUB_TOKEN has correct permissions
3. Check Actions logs for errors in "Post Review Comment" step

### Analysis Takes Too Long

**Problem:** Workflow times out

**Solutions:**
1. Increase timeout in workflow:
   ```yaml
   jobs:
     review:
       timeout-minutes: 15  # Default is 360
   ```
2. Use lighter model (gpt-3.5-turbo instead of gpt-4)
3. Enable parallel agent execution (default)

### High API Costs

**Problem:** Many PRs = expensive

**Solutions:**
1. Limit workflow to specific branches:
   ```yaml
   on:
     pull_request:
       branches: [main, develop]
   ```
2. Only run on specific labels:
   ```yaml
   on:
     pull_request:
       types: [labeled]
   # Then add "needs-review" label manually
   ```
3. Use cheaper model for demo
4. Add caching for unchanged files

## Best Practices

### 1. Branch Protection Rules

Set up branch protection:
- `Settings` → `Branches` → `Add rule`
- Branch name pattern: `main`
- Require status checks: "Multi-Agent Review"

### 2. PR Templates

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Refactoring

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have tested my changes
- [ ] I have updated documentation

## Multi-Agent Review
The automated review will check for:
- Security vulnerabilities
- Performance issues
- Architecture concerns
- Code quality
```

### 3. Cost Management

Monitor API costs:
```bash
# Track costs per PR
echo "PR #${{ github.event.pull_request.number }}: ~$0.10" >> costs.log
```

### 4. Quality Gates

Enforce quality standards:
```yaml
- name: Check Quality
  if: steps.review.outputs.quality_score < 70
  run: |
    echo "Quality score too low!"
    exit 1
```

## Integration with Existing Projects

To add to your real project:

1. **Copy workflow:**
   ```bash
   cp demo-project/.github/workflows/pr-review.yml your-project/.github/workflows/
   ```

2. **Copy review script:**
   ```bash
   cp .github/scripts/run_review.py your-project/.github/scripts/
   ```

3. **Adjust for your stack:**
   - Update file patterns to ignore
   - Customize quality thresholds
   - Adjust weight profiles

4. **Add to requirements.txt:**
   ```
   PyGithub==1.59.0
   litellm==1.0.0
   python-dotenv==1.0.0
   ```

## Thesis Demonstration

Use this setup to:

1. **Demonstrate real-world deployment**
   - Show working GitHub integration
   - Automated PR reviews

2. **Collect evaluation data**
   - Run on 20-30 PRs
   - Compare quality scores
   - Analyze findings

3. **Show multi-agent advantage**
   - Compare with single-agent results
   - Demonstrate specialized detection
   - Show conflict resolution

4. **Present at defense**
   - Live demo of PR creation
   - Show automated review
   - Discuss practical deployment

## Example Defense Scenario

```
Examiner: "How would this work in practice?"

You: "Let me show you..."
[Create PR with SQL injection]
[Wait 30 seconds]
[Show PR comment with review results]
[Point out security agent caught the issue]
```

## Cost Estimate

Per PR review (GPT-3.5-turbo):
- Single agent: ~$0.02-0.05
- Multi-agent: ~$0.05-0.15
- With advanced scoring: ~$0.05-0.15

For 100 PRs/month:
- Single: ~$2-5
- Multi: ~$5-15

Very affordable for demonstration and thesis evaluation!

## Next Steps

1. Set up demo repository
2. Create 5-10 test PRs with different issues
3. Collect review results
4. Analyze metrics
5. Compare with single-agent baseline
6. Document findings for thesis

## Support

For issues:
1. Check Actions logs in GitHub
2. Review run_review.py output
3. Test locally first: `python run_review.py --repo owner/repo --pr 1 --output test.json`
