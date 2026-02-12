# GitLab Issues Deletion Tool

A Python script to delete issues from GitLab projects using the GitLab API.

## Overview

This tool provides a simple command-line interface to delete issues from GitLab projects. Since GitLab doesn't provide a bulk delete feature in the UI, this script uses the GitLab API to automate the deletion process.

## Features

- ✅ Delete issues from any GitLab project (GitLab.com or self-hosted)
- ✅ Filter issues by state (opened, closed, or all)
- ✅ Confirmation prompt before deletion (can be skipped with `--yes` flag)
- ✅ Progress feedback during deletion
- ✅ Summary report of successful and failed deletions
- ✅ Support for both project IDs and URL-encoded project paths

## Prerequisites

- Python 3.6 or higher
- GitLab personal access token with `api` scope
- Project ID or URL-encoded project path

## Installation

1. Clone this repository:
```bash
git clone https://github.com/rafacostaa/gitlab_issues.git
cd gitlab_issues
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install the required package directly:
```bash
pip install requests
```

## Getting Your GitLab Token

1. Log in to your GitLab instance
2. Go to **Settings** → **Access Tokens** (or visit https://gitlab.com/-/profile/personal_access_tokens)
3. Create a new token with the `api` scope
4. Copy the token (you won't be able to see it again!)

## Finding Your Project ID

You can find your project ID in several ways:

1. **From the project page**: It's displayed below the project name
2. **From the project settings**: Go to **Settings** → **General**
3. **URL-encoded path**: Use `namespace%2Fproject-name` format (e.g., `mygroup%2Fmyproject`)

## Usage

### Basic Usage

Delete all opened issues from a project:
```bash
python delete_gitlab_issues.py --url https://gitlab.com --token YOUR_TOKEN --project-id 12345
```

### Advanced Usage

Delete all issues (opened and closed) without confirmation:
```bash
python delete_gitlab_issues.py --url https://gitlab.com --token YOUR_TOKEN --project-id 12345 --state all --yes
```

Delete only closed issues:
```bash
python delete_gitlab_issues.py --url https://gitlab.com --token YOUR_TOKEN --project-id 12345 --state closed
```

Use URL-encoded project path:
```bash
python delete_gitlab_issues.py --url https://gitlab.com --token YOUR_TOKEN --project-id namespace%2Fproject-name
```

### Using a Self-Hosted GitLab Instance

```bash
python delete_gitlab_issues.py --url https://gitlab.example.com --token YOUR_TOKEN --project-id 12345
```

## Command-Line Options

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--url` | Yes | GitLab instance URL (e.g., https://gitlab.com) | - |
| `--token` | Yes | GitLab personal access token with API access | - |
| `--project-id` | Yes | Project ID or URL-encoded project path | - |
| `--state` | No | State of issues to delete: `opened`, `closed`, or `all` | `opened` |
| `--yes` | No | Skip confirmation prompt | `False` |

## Configuration File (Optional)

You can create a `config.ini` file to avoid typing credentials every time:

1. Copy the example configuration:
```bash
cp config.ini.example config.ini
```

2. Edit `config.ini` and fill in your values

**Note**: The `config.ini` file is gitignored for security. Never commit your tokens to version control!

## Examples

### Example 1: Delete all opened issues with confirmation
```bash
$ python delete_gitlab_issues.py --url https://gitlab.com --token glpat-xxxx --project-id 12345

Found 5 opened issue(s) in project 12345
Are you sure you want to delete 5 issue(s)? (yes/no): yes
Deleting issue #1: Bug in login feature
  ✓ Successfully deleted issue #1
Deleting issue #2: Feature request: Dark mode
  ✓ Successfully deleted issue #2
...

==================================================
Deletion Summary:
  Successfully deleted: 5
  Failed to delete: 0
==================================================
```

### Example 2: Delete all issues without confirmation
```bash
$ python delete_gitlab_issues.py --url https://gitlab.com --token glpat-xxxx --project-id 12345 --state all --yes

Found 10 all issue(s) in project 12345
Deleting issue #1: Bug in login feature
  ✓ Successfully deleted issue #1
...
```

## Security Considerations

⚠️ **Important Security Notes**:

- Never commit your GitLab token to version control
- Store your token securely (use environment variables or a secure secrets manager)
- The `config.ini` file is gitignored by default
- Limit token scope to only what's needed (`api` scope)
- Consider using project-specific tokens when possible
- Regularly rotate your tokens

## Troubleshooting

### "Error fetching issues: 401"
- Your token is invalid or expired
- Generate a new token with the `api` scope

### "Error fetching issues: 404"
- The project ID is incorrect
- You don't have access to the project
- Double-check the project ID or use the URL-encoded path

### "Error deleting issue: 403"
- You don't have permission to delete issues in this project
- Make sure you have at least Developer role in the project

## Limitations

- Requires API access to the GitLab instance
- Requires appropriate permissions in the project
- Rate limiting may apply for large numbers of issues
- Deleted issues cannot be recovered (use with caution!)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

⚠️ **Use at your own risk!** This tool permanently deletes issues from your GitLab projects. There is no undo operation. Always:
- Test on a non-production project first
- Make sure you have backups if needed
- Review the issues before confirming deletion
- Use the confirmation prompt (don't use `--yes` unless you're absolutely sure)

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Author

Created by Rafael Costa

## Changelog

### Version 1.0.0 (Initial Release)
- Basic issue deletion functionality
- Support for state filtering (opened, closed, all)
- Confirmation prompts
- Progress feedback and summary reports