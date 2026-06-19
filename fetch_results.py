#!/usr/bin/env python3
"""
Fetch PR review results from GitHub data-collection-v2 branch

Downloads all JSON files from the data-collection-v2 branch
and saves them locally for analysis.
"""

import os
import requests
from pathlib import Path


def fetch_data_from_github(
    repo_owner: str = "4ndr-34",
    repo_name: str = "demo-pr-review",
    branch: str = "data-collection-v2",
    output_dir: str = "thesis_data"
):
    """
    Fetch all JSON files from GitHub data-collection-v2 branch
    
    Args:
        repo_owner: GitHub username
        repo_name: Repository name
        branch: Branch name (data-collection-v2)
        output_dir: Local directory to save files
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("="*80)
    print("FETCHING REVIEW RESULTS FROM GITHUB")
    print("="*80)
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Branch: {branch}")
    print(f"Output: {output_path}/")
    print()
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/pr_reviews"
    
    try:
        # Get list of files in pr_reviews/ directory
        response = requests.get(
            api_url,
            params={'ref': branch},
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        response.raise_for_status()
        
        files = response.json()
        json_files = [f for f in files if f['name'].endswith('.json')]
        
        print(f"Found {len(json_files)} JSON files\n")
        
        # Download each file
        for i, file_info in enumerate(json_files, 1):
            filename = file_info['name']
            download_url = file_info['download_url']
            
            print(f"[{i}/{len(json_files)}] Downloading {filename}...", end=' ')
            
            file_response = requests.get(download_url)
            file_response.raise_for_status()
            
            # Save file
            output_file = output_path / filename
            with open(output_file, 'wb') as f:
                f.write(file_response.content)
            
            print("OK")
        
        print()
        print("="*80)
        print(f"SUCCESS: Downloaded {len(json_files)} files to {output_path}/")
        print("="*80)
        print()
        print("Next step: Run comparative_analysis.py")
        
        return len(json_files)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"\nERROR: Branch '{branch}' or directory 'pr_reviews' not found")
            print("Make sure PRs have been reviewed and data is saved to data-collection-v2 branch")
        else:
            print(f"\nERROR: HTTP Error: {e}")
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch PR review results from GitHub')
    parser.add_argument('--owner', default='4ndr-34', help='GitHub username')
    parser.add_argument('--repo', default='demo-pr-review', help='Repository name')
    parser.add_argument('--branch', default='data-collection-v2', help='Branch name')
    parser.add_argument('--output', default='thesis_data', help='Output directory')
    
    args = parser.parse_args()
    
    count = fetch_data_from_github(
        repo_owner=args.owner,
        repo_name=args.repo,
        branch=args.branch,
        output_dir=args.output
    )
    
    if count > 0:
        print("You can now run: python comparative_analysis.py")
    else:
        print("\nTroubleshooting:")
        print("1. Check that PRs have been created and reviewed")
        print("2. Check that GitHub Actions workflow has run successfully")
        print(f"3. Visit: https://github.com/{args.owner}/{args.repo}/tree/{args.branch}")


if __name__ == "__main__":
    main()
