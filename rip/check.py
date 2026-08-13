#!/usr/bin/env python3
"""Corpus integrity checker.

Enforces the rip/ layout conventions:

- Every markdown link in every .md file resolves.
- Every clean/*.md page has a matching raw/*.html page.
- Every clean page is listed in the site README inventory (and vice versa).
- Every site has a summaries/ folder with an index README.
- No summary links point outside its own site folder.

Run from rip/:  python3 check.py
Exit code 0 = all good, 1 = broken links/layout.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LINK_RE = re.compile(r"\]\(([^)#]+\.md(?:#[^)]*)?)\)")


def fail(msg):
    print("FAIL:", msg)


def main():
    problems = 0

    # 1. All markdown links resolve
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        for f in sorted(filenames):
            if not f.endswith(".md"):
                continue
            p = os.path.join(dirpath, f)
            text = open(p, encoding="utf-8").read()
            for m in LINK_RE.finditer(text):
                tgt = m.group(1).split("#")[0]
                full = os.path.normpath(os.path.join(dirpath, tgt))
                if not os.path.exists(full):
                    fail(f"{os.path.relpath(p, ROOT)} -> {tgt}")
                    problems += 1

    # 2. Per-site conventions
    for site in sorted(os.listdir(ROOT)):
        site_dir = os.path.join(ROOT, site)
        if not os.path.isdir(site_dir) or site.startswith("."):
            continue
        if site in (".git",):
            continue

        # site must have the expected folders
        for sub in ("raw", "clean", "summaries", "sitemaps"):
            if not os.path.isdir(os.path.join(site_dir, sub)):
                fail(f"{site}/ missing {sub}/ folder")
                problems += 1

        # every clean page has a raw counterpart
        clean_dir = os.path.join(site_dir, "clean")
        raw_dir = os.path.join(site_dir, "raw")
        if os.path.isdir(clean_dir) and os.path.isdir(raw_dir):
            clean_files = sorted(f for f in os.listdir(clean_dir) if f.endswith(".md"))
            raw_files = set(os.listdir(raw_dir))
            for c in clean_files:
                if c[:-3] + ".html" not in raw_files:
                    fail(f"{site}/clean/{c} has no {site}/raw/{c[:-3]}.html")
                    problems += 1
            for r in sorted(raw_files):
                if r.endswith(".html") and r[:-5] + ".md" not in clean_files:
                    fail(f"{site}/raw/{r} has no {site}/clean/{r[:-5]}.md")
                    problems += 1

        # clean pages listed in site README inventory (and vice versa);
        # only look inside the "Clean page inventory" section
        readme = os.path.join(site_dir, "README.md")
        if os.path.isfile(readme) and os.path.isdir(clean_dir):
            text = open(readme, encoding="utf-8").read()
            m = re.search(r"## Clean page inventory(.*?)(?:\n## |\Z)", text, re.S)
            if m:
                listed = set(re.findall(r"`([\w.-]+\.md)`", m.group(1)))
                actual = set(f for f in os.listdir(clean_dir) if f.endswith(".md"))
                for c in sorted(actual - listed):
                    fail(f"{site}/clean/{c} not listed in {site}/README.md inventory")
                    problems += 1
                for c in sorted(listed - actual):
                    fail(f"{site}/README.md lists {c} but file missing in clean/")
                    problems += 1

        # summaries folder has an index README and no broken internal links
        summ_dir = os.path.join(site_dir, "summaries")
        if os.path.isdir(summ_dir):
            if not os.path.isfile(os.path.join(summ_dir, "README.md")):
                fail(f"{site}/summaries/ missing README.md index")
                problems += 1
            # summaries must not link outside their site folder
            for f in os.listdir(summ_dir):
                if not f.endswith(".md"):
                    continue
                p = os.path.join(summ_dir, f)
                text = open(p, encoding="utf-8").read()
                for m in LINK_RE.finditer(text):
                    tgt = m.group(1).split("#")[0]
                    full = os.path.normpath(os.path.join(summ_dir, tgt))
                    if not os.path.exists(full):
                        fail(f"{site}/summaries/{f} -> {tgt}")
                        problems += 1
                    if full.startswith(os.path.normpath(os.path.join(site_dir, "summaries"))):
                        continue
                    if not full.startswith(os.path.normpath(site_dir) + os.sep):
                        fail(f"{site}/summaries/{f} links outside site: {tgt}")
                        problems += 1

    if problems:
        print(f"\n{problems} problem(s) found.")
        return 1
    print("All checks passed: links resolve, clean<->raw pairs match, "
          "inventories complete, summaries inside site folders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
