#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-Agent vs Multi-Agent Comparison

Compares the performance of a single powerful agent against
the multi-agent collaborative system.

This is the core evaluation for the thesis hypothesis.
"""

import json
import logging
import sys
from dotenv import load_dotenv
from typing import Dict, Any, List

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator
from agents import MultiAgentOrchestrator
from agents.single_agent import SingleAgent

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def compare_coverage(single_findings: List, multi_findings: List) -> Dict[str, Any]:
    """
    Compare coverage of different categories
    
    Args:
        single_findings: Findings from single agent
        multi_findings: Findings from multi-agent system
        
    Returns:
        Coverage comparison metrics
    """
    def categorize_findings(findings):
        categories = {'security': 0, 'performance': 0, 'architecture': 0, 'other': 0}
        for f in findings:
            if hasattr(f, 'context'):
                cat = f.context.get('category') or f.context.get('agent', 'other')
            else:
                cat = f.get('agent', 'other')
            
            if cat in categories:
                categories[cat] += 1
            else:
                categories['other'] += 1
        return categories
    
    single_cats = categorize_findings(single_findings)
    multi_cats = categorize_findings(multi_findings)
    
    return {
        'single_agent': single_cats,
        'multi_agent': multi_cats,
        'coverage_difference': {
            cat: multi_cats.get(cat, 0) - single_cats.get(cat, 0)
            for cat in set(list(single_cats.keys()) + list(multi_cats.keys()))
        }
    }


def compare_severity_distribution(single_findings: List, multi_findings: List) -> Dict[str, Any]:
    """Compare severity distribution"""
    def count_severity(findings):
        severity_count = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for f in findings:
            if hasattr(f, 'severity'):
                sev = f.severity.value
            else:
                sev = f.get('severity', 'medium')
            severity_count[sev] = severity_count.get(sev, 0) + 1
        return severity_count
    
    single_sev = count_severity(single_findings)
    multi_sev = count_severity(multi_findings)
    
    return {
        'single_agent': single_sev,
        'multi_agent': multi_sev,
        'difference': {
            sev: multi_sev.get(sev, 0) - single_sev.get(sev, 0)
            for sev in ['critical', 'high', 'medium', 'low', 'info']
        }
    }


def analyze_unique_findings(single_findings: List, multi_findings: List) -> Dict[str, Any]:
    """
    Analyze which findings are unique to each approach
    
    Args:
        single_findings: Single agent findings
        multi_findings: Multi-agent findings
        
    Returns:
        Analysis of unique vs shared findings
    """
    def get_signature(finding):
        """Create a signature for finding comparison"""
        if hasattr(finding, 'type'):
            return (finding.type, finding.file, finding.severity.value)
        else:
            return (finding.get('type'), finding.get('file'), finding.get('severity'))
    
    single_sigs = set(get_signature(f) for f in single_findings)
    multi_sigs = set(get_signature(f) for f in multi_findings)
    
    only_single = len(single_sigs - multi_sigs)
    only_multi = len(multi_sigs - single_sigs)
    shared = len(single_sigs & multi_sigs)
    
    return {
        'only_single_agent': only_single,
        'only_multi_agent': only_multi,
        'shared_findings': shared,
        'single_total': len(single_findings),
        'multi_total': len(multi_findings),
        'overlap_percentage': round((shared / max(len(single_findings), 1)) * 100, 1)
    }


def calculate_comprehensiveness_score(findings: List, categories: Dict[str, int]) -> float:
    """
    Calculate how comprehensive the review is
    
    Factors:
    - Coverage of all categories (security, performance, architecture)
    - Number of findings
    - Severity distribution
    
    Returns:
        Comprehensiveness score (0-100)
    """
    score = 0.0
    
    # Category coverage (30 points)
    categories_covered = sum(1 for count in categories.values() if count > 0)
    score += (categories_covered / 4) * 30  # Assuming 4 categories
    
    # Depth of analysis (40 points) - more findings = more thorough
    # But with diminishing returns
    finding_count = len(findings)
    if finding_count >= 15:
        score += 40
    elif finding_count >= 10:
        score += 30
    elif finding_count >= 5:
        score += 20
    else:
        score += finding_count * 3
    
    # Balance across categories (30 points)
    if categories_covered > 0:
        counts = [c for c in categories.values() if c > 0]
        avg_count = sum(counts) / len(counts)
        variance = sum((c - avg_count) ** 2 for c in counts) / len(counts)
        # Lower variance = better balance
        balance_score = max(0, 30 - (variance * 2))
        score += balance_score
    
    return min(100, score)


def main():
    print("=" * 80)
    print("SINGLE-AGENT vs MULTI-AGENT COMPARISON")
    print("=" * 80)
    print()
    
    # Configuration
    repo = "tiangolo/fastapi"
    pr_number = 1
    single_model = "gpt-3.5-turbo"  # Can use gpt-4 for stronger baseline
    multi_model = "gpt-3.5-turbo"
    
    print(f"Configuration:")
    print(f"  Repository: {repo}")
    print(f"  PR Number: {pr_number}")
    print(f"  Single Agent Model: {single_model}")
    print(f"  Multi-Agent Model: {multi_model}")
    print()
    
    # Fetch PR
    print("-" * 80)
    print("STEP 1: Fetching PR Data")
    print("-" * 80)
    
    crawler = PRCrawler()
    pr_data = crawler.crawl_pr(repo, pr_number)
    
    if not pr_data:
        print("Failed to fetch PR")
        return False
    
    print(f"✓ PR fetched: {pr_data['title']}")
    print(f"  Files changed: {len(pr_data['files'])}")
    print()
    
    # Run Single Agent
    print("=" * 80)
    print("TEST 1: SINGLE AGENT ANALYSIS")
    print("=" * 80)
    print()
    
    llm_client_single = LLMIntegrator(model=single_model)
    single_agent = SingleAgent(llm_client=llm_client_single, model=single_model)
    
    print(f"Running single {single_model} agent...")
    print("(This will take 20-40 seconds)")
    print()
    
    single_report = single_agent.analyze(pr_data)
    
    print("Single Agent Results:")
    print(f"  Quality Score: {single_report.quality_score}% (Grade: {single_report.quality_grade})")
    print(f"  Risk Level: {single_report.risk_level.upper()}")
    print(f"  Total Findings: {len(single_report.findings)}")
    print(f"  Confidence: {single_report.confidence:.2f}")
    print(f"  Execution Time: {single_report.execution_time:.2f}s")
    print()
    
    # Run Multi-Agent
    print("=" * 80)
    print("TEST 2: MULTI-AGENT ANALYSIS")
    print("=" * 80)
    print()
    
    llm_client_multi = LLMIntegrator(model=multi_model)
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client_multi,
        model=multi_model,
        parallel=True,
        use_advanced_scoring=False  # Use same scoring as single agent
    )
    
    print(f"Running multi-agent system (3 specialized agents)...")
    print("(This will take 30-60 seconds)")
    print()
    
    multi_report = orchestrator.analyze_pr(pr_data)
    
    print("Multi-Agent Results:")
    print(f"  Quality Score: {multi_report.overall_assessment['quality_score']}% (Grade: {multi_report.overall_assessment['quality_grade']})")
    print(f"  Risk Level: {multi_report.overall_assessment['risk_level'].upper()}")
    print(f"  Total Findings: {len(multi_report.all_findings)}")
    print(f"  Confidence: {multi_report.overall_assessment['confidence']:.2f}")
    print(f"  Execution Time: {multi_report.execution_time:.2f}s")
    print(f"  Agent Consensus: {multi_report.overall_assessment['agents_consensus']}")
    print()
    
    # Compare Results
    print("=" * 80)
    print("COMPARISON ANALYSIS")
    print("=" * 80)
    print()
    
    # Coverage comparison
    coverage = compare_coverage(single_report.findings, multi_report.all_findings)
    print("Category Coverage:")
    print(f"  Single Agent: {coverage['single_agent']}")
    print(f"  Multi-Agent:  {coverage['multi_agent']}")
    print(f"  Difference:   {coverage['coverage_difference']}")
    print()
    
    # Severity distribution
    severity_comp = compare_severity_distribution(single_report.findings, multi_report.all_findings)
    print("Severity Distribution:")
    print(f"  Single Agent: {severity_comp['single_agent']}")
    print(f"  Multi-Agent:  {severity_comp['multi_agent']}")
    print(f"  Difference:   {severity_comp['difference']}")
    print()
    
    # Unique findings
    unique_analysis = analyze_unique_findings(single_report.findings, multi_report.all_findings)
    print("Finding Overlap Analysis:")
    print(f"  Only found by single agent: {unique_analysis['only_single_agent']}")
    print(f"  Only found by multi-agent:  {unique_analysis['only_multi_agent']}")
    print(f"  Found by both:              {unique_analysis['shared_findings']}")
    print(f"  Overlap:                    {unique_analysis['overlap_percentage']}%")
    print()
    
    # Comprehensiveness
    single_comprehensive = calculate_comprehensiveness_score(
        single_report.findings,
        coverage['single_agent']
    )
    multi_comprehensive = calculate_comprehensiveness_score(
        multi_report.all_findings,
        coverage['multi_agent']
    )
    
    print("Comprehensiveness Score:")
    print(f"  Single Agent: {single_comprehensive:.1f}/100")
    print(f"  Multi-Agent:  {multi_comprehensive:.1f}/100")
    print(f"  Difference:   +{multi_comprehensive - single_comprehensive:.1f}")
    print()
    
    # Performance comparison
    print("Performance Metrics:")
    print(f"  Single Agent Time: {single_report.execution_time:.2f}s")
    print(f"  Multi-Agent Time:  {multi_report.execution_time:.2f}s")
    print(f"  Time Overhead:     {multi_report.execution_time - single_report.execution_time:.2f}s ({((multi_report.execution_time / single_report.execution_time - 1) * 100):.1f}%)")
    print()
    
    # Quality comparison
    print("Quality Assessment:")
    print(f"  Single Agent Score: {single_report.quality_score}% ({single_report.quality_grade})")
    print(f"  Multi-Agent Score:  {multi_report.overall_assessment['quality_score']}% ({multi_report.overall_assessment['quality_grade']})")
    score_diff = multi_report.overall_assessment['quality_score'] - single_report.quality_score
    print(f"  Difference:         {'+' if score_diff >= 0 else ''}{score_diff:.1f} points")
    print()
    
    # Save reports
    with open('comparison_single_agent.json', 'w') as f:
        json.dump(single_report.to_dict(), f, indent=2, default=str)
    
    with open('comparison_multi_agent.json', 'w') as f:
        json.dump(multi_report.to_dict(), f, indent=2, default=str)
    
    # Save comparison
    comparison_data = {
        'pr_info': {
            'repo': repo,
            'pr_number': pr_number,
            'title': pr_data['title']
        },
        'single_agent': {
            'model': single_model,
            'findings_count': len(single_report.findings),
            'quality_score': single_report.quality_score,
            'quality_grade': single_report.quality_grade,
            'execution_time': single_report.execution_time,
            'risk_level': single_report.risk_level,
            'confidence': single_report.confidence
        },
        'multi_agent': {
            'model': multi_model,
            'findings_count': len(multi_report.all_findings),
            'quality_score': multi_report.overall_assessment['quality_score'],
            'quality_grade': multi_report.overall_assessment['quality_grade'],
            'execution_time': multi_report.execution_time,
            'risk_level': multi_report.overall_assessment['risk_level'],
            'confidence': multi_report.overall_assessment['confidence']
        },
        'coverage': coverage,
        'severity_distribution': severity_comp,
        'unique_findings': unique_analysis,
        'comprehensiveness': {
            'single_agent': single_comprehensive,
            'multi_agent': multi_comprehensive,
            'difference': multi_comprehensive - single_comprehensive
        }
    }
    
    with open('comparison_results.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print("✓ Reports saved:")
    print("  - comparison_single_agent.json")
    print("  - comparison_multi_agent.json")
    print("  - comparison_results.json")
    print()
    
    # Final verdict
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    print()
    
    winner_findings = "Multi-Agent" if len(multi_report.all_findings) > len(single_report.findings) else "Single Agent"
    winner_quality = "Multi-Agent" if multi_report.overall_assessment['quality_score'] > single_report.quality_score else "Single Agent"
    winner_comprehensive = "Multi-Agent" if multi_comprehensive > single_comprehensive else "Single Agent"
    winner_coverage = "Multi-Agent" if sum(coverage['multi_agent'].values()) > sum(coverage['single_agent'].values()) else "Single Agent"
    
    print(f"More Findings:      {winner_findings}")
    print(f"Better Quality:     {winner_quality}")
    print(f"More Comprehensive: {winner_comprehensive}")
    print(f"Better Coverage:    {winner_coverage}")
    print()
    
    # Count wins
    wins = {
        'multi': sum([
            len(multi_report.all_findings) > len(single_report.findings),
            multi_report.overall_assessment['quality_score'] > single_report.quality_score,
            multi_comprehensive > single_comprehensive,
            sum(coverage['multi_agent'].values()) > sum(coverage['single_agent'].values())
        ]),
        'single': 0
    }
    wins['single'] = 4 - wins['multi']
    
    if wins['multi'] > wins['single']:
        print(f"🏆 WINNER: Multi-Agent System ({wins['multi']}/4 metrics)")
    elif wins['single'] > wins['multi']:
        print(f"🏆 WINNER: Single Agent ({wins['single']}/4 metrics)")
    else:
        print(f"🤝 TIE: Both approaches performed equally well")
    
    print()
    print("✅ Comparison complete!")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nComparison interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
