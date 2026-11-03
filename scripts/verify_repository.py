#!/usr/bin/env python3
"""Verify the imported collection and local references without third-party packages.

This checks integrity and syntax only. It does not execute scientific models,
rebuild the report, fetch remote URLs, or establish scientific agreement.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
from urllib.parse import unquote, urlsplit


EXPECTED_IMPORTS = 126
INVENTORY_FIELDS = (
    "original_path", "repository_path", "bytes", "sha256",
    "source_sha256", "modified_for_portability",
)
IGNORED_PARTS = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints", "tmp", ".cache", "build", "outputs", "results"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def inside(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def imported_path(value: str) -> bool:
    """Inventory paths are portable, root-relative POSIX paths."""
    path = PurePosixPath(value)
    return bool(
        value and "\\" not in value and not path.is_absolute()
        and not PureWindowsPath(value).drive
        and not any(part in {".", "..", ".git"} for part in value.split("/"))
        and "" not in value.split("/")
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_inventory(root: Path, errors: list[str]) -> int:
    manifest = root / "docs" / "inventory.csv"
    if not manifest.is_file():
        errors.append("Missing docs/inventory.csv")
        return 0
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != INVENTORY_FIELDS:
            errors.append("inventory.csv: unexpected columns; expected " + ", ".join(INVENTORY_FIELDS))
            return 0
        rows = list(reader)
    if len(rows) != EXPECTED_IMPORTS:
        errors.append(f"inventory.csv: expected {EXPECTED_IMPORTS} imports, found {len(rows)}")
    originals: set[str] = set()
    destinations: set[str] = set()
    for line, row in enumerate(rows, 2):
        prefix = f"inventory.csv:{line}"
        if None in row or any(row.get(field) is None for field in INVENTORY_FIELDS):
            errors.append(f"{prefix}: malformed CSV row")
            continue
        for field, known in (("original_path", originals), ("repository_path", destinations)):
            value = row[field]
            if not imported_path(value):
                errors.append(f"{prefix}: unsafe {field}: {value!r}")
            # Windows and common macOS filesystems are case-insensitive.
            if value.casefold() in known:
                errors.append(f"{prefix}: duplicate {field}: {value}")
            known.add(value.casefold())
        destination = row["repository_path"]
        if not imported_path(destination):
            continue
        asset = root / destination
        if not inside(root, asset):
            errors.append(f"{prefix}: path escapes repository: {destination}")
            continue
        if not asset.is_file():
            errors.append(f"{prefix}: missing imported file: {destination}")
            continue
        try:
            size = int(row["bytes"])
            if size < 0:
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}: invalid bytes value: {row['bytes']!r}")
        else:
            if asset.stat().st_size != size:
                errors.append(f"{prefix}: size mismatch: {destination}")
        for field in ("sha256", "source_sha256"):
            if not SHA256.fullmatch(row[field]):
                errors.append(f"{prefix}: invalid {field}")
        if sha256(asset) != row["sha256"]:
            errors.append(f"{prefix}: SHA256 mismatch: {destination}")
        modified = row["modified_for_portability"]
        if modified not in {"true", "false"}:
            errors.append(f"{prefix}: modified_for_portability must be true or false")
        elif (row["sha256"] != row["source_sha256"]) != (modified == "true"):
            errors.append(f"{prefix}: modification flag disagrees with source/current hashes: {destination}")
    return len(rows)


def files(root: Path, suffix: str):
    for path in sorted(root.rglob("*" + suffix)):
        relative = path.relative_to(root)
        if not any(part in IGNORED_PARTS for part in relative.parts) and path.is_file():
            yield path


def verify_tex(root: Path, errors: list[str]) -> int:
    pattern = re.compile(
        r"\\(input|include|includegraphics\*?|bibliography|addbibresource)"
        r"\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}"
    )
    checked = 0
    for source in files(root, ".tex"):
        content = re.sub(r"(?<!\\)%[^\n]*", "", source.read_text(encoding="utf-8-sig"))
        for match in pattern.finditer(content):
            command, value = match.groups()
            for name in value.split(",") if command == "bibliography" else [value]:
                name = name.strip()
                if "\\" in name or "#" in name:
                    errors.append(f"{source.relative_to(root)}: cannot statically resolve LaTeX asset {name!r}")
                    continue
                target = source.parent / name
                candidates = [target]
                if not target.suffix:
                    extensions = (".tex",) if command in {"input", "include"} else (
                        (".bib",) if command in {"bibliography", "addbibresource"}
                        else (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")
                    )
                    candidates.extend(target.with_suffix(ext) for ext in extensions)
                if not inside(root, target):
                    errors.append(f"{source.relative_to(root)}: LaTeX asset escapes repository: {name}")
                elif not any(candidate.is_file() for candidate in candidates):
                    errors.append(f"{source.relative_to(root)}: missing LaTeX asset: {name}")
                checked += 1
    return checked


def markdown_targets(content: str):
    # Ignore examples in fenced blocks and inline code.
    content = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", content)
    content = re.sub(r"`+[^`\n]*`+", "", content)
    # Inline links/images; support angle-bracket destinations and balanced () in filenames.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*", content):
        start = match.end()
        if content[start:start + 1] == "<":
            end = content.find(">", start + 1)
            if end != -1:
                yield content[start + 1:end]
            continue
        depth, cursor = 0, start
        while cursor < len(content):
            char = content[cursor]
            if char == "\\":
                cursor += 2
                continue
            if char == "(" :
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            cursor += 1
        if cursor > start:
            yield content[start:cursor]
    # Also verify reference-style destinations, whether or not reused in the page.
    for match in re.finditer(r"(?m)^\s{0,3}\[[^\]\n]+\]:\s*(?:<([^>]+)>|(\S+))", content):
        yield match.group(1) or match.group(2)


def verify_markdown(root: Path, errors: list[str]) -> int:
    checked = 0
    for source in files(root, ".md"):
        for raw in markdown_targets(source.read_text(encoding="utf-8-sig")):
            if raw.startswith(("#", "//")):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            name = unquote(parsed.path)
            if not name:
                continue
            target = (root / name.lstrip("/")) if name.startswith("/") else (source.parent / name)
            if not inside(root, target):
                errors.append(f"{source.relative_to(root)}: Markdown link escapes repository: {raw}")
            elif not target.exists():
                errors.append(f"{source.relative_to(root)}: missing Markdown target: {raw}")
            checked += 1
    return checked


def verify_python(root: Path, errors: list[str], compile_cells: bool) -> tuple[int, int, int]:
    python_count = notebook_count = cell_count = 0
    for source in files(root, ".py"):
        python_count += 1
        try:
            ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"{source.relative_to(root)}: invalid Python syntax: {exc}")
    for source in files(root, ".ipynb"):
        notebook_count += 1
        try:
            notebook = json.loads(source.read_text(encoding="utf-8-sig"))
            if not isinstance(notebook, dict) or notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
                raise ValueError("expected nbformat 4 and a cells list")
            for index, cell in enumerate(notebook["cells"], 1):
                if not isinstance(cell, dict) or cell.get("cell_type") not in {"code", "markdown", "raw"}:
                    raise ValueError(f"invalid cell {index}")
                value = cell.get("source")
                if not isinstance(value, str) and not (isinstance(value, list) and all(isinstance(line, str) for line in value)):
                    raise ValueError(f"invalid source in cell {index}")
                if cell["cell_type"] == "code":
                    cell_count += 1
                    if compile_cells:
                        code = value if isinstance(value, str) else "".join(value)
                        compile(code, f"{source.relative_to(root)}:cell-{index}", "exec")
        except (ValueError, SyntaxError, UnicodeError) as exc:
            errors.append(f"{source.relative_to(root)}: invalid notebook: {exc}")
    return python_count, notebook_count, cell_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-notebook-compile", action="store_true", help="validate notebook JSON without compiling code cells")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    try:
        imports = verify_inventory(root, errors)
        tex = verify_tex(root, errors)
        links = verify_markdown(root, errors)
        python, notebooks, cells = verify_python(root, errors, not args.skip_notebook_compile)
    except (OSError, csv.Error, UnicodeError) as exc:
        errors.append(f"Cannot complete verification: {exc}")
    if errors:
        print(f"Repository verification FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Repository verification PASSED: {imports} imported files; {tex} LaTeX assets; {links} local Markdown links; {python} Python files; {notebooks} notebooks / {cells} code cells.")
    print("Checks cover file integrity, local references, and syntax. Models and remote links were not executed or fetched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
