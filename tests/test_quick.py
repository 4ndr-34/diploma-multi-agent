#!/usr/bin/env python3
"""
Quick test script to verify the PR crawler implementation
This tests the crawler without requiring LLM API calls
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from crawler.crawler import PRCrawler
        from crawler.llm_formatter import LLMFormatter
        from crawler.llm_integration import LLMIntegrator
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_github_connection():
    """Test GitHub API connection"""
    print("\nTesting GitHub connection...")
    
    github_token = os.getenv("GITHUB_PAT")
    if not github_token:
        print("✗ GITHUB_PAT not found in environment")
        print("  Please create a .env file with your GitHub token")
        print("  See .env.example for reference")
        return False
    
    try:
        from crawler.crawler import PRCrawler
        crawler = PRCrawler()
        
        # Test with a small public repo PR
        test_repo = "octocat/Hello-World"
        print(f"  Fetching recent PRs from {test_repo}...")
        recent_prs = crawler.get_recent_prs(test_repo, limit=1, state="all")
        
        if recent_prs:
            print(f"✓ GitHub connection working! Found PR(s): {recent_prs}")
            return True
        else:
            print("✓ GitHub connection working (no PRs found, but connection successful)")
            return True
            
    except Exception as e:
        print(f"✗ GitHub connection failed: {e}")
        return False


def test_crawler():
    """Test PR crawling functionality"""
    print("\nTesting PR crawler...")
    
    try:
        from crawler.crawler import PRCrawler
        crawler = PRCrawler()
        
        # Use a well-known public repo with PRs
        test_repo = "tiangolo/fastapi"
        test_pr = 1  # PR #1 usually exists in most repos
        
        print(f"  Crawling PR #{test_pr} from {test_repo}...")
        pr_data = crawler.crawl_pr(test_repo, test_pr)
        
        if pr_data:
            print(f"✓ PR crawled successfully!")
            print(f"  Title: {pr_data.get('title', 'N/A')}")
            print(f"  Author: {pr_data.get('author', 'N/A')}")
            print(f"  Files changed: {len(pr_data.get('files', []))}")
            print(f"  Additions: +{pr_data.get('additions', 0)}")
            print(f"  Deletions: -{pr_data.get('deletions', 0)}")
            return True
        else:
            print("✗ Failed to crawl PR (might not exist)")
            return False
            
    except Exception as e:
        print(f"✗ Crawler test failed: {e}")
        return False


def test_formatter():
    """Test LLM formatter"""
    print("\nTesting LLM formatter...")
    
    try:
        from crawler.llm_formatter import LLMFormatter
        
        # Create mock PR data
        mock_pr = {
            "id": 123,
            "title": "Test PR",
            "author": "testuser",
            "repo": "owner/repo",
            "state": "open",
            "created_at": "2024-01-01T00:00:00",
            "labels": ["bug", "enhancement"],
            "additions": 50,
            "deletions": 20,
            "files": [
                {
                    "filename": "test.py",
                    "status": "modified",
                    "additions": 50,
                    "deletions": 20,
                    "changes": 70,
                    "patch": "@@ -1,3 +1,4 @@\n+import new_module\n import old_module"
                }
            ],
            "comments_count": 5,
            "review_comments_count": 3
        }
        
        formatter = LLMFormatter()
        formatted = formatter.format_for_llm(mock_pr, include_full_diff=True)
        
        if formatted and "Pull Request Analysis Request" in formatted:
            print("✓ Formatter working correctly")
            print(f"  Generated prompt length: {len(formatted)} characters")
            return True
        else:
            print("✗ Formatter output invalid")
            return False
            
    except Exception as e:
        print(f"✗ Formatter test failed: {e}")
        return False


def test_llm_setup():
    """Test LLM integration setup (without making actual API calls)"""
    print("\nTesting LLM integration setup...")
    
    try:
        from crawler.llm_integration import LLMIntegrator
        
        llm = LLMIntegrator(model="gpt-3.5-turbo")
        print(f"✓ LLM integrator initialized with model: {llm.model}")
        
        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key:
            print("  ✓ OpenAI API key found")
        else:
            print("  ⚠ OpenAI API key not found (needed for GPT models)")
            
        if anthropic_key:
            print("  ✓ Anthropic API key found")
        else:
            print("  ⚠ Anthropic API key not found (needed for Claude models)")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("PR CRAWLER - QUICK TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Run tests in order
    results.append(("Imports", test_imports()))
    results.append(("GitHub Connection", test_github_connection()))
    results.append(("PR Crawler", test_crawler()))
    results.append(("Formatter", test_formatter()))
    results.append(("LLM Setup", test_llm_setup()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your implementation is ready to use.")
        print("\nNext steps:")
        print("1. Try analyzing a real PR with:")
        print("   python main.py tiangolo/fastapi --pr 1")
        print("2. Or analyze recent PRs with:")
        print("   python main.py tiangolo/fastapi --recent 3")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
