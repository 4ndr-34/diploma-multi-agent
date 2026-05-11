import datetime
import time
import logging
from typing import Dict, Optional, List
from litellm import completion
from dotenv import load_dotenv

from crawler.crawler import PRCrawler
from crawler.llm_formatter import LLMFormatter

load_dotenv()

logger = logging.getLogger(__name__)


class LLMIntegrator:
    def __init__(self, model: str = "gpt-4", max_tokens: int = 4000):
        """
        Initialize LLM integrator

        Args:
            model: LLM model to use (supports OpenAI, Anthropic, etc.)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.max_tokens = max_tokens

        # Optional: Configure for specific providers
        # For OpenAI: set OPENAI_API_KEY in .env
        # For Anthropic: set ANTHROPIC_API_KEY in .env
        # For local models: set appropriate environment variables

    def analyze_pr(self, pr_payload: Dict, formatter, include_full_diff: bool = True) -> Optional[str]:
        """
        Analyze a single PR using LLM

        Args:
            pr_payload: PR data from crawler
            formatter: LLMFormatter instance
            include_full_diff: Whether to include full diffs

        Returns:
            LLM analysis as string or None if failed
        """
        try:
            # Format the prompt
            prompt = formatter.format_for_llm(pr_payload, include_full_diff=include_full_diff)

            # Call LLM
            response = self._call_llm(prompt)

            return response

        except Exception as e:
            logger.error(f"Error analyzing PR: {e}", exc_info=True)
            return None

    def analyze_pr_batch(self, pr_data_list: List[Dict], formatter,
                         include_full_diff: bool = False) -> Dict[int, Optional[str]]:
        """
        Analyze multiple PRs (manually iterating, not concurrent to avoid rate limits)

        Args:
            pr_data_list: List of (pr_number, pr_payload) tuples
            formatter: LLMFormatter instance
            include_full_diff: Whether to include full diffs

        Returns:
            Dictionary mapping PR numbers to analysis
        """
        results = {}

        for pr_number, pr_payload in pr_data_list:
            if not pr_payload:
                results[pr_number] = None
                continue

            logger.info(f"Analyzing PR #{pr_number}...")
            analysis = self.analyze_pr(pr_payload, formatter, include_full_diff)
            results[pr_number] = analysis

            # Small delay to avoid hitting rate limits
            time.sleep(1)

        return results

    def _call_llm(self, prompt: str) -> str:
        """
        Make the actual LLM API call with retry logic

        Args:
            prompt: Formatted prompt string

        Returns:
            LLM response text
        """
        messages = [
            {"role": "system",
             "content": "You are an expert code reviewer with deep experience in software engineering best practices, security, and performance optimization."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = completion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            # Fallback to simpler model if main one fails
            if "rate_limit" in str(e).lower():
                logger.warning("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return self._call_llm(prompt)
            raise e

    def get_pr_with_analysis(self, crawler, repo_full_name: str, pr_number: int,
                             formatter, include_full_diff: bool = True) -> Optional[Dict]:
        """
        Complete pipeline: crawl PR and analyze it

        Returns:
            Dictionary with PR data and analysis
        """
        # Crawl the PR
        pr_data = crawler.crawl_pr(repo_full_name, pr_number)

        if not pr_data:
            logger.error(f"Failed to crawl PR #{pr_number}")
            return None

        # Analyze with LLM
        analysis = self.analyze_pr(pr_data, formatter, include_full_diff)

        return {
            "pr_data": pr_data,
            "analysis": analysis,
            "analyzed_at": datetime.now().isoformat()
        }


# Simple wrapper for quick use
def quick_analyze_pr(repo: str, pr_number: int, model: str = "gpt-3.5-turbo"):
    """
    Quick one-shot analysis of a PR

    Args:
        repo: Repository name (e.g., "tiangolo/fastapi")
        pr_number: PR number
        model: LLM model to use
    """
    crawler = PRCrawler()
    formatter = LLMFormatter()
    llm = LLMIntegrator(model=model)

    result = llm.get_pr_with_analysis(crawler, repo, pr_number, formatter)

    if result:
        logger.info(f"{'=' * 80}")
        logger.info(f"ANALYSIS FOR PR #{pr_number}: {result['pr_data']['title']}")
        logger.info(f"{'=' * 80}")
        logger.info(result['analysis'])
        return result

    return None