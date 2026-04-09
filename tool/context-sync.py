#!/usr/bin/env python3
"""
Context Garden Sync Tool
Syncs context directories between local and GitHub repositories with offline support.

Usage:
    python context-sync.py --config sync_config.json
    python context-sync.py --config sync_config.json --dry-run
    python context-sync.py --config sync_config.json --sync-queue
"""

import os
import sys
import json
import shutil
import argparse
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class SyncStatus(Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SyncRecord:
    source: str
    target: str
    timestamp: str
    status: str
    message: str = ""
    file_hash: str = ""


class ContextGardenSync:
    """Main synchronization engine for Context Garden repositories."""

    def __init__(self, config_path: str, dry_run: bool = False, verbose: bool = True):
        self.config_path = Path(config_path)
        self.dry_run = dry_run
        self.verbose = verbose
        self.config = self._load_config()
        self.sync_records: List[SyncRecord] = []
        self.base_dir = self.config_path.parent

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config = json.load(f)

        self._log(f"✅ Loaded config from {self.config_path}")
        return config

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self._log(f"Failed to hash {file_path}: {e}", "WARN")
            return ""

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file matches ignore patterns."""
        ignore_patterns = self.config["sync_options"]["ignore_patterns"]
        file_name = file_path.name

        for pattern in ignore_patterns:
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(file_name, pattern):
                    return True
            elif pattern in str(file_path):
                return True

        return False

    def _copy_file(self, source: Path, target: Path) -> bool:
        """Copy file from source to target."""
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            self._log(f"📋 Copied: {source} → {target}")
            return True
        except Exception as e:
            self._log(f"❌ Failed to copy {source}: {e}", "ERROR")
            return False

    def _sync_directory(self, source_dir: Path, target_dir: Path) -> Tuple[int, int]:
        """
        Recursively sync a directory tree.
        
        Returns: (success_count, failed_count)
        """
        success_count = 0
        failed_count = 0

        if not source_dir.exists():
            self._log(f"⚠️  Source directory not found: {source_dir}", "WARN")
            return 0, 1

        for source_file in source_dir.rglob("*"):
            if source_file.is_file() and not self._should_ignore(source_file):
                # Calculate relative path
                rel_path = source_file.relative_to(source_dir)
                target_file = target_dir / rel_path

                # Check if copy is needed (hash comparison)
                if target_file.exists():
                    source_hash = self._get_file_hash(source_file)
                    target_hash = self._get_file_hash(target_file)

                    if source_hash == target_hash:
                        self._log(
                            f"⏭️  Skipped (identical): {source_file.name}",
                            "DEBUG",
                        )
                        continue

                if not self.dry_run:
                    if self._copy_file(source_file, target_file):
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    self._log(f"[DRY-RUN] Would copy: {source_file} → {target_file}")
                    success_count += 1

        return success_count, failed_count

    def _git_commit_push(self, repo_path: Path, commit_message: str) -> bool:
        """Perform git add, commit, and push."""
        try:
            os.chdir(repo_path)

            # Check if we're already in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5,
            )

            if result.returncode != 0:
                self._log(
                    f"⚠️  {repo_path} is not a git repository", "WARN"
                )
                return False

            if not self.dry_run:
                # Add changes
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=repo_path,
                    capture_output=True,
                    timeout=10,
                )

                # Check if there are changes to commit
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if not status.stdout.strip():
                    self._log("ℹ️  No changes to commit", "INFO")
                    return True

                # Commit
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=repo_path,
                    capture_output=True,
                    timeout=10,
                )

                # Push
                push_result = subprocess.run(
                    ["git", "push"],
                    cwd=repo_path,
                    capture_output=True,
                    timeout=30,
                )

                if push_result.returncode == 0:
                    self._log(f"✅ Pushed to {repo_path}")
                    return True
                else:
                    error = push_result.stderr.decode()
                    self._log(f"❌ Push failed: {error}", "ERROR")
                    return False
            else:
                self._log(f"[DRY-RUN] Would commit and push to {repo_path}")
                return True

        except subprocess.TimeoutExpired:
            self._log(f"❌ Git operation timed out in {repo_path}", "ERROR")
            return False
        except Exception as e:
            self._log(f"❌ Git operation failed: {e}", "ERROR")
            return False

    def sync_all(self) -> Dict[str, any]:
        """Execute full synchronization based on config."""
        self._log("=" * 60)
        self._log("🌿 Context Garden Sync Started")
        self._log(f"Dry Run: {self.dry_run}")
        self._log("=" * 60)

        results = {
            "total_syncs": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
        }

        for mapping in self.config["sync_mappings"]:
            mapping_name = mapping["name"]
            source_rel = mapping["source"]
            source_path = self.base_dir / source_rel

            self._log(f"\n📦 Syncing: {mapping_name}")
            self._log(f"   Source: {source_path}")

            for target in mapping["targets"]:
                if not target["enabled"]:
                    self._log(f"   ⏭️  Skipped (disabled): {target['repo']}")
                    results["skipped"] += 1
                    continue

                repo_name = target["repo"]
                repo_config = self.config["repositories"][repo_name]

                if not repo_config["enabled"]:
                    self._log(f"   ⏭️  Skipped (repo disabled): {repo_name}")
                    results["skipped"] += 1
                    continue

                target_repo_path = Path(repo_config["local_path"])
                target_rel = target["path"]
                target_path = target_repo_path / target_rel

                self._log(f"   → {repo_name}: {target_path}")

                # Sync the directory
                success, failed = self._sync_directory(source_path, target_path)

                results["total_syncs"] += 1
                results["successful"] += success
                results["failed"] += failed

                # Git commit if configured
                if self.config["sync_options"]["auto_commit"]:
                    commit_msg = self.config["sync_options"][
                        "commit_message_template"
                    ].format(timestamp=datetime.now().isoformat())

                    if self._git_commit_push(target_repo_path, commit_msg):
                        results["details"].append(
                            {
                                "mapping": mapping_name,
                                "target": repo_name,
                                "status": "success",
                            }
                        )
                    else:
                        results["details"].append(
                            {
                                "mapping": mapping_name,
                                "target": repo_name,
                                "status": "failed",
                            }
                        )

        self._print_summary(results)
        return results

    def _print_summary(self, results: Dict):
        """Print synchronization summary."""
        self._log("\n" + "=" * 60)
        self._log("📊 Sync Summary")
        self._log("=" * 60)
        self._log(f"✅ Successful: {results['successful']}")
        self._log(f"❌ Failed: {results['failed']}")
        self._log(f"⏭️  Skipped: {results['skipped']}")
        self._log(f"📦 Total Syncs: {results['total_syncs']}")
        self._log("=" * 60)

    def queue_for_offline(self) -> Dict:
        """Queue changes for offline mode."""
        queue_dir = Path(self.config["offline_mode"]["queue_dir"])
        queue_dir.mkdir(exist_ok=True)

        queue_record = {
            "timestamp": datetime.now().isoformat(),
            "syncs": [],
        }

        for mapping in self.config["sync_mappings"]:
            source_rel = mapping["source"]
            source_path = self.base_dir / source_rel

            for target in mapping["targets"]:
                if not target["enabled"]:
                    continue

                repo_name = target["repo"]
                target_rel = target["path"]

                queue_record["syncs"].append(
                    {
                        "mapping": mapping["name"],
                        "source": str(source_path),
                        "target_repo": repo_name,
                        "target_path": target_rel,
                    }
                )

        # Write queue record
        queue_file = queue_dir / f"queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(queue_file, "w") as f:
            json.dump(queue_record, f, indent=2)

        self._log(f"📝 Queued for offline sync: {queue_file}")
        return queue_record

    def flush_offline_queue(self) -> Dict:
        """Process queued offline syncs."""
        queue_dir = Path(self.config["offline_mode"]["queue_dir"])

        if not queue_dir.exists():
            self._log("ℹ️  No offline queue found", "INFO")
            return {}

        results = {"processed": 0, "failed": 0}

        for queue_file in sorted(queue_dir.glob("queue_*.json")):
            with open(queue_file, "r") as f:
                queue_record = json.load(f)

            self._log(f"📋 Processing queue: {queue_file.name}")

            for sync in queue_record["syncs"]:
                source = Path(sync["source"])
                repo_name = sync["target_repo"]
                target_rel = sync["target_path"]

                if repo_name not in self.config["repositories"]:
                    continue

                target_repo_path = Path(
                    self.config["repositories"][repo_name]["local_path"]
                )
                target_path = target_repo_path / target_rel

                success, _ = self._sync_directory(source, target_path)

                if success > 0:
                    results["processed"] += 1
                else:
                    results["failed"] += 1

            # Archive processed queue
            archive_dir = queue_dir / "archived"
            archive_dir.mkdir(exist_ok=True)
            shutil.move(str(queue_file), str(archive_dir / queue_file.name))

        self._log(f"✅ Flushed offline queue: {results['processed']} syncs")
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Context Garden Sync Tool - Sync context directories to GitHub"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="sync_config.json",
        help="Path to sync configuration file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making actual changes",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Queue changes for offline mode",
    )
    parser.add_argument(
        "--sync-queue",
        action="store_true",
        help="Flush offline sync queue",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        syncer = ContextGardenSync(
            args.config, dry_run=args.dry_run, verbose=args.verbose
        )

        if args.sync_queue:
            syncer.flush_offline_queue()
        elif args.offline:
            syncer.queue_for_offline()
        else:
            syncer.sync_all()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
