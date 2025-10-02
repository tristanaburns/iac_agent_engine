#!/usr/bin/env python3
"""
Claude Code Documentation Fetcher
Iteratively fetches all Claude Code documentation from Anthropic's website
and saves them as markdown files in .claude/docs/
"""

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import markdownify
import requests
from bs4 import BeautifulSoup

# Configuration - Portable: Works from any directory
BASE_URL = "https://docs.anthropic.com"
CLAUDE_CODE_BASE = "/en/docs/claude-code/"
SCRIPT_DIR = Path(__file__).parent.resolve()  # Directory where this script is located
OUTPUT_DIR = SCRIPT_DIR / "docs"  # Save docs relative to script location
DELAY_BETWEEN_REQUESTS = 1  # seconds to be respectful

# Claude Code documentation sections to fetch
CLAUDE_CODE_SECTIONS = [
    "",  # Overview/index
    "quickstart",
    "setup",
    "troubleshooting",
    "settings",
    "iam",
    "hooks",
    "hooks-guide",
    "statusline",
    "slash-commands",
    "sub-agents",
    "memory",
    "mcp",
    "common-workflows",
    "sdk/sdk-overview",
    "sdk/sdk-headless",
    "ide-integrations",
    "github-actions",
    "costs",
    "amazon-bedrock",
    "bedrock-vertex-proxies",
]


def clean_filename(filename):
    """Clean filename for filesystem compatibility"""
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def extract_title_from_content(soup):
    """Extract title from page content"""
    title_elem = soup.find("h1")
    if title_elem:
        return title_elem.get_text().strip()

    # Fallback to page title
    title_elem = soup.find("title")
    if title_elem:
        return title_elem.get_text().strip()

    return "Claude Code Documentation"


def fetch_page_content(url):
    """Fetch page content with error handling"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f" Error fetching {url}: {e}")
        return None


def html_to_markdown(html_content, url):
    """Convert HTML to markdown"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the main content area (adjust selector as needed)
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
        )

        if not main_content:
            # Fallback to body content
            main_content = soup.find("body")

        if not main_content:
            print(f"  Could not find main content for {url}")
            return None

        # Extract title
        title = extract_title_from_content(soup)

        # Convert to markdown
        markdown_content = markdownify.markdownify(
            str(main_content), heading_style="ATX"
        )

        # Add metadata header
        metadata = f"""---
title: {title}
source: {url}
fetched: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

"""

        return metadata + markdown_content

    except Exception as e:
        print(f" Error converting HTML to markdown for {url}: {e}")
        return None


def save_markdown_file(content, filename, section=""):
    """Save markdown content to file"""
    try:
        if section:
            section_dir = OUTPUT_DIR / section
            section_dir.mkdir(parents=True, exist_ok=True)
            filepath = section_dir / f"{filename}.md"
        else:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            filepath = OUTPUT_DIR / f"{filename}.md"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f" Saved: {filepath}")
        return True

    except Exception as e:
        print(f" Error saving {filename}: {e}")
        return False


def main():
    """Main function to fetch all Claude Code documentation"""
    print(" Starting Claude Code Documentation Fetcher")
    print("=" * 50)

    success_count = 0
    error_count = 0

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch each documentation section
    for section in CLAUDE_CODE_SECTIONS:
        if section:
            url = f"{BASE_URL}{CLAUDE_CODE_BASE}{section}"
            filename = clean_filename(section.replace("/", "-"))
        else:
            url = f"{BASE_URL}{CLAUDE_CODE_BASE}"
            filename = "overview"

        print(f" Fetching: {url}")

        # Fetch page content
        html_content = fetch_page_content(url)
        if not html_content:
            error_count += 1
            continue

        # Convert to markdown
        markdown_content = html_to_markdown(html_content, url)
        if not markdown_content:
            error_count += 1
            continue

        # Save to file
        if save_markdown_file(markdown_content, filename):
            success_count += 1
        else:
            error_count += 1

        # Be respectful with requests
        if section != CLAUDE_CODE_SECTIONS[-1]:  # Don't delay after last request
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print("\n" + "=" * 50)
    print(f" Documentation fetch complete!")
    print(f" Successful: {success_count}")
    print(f" Errors: {error_count}")
    print(f" Files saved to: {OUTPUT_DIR.absolute()}")

    # Create index file
    create_index_file(success_count, error_count)


def create_index_file(success_count, error_count):
    """Create an index file for the documentation"""
    index_content = f"""# Claude Code Documentation Archive

Fetched on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Success: {success_count} files
Errors: {error_count} files

## Available Documentation

"""

    # List all markdown files
    for md_file in sorted(OUTPUT_DIR.glob("*.md")):
        if md_file.name != "index.md":
            index_content += f"- [{md_file.stem}]({md_file.name})\n"

    index_content += f"""
## Notes

- Documentation fetched from: https://docs.anthropic.com/en/docs/claude-code/
- Files are in markdown format for easy reading and searching
- Each file includes metadata with source URL and fetch timestamp
- Run the fetch script again to update documentation

## Usage

Use these files as offline reference for Claude Code CLI features and functionality.
For the most up-to-date information, always refer to the official documentation.
"""

    save_markdown_file(index_content, "index")


if __name__ == "__main__":
    main()
