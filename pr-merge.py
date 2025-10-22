#!/usr/bin/env python3
"""
merge_prs_27_31.py

Merge PRs 27-31 from sparesparrow/openssl-tools into a single squashed commit
targeting master branch.

Usage:
    python merge_prs_27_31.py [--dry-run] [--non-interactive]

Requirements:
    - Run from within a git clone of the repository
    - git and gh CLI installed (or GITHUB_TOKEN env var for API)
    - Python 3.7+ with requests library (pip install requests)
"""

from __future__ import annotations
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None

# -------------------------
# Configuration
# -------------------------
OWNER = "sparesparrow"
REPO = "openssl-tools"
UPSTREAM_REMOTE = "upstream"
ORIGIN_REMOTE = "origin"
UPSTREAM_URL = f"git@github.com:{OWNER}/{REPO}.git"
BASE_BRANCH = "master"
PRIMARY_PR = 31
INCLUDE_PRS = [27, 28, 29, 30]  # PRs to merge into PR 31
WORK_BRANCH = "pr-31-merge-work"
PUSH_BRANCH = "pr-31-squashed"
AGENT_FIX_CMD = 'cursor-agent -f agent "fix conflicts and complete merge/rebase"'
AGENT_ACK_CMD = 'cursor-agent -f agent "use ack tool to test and fix all workflows"'
GITHUB_API_BASE = "https://api.github.com"

# -------------------------
# Utilities
# -------------------------
def run(cmd: str, cwd: Optional[str] = None, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command (string). Raises on non-zero when check True."""
    print(f"+ {cmd}")
    if capture:
        return subprocess.run(cmd, cwd=cwd, shell=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        return subprocess.run(cmd, cwd=cwd, shell=True, check=check)


def check_git_repo() -> None:
    try:
        run("git rev-parse --is-inside-work-tree", capture=False)
    except subprocess.CalledProcessError:
        print("ERROR: This script must be run from inside a git repository clone.", file=sys.stderr)
        sys.exit(2)


def git_remote_exists(name: str) -> bool:
    try:
        run(f"git remote get-url {shlex.quote(name)}", capture=True)
        return True
    except subprocess.CalledProcessError:
        return False


def ensure_remote(name: str, url: str) -> None:
    if not git_remote_exists(name):
        print(f"Adding remote {name} -> {url}")
        run(f"git remote add {shlex.quote(name)} {shlex.quote(url)}")


def fetch_all(upstream: str, origin: str) -> None:
    run(f"git fetch {shlex.quote(upstream)} --prune --tags")
    run(f"git fetch {shlex.quote(origin)} --prune --tags")


def fetch_pr_branch(remote: str, pr_num: int, fallback_remote: Optional[str] = None) -> str:
    """
    Fetch pull/<pr_num>/head into refs/heads/pr/<pr_num>.
    Returns the local branch ref name: refs/heads/pr/<pr_num>
    """
    local_branch = f"refs/heads/pr/{pr_num}"
    try:
        run(f"git fetch {shlex.quote(remote)} pull/{pr_num}/head:{local_branch}")
    except subprocess.CalledProcessError:
        if fallback_remote:
            run(f"git fetch {shlex.quote(fallback_remote)} pull/{pr_num}/head:{local_branch}")
        else:
            raise
    return local_branch


def run_cursor_agent(cmd: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[dry-run] would run: {cmd}")
        return
    print(f"Running cursor agent command: {cmd}")
    run(cmd)


def in_merge_or_rebase() -> Tuple[bool, str]:
    if os.path.exists(".git/MERGE_HEAD"):
        return True, "merge"
    if os.path.isdir(".git/rebase-apply") or os.path.isdir(".git/rebase-merge"):
        return True, "rebase"
    return False, ""


def staged_or_uncommitted() -> bool:
    cp = run("git status --porcelain", capture=True)
    return bool(cp.stdout.strip())


# -------------------------
# Git flow helpers
# -------------------------
def create_work_branch_from(local_pr_ref: str, work_branch: str, force: bool = True) -> None:
    if force and branch_exists(work_branch):
        run(f"git branch -D {shlex.quote(work_branch)}")
    run(f"git checkout -b {shlex.quote(work_branch)} {shlex.quote(local_pr_ref)}")


def branch_exists(name: str) -> bool:
    cp = run(f"git show-ref --verify --quiet refs/heads/{shlex.quote(name)}", check=False, capture=False)
    return cp.returncode == 0


def merge_branch(local_branch: str, dry_run: bool = False) -> None:
    cmd = f"git merge --no-ff --no-edit {shlex.quote(local_branch)}"
    if dry_run:
        print("[dry-run] would run:", cmd)
        return
    try:
        run(cmd)
        print(f"Merge of {local_branch} succeeded.")
    except subprocess.CalledProcessError:
        print(f"Merge of {local_branch} returned non-zero (likely conflicts).")
        raise


def finish_merge_or_rebase_after_agent(dry_run: bool = False) -> None:
    in_state, state = in_merge_or_rebase()
    if in_state:
        print(f"Detected {state} in progress; attempting to finalize.")
        if state == "merge":
            run("git add -A")
            try:
                run('git commit --no-edit')
            except subprocess.CalledProcessError:
                run('git commit -m "Merge conflicts resolved by cursor-agent"')
        else:
            try:
                run("git rebase --continue")
            except subprocess.CalledProcessError:
                run("git add -A")
                run("git rebase --continue")
    else:
        if staged_or_uncommitted():
            run("git add -A")
            run('git commit -m "Conflict resolution edits by cursor-agent"')


def compute_merge_base(upstream_master: str, branch: str) -> str:
    cp = run(f"git merge-base {shlex.quote(upstream_master)} {shlex.quote(branch)}", capture=True)
    return cp.stdout.strip()


# -------------------------
# GitHub helpers
# -------------------------
def create_pr_with_gh_cli(remote: str, branch: str, base: str, title: str, body: str = "") -> Optional[dict]:
    """Fallback PR creation via GitHub CLI 'gh' if available."""
    if shutil.which("gh") is None:
        return None
    run(f"git push -u {shlex.quote(remote)} {shlex.quote(branch)}")
    head_ref = f"{remote}:{branch}"
    try:
        cp = run(f"gh pr create --head {shlex.quote(head_ref)} --base {shlex.quote(base)} --title {shlex.quote(title)} --body {shlex.quote(body)} --json url", capture=True)
        parsed = json.loads(cp.stdout.strip())
        return parsed
    except subprocess.CalledProcessError:
        print("gh pr create failed; please create PR manually.", file=sys.stderr)
        return None


def create_github_pr(owner: str, repo: str, head: str, base: str, title: str, body: str = "", token: Optional[str] = None) -> dict:
    """Create a PR via API."""
    if requests is None:
        raise RuntimeError("requests is required to create PR via GitHub API.")
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()


def get_current_user_login_from_token(token: str) -> Optional[str]:
    if requests is None:
        return None
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(f"{GITHUB_API_BASE}/user", headers=headers)
    if r.status_code == 200:
        return r.json().get("login")
    return None


# -------------------------
# Main execution flow
# -------------------------
def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        prog="merge_prs_27_31.py",
        description=f"Merge PRs {INCLUDE_PRS} into PR {PRIMARY_PR} targeting {BASE_BRANCH}."
    )
    parser.add_argument("--dry-run", action="store_true", help="Show actions without executing changes.")
    parser.add_argument("--non-interactive", action="store_true", help="Do not prompt for confirmations.")
    parser.add_argument("--push-force", action="store_true", default=True, help="Force push final squashed branch (default: True).")
    args = parser.parse_args(argv)

    check_git_repo()

    # Setup remotes
    ensure_remote(UPSTREAM_REMOTE, UPSTREAM_URL)
    fetch_all(UPSTREAM_REMOTE, ORIGIN_REMOTE)

    github_token = os.getenv("GITHUB_TOKEN")

    print(f"Primary PR: {PRIMARY_PR}")
    print(f"Including PRs: {INCLUDE_PRS}")
    print(f"Target base: {BASE_BRANCH}")
    print(f"Work branch: {WORK_BRANCH}")
    print(f"Push branch: {PUSH_BRANCH}")
    print("")

    # Fetch all PRs
    all_prs = [PRIMARY_PR] + INCLUDE_PRS
    for p in all_prs:
        try:
            fetch_pr_branch(UPSTREAM_REMOTE, p, fallback_remote=ORIGIN_REMOTE)
        except Exception as e:
            print(f"ERROR: failed to fetch PR #{p}: {e}", file=sys.stderr)
            sys.exit(5)

    # Create work branch from primary PR
    create_work_branch_from(f"refs/heads/pr/{PRIMARY_PR}", WORK_BRANCH, force=True)

    # Merge included PRs one-by-one
    for p in INCLUDE_PRS:
        local_ref = f"refs/heads/pr/{p}"
        try:
            merge_branch(local_ref, dry_run=args.dry_run)
        except subprocess.CalledProcessError:
            print(f"Conflicts detected while merging PR {p}. Invoking agent to fix conflicts.")
            run_cursor_agent(AGENT_FIX_CMD, dry_run=args.dry_run)
            if not args.dry_run:
                finish_merge_or_rebase_after_agent(dry_run=False)

    # Squash all changes onto single commit rebased on upstream/master
    upstream_master_ref = f"{UPSTREAM_REMOTE}/{BASE_BRANCH}"
    print(f"Fetching latest {upstream_master_ref}")
    run(f"git fetch {shlex.quote(UPSTREAM_REMOTE)} {shlex.quote(BASE_BRANCH)}:refs/remotes/{shlex.quote(UPSTREAM_REMOTE)}/{shlex.quote(BASE_BRANCH)}", check=True)

    merge_base = compute_merge_base(f"{UPSTREAM_REMOTE}/{BASE_BRANCH}", WORK_BRANCH)
    print(f"Computed merge-base (fork point): {merge_base}")

    # Create temporary branch from upstream master
    ts = int(time.time())
    temp_branch = f"tmp/{WORK_BRANCH}-squash-{ts}"
    print(f"Creating temporary branch {temp_branch} from {upstream_master_ref}")
    run(f"git checkout -b {shlex.quote(temp_branch)} {shlex.quote(upstream_master_ref)}")

    # Attempt squash-merge
    COMMIT_MSG = f"Squashed changes: PR {PRIMARY_PR} + PRs {INCLUDE_PRS} (rebased on {upstream_master_ref})"
    try:
        if args.dry_run:
            print(f"[dry-run] git merge --squash {WORK_BRANCH}")
        else:
            run(f"git merge --squash {shlex.quote(WORK_BRANCH)}")
    except subprocess.CalledProcessError:
        print("Squash merge had conflicts. Calling agent to resolve.")
        run_cursor_agent(AGENT_FIX_CMD, dry_run=args.dry_run)
        if not args.dry_run:
            finish_merge_or_rebase_after_agent(dry_run=False)

    # Commit squashed changes
    if args.dry_run:
        print("[dry-run] would commit squashed changes")
    else:
        if run("git diff --cached --quiet", check=False).returncode == 0:
            print("No changes to commit after squash. Exiting early.")
            run(f"git checkout {shlex.quote(WORK_BRANCH)}")
            run(f"git branch -D {shlex.quote(temp_branch)}", check=False)
            sys.exit(0)
        run(f'git commit -m {shlex.quote(COMMIT_MSG)}')

    # Push final single commit to origin
    if args.dry_run:
        print(f"[dry-run] would push {temp_branch} to {ORIGIN_REMOTE}:{PUSH_BRANCH} (force: {args.push_force})")
    else:
        push_cmd = f"git push {'--force' if args.push_force else ''} {shlex.quote(ORIGIN_REMOTE)} refs/heads/{shlex.quote(temp_branch)}:refs/heads/{shlex.quote(PUSH_BRANCH)}"
        run(push_cmd)

    # Run ack agent to test workflows
    print("Invoking ack agent to test and fix workflows.")
    run_cursor_agent(AGENT_ACK_CMD, dry_run=args.dry_run)

    # Create GitHub PR targeting upstream base
    title = f"Merged PRs {PRIMARY_PR} and {', '.join(map(str, INCLUDE_PRS))}"
    body = f"""Auto-created PR with squashed changes from:
- PR #{PRIMARY_PR}
- PR #{', #'.join(map(str, INCLUDE_PRS))}

Target branch: {BASE_BRANCH}

This branch was created and squashed by merge_prs_27_31.py."""

    pr_result = None
    # Try gh CLI first
    gh_result = None
    try:
        gh_result = create_pr_with_gh_cli(ORIGIN_REMOTE, temp_branch, BASE_BRANCH, title, body)
    except Exception:
        gh_result = None

    if gh_result:
        print("Created PR using gh CLI:")
        print(json.dumps(gh_result, indent=2))
        pr_result = gh_result
    else:
        # Try direct API if token present
        if github_token and requests is not None:
            user_login = get_current_user_login_from_token(github_token)
            head = f"{user_login}:{PUSH_BRANCH}" if user_login else PUSH_BRANCH
            try:
                pr = create_github_pr(OWNER, REPO, head=head, base=BASE_BRANCH, title=title, body=body, token=github_token)
                print("Created PR via GitHub API:")
                print(pr.get("html_url") or pr)
                pr_result = pr
            except Exception as e:
                print(f"Failed to create PR via GitHub API: {e}", file=sys.stderr)
                print(f"You can create the PR manually from branch: {ORIGIN_REMOTE}/{PUSH_BRANCH}")
        else:
            print(f"No gh CLI or GITHUB_TOKEN/requests available; please create PR manually from branch: {ORIGIN_REMOTE}/{PUSH_BRANCH}")

    print(f"Cleanup: returning to work branch: {WORK_BRANCH}")
    run(f"git checkout {shlex.quote(WORK_BRANCH)}")
    print("Done.")
    print("")
    print("Next steps:")
    print("1. Review the created PR")
    print(f"2. The squashed branch is at: {ORIGIN_REMOTE}/{PUSH_BRANCH}")
    print(f"3. To cleanup temp branch: git branch -D {temp_branch}")


if __name__ == "__main__":
    main()

