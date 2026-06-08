#!/usr/bin/env python3
"""
Example: Using Advanced Scoring System

Demonstrates how to use the advanced scoring system with different weight profiles
for prioritizing findings from multiple agents.
"""

import json
from dotenv import load_dotenv

from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator
from agents import (
    MultiAgentOrchestrator,
    WeightPresets,
    WeightProfile
)

load_dotenv()


def example_1_simple_mode():
    """Example 1: Using simple priority-based scoring (default)"""
    print("=" * 80)
    print("EXAMPLE 1: Simple Priority-Based Scoring (Default)")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create orchestrator with default simple scoring
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=False  # Default: uses simple severity + agent + confidence
    )
    
    print("\n✓ Orchestrator initialized with simple scoring")
    print("  Priority formula: Severity → Agent Type → Confidence")
    print()


def example_2_balanced_scoring():
    """Example 2: Using advanced scoring with balanced weights"""
    print("=" * 80)
    print("EXAMPLE 2: Advanced Scoring - Balanced Profile")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create orchestrator with balanced advanced scoring
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='balanced'  # Default balanced weights
    )
    
    print("\n✓ Orchestrator initialized with advanced balanced scoring")
    print("  Considers: severity, agent type, confidence, impact, complexity, criticality, urgency")
    print("  Weight profile: Balanced (all factors equally weighted)")
    print()


def example_3_security_critical():
    """Example 3: Security-critical project (banking, healthcare)"""
    print("=" * 80)
    print("EXAMPLE 3: Advanced Scoring - Security Critical Profile")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create orchestrator optimized for security
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='security_critical'
    )
    
    print("\n✓ Orchestrator initialized for security-critical project")
    print("  Security findings weighted 2.5x higher")
    print("  Critical/High severity issues boosted 1.5x/1.3x")
    print("  Impact and urgency heavily weighted")
    print("  Use for: Banking, Healthcare, Auth systems, Payment processing")
    print()


def example_4_performance_critical():
    """Example 4: Performance-critical project (high-traffic APIs)"""
    print("=" * 80)
    print("EXAMPLE 4: Advanced Scoring - Performance Critical Profile")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create orchestrator optimized for performance
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='performance_critical'
    )
    
    print("\n✓ Orchestrator initialized for performance-critical project")
    print("  Performance findings weighted 2.5x higher")
    print("  Code complexity heavily weighted (affects performance)")
    print("  Impact focused on performance metrics")
    print("  Use for: High-traffic APIs, Real-time systems, Gaming servers")
    print()


def example_5_startup_mvp():
    """Example 5: Startup/MVP - ship fast, fix critical bugs"""
    print("=" * 80)
    print("EXAMPLE 5: Advanced Scoring - Startup MVP Profile")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create orchestrator optimized for rapid development
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='startup_mvp'
    )
    
    print("\n✓ Orchestrator initialized for startup MVP")
    print("  Critical issues weighted 2.0x (must fix)")
    print("  Architecture issues weighted 0.5x (can wait)")
    print("  High urgency for shipping")
    print("  Use for: MVPs, Prototypes, Early-stage startups")
    print()


def example_6_custom_weights():
    """Example 6: Custom weight profile"""
    print("=" * 80)
    print("EXAMPLE 6: Advanced Scoring - Custom Weight Profile")
    print("=" * 80)
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Create custom weight profile
    custom_weights = WeightProfile(
        severity_weight=15.0,      # Really care about severity
        agent_weight=3.0,          # Agent type less important
        confidence_weight=5.0,     # Trust high confidence findings
        impact_weight=12.0,        # Impact is critical
        complexity_weight=2.0,
        criticality_weight=8.0,    # File criticality important
        urgency_weight=6.0,
        agent_multipliers={
            'security': 1.8,       # Boost security slightly
            'performance': 1.5,    # Boost performance
            'architecture': 0.8    # Lower architecture priority
        },
        severity_multipliers={
            'critical': 2.0,       # Must fix critical
            'high': 1.5,
            'medium': 1.0,
            'low': 0.5,
            'info': 0.2
        }
    )
    
    # Create orchestrator with custom weights
    orchestrator = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        weight_profile=custom_weights
    )
    
    print("\n✓ Orchestrator initialized with custom weights")
    print("  Severity weight: 15.0 (very important)")
    print("  Impact weight: 12.0 (critical)")
    print("  Security multiplier: 1.8x")
    print("  Performance multiplier: 1.5x")
    print("  Critical severity multiplier: 2.0x")
    print()


def example_7_compare_scoring_methods():
    """Example 7: Compare simple vs advanced scoring on same PR"""
    print("=" * 80)
    print("EXAMPLE 7: Comparing Simple vs Advanced Scoring")
    print("=" * 80)
    
    # Fetch a PR
    print("\nFetching PR data...")
    crawler = PRCrawler()
    pr_data = crawler.crawl_pr("tiangolo/fastapi", 1)
    
    if not pr_data:
        print("❌ Failed to fetch PR")
        return
    
    print(f"✓ Fetched PR #{pr_data['id']}: {pr_data['title']}")
    
    llm_client = LLMIntegrator(model="gpt-3.5-turbo")
    
    # Run with simple scoring
    print("\n" + "-" * 80)
    print("Running with SIMPLE scoring...")
    print("-" * 80)
    
    orchestrator_simple = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=False
    )
    
    report_simple = orchestrator_simple.analyze_pr(pr_data)
    
    print(f"\nSimple Scoring Results:")
    print(f"  Total findings: {len(report_simple.all_findings)}")
    print(f"  Top 3 priorities:")
    for issue in report_simple.priority_issues[:3]:
        print(f"    #{issue['priority']}: [{issue['severity']}] {issue['type']} in {issue['file']}")
    
    # Run with advanced scoring
    print("\n" + "-" * 80)
    print("Running with ADVANCED scoring (security-critical)...")
    print("-" * 80)
    
    orchestrator_advanced = MultiAgentOrchestrator(
        llm_client=llm_client,
        model="gpt-3.5-turbo",
        parallel=True,
        use_advanced_scoring=True,
        scoring_preset='security_critical'
    )
    
    report_advanced = orchestrator_advanced.analyze_pr(pr_data)
    
    print(f"\nAdvanced Scoring Results:")
    print(f"  Total findings: {len(report_advanced.all_findings)}")
    print(f"  Top 3 priorities:")
    for issue in report_advanced.priority_issues[:3]:
        score_info = f" (score: {issue.get('normalized_score', 'N/A')}/100)" if 'normalized_score' in issue else ""
        print(f"    #{issue['priority']}: [{issue['severity']}] {issue['type']} in {issue['file']}{score_info}")
    
    # Save both reports
    with open('report_simple_scoring.json', 'w') as f:
        json.dump(report_simple.to_dict(), f, indent=2, default=str)
    
    with open('report_advanced_scoring.json', 'w') as f:
        json.dump(report_advanced.to_dict(), f, indent=2, default=str)
    
    print("\n✓ Reports saved:")
    print("  - report_simple_scoring.json")
    print("  - report_advanced_scoring.json")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("█" * 80)
    print("  ADVANCED SCORING SYSTEM - EXAMPLES & USAGE")
    print("█" * 80)
    print()
    
    examples = [
        ("Simple Priority Scoring", example_1_simple_mode),
        ("Balanced Advanced Scoring", example_2_balanced_scoring),
        ("Security-Critical Profile", example_3_security_critical),
        ("Performance-Critical Profile", example_4_performance_critical),
        ("Startup MVP Profile", example_5_startup_mvp),
        ("Custom Weight Profile", example_6_custom_weights),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}\n")
    
    print("\n" + "=" * 80)
    print("SUMMARY: Advanced Scoring System")
    print("=" * 80)
    print("""
The advanced scoring system allows you to customize how findings are prioritized
based on your project's specific needs:

Available Presets:
  • balanced            - Equal weight to all factors (default)
  • security_critical   - Prioritize security (banking, healthcare)
  • performance_critical - Prioritize performance (high-traffic APIs)
  • architecture_focused - Prioritize code quality (large codebases)
  • startup_mvp         - Focus on critical issues, ship fast

Custom Weights:
You can create custom WeightProfile objects to fine-tune:
  - severity_weight      : How important is severity level?
  - agent_weight         : How much to trust different agent types?
  - confidence_weight    : How much to trust confidence scores?
  - impact_weight        : How important is estimated impact?
  - complexity_weight    : Consider code complexity?
  - criticality_weight   : Consider file importance?
  - urgency_weight       : How urgent is the fix?

Plus agent-specific and severity-specific multipliers for fine control.

Usage:
  orchestrator = MultiAgentOrchestrator(
      llm_client=llm_client,
      use_advanced_scoring=True,
      scoring_preset='security_critical'  # or custom WeightProfile
  )
    """)
    
    # Optional: Run comparison if user wants
    print("\nWant to see a real comparison? (requires API key)")
    response = input("Run Example 7 - Compare scoring methods on real PR? (y/n): ")
    if response.lower() == 'y':
        try:
            example_7_compare_scoring_methods()
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Examples complete!\n")


if __name__ == "__main__":
    main()
