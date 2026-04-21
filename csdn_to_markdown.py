#!/usr/bin/env python3
"""
Convert a CSDN article page to Markdown.

Usage:
    python csdn_to_markdown.py "https://blog.csdn.net/qq_46140768/article/details/132397061" -o article.md

Optional:
    python csdn_to_markdown.py URL -o article.md --cookies cookies.txt
    python csdn_to_markdown.py URL -o article.md --use-playwright

Requirements:
    pip install requests beautifulsoup4 lxml markdownify readability-lxml trafilatura

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


def build_session(user_agent: Optional[str] = None, cookie_header: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent
            or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )
    if cookie_header:
        session.headers["Cookie"] = cookie_header.strip()
    return session


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
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
        )
        page = context.new_page()
        if cookie_header:
            page.set_extra_http_headers({"Cookie": cookie_header})
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        html = page.content()
        browser.close()
        return html


def extract_main_html(html: str) -> tuple[str, str]:
    """Return (title, cleaned_html)."""
    soup = BeautifulSoup(html, "lxml")

    title = "untitled"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Common CSDN selectors first
    candidates = [
        "#content_views",
        ".blog-content-box",
        ".article_content",
        ".htmledit_views",
        "article",
    ]
    main = None
    for sel in candidates:
        main = soup.select_one(sel)
        if main:
            break

    # Fallback to readability-lxml
    if main is None:
        try:
            from readability import Document

            doc = Document(html)
            summary_html = doc.summary(html_partial=True)
            title = doc.short_title() or title
            main = BeautifulSoup(summary_html, "lxml")
        except Exception:
            main = soup.body or soup

    # Remove obvious noise
    for tag in main.select(
        "script, style, iframe, aside, .recommend-box, .blog-footer-bottom, .hljs-button, .copyright-box, .article-info-box, .tag-link"
    ):
        tag.decompose()

    # Normalize code blocks
    for pre in main.find_all("pre"):
        classes = " ".join(pre.get("class", []))
        code = pre.find("code")
        text = code.get_text("\n") if code else pre.get_text("\n")

        lang = ""
        m = re.search(r"language-([\w+-]+)", classes)
        if m:
            lang = m.group(1)

        fenced = BeautifulSoup("<pre></pre>", "lxml").pre
        fenced.string = f"```{lang}\n{text.rstrip()}\n```"
        pre.replace_with(fenced)

    return title, str(main)


def html_to_markdown(title: str, main_html: str, source_url: str) -> str:
    body_md = md(
        main_html,
        heading_style="ATX",
        bullets="-",
        code_language_callback=lambda el: None,
        strip=["span"],
    )

    # Post-clean
    body_md = re.sub(r"\n{3,}", "\n\n", body_md).strip()
    body_md = body_md.replace("\\_", "_")

    header = f"# {title}\n\n> 来源：{source_url}\n\n"
    return header + body_md + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a CSDN article to Markdown")
    parser.add_argument("url", help="Article URL")
    parser.add_argument("-o", "--output", required=True, help="Output markdown file")
    parser.add_argument("--cookies", help="Path to a text file containing the Cookie header")
    parser.add_argument("--use-playwright", action="store_true", help="Render page with Playwright before extraction")
    args = parser.parse_args()

    output_path = Path(args.output)
    cookies_file = Path(args.cookies) if args.cookies else None

    try:
        if args.use_playwright:
            html = fetch_html_playwright(args.url, cookies_file=cookies_file)
        else:
            html = fetch_html(args.url, cookies_file=cookies_file)

        title, main_html = extract_main_html(html)
        markdown = html_to_markdown(title, main_html, args.url)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Saved markdown to: {output_path}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
