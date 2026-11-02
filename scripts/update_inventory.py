#!/usr/bin/env python3
"""Review or update current hashes of imported files, preserving source hashes."""
from __future__ import annotations
import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "inventory.csv"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Record intentional changes after reviewing their diff")
    args = parser.parse_args()
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    changed = []
    for row in rows:
        path = (ROOT / row["repository_path"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise SystemExit(f"Invalid or missing imported path: {row['repository_path']}")
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if row["sha256"] != digest or int(row["bytes"]) != len(content):
            changed.append(row["repository_path"])
        row["bytes"] = str(len(content))
        row["sha256"] = digest
        row["modified_for_portability"] = str(digest != row["source_sha256"]).lower()
    for item in changed:
        print(f"CHANGED {item}")
    if args.write:
        with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Recorded {len(changed)} intentional changes; source hashes preserved.")
        return 0
    print(f"{len(changed)} imported files differ; use --write only after reviewing changes.")
    return int(bool(changed))

if __name__ == "__main__":
    raise SystemExit(main())
