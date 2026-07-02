# Context Garden Sync - Getting Started

Quick start guide for syncing your company's context garden to GitHub offline.

---

## What This Tool Does

Sync your Context Garden directory structure from your local machine to GitHub, with **full offline support**:

```
Your Local Context          GitHub Repo
/.context/agents/    ───→   /agents/
/.context/memory/    ───→   /memory/
/.context/rules/     ───→   /rules/
/.context/defects/   ───→   /defects/
/.context/goals/     ───→   /goals/
/.context/techdebt/  ───→   /techdebt/
/.context/sessions/  ───→   /sessions/
```

**Offline Support:**
- Queue changes when disconnected
- Flush all queued syncs when back online
- No lost work

---

## Setup (5 minutes)

### Step 1: Copy Configuration

```bash
cd tool/

# Copy example config
cp sync_config.example.json sync_config.json
```

### Step 2: Edit Configuration

Edit `sync_config.json` to match your setup:

```bash
vim sync_config.json
```

**Key edits:**

```json
{
  "repositories": {
    "company-context": {
      "local_path": "/path/to/YOUR/company/repo/.context",  // ← YOUR PATH
      "remote_url": "git@github.com:your-company/contextgarden.git",  // ← YOUR REPO
      "enabled": true
    }
  }
}
```

### Step 3: Validate Configuration

```bash
# Check configuration is valid
python3 status.py --config sync_config.json --health
```

**Should show:**
```
✅ All checks passed!
```

---

## First Sync (Test)

### Step 1: Dry-Run (Preview Changes)

```bash
python3 context-sync.py --dry-run
```

**Output shows:**
```
[DRY-RUN] Would copy: .context/agents/commands.md → /target/agents/commands.md
[DRY-RUN] Would copy: .context/memory/architecture.md → /target/memory/architecture.md
...
```

✅ No actual changes made - just preview

### Step 2: Execute Sync

```bash
python3 context-sync.py
```

**Output shows:**
```
✅ Successful: 42
❌ Failed: 0
⏭️  Skipped: 0
```

### Step 3: Verify in GitHub

```bash
# Check git log
cd /path/to/company/repo
git log --oneline

# Should show new commit:
# abc1234 sync: context garden updates - 2026-04-09T10:30:45
```

---

## Daily Workflow

### Morning: Sync Local Changes

```bash
# Sync all context updates
python3 context-sync.py

# Verify status
python3 status.py --all
```

### During Work: Update Your Context

Edit files normally:

```bash
# Edit domain logic
vim .context/memory/domain-logic.md

# Add a defect record
vim .context/defects/004-new-issue.md

# Update rules
vim .context/rules/code-style.md
```

### Evening: Push Changes

```bash
# Sync everything to GitHub
python3 context-sync.py
```

---

## Offline Workflow

### Before Going Offline

```bash
# Queue all changes for later
python3 context-sync.py --offline

# Creates: .context-sync-queue/queue_20260409_103045.json
# ✅ Ready to work offline
```

### Work Offline

Make edits as normal:

```bash
# Your changes are stored locally
vim .context/agents/custom-commands.md
vim .context/memory/offline-notes.md
```

### When Back Online

```bash
# Flush all queued syncs to GitHub
python3 context-sync.py --sync-queue

# All your offline changes now synced! ✅
```

---

## Monitoring & Status

### Check Everything

```bash
python3 status.py --all
```

Shows:
- ✅ Configuration details
- 📦 Repository status  
- ⏳ Offline queues
- 📊 Disk usage
- 🏥 Health check

### Specific Checks

```bash
# Queue status only
python3 status.py --queue-status

# Repository git status
python3 status.py --repo-status

# Health check
python3 status.py --health
```

---

## Multiple Repository Setup

If syncing to **multiple target repos**:

### Configuration

```json
{
  "repositories": {
    "company-main": {
      "local_path": "/path/to/company-repo",
      "remote_url": "git@github.com:company/contextgarden.git",
      "enabled": true
    },
    "research-repo": {
      "local_path": "/path/to/research-repo",
      "remote_url": "git@github.com:company/research.git",
      "enabled": true
    }
  },
  "sync_mappings": [
    {
      "name": "All Context",
      "source": ".context",
      "targets": [
        {
          "repo": "company-main",
          "path": "./",
          "enabled": true
        },
        {
          "repo": "research-repo", 
          "path": "context/",
          "enabled": true
        }
      ]
    }
  ]
}
```

### Sync

```bash
# Syncs to BOTH repositories automatically
python3 context-sync.py
```

---

## Practical Examples

### Example 1: Sync After Bug Fix

```bash
# You fixed a bug, document it
vim .context/defects/042-broken-settlement.md

# Push to GitHub
python3 context-sync.py

# Verify
grep "settlement" /target/defects/042-broken-settlement.md
```

### Example 2: Update Coding Guidelines

```bash
# Improve your code rules
vim .context/rules/code-style.md

# Sync all changes (including other edits)
python3 context-sync.py

# GitHub now has latest guidelines ✅
```

### Example 3: Field Work (No Internet)

**Morning (has internet):**
```bash
# Queue work
python3 context-sync.py --offline
```

**During Day (no internet):**
```bash
# Edit context as much as needed
vim .context/agents/*.md
vim .context/goals/*.md
# All changes saved locally
```

**Evening (has internet):**
```bash
# Everything syncs automatically
python3 context-sync.py --sync-queue
```

---

## Troubleshooting

### Problem: "Repository not found"

```
❌ Repository 'company-context' path not found
```

**Fix:**
```bash
# Edit config with correct path
vim sync_config.json
# Update: "local_path": "/actual/path/to/repo"
```

### Problem: "Not a git repository"  

```
⚠️  Repository 'company-context' is not a git repo
```

**Fix:**
```bash
# Initialize as git repo
cd /path/to/repo
git init
git remote add origin git@github.com:company/contextgarden.git
```

### Problem: SSH permission denied

```
❌ Push failed: Permission denied (publickey)
```

**Fix:**
```bash
# Test SSH connection
ssh -T git@github.com

# If fails, add SSH key
ssh-keygen -t ed25519 -C "your@email.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Problem: Files not syncing

```bash
# Check health
python3 status.py --health

# Check file paths exist
python3 status.py --config-summary

# Try dry-run to debug
python3 context-sync.py --dry-run
```

---

## Advanced Usage

### Selective Sync

Sync only specific mappings:

```json
{
  "sync_mappings": [
    {
      "name": "Rules Only",
      "source": ".context/rules",
      "targets": [
        {
          "repo": "company-context",
          "path": "rules/",
          "enabled": true          // ← Only this syncs
        }
      ]
    },
    {
      "name": "Goals",
      "source": ".context/goals",
      "targets": [
        {
          "repo": "company-context",
          "path": "goals/",
          "enabled": false         // ← This is skipped
        }
      ]
    }
  ]
}
```

### Ignore Patterns

Exclude files from sync:

```json
{
  "sync_options": {
    "ignore_patterns": [
      ".DS_Store",
      "*.swp",
      "node_modules",
      ".env",
      "private/*"
    ]
  }
}
```

### Custom Commit Messages

```json
{
  "sync_options": {
    "commit_message_template": "[CONTEXT] {timestamp} - automated sync"
  }
}
```

### Conflict Resolution

```json
{
  "sync_options": {
    "conflict_strategy": "remote-wins"  // or "local-wins", "manual"
  }
}
```

---

## Integration with Your Workflow

### Schedule Automatic Syncs

```bash
# Add to crontab (syncs every 2 hours)
crontab -e

# Add line:
0 */2 * * * cd /path/to/tool && python3 context-sync.py >> /tmp/sync.log 2>&1
```

### Git Alias

```bash
# Add to ~/.gitconfig
[alias]
    context-sync = "!python3 /path/to/tool/context-sync.py"
    context-status = "!python3 /path/to/tool/status.py --all"
```

**Usage:**
```bash
git context-sync         # Sync changes
git context-status       # Check status
```

---

## File Reference

| File | Purpose |
|------|---------|
| `context-sync.py` | Main sync engine |
| `status.py` | Monitoring & diagnostics |
| `sync_config.json` | Your configuration |
| `sync_config.example.json` | Example template |
| `setup-sync.sh` | One-click setup |
| `CONTEXT_SYNC_README.md` | Full documentation |

---

## Need Help?

### Check Logs

```bash
# View sync history
python3 status.py --history

# Check for errors
cat .context-sync-logs/sync.log
```

### Debug Mode

```bash
# Verbose output
python3 context-sync.py --verbose

# Dry-run to preview
python3 context-sync.py --dry-run
```

### Common Commands

```bash
# Full sync
python3 context-sync.py

# Queue for offline
python3 context-sync.py --offline

# Flush offline queue
python3 context-sync.py --sync-queue

# Check status
python3 status.py --all

# Health check
python3 status.py --health
```

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Quick Start Time:** ~5 minutes
