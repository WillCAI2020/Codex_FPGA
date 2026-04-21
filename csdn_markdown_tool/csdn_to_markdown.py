#!/usr/bin/env python3
"""
Convert a CSDN article page to Markdown.

Usage:
    python csdn_to_markdown.py "https://blog.csdn.net/qq_46140768/article/details/132397061" -o article.md

Optional:
    python csdn_to_markdown.py URL -o article.md --cookies cookies.txt
    python csdn_to_markdown.py URL -o article.md --use-playwright

Requirements:
    pip install requests beautifulsoup4 lxml markdownify

Optional for dynamic rendering:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def build_session(user_agent: Optional[str] = None, cookie_header: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent or UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://blog.csdn.net/",
        }
    )
    if cookie_header:
        session.headers["Cookie"] = cookie_header.strip()
    return session


def normalize_code_text(text: str) -> str:
    """Normalize code text while keeping token continuity."""
    lines = text.splitlines()
    short_ratio = (sum(1 for line in lines if len(line.strip()) <= 4) / len(lines)) if lines else 0

    # Heuristic: if code is highly tokenized, rebuild by joining stripped tokens.
    if lines and short_ratio > 0.35:
        merged = " ".join(line.strip() for line in lines if line.strip())
    else:
        merged = text
        merged = re.sub(r"\n\s*([\[\]{}();:,.=+\-*/<>|&!])\s*\n", r"\1", merged)
        merged = re.sub(r"([A-Za-z_0-9])\n\s*([A-Za-z_0-9])", r"\1 \2", merged)

    merged = re.sub(r"\s*([()\[\]{};,:])\s*", r"\1", merged)
    merged = re.sub(r"([=+\-*/<>|&])\s*", r"\1 ", merged)
    merged = re.sub(r"\s{2,}", " ", merged)
    merged = re.sub(r"\n{3,}", "\n\n", merged)
    return merged.strip()


def detect_code_language(pre_tag) -> str:
    classes = []
    for tag in [pre_tag, pre_tag.find("code") if pre_tag else None]:
        if tag is not None:
            classes.extend(tag.get("class", []))

    class_text = " ".join(classes)
    match = re.search(r"language-([\w+-]+)", class_text)
    if match:
        return match.group(1)

    if "verilog" in class_text.lower():
        return "verilog"
    return ""


def fetch_html(url: str, cookies_file: Optional[Path] = None, timeout: int = 20) -> str:
    cookie_header = None
    if cookies_file:
        cookie_header = cookies_file.read_text(encoding="utf-8").strip()

    session = build_session(cookie_header=cookie_header)
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def fetch_html_playwright(url: str, cookies_file: Optional[Path] = None, timeout_ms: int = 30000) -> str:
    from playwright.sync_api import sync_playwright

    cookie_header = None
    if cookies_file:
        cookie_header = cookies_file.read_text(encoding="utf-8").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=UA, locale="zh-CN")
        page = context.new_page()
        if cookie_header:
            page.set_extra_http_headers({"Cookie": cookie_header})
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        html = page.content()
        browser.close()
        return html


def fetch_markdown_via_jina(url: str, timeout: int = 30) -> str:
    """Fetch already-extracted markdown from r.jina.ai as a fallback for anti-bot pages."""
    mirror_url = f"https://r.jina.ai/http://{url.removeprefix('https://').removeprefix('http://')}"
    resp = requests.get(mirror_url, timeout=timeout)
    resp.raise_for_status()

    text = resp.text
    marker = "Markdown Content:"
    if marker in text:
        text = text.split(marker, 1)[1].strip()

    if not text:
        raise ValueError("jina fallback returned empty content")

    return text + "\n"


def extract_main_html(html: str) -> tuple[str, str]:
    """Return (title, cleaned_html)."""
    soup = BeautifulSoup(html, "lxml")

    title = "untitled"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    candidates = ["#content_views", ".blog-content-box", ".article_content", ".htmledit_views", "article"]
    main = None
    for sel in candidates:
        main = soup.select_one(sel)
        if main:
            break

    if main is None:
        main = soup.body or soup

    for tag in main.select(
        "script, style, iframe, aside, .recommend-box, .blog-footer-bottom, .hljs-button, .copyright-box, .article-info-box, .tag-link"
    ):
        tag.decompose()

    for pre in main.find_all("pre"):
        code = pre.find("code")
        text = code.get_text("\n") if code else pre.get_text("\n")
        text = normalize_code_text(text)
        lang = detect_code_language(pre)

        fenced = BeautifulSoup("<pre></pre>", "lxml").pre
        fenced.string = f"```{lang}\n{text}\n```"
        pre.replace_with(fenced)

    return title, str(main)


def clean_nested_fences(markdown: str) -> str:
    # Remove accidental nested code fences produced after markdownify.
    markdown = re.sub(r"```\s*\n```", "```", markdown)
    markdown = re.sub(r"\n```\s*\n```", "\n```", markdown)
    return markdown


def html_to_markdown(title: str, main_html: str, source_url: str) -> str:
    body_md = md(
        main_html,
        heading_style="ATX",
        bullets="-",
        code_language_callback=lambda el: None,
        strip=["span"],
    )

    body_md = clean_nested_fences(body_md)
    body_md = re.sub(r"\n{3,}", "\n\n", body_md).strip()
    body_md = body_md.replace("\\_", "_")

    header = f"# {title}\n\n> 来源：{source_url}\n\n"
    return header + body_md + "\n"


def ensure_source_block(markdown: str, source_url: str) -> str:
    if f"来源：{source_url}" in markdown:
        return markdown

    if markdown.lstrip().startswith("# "):
        lines = markdown.splitlines()
        if len(lines) >= 1:
            lines.insert(1, "")
            lines.insert(2, f"> 来源：{source_url}")
            lines.insert(3, "")
            return "\n".join(lines).strip() + "\n"

    return f"> 来源：{source_url}\n\n{markdown.strip()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a CSDN article to Markdown")
    parser.add_argument("url", help="Article URL")
    parser.add_argument("-o", "--output", required=True, help="Output markdown file")
    parser.add_argument("--cookies", help="Path to a text file containing the Cookie header")
    parser.add_argument("--use-playwright", action="store_true", help="Render page with Playwright before extraction")
    parser.add_argument(
        "--no-jina-fallback",
        action="store_true",
        help="Disable fallback to r.jina.ai when direct fetching is blocked",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    cookies_file = Path(args.cookies) if args.cookies else None

    try:
        html = fetch_html_playwright(args.url, cookies_file=cookies_file) if args.use_playwright else fetch_html(args.url, cookies_file=cookies_file)
        title, main_html = extract_main_html(html)
        markdown = html_to_markdown(title, main_html, args.url)
    except Exception as primary_exc:
        if args.no_jina_fallback:
            print(f"ERROR: {primary_exc}", file=sys.stderr)
            return 1
        print(f"Direct fetch failed ({primary_exc}), trying r.jina.ai fallback...", file=sys.stderr)
        try:
            markdown = ensure_source_block(fetch_markdown_via_jina(args.url), args.url)
        except Exception as fallback_exc:
            print(f"ERROR: direct fetch failed ({primary_exc}); fallback failed ({fallback_exc})", file=sys.stderr)
            return 1

    output_path.write_text(clean_nested_fences(markdown), encoding="utf-8")
    print(f"Saved markdown to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
