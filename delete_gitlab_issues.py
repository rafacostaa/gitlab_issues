#!/usr/bin/env python3
"""
GitLab Issues Deletion Tool

This script provides functionality to delete issues from GitLab projects using the GitLab API.
"""

import argparse
import sys
import requests
from typing import List, Optional


class GitLabIssueDeleter:
    """Class to handle GitLab issue deletion operations."""
    
    def __init__(self, gitlab_url: str, private_token: str):
        """
        Initialize the GitLab Issue Deleter.
        
        Args:
            gitlab_url: The GitLab instance URL (e.g., https://gitlab.com)
            private_token: Your GitLab personal access token
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.headers = {
            'PRIVATE-TOKEN': private_token
        }
        self.api_base = f"{self.gitlab_url}/api/v4"
    
    def get_project_issues(self, project_id: str, state: str = 'opened') -> List[dict]:
        """
        Get all issues for a project.
        
        Args:
            project_id: The project ID or URL-encoded path
            state: Issue state filter ('opened', 'closed', or 'all')
        
        Returns:
            List of issue dictionaries
        """
        url = f"{self.api_base}/projects/{project_id}/issues"
        params = {'state': state, 'per_page': 100}
        
        all_issues = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to GitLab while fetching page {page} for project {project_id}: {e}")
                break
            
            if response.status_code != 200:
                print(f"Error fetching issues: {response.status_code} - {response.text}")
                break
            
            issues = response.json()
            if not issues:
                break
            
            all_issues.extend(issues)
            page += 1
        
        return all_issues
    
    def delete_issue(self, project_id: str, issue_iid: int) -> bool:
        """
        Delete a specific issue from a project.
        
        Args:
            project_id: The project ID or URL-encoded path
            issue_iid: The internal ID of the issue
        
        Returns:
            True if deletion was successful, False otherwise
        """
        url = f"{self.api_base}/projects/{project_id}/issues/{issue_iid}"
        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to GitLab while deleting issue #{issue_iid}: {e}")
            return False
        
        if response.status_code == 204:
            return True
        else:
            print(f"Error deleting issue #{issue_iid}: {response.status_code} - {response.text}")
            return False
    
    def delete_all_issues(self, project_id: str, state: str = 'opened', 
                         confirm: bool = False) -> tuple:
        """
        Delete all issues from a project.
        
        Args:
            project_id: The project ID or URL-encoded path
            state: Issue state filter ('opened', 'closed', or 'all')
            confirm: If True, proceed with deletion without confirmation
        
        Returns:
            Tuple of (successful_deletions, failed_deletions)
        """
        issues = self.get_project_issues(project_id, state)
        
        if not issues:
            print(f"No {state} issues found in project {project_id}")
            return (0, 0)
        
        print(f"Found {len(issues)} {state} issue(s) in project {project_id}")
        
        if not confirm:
            response = input(f"Are you sure you want to delete {len(issues)} issue(s)? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Deletion cancelled.")
                return (0, 0)
        
        successful = 0
        failed = 0
        
        for issue in issues:
            issue_iid = issue['iid']
            issue_title = issue['title']
            
            print(f"Deleting issue #{issue_iid}: {issue_title}")
            if self.delete_issue(project_id, issue_iid):
                successful += 1
                print(f"  ✓ Successfully deleted issue #{issue_iid}")
            else:
                failed += 1
                print(f"  ✗ Failed to delete issue #{issue_iid}")
        
        return (successful, failed)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Delete issues from GitLab projects using the API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Delete all opened issues from a project
  %(prog)s --url https://gitlab.com --token YOUR_TOKEN --project-id 12345
  
  # Delete all issues (opened and closed) with auto-confirmation
  %(prog)s --url https://gitlab.com --token YOUR_TOKEN --project-id 12345 --state all --yes
  
  # Delete issues from a project using URL-encoded path
  %(prog)s --url https://gitlab.com --token YOUR_TOKEN --project-id namespace%%2Fproject-name
        '''
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='GitLab instance URL (e.g., https://gitlab.com)'
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='GitLab personal access token with API access'
    )
    
    parser.add_argument(
        '--project-id',
        required=True,
        help='Project ID or URL-encoded project path (e.g., 12345 or namespace%%2Fproject)'
    )
    
    parser.add_argument(
        '--state',
        choices=['opened', 'closed', 'all'],
        default='opened',
        help='State of issues to delete (default: opened)'
    )
    
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Create deleter instance
    deleter = GitLabIssueDeleter(args.url, args.token)
    
    # Delete issues
    successful, failed = deleter.delete_all_issues(
        args.project_id,
        state=args.state,
        confirm=args.yes
    )
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Deletion Summary:")
    print(f"  Successfully deleted: {successful}")
    print(f"  Failed to delete: {failed}")
    print(f"{'='*50}")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
