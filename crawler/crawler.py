import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import List, Dict, Optional, Any
from github import Github, RateLimitExceededException, GithubException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PRCrawler:
    def __init__(self, max_files: int = 25, max_patch_size: int = 25000, max_workers: int = 5):
        """
        Initialize the PR Crawler

        Args:
            max_files: Maximum number of files to fetch per PR
            max_patch_size: Maximum size of a patch file in characters
            max_workers: Number of concurrent threads for batch processing
        """
        self.g = Github(os.getenv("GITHUB_PAT"))
        self.max_files = max_files
        self.max_patch_size = max_patch_size
        self.max_workers = max_workers

    def crawl_pr(self, repo_full_name: str, pr_number: int, max_retries: int = 3) -> Optional[Dict]:
        """
        Fetches data for any public PR with rate limiting and error handling

        Args:
            repo_full_name: Repository name in format "owner/repo"
            pr_number: Pull request number
            max_retries: Maximum number of retries on rate limit

        Returns:
            Dictionary containing PR data or None if failed
        """
        try:
            repo = self.g.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)

            # Prepare unified data object
            pr_payload = {
                "id": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "repo": repo_full_name,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                "state": pr.state,
                "is_draft": pr.draft,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "labels": [label.name for label in pr.labels],
                "body_preview": pr.body[:500] if pr.body else None,
                "body_full": pr.body if pr.body else None,
                "comments_count": pr.comments,
                "review_comments_count": pr.review_comments,
                "mergeable": pr.mergeable,
                "files": [],
                "truncated": False
            }

            # Fetch changed files with size limits
            file_count = 0
            for file in pr.get_files():
                if file_count >= self.max_files:
                    pr_payload["truncated"] = True
                    logger.warning(f"PR #{pr_number} has {file_count}+ files, truncating at {self.max_files}")
                    break

                # Handle patches (they can be None for binary files)
                patch = file.patch
                if patch and len(patch) > self.max_patch_size:
                    patch = patch[:self.max_patch_size] + "\n... [TRUNCATED DUE TO SIZE]"
                    pr_payload["truncated"] = True

                pr_payload["files"].append({
                    "filename": file.filename,
                    "patch": patch,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "raw_url": file.raw_url,
                    "blob_url": file.blob_url
                })
                file_count += 1

            return pr_payload

        except RateLimitExceededException as e:
            if max_retries <= 0:
                logger.error(f"Rate limit exceeded for PR #{pr_number}, no retries left")
                return None

            reset_time = self.g.get_rate_limit().core.reset
            wait_seconds = max(0, (reset_time - datetime.now()).total_seconds() + 5)
            logger.warning(f"Rate limit exceeded. Waiting {wait_seconds:.0f} seconds before retry...")
            time.sleep(wait_seconds)
            return self.crawl_pr(repo_full_name, pr_number, max_retries - 1)

        except GithubException as e:
            if e.status == 404:
                logger.error(f"PR #{pr_number} not found in {repo_full_name}")
            elif e.status == 403:
                logger.error(f"Access forbidden for PR #{pr_number}. Check token permissions.")
            else:
                logger.error(f"GitHub error for PR #{pr_number}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error crawling PR #{pr_number}: {e}", exc_info=True)
            return None

    def crawl_prs_batch(self, repo_full_name: str, pr_numbers: List[int]) -> Dict[int, Optional[Dict]]:
        """
        Crawl multiple PRs concurrently

        Args:
            repo_full_name: Repository name in format "owner/repo"
            pr_numbers: List of PR numbers to crawl

        Returns:
            Dictionary mapping PR numbers to their data (or None if failed)
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.crawl_pr, repo_full_name, pr_num): pr_num
                for pr_num in pr_numbers
            }

            for future in as_completed(futures):
                pr_num = futures[future]
                try:
                    results[pr_num] = future.result()
                    if results[pr_num]:
                        logger.info(f"Crawled PR #{pr_num}")
                    else:
                        logger.warning(f"Failed to crawl PR #{pr_num}")
                except Exception as e:
                    logger.error(f"Exception while crawling PR #{pr_num}: {e}", exc_info=True)
                    results[pr_num] = None

        return results

    def get_recent_prs(self, repo_full_name: str, limit: int = 10, state: str = "open") -> List[int]:
        """
        Get recent PR numbers from a repository

        Args:
            repo_full_name: Repository name in format "owner/repo"
            limit: Maximum number of PRs to return
            state: PR state ("open", "closed", or "all")

        Returns:
            List of PR numbers
        """
        try:
            repo = self.g.get_repo(repo_full_name)
            pulls = repo.get_pulls(state=state, sort="created", direction="desc")

            pr_numbers = []
            for i, pr in enumerate(pulls):
                if i >= limit:
                    break
                pr_numbers.append(pr.number)

            return pr_numbers

        except Exception as e:
            logger.error(f"Error fetching recent PRs: {e}", exc_info=True)
            return []


# Cached version for repeated access
@lru_cache(maxsize=128)
def cached_crawl_pr(crawler: PRCrawler, repo_full_name: str, pr_number: int) -> Optional[Dict]:
    """Cached version to avoid re-crawling same PR"""
    return crawler.crawl_pr(repo_full_name, pr_number)