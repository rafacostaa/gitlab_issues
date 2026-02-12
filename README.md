# GitLab Issue Deleter v3 🚀

A high-performance Python script for bulk deletion of GitLab issues using parallel processing with threads. This tool can delete thousands of issues quickly and efficiently via the GitLab API.

## ⚡ Features

- **Ultra-fast parallel deletion** using multi-threading (5-20 concurrent threads)
- **Multiple selection methods**:
  - Delete by ID range (e.g., #1001 to #36000)
  - Filter by labels, creation dates, and state
  - Delete individual issues
- **Fast mode**: Delete directly without fetching issue details first
- **Automatic retry** on connection errors
- **Real-time progress tracking** with statistics
- **SSL verification control** for self-hosted GitLab instances
- **Thread-safe operations** with proper locking

## 📋 Requirements

```bash
pip install requests
```

Python 3.7+ required (uses type hints and concurrent.futures)

## 🔧 Configuration

The script will interactively prompt you for:

1. **GitLab URL** - Base URL of your GitLab instance (e.g., `https://gitlab.com`)
2. **Private Token** - Your GitLab personal access token with API permissions
3. **Project ID** - Project ID (number) or namespace/project-name format
4. **SSL Verification** - Whether to verify SSL certificates (useful for self-hosted instances)
5. **Thread Count** - Number of parallel threads (5-20 recommended, default: 10)

### Creating a GitLab Personal Access Token

1. Go to GitLab → Settings → Access Tokens
2. Create a token with `api` scope
3. Copy the token for use with this script

## 🚀 Usage

Run the script:

```bash
python3 main.py
```

### Selection Methods

#### 1️⃣ Delete by ID Range

Delete issues within a specific range of IDs:

- Choose option `1`
- Enter start and end IID (Internal ID)
- **Fast Mode** (recommended): Skip fetching issue details and delete directly
- **Preview Mode**: Fetch issues first to preview before deletion

**Example**: Delete issues #1001 through #36000

#### 2️⃣ Delete by Filters

Filter issues by specific criteria:

- **Labels**: Comma-separated list of labels
- **Creation Date**: Filter by created_after and/or created_before (YYYY-MM-DD format)
- **State**: `opened`, `closed`, or `all`
- **Max Pages**: Limit the number of API result pages (100 issues per page)

**Example**: Delete all issues with label "bug" created in January 2026

#### 3️⃣ Delete Single Issue

Delete one specific issue by its IID.

## 📊 Performance

- **Parallel Processing**: Uses ThreadPoolExecutor for concurrent deletions
- **Configurable Workers**: 5-20 threads (default: 10)
- **Estimated Speed**: ~2 deletions per second per thread
- **Example**: 1000 issues with 10 threads ≈ 50 seconds

### Progress Tracking

The script displays:
- Current progress (completed/total)
- Success and failure counts
- Deletion rate (issues/second)
- Estimated time remaining

## ⚠️ Safety Features

- **Confirmation Required**: Must type "SIM" (uppercase) to confirm bulk deletion
- **Preview**: Shows issue IDs or titles before deletion (up to 20 issues)
- **Retry Logic**: Automatic retry on connection errors
- **Error Handling**: Reports failed deletions with IID list
- **Irreversible Warning**: Clear warning that deletions cannot be undone

## 📈 Output Example

```
🚀 Deletando 1000 issues com 10 threads paralelas...
⏱️  Tempo estimado: ~50 segundos

[50/1000] ✓ 48 | ✗ 2 | ⚡ 2.1/s | ⏱️ 45s restantes
[100/1000] ✓ 97 | ✗ 3 | ⚡ 2.2/s | ⏱️ 40s restantes
...

⏱️  Tempo total: 47.3 segundos (0.8 minutos)

======================================================================
📈 RESULTADOS FINAIS:
  Total: 1000
  ✓ Sucesso: 985 (98.5%)
  ✗ Falhas: 15
======================================================================
```

## 🔄 Multiple Operations

After each deletion operation, you can:
- Delete more issues without re-entering credentials
- View updated project statistics
- Continue with different selection methods

## 🛡️ Error Handling

- **Connection Errors**: Automatic retry with exponential backoff
- **SSL Warnings**: Suppressed when SSL verification is disabled
- **Keyboard Interrupt**: Graceful shutdown on Ctrl+C
- **Failed Deletions**: Tracked and reported separately

## ⚙️ Class: GitLabIssueDeleterFast

### Methods

- `__init__()` - Initialize with GitLab credentials
- `get_project_info()` - Fetch project details and issue counts
- `list_issues_by_id_range()` - Fetch issues in an ID range (parallel)
- `list_issues_by_filter()` - Fetch issues matching filters
- `delete_issue()` - Delete a single issue
- `delete_issues_parallel()` - Delete multiple issues using threads

## 📝 Notes

- **API Rate Limits**: Be aware of your GitLab instance's API rate limits
- **Permissions**: Requires project maintainer/owner permissions
- **Backups**: Always backup important data before bulk deletion
- **Testing**: Test with a small range first to verify configuration

## ⚠️ Warning

**This script performs IRREVERSIBLE deletions.** Deleted issues cannot be recovered. Always double-check your selection criteria and confirm the issue count before proceeding.

## 📄 License

This script is provided as-is for educational and utility purposes.

---

**Version**: 3.0 (Ultra-Fast Parallel Processing)
