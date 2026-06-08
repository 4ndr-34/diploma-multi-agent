#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test: Advanced Scoring System

Compares simple vs advanced scoring on a real PR.
"""

import json
import logging
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator
from agents import MultiAgentOrchestrator

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    print("=" * 80)
    print("TESTING ADVANCED SCORING SYSTEM")
    print("=" * 80)
    
    # Configuration
    repo = "tiangolo/fastapi"
    pr_number = 1
    model = "gpt-3.5-turbo"
    
    print(f"\nTest Configuration:")
    print(f"  Repository: {repo}")
    print(f"  PR Number: {pr_number}")
    print(f"  Model: {model}")
    print()
    
    # Step 1: Fetch PR
    print("-" * 80)
    print("STEP 1: Fetching PR Data")
    print("-" * 80)
    
    crawler = PRCrawler()
    pr_data = crawler.crawl_pr(repo, pr_number)
    
    if not pr_data:
        print("❌ Failed to fetch PR")
        return False
    
    print(f"✓ PR fetched successfully")
    print(f"  Title: {pr_data['title']}")
    print(f"  Files changed: {len(pr_data['files'])}")
    print()
    
    # Step 2: Test with SIMPLE scoring
    print("=" * 80)
    print("TEST 1: SIMPLE PRIORITY-BASED SCORING")
    print("=" * 80)
    print()
    
    llm_client = LLMIntegrator(model=model)
    
    orchestrator_simple = MultiAgentOrchestrator(
        llm_client=llm_client,
        model=model,
        parallel=True,
        use_advanced_scoring=False  # Simple mode
    )
    
    print("Running multi-agent analysis with simple scoring...")
    print("(This will take 30-60 seconds)")
    print()
    
    report_simple = orchestrator_simple.analyze_pr(pr_data)
    
    print("\n" + "-" * 80)
    print("SIMPLE SCORING RESULTS")
    print("-" * 80)
    print(f"Quality Score: {report_simple.overall_assessment.get('quality_score', 'N/A')}% (Grade: {report_simple.overall_assessment.get('quality_grade', 'N/A')})")
    print(f"Risk Level: {report_simple.overall_assessment['risk_level'].upper()}")
    print(f"Total Findings: {report_simple.overall_assessment['total_findings']}")
    print(f"Critical: {report_simple.overall_assessment['critical_findings']}")
    print(f"High: {report_simple.overall_assessment['high_findings']}")
    print(f"Medium: {report_simple.overall_assessment['medium_findings']}")
    print()
    
    print("Top 5 Priority Issues (Simple Scoring):")
    for i, issue in enumerate(report_simple.priority_issues[:5], 1):
        print(f"\n  {i}. [{issue['severity'].upper()}] {issue['type']}")
        print(f"     Agent: {issue['agent']}")
        print(f"     File: {issue['file']}")
        print(f"     Confidence: {issue['confidence']:.2f}")
        print(f"     Description: {issue['description'][:80]}...")
    
    # Save simple report
    with open('test_report_simple.json', 'w') as f:
        json.dump(report_simple.to_dict(), f, indent=2, default=str)
    print(f"\n✓ Simple scoring report saved: test_report_simple.json")
    
    # Step 3: Test with ADVANCED scoring (Balanced)
    print("\n" + "=" * 80)
    print("TEST 2: ADVANCED SCORING - BALANCED PRESET")
    print("=" * 80)
    print()
    
    orchestrator_balanced = MultiAgentOrchestrator(
        llm_client=llm_client,
        model=model,
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='balanced'
    )
    
    print("Running multi-agent analysis with balanced advanced scoring...")
    print("(This will take 30-60 seconds)")
    print()
    
    report_balanced = orchestrator_balanced.analyze_pr(pr_data)
    
    print("\n" + "-" * 80)
    print("ADVANCED SCORING RESULTS (Balanced)")
    print("-" * 80)
    print(f"Quality Score: {report_balanced.overall_assessment.get('quality_score', 'N/A')}% (Grade: {report_balanced.overall_assessment.get('quality_grade', 'N/A')})")
    print(f"Risk Level: {report_balanced.overall_assessment['risk_level'].upper()}")
    print(f"Total Findings: {report_balanced.overall_assessment['total_findings']}")
    print()
    
    print("Top 5 Priority Issues (Advanced Balanced Scoring):")
    for i, issue in enumerate(report_balanced.priority_issues[:5], 1):
        print(f"\n  {i}. [{issue['severity'].upper()}] {issue['type']}")
        print(f"     Agent: {issue['agent']}")
        print(f"     File: {issue['file']}")
        print(f"     Score: {issue.get('normalized_score', 'N/A')}/100")
        print(f"     Confidence: {issue['confidence']:.2f}")
        if 'score_factors' in issue:
            print(f"     Impact: {issue['score_factors']['impact']:.2f}")
            print(f"     Criticality: {issue['score_factors']['criticality']:.2f}")
            print(f"     Urgency: {issue['score_factors']['urgency']:.2f}")
        print(f"     Description: {issue['description'][:80]}...")
    
    # Save balanced report
    with open('test_report_balanced.json', 'w') as f:
        json.dump(report_balanced.to_dict(), f, indent=2, default=str)
    print(f"\n✓ Balanced scoring report saved: test_report_balanced.json")
    
    # Step 4: Test with ADVANCED scoring (Security Critical)
    print("\n" + "=" * 80)
    print("TEST 3: ADVANCED SCORING - SECURITY CRITICAL PRESET")
    print("=" * 80)
    print()
    
    orchestrator_security = MultiAgentOrchestrator(
        llm_client=llm_client,
        model=model,
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='security_critical'
    )
    
    print("Running multi-agent analysis with security-critical scoring...")
    print("(This will take 30-60 seconds)")
    print()
    
    report_security = orchestrator_security.analyze_pr(pr_data)
    
    print("\n" + "-" * 80)
    print("ADVANCED SCORING RESULTS (Security Critical)")
    print("-" * 80)
    print(f"Quality Score: {report_security.overall_assessment.get('quality_score', 'N/A')}% (Grade: {report_security.overall_assessment.get('quality_grade', 'N/A')})")
    print(f"Risk Level: {report_security.overall_assessment['risk_level'].upper()}")
    print(f"Total Findings: {report_security.overall_assessment['total_findings']}")
    print()
    
    print("Top 5 Priority Issues (Security Critical Scoring):")
    for i, issue in enumerate(report_security.priority_issues[:5], 1):
        print(f"\n  {i}. [{issue['severity'].upper()}] {issue['type']}")
        print(f"     Agent: {issue['agent']}")
        print(f"     File: {issue['file']}")
        print(f"     Score: {issue.get('normalized_score', 'N/A')}/100")
        print(f"     Confidence: {issue['confidence']:.2f}")
        print(f"     Description: {issue['description'][:80]}...")
    
    # Save security report
    with open('test_report_security_critical.json', 'w') as f:
        json.dump(report_security.to_dict(), f, indent=2, default=str)
    print(f"\n✓ Security critical report saved: test_report_security_critical.json")
    
    # Step 5: Compare priorities
    print("\n" + "=" * 80)
    print("COMPARISON: HOW PRIORITIES CHANGED")
    print("=" * 80)
    print()
    
    print("Issue Priority Changes:")
    print("-" * 80)
    
    # Get top 5 from each
    simple_top5 = [(issue['type'], issue['agent'], issue['file']) for issue in report_simple.priority_issues[:5]]
    balanced_top5 = [(issue['type'], issue['agent'], issue['file']) for issue in report_balanced.priority_issues[:5]]
    security_top5 = [(issue['type'], issue['agent'], issue['file']) for issue in report_security.priority_issues[:5]]
    
    print("\nSimple Scoring Top 5:")
    for i, (type_, agent, file) in enumerate(simple_top5, 1):
        print(f"  {i}. {type_} ({agent}) - {file}")
    
    print("\nBalanced Advanced Top 5:")
    for i, (type_, agent, file) in enumerate(balanced_top5, 1):
        print(f"  {i}. {type_} ({agent}) - {file}")
    
    print("\nSecurity Critical Top 5:")
    for i, (type_, agent, file) in enumerate(security_top5, 1):
        print(f"  {i}. {type_} ({agent}) - {file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print("\nGenerated Reports:")
    print("  1. test_report_simple.json         - Simple priority-based")
    print("  2. test_report_balanced.json       - Advanced balanced")
    print("  3. test_report_security_critical.json - Advanced security-critical")
    
    print("\nKey Observations:")
    
    # Count security findings in top 5
    simple_security_count = sum(1 for _, agent, _ in simple_top5 if agent == 'security')
    balanced_security_count = sum(1 for _, agent, _ in balanced_top5 if agent == 'security')
    security_critical_count = sum(1 for _, agent, _ in security_top5 if agent == 'security')
    
    print(f"\nSecurity findings in top 5:")
    print(f"  Simple:          {simple_security_count}/5")
    print(f"  Balanced:        {balanced_security_count}/5")
    print(f"  Security-Critical: {security_critical_count}/5")
    
    print("\n✅ Advanced scoring test completed successfully!")
    print(f"\nTotal cost estimate: ~$2-3 (ran analysis 3 times)")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
