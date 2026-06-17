#!/usr/bin/env python3
"""
GitHub Actions Review Runner

Runs multi-agent PR review and outputs results for GitHub Actions.
"""

import sys
import json
import argparse
import logging
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from crawler.crawler import PRCrawler
from crawler.llm_integration import LLMIntegrator
from agents import MultiAgentOrchestrator, SingleAgent

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Run multi-agent PR review')
    parser.add_argument('--repo', required=True, help='Repository (owner/name)')
    parser.add_argument('--pr', required=True, type=int, help='PR number')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='LLM model to use for multi-agent')
    parser.add_argument('--single-model', default=None, help='LLM model to use for single agent (defaults to --model)')
    parser.add_argument('--compare', action='store_true', help='Compare with single agent')
    
    args = parser.parse_args()
    
    # If single-model not specified, use same as multi-agent model
    if args.single_model is None:
        args.single_model = args.model
    
    try:
        logger.info(f"Starting review of {args.repo} PR #{args.pr}")
        
        # Fetch PR data
        crawler = PRCrawler()
        pr_data = crawler.crawl_pr(args.repo, args.pr)
        
        if not pr_data:
            logger.error("Failed to fetch PR data")
            sys.exit(1)
        
        logger.info(f"PR fetched: {pr_data['title']}")
        
        # Run single agent if comparison requested
        single_report = None
        if args.compare:
            logger.info(f"Running single agent for comparison (model: {args.single_model})...")
            llm_client_single = LLMIntegrator(model=args.single_model)
            single_agent = SingleAgent(llm_client=llm_client_single, model=args.single_model)
            single_report = single_agent.analyze(pr_data)
            logger.info(f"Single agent ({args.single_model}): {len(single_report.findings)} findings, {single_report.quality_score}% quality")
        
        # Run multi-agent analysis
        llm_client = LLMIntegrator(model=args.model)
        orchestrator = MultiAgentOrchestrator(
            llm_client=llm_client,
            model=args.model,
            parallel=True,
            use_advanced_scoring=False
        )
        
        logger.info("Running multi-agent analysis...")
        report = orchestrator.analyze_pr(pr_data)
        
        # Format results for GitHub Actions
        results = {
            'comparison_mode': args.compare,
            'pr_number': args.pr,
            'pr_title': pr_data['title'],
            'quality_score': report.overall_assessment['quality_score'],
            'quality_grade': report.overall_assessment['quality_grade'],
            'risk_level': report.overall_assessment['risk_level'],
            'recommendation': report.overall_assessment['recommendation'],
            'confidence': report.overall_assessment['confidence'],
            'total_findings': report.overall_assessment['total_findings'],
            'critical_findings': report.overall_assessment['critical_findings'],
            'high_findings': report.overall_assessment['high_findings'],
            'medium_findings': report.overall_assessment['medium_findings'],
            'agents_consensus': report.overall_assessment['agents_consensus'],
            'execution_time': report.execution_time,
            'agent_summaries': report.agent_summaries,
            'priority_issues': report.priority_issues[:10],  # Top 10 for display
            'all_findings': report.priority_issues  # All findings for analysis
        }
        
        # Add comparison data if available
        if single_report:
            # Convert single agent findings to dictionaries
            single_findings = [
                {
                    'type': f.type,
                    'severity': f.severity.value if hasattr(f.severity, 'value') else str(f.severity),
                    'confidence': f.confidence,
                    'file': f.file,
                    'line': f.line,
                    'description': f.description,
                    'recommendation': f.recommendation,
                    'code_snippet': f.code_snippet,
                    'context': f.context
                }
                for f in single_report.findings
            ]
            
            results['comparison'] = {
                'single_agent': {
                    'quality_score': single_report.quality_score,
                    'quality_grade': single_report.quality_grade,
                    'findings_count': len(single_report.findings),
                    'findings': single_findings,
                    'risk_level': single_report.risk_level,
                    'execution_time': single_report.execution_time
                },
                'multi_agent': {
                    'quality_score': results['quality_score'],
                    'quality_grade': results['quality_grade'],
                    'findings_count': results['total_findings'],
                    'risk_level': results['risk_level'],
                    'execution_time': results['execution_time']
                },
                'advantage': {
                    'more_findings': results['total_findings'] - len(single_report.findings),
                    'quality_difference': results['quality_score'] - single_report.quality_score,
                    'time_overhead': results['execution_time'] - single_report.execution_time
                }
            }
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {args.output}")
        logger.info(f"Quality Score: {results['quality_score']}% ({results['quality_grade']})")
        logger.info(f"Risk Level: {results['risk_level']}")
        
        # Log warnings but don't fail - let the workflow decide
        if results['critical_findings'] > 0:
            logger.warning(f"{results['critical_findings']} critical issues found!")
        if results['quality_score'] < 70:
            logger.warning(f"Quality score below threshold: {results['quality_score']}%")
        
        # Always exit successfully if review completed
        logger.info("Review completed successfully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Review failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
