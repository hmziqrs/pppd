#!/usr/bin/env python3
"""Extract clean markdown from cached balanceanddizziness.org HTML pages.

Strategy:
- Take only <main id="genesis-content">.
- Inside it, prefer <article> (posts) else the whole main (pages).
- Drop known shared boilerplate: breadcrumbs, entry-meta, share buttons,
  'Recent Posts' sidebars, FAQ widget sections, filler images, embedded
  svg placeholders, 'How can we improve this page?' links.
- Convert remaining content to GitHub-flavoured markdown.
"""
import glob
import html as html_mod
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString, Tag
import html2text

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
CLEAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clean")

SKIP_CLASS_PATTERNS = [
    "breadcrumb",
    "entry-meta",
    "entry-footer",
    "dynamik-content-filler",
    "fl-sharing",
    "sharedaddy",
    "sfsi",
    "social",
    "a2a_kit",
    "heateor",
    "essb",
    "post-navigation",
    "uabb-js-breakpoint",
    "wpgdprc",
    "cookie",
    "related-posts",
    "recent-posts",
    "widget-area",
    "sidebar",
    "newsletter",
    "subscribe",
    "yuzo",
    "bloom",
    "scroll-to-top",
    "back-to-top",
    "web-stories",
    "screen-reader",
    "grecaptcha",
    "fb-",
    "twitter",
    "facebook",
    "fl-module-photo",  # generic image modules without meaningful captions
    "wp-caption",       # keep? no — captions inside post images are fine, keep
]

SKIP_ID_PATTERNS = [
    "genesis-sidebar",
    "comments",
    "respond",
    "footer",
    "header",
    "ubermenu",
    "fl-theme-builder",
    "cookie",
]

# classes that mark the page's own content container (fl-builder content)
KEEP_FL_CLASS = re.compile(r"^fl-builder-content fl-builder-content-\d+")


def class_list(node):
    return set(node.get("class", []))


def looks_like_boilerplate(node):
    classes = class_list(node)
    ids = {node.get("id", "")}
    for pat in SKIP_CLASS_PATTERNS:
        for c in classes:
            if pat in c.lower():
                return True
    for pat in SKIP_ID_PATTERNS:
        for i in ids:
            if pat in i.lower():
                return True
    return False


def find_article_content(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    main = soup.find("main")
    if main is None:
        main = soup

    article = main.find("article")
    root = article if article is not None else main

    # strip boilerplate
    for node in list(root.find_all(True)):
        if not getattr(node, "name", None):
            continue
        if looks_like_boilerplate(node):
            node.decompose()
            continue

    # strip share/utility links by their href/text
    for a in list(root.find_all("a")):
        href = (a.get("href") or "").lower()
        text = a.get_text(strip=True).lower()
        if any(s in href for s in [
            "facebook.com/sharer", "twitter.com/intent", "twitter.com/share",
            "mailto:?body=", "linkedin.com/share", "pinterest.com/pin",
            "#how-can-we-improve", "reddit.com/submit",
        ]) or any(s in text for s in [
            "share", "how can we improve", "expand", "click to enlarge",
        ]):
            if not a.find("img"):
                a.decompose()

    # strip images that are just placeholders / lazy-load gifs / icons
    for img in list(root.find_all("img")):
        src = (img.get("src") or "").lower()
        data_src = (img.get("data-src") or "").lower()
        if "data:image" in src or "svg+xml" in src or "pixel" in src:
            img.decompose()
            continue
        if data_src and not src:
            img["src"] = data_src
        if "data:image" in data_src or "svg+xml" in data_src:
            img.decompose()

    # strip script/style/noscript/form
    for t in root.find_all(["script", "style", "noscript", "form", "iframe",
                            "button", "input"]):
        t.decompose()

    # strip empty wrappers
    changed = True
    while changed:
        changed = False
        for div in list(root.find_all(["div", "span", "p"])):
            if not div.get_text(strip=True) and not div.find("img") \
               and not div.find("iframe"):
                div.decompose()
                changed = True

    return root


def clean_markdown(md):
    lines = md.splitlines()
    out = []
    blank_run = 0
    for line in lines:
        s = line.strip()
        # strip spam/pharma link injections (kept the rest of the line)
        if re.search(r"(lekarna|apotek|genericky|generisk)", s, re.I):
            s = re.sub(
                r"\[?\[?(<|\[)?https?://[^\s<>()\]]*(lekarna|apotek|genericky|generisk)[^\s<>()\]]*(>|\])?\]?\)?",
                "", s, flags=re.I)
            s = re.sub(r"\s{2,}", " ", s).strip()
            if not s.strip():
                continue
        # drop leftover boilerplate-ish lines
        if not s:
            blank_run += 1
            if blank_run <= 1:
                out.append("")
            continue
        blank_run = 0
        if re.match(r"^\[!\[.*\]\(data:image.*\]\(.*\)$", s):
            continue
        if re.match(r"^\[(Skip to .*|Home)\]\(#", s):
            continue
        if s.startswith("You are here:"):
            continue
        if re.match(r"^\[(Home|Disorders|Vestibular Disorders|Diagnosis and Treatment|Stories|Educational|Support|Help Yourself|Announcements)\]", s):
            continue
        out.append(s)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def is_toc_block(text):
    """A TOC block is a list of short items (all <= 40 chars) with >= 3 entries."""
    items = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(items) < 3:
        return False
    for it in items:
        if len(it) > 40:
            return False
        if not (it.startswith("* ") or re.match(r"^\d+\.\s", it)):
            return False
    return True


def dedupe_toc_and_title(md, title):
    """The site renders desktop+mobile copies of nav/TOC blocks; remove exact
    duplicate blocks and repeated TOC-style lists."""
    # split into blocks separated by blank lines
    blocks = [b for b in re.split(r"\n\s*\n", md)]
    seen = set()
    out = []
    toc_items = []
    in_toc_run = False
    toc_run_done = False
    in_recent = False
    in_sources = False
    for b in blocks:
        stripped = b.strip()
        if not stripped:
            continue
        key = stripped[:200]
        # drop 'Recent Posts' widgets and everything after them
        if stripped.startswith("## Recent Posts") or stripped.startswith("### Recent Posts"):
            in_recent = True
            continue
        if in_recent:
            continue
        # drop the language-switch line
        if stripped.startswith("[ Français") or stripped.startswith("* [ Français"):
            continue
        # drop trailing 'This form is for general feedback' notice
        if stripped.startswith("This form is for general feedback"):
            continue
        # drop 'Page updated' footer lines
        if re.match(r"^Page updated ", stripped):
            continue
        # drop the reference/citation tail (starts with Sources/Source heading)
        if stripped in ("## Sources", "### Sources", "## Source", "### Source"):
            in_sources = True
            continue
        if in_sources:
            continue
        if re.match(r"^(How can we improve this page|\[\*Expand\*\])", stripped):
            continue
        # desktop/mobile duplicate TOCs: collect the first contiguous run of
        # short-bullet blocks into one deduped list; drop any later TOC blocks
        if is_toc_block(stripped):
            if toc_run_done:
                continue
            for it in stripped.splitlines():
                item = it.strip()
                if item and item not in toc_items:
                    toc_items.append(item)
            in_toc_run = True
            continue
        if in_toc_run:
            toc_run_done = True
            in_toc_run = False
            out.append("\n".join(toc_items))
        # drop repeated identical blocks
        if len(stripped) > 60 and key in seen:
            continue
        seen.add(key)
        out.append(stripped)
    if in_toc_run:
        out.append("\n".join(toc_items))
    return "\n\n".join(out) + "\n"


def process_file(path):
    html_str = open(path, encoding="utf-8", errors="replace").read()
    root = find_article_content(html_str)

    # get title
    title = None
    h1 = root.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    if not title:
        t = root.find("title")
        if t:
            title = t.get_text(" ", strip=True)

    # find the real content: prefer fl-builder content container
    content = None
    for div in root.find_all("div", recursive=True):
        classes = class_list(div)
        joined = " ".join(classes)
        if KEEP_FL_CLASS.match(joined) and len(div.get_text(strip=True)) > 200:
            content = div
            break
    if content is None:
        entry = root.find("div", class_="entry-content")
        content = entry or root

    # drop 'Page updated' footer line inside content later via regex
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.mark_code = True
    h.unicode_snob = True
    h.ignore_emphasis = False
    h.protect_links = True

    md = h.handle(str(content))
    md = html_mod.unescape(md)
    md = clean_markdown(md)

    # remove trailing 'Page updated...' and 'How can we improve' remnants
    md = re.sub(r"\n+\*?\*?Page updated[^\n]*\.\*?\*?\n*$", "\n", md)
    md = re.sub(r"\n+\[How can we improve this page\?\]\([^)]*\)\n*$", "\n", md)
    md = re.sub(r"\n+\[\*Expand\*\]\([^)]*\)\n*$", "\n", md)

    if title:
        md = dedupe_toc_and_title(md, title)
        # strip all H1 lines from content (page builder duplicates the title);
        # real section headings are H2+ and we prepend our own H1
        md = "\n".join(
            ln for ln in md.splitlines()
            if not (ln.strip().startswith("# ") and not ln.strip().startswith("## "))
        )
        header = f"# {title}\n\n"
        md = header + md
    return md


def main():
    os.makedirs(CLEAN, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "*.html")))
    files = [f for f in files if os.path.basename(f) != "index.html"]
    counts = {"ok": 0, "fail": 0}
    for f in files:
        try:
            md = process_file(f)
            base = os.path.basename(f).replace(".html", ".md")
            out = os.path.join(CLEAN, base)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(md)
            counts["ok"] += 1
            print(f"  {base}: {len(md)} chars")
        except Exception as e:
            counts["fail"] += 1
            print(f"FAIL {os.path.basename(f)}: {e}")
    print(f"\n{counts['ok']} ok, {counts['fail']} failed -> {CLEAN}")


if __name__ == "__main__":
    main()
