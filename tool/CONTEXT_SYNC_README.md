# Context Garden Sync Tool

A Python tool for synchronizing Context Garden directories between local repositories and GitHub with comprehensive offline support.

## Overview

The Context Garden Sync tool enables:

✅ **Multi-Repository Sync** - Sync context from one source to multiple targets  
✅ **Configurable Mappings** - Define exactly which directories sync where  
✅ **Offline Mode** - Queue changes when offline, flush when reconnected  
✅ **Dry-Run Testing** - Preview changes before applying  
✅ **Git Integration** - Auto-commit and push with configurable messages  
✅ **Smart Deduplication** - Uses file hashing to skip unchanged files  
✅ **Conflict Resolution** - Configurable strategies for handling conflicts  

---

## Quick Start

### 1. Setup Configuration

Edit `sync_config.json` to define your repositories:

```json
{
  "repositories": {
    "company": {
      "local_path": "/path/to/company/repo",
      "remote_url": "git@github.com:company/contextgarden.git",
      "enabled": true
    }
  },
  "sync_mappings": [
    {
      "name": "Agents",
      "source": ".context/agents",
      "targets": [
        {
          "repo": "company",
          "path": "agents/",
          "enabled": true
        }
      ]
    }
  ]
}
```

### 2. Run in Dry-Run Mode

```bash
python context-sync.py --dry-run
```

**Output:**
```
[2026-04-09 10:30:45] INFO: = Loaded config from sync_config.json
[2026-04-09 10:30:45] INFO: = Context Garden Sync Started
[DRY-RUN] Would copy: /path/to/source/file.md → /path/to/target/file.md
```

### 3. Execute Sync

```bash
python context-sync.py
```

---

## Configuration Reference

### Repository Definition

```json
{
  "repositories": {
    "company": {
      "local_path": "/absolute/path/to/repo",
      "remote_url": "git@github.com:org/repo.git",
      "remote_branch": "main",
      "enabled": true
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `local_path` | Absolute path to local repository root |
| `remote_url` | GitHub SSH or HTTPS URL |
| `remote_branch` | Target branch (usually `main`) |
| `enabled` | Enable/disable this repository |

### Sync Mapping Definition

```json
{
  "sync_mappings": [
    {
      "name": "Agents & Commands",
      "source": ".context/agents",
      "targets": [
        {
          "repo": "company",
          "path": "agents/",
          "enabled": true
        },
        {
          "repo": "personal",
          "path": "skills/agents/",
          "enabled": false
        }
      ]
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `name` | Descriptive name for this sync group |
| `source` | Source path relative to repository root |
| `targets` | Array of target destinations |
| `targets[].repo` | Repository key from `repositories` section |
| `targets[].path` | Target path within repository |
| `targets[].enabled` | Enable/disable this target |

### Sync Options

```json
{
  "sync_options": {
    "dry_run": false,
    "verbose": true,
    "auto_commit": true,
    "commit_message_template": "sync: context garden updates - {timestamp}",
    "preserve_history": true,
    "ignore_patterns": [".DS_Store", "*.swp", ".git"],
    "conflict_strategy": "remote-wins"
  }
}
```

| Option | Description |
|--------|-------------|
| `dry_run` | Don't make actual changes (can override with `--dry-run` flag) |
| `verbose` | Enable detailed logging |
| `auto_commit` | Automatically git add/commit/push changes |
| `commit_message_template` | Template for commit messages (supports `{timestamp}`) |
| `preserve_history` | Keep historical sync records |
| `ignore_patterns` | Files/patterns to exclude from sync |
| `conflict_strategy` | How to handle conflicts: `remote-wins`, `local-wins`, `manual` |

---

## Usage Modes

### Mode 1: Standard Sync

Sync all enabled mappings and auto-commit:

```bash
python context-sync.py
```

### Mode 2: Dry-Run Preview

Preview all changes without applying:

```bash
python context-sync.py --dry-run
```

### Mode 3: Offline Queue

When offline, queue changes instead of syncing:

```bash
python context-sync.py --offline
```

Creates `.context-sync-queue/queue_20260409_103045.json` for later processing.

### Mode 4: Flush Offline Queue

When back online, process all queued syncs:

```bash
python context-sync.py --sync-queue
```

### Mode 5: Verbose Debugging

Enable detailed logging:

```bash
python context-sync.py --verbose
```

---

## Offline Mode

### How It Works

1. **Offline Phase**
   ```bash
   python context-sync.py --offline
   # Creates: .context-sync-queue/queue_TIMESTAMP.json
   ```

2. **Queue Storage**
   Queues are stored as JSON records in `.context-sync-queue/`:
   ```json
   {
     "timestamp": "2026-04-09T10:30:45",
     "syncs": [
       {
         "mapping": "Agents",
         "source": "/path/to/source",
         "target_repo": "company",
         "target_path": "agents/"
       }
     ]
   }
   ```

3. **Online Phase (when reconnected)**
   ```bash
   python context-sync.py --sync-queue
   # Processes all queued syncs and archives completed queues
   ```

### Configuration

```json
{
  "offline_mode": {
    "enabled": true,
    "queue_dir": ".context-sync-queue",
    "auto_sync_on_online": true
  }
}
```

---

## Examples

### Example 1: Company Context Sync

**Scenario:** Sync company context garden to GitHub and personal dev context

**Configuration:**
```json
{
  "repositories": {
    "company": {
      "local_path": "/home/user/company-repo/.context",
      "remote_url": "git@github.com:mycompany/contextgarden.git",
      "enabled": true
    }
  },
  "sync_mappings": [
    {
      "name": "All Context",
      "source": ".",
      "targets": [
        {
          "repo": "company",
          "path": "./",
          "enabled": true
        }
      ]
    }
  ]
}
```

**Execute:**
```bash
python context-sync.py --dry-run  # Preview
python context-sync.py            # Execute
```

### Example 2: Selective Sync with Multiple Repos

**Scenario:** Sync only specific directories to different target repos

**Configuration:**
```json
{
  "repositories": {
    "skills": {
      "local_path": "/home/user/dev/skills-repo",
      "remote_url": "git@github.com:org/skills.git",
      "enabled": true
    },
    "knowledge": {
      "local_path": "/home/user/dev/knowledge-base",
      "remote_url": "git@github.com:org/knowledge.git",
      "enabled": true
    }
  },
  "sync_mappings": [
    {
      "name": "Skills Only",
      "source": ".context/memory",
      "targets": [
        {
          "repo": "skills",
          "path": "knowledge/",
          "enabled": true
        }
      ]
    },
    {
      "name": "Defects & History",
      "source": ".context/defects",
      "targets": [
        {
          "repo": "knowledge",
          "path": "defects/",
          "enabled": true
        }
      ]
    }
  ]
}
```

### Example 3: Offline Field Work

**Scenario:** Developer working offline on multiple issues

**Phase 1 - Before going offline:**
```bash
# Queue all pending syncs
python context-sync.py --offline
# Generates: .context-sync-queue/queue_20260409_103045.json
```

**Phase 2 - Work offline:**
```bash
# Make edits to local context
vim .context/agents/custom-rules.md
vim .context/memory/domain-logic.md
```

**Phase 3 - Back online:**
```bash
# Flush all queued syncs
python context-sync.py --sync-queue
# Syncs all changes and archives the queue
```

---

## Advanced Features

### Smart File Deduplication

Files are compared using SHA256 hashing to avoid unnecessary copies:

```
Source: agents/commands.md (hash: abc123...)
Target: agents/commands.md (hash: abc123...)
➜ ⏭️  Skipped (identical)
```

### Versioned Sync Records

When `preserve_history` is enabled, each sync creates a record:

```json
{
  "timestamp": "2026-04-09T10:30:45",
  "source": ".context/agents",
  "target": "company:agents/",
  "status": "success",
  "files_synced": 12,
  "hash": "abc123..."
}
```

### Flexible Ignore Patterns

Exclude files from sync:

```json
{
  "ignore_patterns": [
    ".DS_Store",        # Specific file
    "*.swp",           # Glob patterns
    "node_modules",    # Directories
    ".git",
    "__pycache__"
  ]
}
```

### Conflict Resolution Strategies

- **`remote-wins`** (default): Remote version takes precedence
- **`local-wins`**: Local version takes precedence  
- **`manual`**: Requires manual resolution

---

## Troubleshooting

### Issue: "Not a git repository"

**Cause:** Target path isn't a git repository  
**Solution:**
```bash
# Initialize the target as a git repository
cd /target/path
git init
git add remote origin <url>
```

### Issue: "Push failed"

**Cause:** Network issue or authentication problem  
**Solution:**
```bash
# Test git connectivity
git clone <repo-url> /tmp/test-clone

# Check SSH keys
ssh -T git@github.com
```

### Issue: Offline queue not syncing

**Cause:** Offline mode may be disabled or queue directory missing  
**Solution:**
```bash
# Verify offline mode is enabled
cat sync_config.json | grep offline_mode -A 5

# Check queue directory
ls -la .context-sync-queue/
```

### Issue: File permissions errors

**Cause:** Insufficient write permissions  
**Solution:**
```bash
# Check directory permissions
ls -la /target/path

# Grant write permissions
chmod -R u+w /target/path
```

---

## Performance Tuning

### For Large Repositories

1. **Use `.gitignore`** in source to exclude unnecessary files
2. **Configure `ignore_patterns`** to skip large binary files
3. **Split mappings** into smaller groups for incremental syncs

```json
{
  "ignore_patterns": [
    "node_modules",
    "dist",
    "*.tar.gz",
    ".cache"
  ]
}
```

### For Multiple Large Syncs

Use worktrees for parallel syncs:
```bash
# Sync in parallel using git worktrees
git worktree add ../sync-worker-1 -b sync-branch-1
cd ../sync-worker-1
python context-sync.py --config sync_config.json
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Sync Context Garden

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run Context Sync
        run: python tool/context-sync.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## API Usage (Advanced)

```python
from context-sync import ContextGardenSync

# Initialize syncer
syncer = ContextGardenSync("sync_config.json", dry_run=False, verbose=True)

# Execute sync
results = syncer.sync_all()

# Access results
print(f"Success: {results['successful']}")
print(f"Failed: {results['failed']}")

# Queue for offline
queue_record = syncer.queue_for_offline()

# Flush offline queue
syncer.flush_offline_queue()
```

---

## Requirements

- Python 3.8+
- `git` command-line tool
- SSH or HTTPS credentials for GitHub access

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Maintained by:** Context Garden Team
