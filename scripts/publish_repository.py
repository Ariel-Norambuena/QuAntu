#!/usr/bin/env python3
"""Publish this reviewed checkout as Ariel-Norambuena/QuAntu, public.

Requires an authenticated GitHub CLI and an existing local main commit.
Does not overwrite remote history or change an existing repository's visibility.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Ariel-Norambuena/QuAntu"
URL = "https://github.com/" + REPOSITORY + ".git"

def run(*args: str, capture: bool = False, check: bool = True):
    command = list(args)
    if command[0] == "git":
        command[1:1] = ["-c", "safe.directory=" + ROOT.as_posix()]
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=capture, check=check)

def main() -> int:
    if not shutil.which("gh") or not shutil.which("git"):
        raise SystemExit("Git and GitHub CLI are required.")
    run(sys.executable, "scripts/verify_repository.py")
    auth = run("gh", "api", "user", "--jq", ".login", capture=True)
    if auth.stdout.strip().lower() != "ariel-norambuena":
        raise SystemExit("Authenticate as Ariel-Norambuena before publishing.")
    if run("git", "branch", "--show-current", capture=True).stdout.strip() != "main":
        raise SystemExit("Expected the reviewed local main branch.")
    if run("git", "status", "--porcelain", capture=True).stdout.strip():
        raise SystemExit("Commit or review local changes before publishing.")
    remote = run("git", "remote", "get-url", "origin", capture=True, check=False)
    if remote.returncode == 0 and remote.stdout.strip() != URL:
        raise SystemExit("Existing origin differs from the approved repository; inspect it manually.")
    existing = run("gh", "repo", "view", REPOSITORY, "--json", "isPrivate,nameWithOwner", capture=True, check=False)
    if existing.returncode == 0:
        metadata = json.loads(existing.stdout)
        if metadata["isPrivate"]:
            raise SystemExit("The existing remote is private. Publication stopped; visibility was not changed.")
    else:
        run("gh", "repo", "create", REPOSITORY, "--public", "--description",
            "QuAntü | Neutral-atom-based quantum computing in Chile — Proyecto Anillo Temático de ANID ATE250066. Algoritmos, experimentación y teoría.")
    if remote.returncode != 0:
        run("git", "remote", "add", "origin", URL)
    run("git", "push", "--set-upstream", "origin", "main")
    print("Published public repository: https://github.com/" + REPOSITORY)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
