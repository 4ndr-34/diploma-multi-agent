#!/usr/bin/env python3
"""
Demo script to show what the crawler actually captures from a PR
"""

import json
import sys
from dotenv import load_dotenv
from crawler.crawler import PRCrawler

load_dotenv()


def demo_crawler_output():
    """Fetch a real PR and show what data we get"""
    
    # Use a small, well-known PR for demo
    repo = "tiangolo/fastapi"
    pr_number = 1
    
    print("=" * 70)
    print(f"DEMO: Crawling PR #{pr_number} from {repo}")
    print("=" * 70)
    
    crawler = PRCrawler()
    pr_data = crawler.crawl_pr(repo, pr_number)
    
    if not pr_data:
        print("Failed to crawl PR. Check your GITHUB_PAT in .env")
        sys.exit(1)
    
    # Show high-level info
    print(f"\n📋 PR METADATA")
    print(f"{'=' * 70}")
    print(f"Title:       {pr_data['title']}")
    print(f"Author:      @{pr_data['author']}")
    print(f"State:       {pr_data['state']}")
    print(f"Files:       {len(pr_data['files'])} changed")
    print(f"Changes:     +{pr_data['additions']} / -{pr_data['deletions']} lines")
    print(f"Truncated:   {pr_data['truncated']}")
    
    # Show description preview
    if pr_data.get('body_preview'):
        print(f"\n📝 DESCRIPTION (first 200 chars)")
        print(f"{'=' * 70}")
        print(pr_data['body_preview'][:200])
    
    # Show files changed
    print(f"\n📂 FILES CHANGED")
    print(f"{'=' * 70}")
    for i, file in enumerate(pr_data['files'][:5], 1):
        print(f"\n{i}. {file['filename']}")
        print(f"   Status:    {file['status']}")
        print(f"   Changes:   +{file['additions']} / -{file['deletions']} lines")
        print(f"   Has patch: {'Yes' if file.get('patch') else 'No (binary file?)'}")
    
    if len(pr_data['files']) > 5:
        print(f"\n   ... and {len(pr_data['files']) - 5} more files")
    
    # Show actual code changes (patch) for first file
    print(f"\n💻 ACTUAL CODE CHANGES (PATCH)")
    print(f"{'=' * 70}")
    
    first_file_with_patch = None
    for file in pr_data['files']:
        if file.get('patch'):
            first_file_with_patch = file
            break
    
    if first_file_with_patch:
        print(f"\nFile: {first_file_with_patch['filename']}")
        print(f"Status: {first_file_with_patch['status']}\n")
        
        patch = first_file_with_patch['patch']
        # Show first 1000 chars of the patch
        if len(patch) > 1000:
            print(patch[:1000])
            print(f"\n... (showing first 1000 of {len(patch)} characters)")
        else:
            print(patch)
        
        print(f"\n📖 EXPLANATION:")
        print(f"{'=' * 70}")
        print("The patch above shows:")
        print("  - Lines starting with '@@ ... @@' = location in the file")
        print("  - Lines starting with '-' = code REMOVED")
        print("  - Lines starting with '+' = code ADDED")
        print("  - Lines with no symbol = unchanged context")
    else:
        print("No patches found (all binary files?)")
    
    # Optionally save full output
    print(f"\n💾 SAVE FULL OUTPUT?")
    print(f"{'=' * 70}")
    filename = f"pr_{pr_number}_full_data.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(pr_data, f, indent=2, default=str)
    print(f"✓ Full PR data saved to: {filename}")
    print(f"  Open it to see ALL the code changes captured!")
    
    return pr_data


if __name__ == "__main__":
    try:
        demo_crawler_output()
        print("\n" + "=" * 70)
        print("✨ This is what your LLM will receive for analysis!")
        print("=" * 70)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
