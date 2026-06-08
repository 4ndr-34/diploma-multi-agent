# Enable Single vs Multi-Agent Comparison in GitHub Actions

## Overview

By default, the GitHub Actions workflow only runs the **multi-agent** system. This guide shows how to enable **comparison mode** to run both single and multi-agent on every PR.

## What Changes

**Default mode:**
- Runs multi-agent only
- Fast (~60 seconds)
- Cost: ~$0.10/PR

**Comparison mode:**
- Runs BOTH single + multi-agent
- Slower (~90 seconds)
- Cost: ~$0.15/PR
- Shows side-by-side comparison in PR comment

## Step 1: Update Workflow File

In your **demo-pr-review** repository, edit `.github/workflows/pr-review.yml`:

Find this section (around line 38):
```yaml
run: |
  python .github/scripts/run_review.py \
    --repo ${{ github.repository }} \
    --pr ${{ github.event.pull_request.number }} \
    --output review_results.json
```

Add `--compare` flag:
```yaml
run: |
  python .github/scripts/run_review.py \
    --repo ${{ github.repository }} \
    --pr ${{ github.event.pull_request.number }} \
    --output review_results.json \
    --compare  # ← Add this line
```

## Step 2: Update Comment Posting

In the same workflow file, find the "Post Review Comment" step (around line 60).

After the priority issues section, add this before the `---`:

```javascript
// Add comparison section if available
if (results.comparison) {
  const comp = results.comparison;
  comment += `### 📊 Single-Agent vs Multi-Agent Comparison\n\n`;
  comment += `| Metric | Single Agent | Multi-Agent | Difference |\n`;
  comment += `|--------|--------------|-------------|------------|\n`;
  comment += `| Quality Score | ${comp.single_agent.quality_score}% (${comp.single_agent.quality_grade}) | ${comp.multi_agent.quality_score}% (${comp.multi_agent.quality_grade}) | ${comp.advantage.quality_difference > 0 ? '+' : ''}${comp.advantage.quality_difference.toFixed(1)} |\n`;
  comment += `| Findings | ${comp.single_agent.findings_count} | ${comp.multi_agent.findings_count} | +${comp.advantage.more_findings} |\n`;
  comment += `| Time | ${comp.single_agent.execution_time.toFixed(1)}s | ${comp.multi_agent.execution_time.toFixed(1)}s | +${comp.advantage.time_overhead.toFixed(1)}s |\n\n`;
  
  if (comp.advantage.more_findings > 0) {
    comment += `✅ Multi-agent found **${comp.advantage.more_findings} more issues** than single agent\n\n`;
  }
}
```

## Step 3: Commit and Push

```bash
git add .github/workflows/pr-review.yml
git commit -m "Enable single vs multi-agent comparison"
git push
```

## Expected PR Comment Output

With comparison enabled, PR comments will look like this:

```markdown
## 🤖 Multi-Agent PR Review

### Overall Assessment
- **Quality Score:** 78% (Grade: C+)
- **Risk Level:** MEDIUM
- **Total Findings:** 9

### Findings by Category
**Security:** Found 3 input validation issues
**Performance:** Identified 2 optimization opportunities  
**Architecture:** Detected 4 code quality improvements

### Top Priority Issues
1. **[HIGH]** sql_injection in src/api/users.py
   - **Action:** Should fix before merge

### 📊 Single-Agent vs Multi-Agent Comparison

| Metric | Single Agent | Multi-Agent | Difference |
|--------|--------------|-------------|------------|
| Quality Score | 75% (C) | 78% (C+) | +3.0 |
| Findings | 6 | 9 | +3 |
| Time | 28.5s | 45.2s | +16.7s |

✅ Multi-agent found **3 more issues** than single agent

---
*Analysis completed in 45.2s*
*Agent consensus: majority_agreement*
*Comparison mode: Single vs Multi-agent*
```

## Option: Comparison Only on Specific Label

If you want comparison only for certain PRs, modify the workflow trigger:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled]

jobs:
  review:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'full-review')
    # ... rest of workflow
```

Then add `--compare` flag conditionally:

```yaml
run: |
  python .github/scripts/run_review.py \
    --repo ${{ github.repository }} \
    --pr ${{ github.event.pull_request.number }} \
    --output review_results.json \
    ${{ contains(github.event.pull_request.labels.*.name, 'compare') && '--compare' || '' }}
```

This way:
- Normal PRs: Multi-agent only
- PRs with "compare" label: Both single + multi

## Alternative: Run Comparison Locally

Instead of on every PR, you can run comparisons locally for thesis evaluation:

```bash
cd C:\Users\andre\Desktop\Uni\Msc2\Diploma

# Activate venv
.venv\Scripts\activate

# Run comparison on specific PR
python compare_single_vs_multi.py

# This will:
# - Fetch PR data
# - Run both single and multi-agent
# - Generate detailed comparison report
# - Save to comparison_results.json
```

This is better for:
- Thesis data collection
- Detailed analysis
- Cost control (only run when needed)
- Multiple model comparisons

## Recommendation for Thesis 🎓

### For Demonstrations (Live demos, defense):
✅ Enable `--compare` in GitHub Actions
- Shows both approaches live
- Impressive during presentation
- Clear visual comparison

### For Evaluation (Data collection):
✅ Use `compare_single_vs_multi.py` locally
- More control
- Cheaper (run on demand)
- Can test different models
- Detailed comparison data
- Run on 20-30 diverse PRs

### Best of Both:
1. **Keep GitHub Actions simple** (multi-agent only)
2. **For thesis evaluation PRs**, add "compare" label
3. **Collect detailed data** using local script

## Cost Comparison

**Multi-agent only:**
- Cost per PR: ~$0.10
- 30 PRs: ~$3.00

**With comparison (both on every PR):**
- Cost per PR: ~$0.15
- 30 PRs: ~$4.50

**Selective comparison (10 PRs with label):**
- 20 normal: $2.00
- 10 comparison: $1.50
- Total: ~$3.50

## Files Modified

All changes are in your **main diploma repo** (`diploma-multi-agent`):
- ✅ `.github/scripts/run_review.py` - Already updated (added --compare support)
- 📝 Need to update in demo repo: `.github/workflows/pr-review.yml`

The updates to `run_review.py` are already done in your main repo, so they'll be pulled automatically by the demo workflow!

## Summary

**To enable comparison:**
1. Add `--compare` to workflow in demo-pr-review repo
2. Add comparison table to comment section
3. Push changes
4. Next PR will show both results!

**For thesis:**
- Use GitHub Actions for live demos
- Use local script for detailed evaluation
- Best of both worlds! 🎉
