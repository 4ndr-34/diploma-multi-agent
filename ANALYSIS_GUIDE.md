# Comparative Analysis Guide

This guide explains how to analyze the multi-agent vs single-agent PR review results for your thesis.

## Overview

The analysis framework provides comparative evaluation **without requiring ground truth labels**, focusing on:

- **Consensus**: How often do both systems agree on findings?
- **Specificity**: How detailed and actionable are the findings?
- **Consistency**: How consistent are scores within PR categories?
- **Specialization**: Do specialized agents show domain expertise?
- **Quality Scores**: Overall comparison of assessment accuracy
- **Execution Time**: Performance overhead analysis

## Files

1. **`fetch_results.py`** - Downloads PR review results from GitHub
2. **`comparative_analysis.py`** - Performs comprehensive analysis
3. **`analysis_requirements.txt`** - Python dependencies

## Setup

### 1. Install Dependencies

```bash
pip install -r analysis_requirements.txt
```

### 2. Fetch Data from GitHub

Once all 20 PRs have been reviewed and results are saved to `data-collection-v2` branch:

```bash
python fetch_results.py
```

This will download all JSON files to `thesis_data/` directory.

**Optional arguments:**
```bash
python fetch_results.py --owner YOUR_USERNAME --repo YOUR_REPO --branch data-collection-v2
```

### 3. Run Analysis

```bash
python comparative_analysis.py
```

This will:
- Load all review results
- Calculate comparative metrics
- Generate visualizations
- Create LaTeX tables for thesis
- Save summary statistics

## Output Files

After running the analysis, you'll get:

### Visualizations (`analysis_output/`)

1. **`quality_scores_comparison.png`**
   - Line plot comparing scores across all PRs
   - Box plot showing distribution

2. **`category_performance.png`**
   - Bar chart comparing performance by PR category
   - Shows if one system excels in specific areas

3. **`findings_distribution.png`**
   - Scatter plot comparing number of findings
   - Identifies if one system is more thorough

4. **`execution_time.png`**
   - Bar chart comparing execution times
   - Shows performance overhead

### LaTeX Table (`comparison_table.tex`)

Ready-to-use table for your thesis:
- Quality scores (mean, median, std)
- Findings per PR
- Execution time
- Time overhead

### Raw Data (`analysis_summary.json`)

Complete metrics in JSON format for further analysis:
- Consensus rates per PR
- Specificity scores
- Consistency by category
- Specialization metrics
- All quality scores
- All execution times

## Analysis Metrics Explained

### 1. Consensus Analysis

**What it measures:** Agreement between multi-agent and single-agent

**Metrics:**
- Findings both found (consensus)
- Findings only multi-agent found
- Findings only single-agent found
- Consensus rate (%)

**Interpretation:**
- High consensus (>70%) = Both systems reliable
- Low consensus (<50%) = Systems see different issues
- One system finding more = May be more thorough OR finding false positives

### 2. Specificity Analysis

**What it measures:** Quality and actionability of findings

**Scoring criteria** (0-1 scale):
- Has file path? +0.2
- Has line number? +0.2
- Has code snippet? +0.2
- Has detailed recommendation (>50 chars)? +0.2
- Is critical/high severity? +0.2

**Interpretation:**
- Higher score = More actionable findings
- System with higher specificity provides better developer experience

### 3. Consistency Analysis

**What it measures:** Score stability within PR categories

**Metrics:**
- Standard deviation of scores per category
- Mean scores per category

**Interpretation:**
- Lower std = More consistent/predictable
- High std = May be overly sensitive to minor differences
- Compare consistency vs accuracy trade-off

### 4. Specialization Analysis

**What it measures:** Domain expertise of specialized agents

**Metrics:**
- % of findings from relevant specialized agent
- Example: Security agent finding security issues in security PRs

**Interpretation:**
- High relevance = Specialization works
- Low relevance = Agents may be redundant
- Only applies to multi-agent system

### 5. Quality Score Comparison

**What it measures:** Overall assessment accuracy

**Metrics:**
- Mean, median, std of quality scores
- Correlation between systems
- Per-category comparison

**Interpretation:**
- Similar means = Both systems calibrated similarly
- High correlation = Systems agree on overall quality
- Differences by category = Different strengths

### 6. Execution Time Comparison

**What it measures:** Performance overhead

**Metrics:**
- Average execution time
- Time overhead (%)

**Interpretation:**
- Shows cost of multi-agent coordination
- Helps assess if benefits justify overhead

## Using Results in Your Thesis

### For Discussion Section

1. **Consensus Analysis**: 
   - "The systems achieved X% consensus rate, indicating..."
   - Discuss what types of issues had high/low agreement

2. **Specialization**:
   - "Security agent found X% of security issues, demonstrating..."
   - Compare to baseline

3. **Quality vs Speed Trade-off**:
   - "Multi-agent showed X% overhead but Y% better specificity..."

### For Results Section

- Use the LaTeX table directly
- Include 2-3 key visualizations
- Report statistical significance if needed

### For Conclusions

- Which system would you recommend and when?
- What are the trade-offs?
- Future work suggestions

## Example Thesis Findings

Based on the metrics, you might conclude:

**Scenario A: Multi-Agent Wins**
- Higher specificity scores (0.85 vs 0.72)
- Better domain specialization (80%+ relevant findings)
- Acceptable overhead (20%)
- **Conclusion**: Multi-agent better for production use

**Scenario B: Single-Agent Wins**
- Similar quality scores (no significant difference)
- Much faster (50% less time)
- More consistent across categories
- **Conclusion**: Single-agent better for cost-sensitive environments

**Scenario C: Complementary**
- High consensus on critical issues (>80%)
- Each finds unique issues (30% unique per system)
- Different category strengths
- **Conclusion**: Hybrid approach recommended

## Customization

### Add Your Own Metrics

Edit `comparative_analysis.py` and add methods like:

```python
def custom_metric(self) -> Dict:
    """Your metric description"""
    # Your analysis logic
    return results
```

Then call it in `run_full_analysis()`.

### Adjust Visualizations

Modify the `_plot_*` methods in `comparative_analysis.py` to customize:
- Colors
- Labels
- Plot types
- Axes ranges

### Change PR Categories

Update the `pr_categories` dict in `ComparativeAnalyzer.__init__`:

```python
self.pr_categories = {
    'YourCategory': [PR_NUMBERS],
    # ...
}
```

## Troubleshooting

### No data found

**Problem:** `❌ No data found. Please ensure PR reviews are in thesis_data/`

**Solutions:**
1. Run `fetch_results.py` first
2. Check that PRs have been reviewed
3. Verify data-collection-v2 branch exists on GitHub
4. Check GitHub Actions workflow succeeded

### Branch not found

**Problem:** `❌ Error: Branch 'data-collection-v2' or directory 'pr_reviews' not found`

**Solutions:**
1. Ensure at least one PR has been reviewed successfully
2. Check workflow saved results to correct branch
3. Visit GitHub repo to verify branch exists

### Import errors

**Problem:** `ModuleNotFoundError: No module named 'numpy'`

**Solution:**
```bash
pip install -r analysis_requirements.txt
```

### Incomplete data

**Problem:** Some PRs missing single-agent comparison

**Solutions:**
1. Ensure `comparison_mode: true` in `.env`
2. Re-run affected PRs
3. Analysis will skip PRs without comparison data

## Advanced Usage

### Statistical Significance Testing

Add to your analysis:

```python
from scipy import stats

# T-test for quality scores
t_stat, p_value = stats.ttest_ind(multi_scores, single_scores)
print(f"T-test p-value: {p_value:.4f}")
```

### Per-Agent Breakdown

Analyze individual agent performance:

```python
for result in self.results:
    if 'agent_summaries' in result:
        for agent, summary in result['agent_summaries'].items():
            # Analyze each agent separately
```

### Time Series Analysis

If you have multiple runs over time:

```python
# Group by date
results_by_date = defaultdict(list)
for result in self.results:
    date = result['timestamp'].split('T')[0]
    results_by_date[date].append(result)
```

## Next Steps

After analysis:

1. ✅ Review all visualizations
2. ✅ Check statistical summaries
3. ✅ Identify key findings for thesis
4. ✅ Write discussion section
5. ✅ Consider additional experiments if needed

## Questions?

Common thesis questions answered by this analysis:

**Q: Which system is more accurate?**
A: Use consensus analysis + specificity scores

**Q: Is multi-agent worth the complexity?**
A: Compare specialization gains vs time overhead

**Q: When would you use each system?**
A: Analyze per-category performance

**Q: What are the limitations?**
A: Note: no ground truth, limited to 20 PRs, specific to this codebase

## Citation

If you use this analysis framework in your thesis:

```
Comparative evaluation methodology adapted from software engineering
best practices for assessing automated code review systems without
requiring manually labeled ground truth datasets.
```

---

Good luck with your thesis! 🎓
