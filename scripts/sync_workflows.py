#!/usr/bin/env python3
"""Materialize IDE-agnostic workflow definitions into each supported IDE's
native directory.

Single source of truth:
    shared/workflows/<slug>.md   (frontmatter: title / slug / stage / description + body)

Generated targets (do NOT hand-edit):
    .devin/workflows/<slug>.md       (Devin workflows)
    .windsurf/workflows/<slug>.md    (Windsurf native Workflows, slash command /<slug>)
    .cursor/commands/<slug>.md       (Cursor slash commands /<slug>)

Usage:
    python scripts/sync_workflows.py           # regenerate all IDE copies
    python scripts/sync_workflows.py --check    # verify no drift (CI / pre-commit), exit 1 if stale

To add an IDE, append an entry to TARGETS.
"""
from __future__ import annotations
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "shared", "workflows")

# Per-IDE materialization rules.
#   frontmatter: which source frontmatter keys to re-emit (in order); [] = no frontmatter block.
TARGETS = {
    "devin": {"dir": ".devin/workflows", "frontmatter": ["description"]},
    "windsurf": {"dir": ".windsurf/workflows", "frontmatter": ["description"]},
    "cursor": {"dir": ".cursor/commands", "frontmatter": []},
}

GEN_NOTE = (
    "<!-- AUTO-GENERATED from {src}. Do not edit here; "
    "edit the source and run `python scripts/sync_workflows.py`. -->"
)


def parse(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    fm_raw, body = m.group(1), m.group(2).lstrip("\n")
    fm: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body.rstrip() + "\n"


def render(slug: str, fm: dict[str, str], body: str, target: dict) -> str:
    note = GEN_NOTE.format(src=f"shared/workflows/{slug}.md")
    keys = target["frontmatter"]
    if keys:
        lines = [f"{k}: {fm[k]}" for k in keys if fm.get(k)]
        block = "---\n" + "\n".join(lines) + "\n---\n"
        return f"{block}\n{note}\n\n{body}"
    # No frontmatter (e.g. Cursor): keep a title heading so the command reads well.
    title = fm.get("title", slug)
    head = body if body.lstrip().startswith("#") else f"# {title}\n\n{body}"
    return f"{note}\n\n{head}"


def build() -> dict[str, str]:
    if not os.path.isdir(SRC):
        sys.exit(f"source dir not found: {SRC}")
    out: dict[str, str] = {}
    slugs = sorted(
        f[:-3]
        for f in os.listdir(SRC)
        if f.endswith(".md") and re.match(r"^\d{2}-", f)
    )
    for slug in slugs:
        with open(os.path.join(SRC, slug + ".md"), encoding="utf-8") as f:
            fm, body = parse(f.read())
        for target in TARGETS.values():
            path = os.path.join(ROOT, target["dir"], slug + ".md")
            out[path] = render(slug, fm, body, target)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify no drift; exit 1 if stale")
    args = ap.parse_args()

    out = build()
    drift = []
    for path, content in out.items():
        existing = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = f.read()
        if existing != content:
            drift.append(path)
        if not args.check:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)

    if args.check:
        if drift:
            print("Workflow IDE copies are OUT OF SYNC with shared/workflows/:")
            for p in sorted(drift):
                print("   -", os.path.relpath(p, ROOT))
            print("Fix: python scripts/sync_workflows.py")
            sys.exit(1)
        print(f"OK: {len(out)} generated workflow files in sync across {len(TARGETS)} IDE targets.")
    else:
        print(f"Synced {len(out)} files across {len(TARGETS)} IDE targets "
              f"({', '.join(TARGETS)}).")


if __name__ == "__main__":
    main()
