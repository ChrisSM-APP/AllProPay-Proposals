#!/usr/bin/env python3
"""Validate AllProPay proposal pages.

This repo is a static publishing site (no application code), so the failure
mode we guard against is *content/publishing regressions* -- a proposal that
silently renders broken in front of a prospect. This script is the test suite
for that: run it locally or in CI before anything ships.

Checks performed per proposal page (*/index.html):
  1. Link & asset integrity -- every local src/href resolves on disk.
  2. Required structure       -- DOCTYPE, <html lang>, non-empty <title>, viewport.
  3. noindex consistency      -- robots noindex,nofollow present (obscurity model).
  4. Logo standardization     -- no per-proposal logo copy; uses shared assets/.
  5. External-dependency budget -- only allowlisted third-party origins.

Exit code 0 = all good, 1 = at least one error.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Origins a proposal page is allowed to reference. Anything else is flagged so a
# new third-party dependency can't slip in unnoticed (availability + privacy).
ALLOWED_ORIGINS = {
    "fonts.googleapis.com",  # web fonts (@import)
    "fonts.gstatic.com",     # web font files
    "allpropay.com",
    "www.allpropay.com",
}

# Schemes that point off-disk and shouldn't be checked for file existence.
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "//")

ORIGIN_RE = re.compile(r"https?://([^/\"'\s)]+)", re.IGNORECASE)


class RefParser(HTMLParser):
    """Collect src/href attribute values and key <meta>/<html> facts."""

    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.has_viewport = False
        self.has_noindex = False
        self.html_lang: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag in ("img", "script") and a.get("src"):
            self.refs.append(a["src"])
        if tag in ("a", "link") and a.get("href"):
            self.refs.append(a["href"])
        if tag == "html" and a.get("lang"):
            self.html_lang = a["lang"]
        if tag == "meta":
            name = a.get("name", "").lower()
            content = a.get("content", "").lower()
            if name == "viewport":
                self.has_viewport = True
            if name == "robots" and "noindex" in content:
                self.has_noindex = True


def check_page(page: Path, *, is_root: bool) -> list[str]:
    errors: list[str] = []
    rel = page.relative_to(REPO)
    text = page.read_text(encoding="utf-8", errors="replace")

    parser = RefParser()
    parser.feed(text)

    # 2. Required structure
    if "<!doctype html>" not in text.lower():
        errors.append(f"{rel}: missing <!DOCTYPE html>")
    if not parser.html_lang:
        errors.append(f"{rel}: <html> missing lang attribute")
    title = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not title or not title.group(1).strip():
        errors.append(f"{rel}: missing or empty <title>")
    if not parser.has_viewport:
        errors.append(f"{rel}: missing viewport meta")

    # 3. noindex consistency (proposal pages only; root already handled in README)
    if not is_root and not parser.has_noindex:
        errors.append(f"{rel}: missing robots noindex,nofollow meta")

    # 4. Logo standardization -- proposals must not ship their own logo copy
    if not is_root and (page.parent / "AllProPay_Logo.jpg").exists():
        errors.append(
            f"{rel}: per-proposal AllProPay_Logo.jpg present "
            "(use shared ../assets/AllProPay_Logo.jpg instead)"
        )

    # 1. Link & asset integrity
    for ref in parser.refs:
        r = ref.strip()
        if not r or r.startswith("#") or r.lower().startswith(EXTERNAL_SCHEMES):
            continue
        target = (page.parent / r.split("?", 1)[0].split("#", 1)[0]).resolve()
        if not target.exists():
            errors.append(f"{rel}: broken local reference -> {ref}")

    # 5. External-dependency budget
    for origin in {m.lower() for m in ORIGIN_RE.findall(text)}:
        if origin not in ALLOWED_ORIGINS:
            errors.append(f"{rel}: disallowed external origin -> {origin}")

    return errors


def main() -> int:
    root = REPO / "index.html"
    pages = sorted(
        p for p in REPO.glob("*/index.html") if p.parent.name != "assets"
    )

    all_errors: list[str] = []
    if root.exists():
        all_errors += check_page(root, is_root=True)
    for page in pages:
        all_errors += check_page(page, is_root=False)

    checked = len(pages) + (1 if root.exists() else 0)
    if all_errors:
        print(f"FAIL: {len(all_errors)} issue(s) across {checked} page(s):\n")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {checked} page(s) validated, no issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
