#!/usr/bin/env python3
"""
PR Crawler & Analyzer - Main entry point
"""

import json
import sys
import argparse
import logging
from datetime import datetime
from typing import Optional

from crawler.crawler import PRCrawler
from crawler.llm_formatter import LLMFormatter
from crawler.llm_integration import LLMIntegrator, quick_analyze_pr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def save_results(results: dict, filename: str = None):
    """Save results to a JSON file"""
    if not filename:
        filename = f"pr_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Results saved to {filename}")
    return filename


def analyze_single_pr(repo: str, pr_number: int, model: str = "gpt-3.5-turbo",
                      save: bool = False, include_diffs: bool = True):
    """Analyze a single pull request"""
    logger.info(f"Analyzing PR #{pr_number} from {repo}")
    logger.info(f"Using model: {model}")
    logger.info("-" * 60)

    result = quick_analyze_pr(repo, pr_number, model)

    if result and save:
        save_results(result, f"pr_{pr_number}_analysis.json")

    return result


def analyze_multiple_prs(repo: str, pr_numbers: list, model: str = "gpt-3.5-turbo",
                         max_workers: int = 3, save: bool = False):
    """Analyze multiple pull requests"""
    logger.info(f"Analyzing {len(pr_numbers)} PRs from {repo}")
    logger.info(f"Using model: {model}")
    logger.info("-" * 60)

    crawler = PRCrawler(max_workers=max_workers)
    formatter = LLMFormatter()
    llm = LLMIntegrator(model=model)

    # Crawl all PRs
    logger.info("Crawling PRs...")
    pr_data_map = crawler.crawl_prs_batch(repo, pr_numbers)

    # Filter successful crawls
    success_data = [(num, data) for num, data in pr_data_map.items() if data]
    logger.info(f"Successfully crawled {len(success_data)}/{len(pr_numbers)} PRs")

    # Analyze each PR
    logger.info("Analyzing with LLM...")
    analyses = {}

    for pr_num, pr_data in success_data:
        logger.info(f"Analyzing PR #{pr_num}")
        analysis = llm.analyze_pr(pr_data, formatter, include_full_diff=False)
        analyses[pr_num] = {
            "pr_data": pr_data,
            "analysis": analysis,
            "analyzed_at": datetime.now().isoformat()
        }

    if save:
        save_results(analyses, f"batch_analysis_{len(pr_numbers)}_prs.json")

    return analyses


def analyze_recent_prs(repo: str, limit: int = 5, model: str = "gpt-3.5-turbo",
                       save: bool = False):
    """Analyze recent PRs from a repository"""
    logger.info(f"Fetching {limit} recent PRs from {repo}")

    crawler = PRCrawler()
    recent_prs = crawler.get_recent_prs(repo, limit=limit, state="open")

    if not recent_prs:
        logger.warning("No PRs found")
        return None

    logger.info(f"Found PRs: {recent_prs}")
    return analyze_multiple_prs(repo, recent_prs, model, save=save)


def main():
    parser = argparse.ArgumentParser(description="GitHub PR Crawler and LLM Analyzer")
    parser.add_argument("repo", help="Repository name (e.g., tiangolo/fastapi)")
    parser.add_argument("--pr", type=int, help="Single PR number to analyze")
    parser.add_argument("--prs", nargs="+", type=int, help="Multiple PR numbers to analyze")
    parser.add_argument("--recent", type=int, help="Analyze N most recent PRs")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--save", action="store_true", help="Save results to file")
    parser.add_argument("--no-diffs", action="store_true", help="Exclude code diffs from analysis")

    args = parser.parse_args()

    # Validate inputs
    if not args.pr and not args.prs and not args.recent:
        parser.error("Please specify either --pr, --prs, or --recent")

    include_diffs = not args.no_diffs

    try:
        if args.pr:
            analyze_single_pr(args.repo, args.pr, args.model, args.save, include_diffs)

        elif args.prs:
            analyze_multiple_prs(args.repo, args.prs, args.model, save=args.save)

        elif args.recent:
            analyze_recent_prs(args.repo, args.recent, args.model, args.save)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()