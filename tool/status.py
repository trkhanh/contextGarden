#!/usr/bin/env python3
"""
Context Garden Sync Status Monitor
Displays sync status, queue information, and repository state.

Usage:
    python status.py --config sync_config.json
    python status.py --queue-status
    python status.py --repo-status
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class SyncStatusMonitor:
    """Monitor sync status and offline queues."""

    def __init__(self, config_path: str = "sync_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return json.load(f)

    def print_header(self, title: str):
        """Print formatted section header."""
        print(f"\n{'=' * 70}")
        print(f"🌿 {title}")
        print(f"{'=' * 70}\n")

    def show_config_summary(self):
        """Display configuration summary."""
        self.print_header("Configuration Summary")

        print("📦 Repositories:")
        for repo_name, repo_config in self.config["repositories"].items():
            status = "✅" if repo_config.get("enabled", True) else "❌"
            print(f"  {status} {repo_name}")
            print(f"     Path: {repo_config['local_path']}")
            print(f"     Remote: {repo_config.get('remote_url', 'N/A')}")

        print("\n📋 Sync Mappings:")
        for mapping in self.config["sync_mappings"]:
            print(f"  📂 {mapping['name']}")
            print(f"     Source: {mapping['source']}")
            for target in mapping["targets"]:
                status = "✅" if target.get("enabled", True) else "⏭️ "
                print(f"     {status} → {target['repo']}: {target['path']}")

    def show_queue_status(self):
        """Display offline queue status."""
        self.print_header("Offline Queue Status")

        queue_dir = Path(self.config["offline_mode"]["queue_dir"])

        if not queue_dir.exists():
            print("✅ No offline queues found")
            return

        queues = list(queue_dir.glob("queue_*.json"))
        if not queues:
            print("✅ No pending queues")
            return

        print(f"⏳ Found {len(queues)} pending queue(s):\n")

        for queue_file in sorted(queues):
            with open(queue_file, "r") as f:
                queue_data = json.load(f)

            timestamp = queue_data.get("timestamp", "unknown")
            syncs = queue_data.get("syncs", [])

            print(f"  📝 {queue_file.name}")
            print(f"     Timestamp: {timestamp}")
            print(f"     Pending syncs: {len(syncs)}")

            for sync in syncs[:3]:  # Show first 3
                print(f"       - {sync['mapping']} → {sync['target_repo']}")

            if len(syncs) > 3:
                print(f"       ... and {len(syncs) - 3} more")
            print()

        # Show archived queues
        archived_dir = queue_dir / "archived"
        if archived_dir.exists():
            archived = list(archived_dir.glob("queue_*.json"))
            if archived:
                print(f"📦 Archived: {len(archived)} completed queue(s)")

    def show_repo_status(self):
        """Display git repository status."""
        self.print_header("Repository Status")

        for repo_name, repo_config in self.config["repositories"].items():
            if not repo_config.get("enabled", True):
                print(f"⏭️  {repo_name} (disabled)")
                continue

            repo_path = Path(repo_config["local_path"])

            if not repo_path.exists():
                print(f"❌ {repo_name}")
                print(f"   Path not found: {repo_path}\n")
                continue

            print(f"✅ {repo_name}")
            print(f"   Path: {repo_path}")

            # Check git status
            git_dir = repo_path / ".git"
            if git_dir.exists():
                # Get current branch
                try:
                    import subprocess

                    result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    branch = result.stdout.strip() if result.returncode == 0 else "unknown"
                    print(f"   Branch: {branch}")

                    # Get last commit
                    result = subprocess.run(
                        ["git", "log", "-1", "--oneline"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    last_commit = result.stdout.strip() if result.returncode == 0 else "N/A"
                    print(f"   Last commit: {last_commit}")
                except Exception as e:
                    print(f"   Git info: Error - {e}")
            else:
                print(f"   ⚠️  Not a git repository")

            print()

    def show_sync_history(self):
        """Display sync history."""
        self.print_header("Sync History")

        history_dir = Path(self.config["sync_options"].get("history_dir", ".sync-history"))

        if not history_dir.exists():
            print("📋 No sync history found")
            return

        history_files = sorted(history_dir.glob("*.json"), reverse=True)[:10]

        if not history_files:
            print("📋 No sync records")
            return

        print(f"📊 Last 10 syncs:\n")

        for history_file in history_files:
            try:
                with open(history_file, "r") as f:
                    record = json.load(f)

                timestamp = record.get("timestamp", "unknown")
                status = record.get("status", "unknown")
                details = record.get("details", {})

                status_icon = "✅" if status == "success" else "❌"
                print(f"  {status_icon} {history_file.name} ({timestamp})")

                if isinstance(details, dict):
                    for key, value in list(details.items())[:3]:
                        print(f"       {key}: {value}")

            except Exception as e:
                print(f"  ❌ Error reading {history_file}: {e}")

    def show_disk_usage(self):
        """Estimate disk usage of sync operation."""
        self.print_header("Estimated Disk Usage")

        total_size = 0

        print("Source directories:\n")

        for mapping in self.config["sync_mappings"]:
            source_rel = mapping["source"]
            source_path = self.config_path.parent / source_rel

            if source_path.exists():
                size = self._get_directory_size(source_path)
                size_mb = size / (1024 * 1024)
                total_size += size

                print(f"  📂 {mapping['name']}")
                print(f"     Size: {size_mb:.2f} MB")

        total_mb = total_size / (1024 * 1024)
        print(f"\n📊 Total: {total_mb:.2f} MB")

    @staticmethod
    def _get_directory_size(path: Path) -> int:
        """Calculate directory size in bytes."""
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        except PermissionError:
            pass
        return total

    def show_health_check(self):
        """Run health check on sync configuration."""
        self.print_header("Health Check")

        issues = []

        # Check repositories exist
        for repo_name, repo_config in self.config["repositories"].items():
            repo_path = Path(repo_config["local_path"])
            if not repo_path.exists():
                issues.append(
                    f"❌ Repository '{repo_name}' path not found: {repo_path}"
                )

            git_dir = repo_path / ".git"
            if not git_dir.exists():
                issues.append(
                    f"⚠️  Repository '{repo_name}' is not a git repo: {repo_path}"
                )

        # Check source mappings
        for mapping in self.config["sync_mappings"]:
            source_rel = mapping["source"]
            source_path = self.config_path.parent / source_rel

            if not source_path.exists():
                issues.append(
                    f"⚠️  Source not found: {mapping['name']} ({source_path})"
                )

        if not issues:
            print("✅ All checks passed!")
            return

        print("Issues found:\n")
        for issue in issues:
            print(f"  {issue}")

    def show_full_report(self):
        """Display full diagnostic report."""
        self.show_config_summary()
        self.show_queue_status()
        self.show_repo_status()
        self.show_disk_usage()
        self.show_health_check()


def main():
    parser = argparse.ArgumentParser(
        description="Context Garden Sync Status Monitor"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="sync_config.json",
        help="Path to sync configuration file",
    )
    parser.add_argument(
        "--config-summary",
        action="store_true",
        help="Show configuration summary",
    )
    parser.add_argument(
        "--queue-status",
        action="store_true",
        help="Show offline queue status",
    )
    parser.add_argument(
        "--repo-status",
        action="store_true",
        help="Show repository status",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show sync history",
    )
    parser.add_argument(
        "--disk-usage",
        action="store_true",
        help="Show disk usage estimate",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run health check",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show full report (all checks)",
    )

    args = parser.parse_args()

    try:
        monitor = SyncStatusMonitor(args.config)

        if args.all:
            monitor.show_full_report()
        else:
            if args.config_summary:
                monitor.show_config_summary()
            if args.queue_status:
                monitor.show_queue_status()
            if args.repo_status:
                monitor.show_repo_status()
            if args.history:
                monitor.show_sync_history()
            if args.disk_usage:
                monitor.show_disk_usage()
            if args.health:
                monitor.show_health_check()

            # Show all by default if no specific option selected
            if not any(
                [
                    args.config_summary,
                    args.queue_status,
                    args.repo_status,
                    args.history,
                    args.disk_usage,
                    args.health,
                ]
            ):
                monitor.show_full_report()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
