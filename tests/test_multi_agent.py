#!/usr/bin/env python3
"""
Test Multi-Agent System

Quick test to verify the multi-agent architecture works correctly.
"""

import json
import logging
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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


def test_multi_agent_system():
    """Test the multi-agent system on a real PR"""
    
    print("=" * 80)
    print("TESTING MULTI-AGENT PR ANALYSIS SYSTEM")
    print("=" * 80)
    
    # Configuration
    repo = "tiangolo/fastapi"
    pr_number = 1
    model = "gpt-3.5-turbo"
    
    print(f"\nTest Configuration:")
    print(f"  Repository: {repo}")
    print(f"  PR Number: {pr_number}")
    print(f"  Model: {model}")
    print(f"\nStarting test...\n")
    
    # Step 1: Crawl PR
    print("-" * 80)
    print("STEP 1: Crawling PR data")
    print("-" * 80)
    
    crawler = PRCrawler()
    pr_data = crawler.crawl_pr(repo, pr_number)
    
    if not pr_data:
        print("❌ Failed to crawl PR")
        return False
    
    print(f"✓ PR crawled successfully")
    print(f"  Title: {pr_data['title']}")
    print(f"  Files changed: {len(pr_data['files'])}")
    print(f"  Additions: +{pr_data['additions']}")
    print(f"  Deletions: -{pr_data['deletions']}")
    
    # Step 2: Initialize multi-agent orchestrator
    print("\n" + "-" * 80)
    print("STEP 2: Initializing Multi-Agent System")
    print("-" * 80)
    
    llm_client = LLMIntegrator(model=model)
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model=model,
        parallel=True  # Run agents in parallel
    )
    
    print(f"✓ Orchestrator initialized")
    
    agent_status = orchestrator.get_agent_status()
    print(f"\nAgent Configuration:")
    for agent_name, status in agent_status.items():
        if agent_name != 'parallel_execution':
            print(f"  {agent_name.capitalize()}: {status['model']} (temp={status['temperature']})")
    print(f"  Parallel execution: {agent_status['parallel_execution']}")
    
    # Step 3: Run multi-agent analysis
    print("\n" + "-" * 80)
    print("STEP 3: Running Multi-Agent Analysis")
    print("-" * 80)
    print("\nThis will take 30-60 seconds (3 agents analyzing in parallel)...\n")
    
    try:
        report = orchestrator.analyze_pr(pr_data)
        
        # Step 4: Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        # Overall assessment
        print(f"\n📊 Overall Assessment:")
        print(f"  Risk Level: {report.overall_assessment['risk_level'].upper()}")
        print(f"  Readiness: {report.overall_assessment['readiness']}")
        print(f"  Recommendation: {report.overall_assessment['recommendation']}")
        print(f"  Confidence: {report.overall_assessment['confidence']:.2%}")
        print(f"  Total Findings: {report.overall_assessment['total_findings']}")
        
        # Agent summaries
        print(f"\n🤖 Agent Summaries:")
        for agent_name, summary in report.agent_summaries.items():
            print(f"  {agent_name.capitalize()}: {summary}")
        
        # Priority issues
        if report.priority_issues:
            print(f"\n🔴 Top Priority Issues:")
            for issue in report.priority_issues[:5]:  # Show top 5
                print(f"\n  #{issue['priority']} [{issue['severity'].upper()}] {issue['agent'].capitalize()}")
                print(f"     File: {issue['file']}")
                print(f"     Description: {issue['description'][:80]}...")
                print(f"     Action: {issue['action']}")
        
        # Conflicts resolved
        if report.conflicts_resolved:
            print(f"\n⚖️ Conflicts Resolved: {len(report.conflicts_resolved)}")
            for conflict in report.conflicts_resolved:
                print(f"  - {conflict.issue_type}")
                print(f"    Agents: {', '.join(conflict.agents)}")
                print(f"    Resolution: {conflict.resolution}")
        
        # Statistics
        print(f"\n📈 Statistics:")
        print(f"  Total execution time: {report.execution_time:.2f}s")
        print(f"  Critical findings: {report.overall_assessment['critical_findings']}")
        print(f"  High findings: {report.overall_assessment['high_findings']}")
        print(f"  Medium findings: {report.overall_assessment['medium_findings']}")
        print(f"  Agents consensus: {report.overall_assessment['agents_consensus']}")
        
        # Save full report
        output_file = f"multi_agent_report_pr{pr_number}.json"
        with open(output_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("✅ MULTI-AGENT SYSTEM TEST PASSED")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_multi_agent_system()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
