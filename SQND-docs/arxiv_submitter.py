#!/usr/bin/env python3
"""
arXiv Semi-Automated Submission Tool
=====================================
Scans current folder for papers, extracts metadata via Claude API,
fills arXiv submission forms via Selenium, stops at submit for human confirmation.

Usage:
    python arxiv_submitter.py --api-key YOUR_ANTHROPIC_KEY --arxiv-user YOUR_USERNAME --arxiv-pass YOUR_PASSWORD

Author: Andrew H. Bond
License: MIT
"""

import os
import sys
import json
import argparse
import hashlib
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import time

# =============================================================================
# CONFIGURATION - Edit these constants for your submissions
# =============================================================================

AUTHOR_NAME = "Andrew H. Bond"
AUTHOR_EMAIL = "andrew.bond@sjsu.edu"  # Will be overridden by CLI if provided
AFFILIATION = "San José State University"
DEPARTMENT = "Department of Computer Engineering"
ADDRESS = "One Washington Square, San José, CA 95192"
COUNTRY = "United States"
HOMEPAGE = ""  # Optional

# Default arXiv category (can be overridden per-paper by Claude)
DEFAULT_CATEGORY = "cs.AI"

# Preferred format priority (highest priority first)
FORMAT_PRIORITY = [".tex", ".md", ".docx", ".pdf"]

# Claude model for metadata extraction
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Selenium settings
ARXIV_SUBMIT_URL = "https://arxiv.org/submit"
BROWSER_HEADLESS = False  # Set True for headless mode
WAIT_TIMEOUT = 30  # seconds

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PaperMetadata:
    """Metadata for a single paper"""
    filepath: str
    title: str
    abstract: str
    authors: list[str]
    category: str
    secondary_categories: list[str]
    comments: str  # e.g., "15 pages, 3 figures"
    journal_ref: str  # Leave empty for new submissions
    doi: str  # Leave empty for new submissions
    report_num: str  # Leave empty usually
    acm_class: str  # Optional ACM classification
    msc_class: str  # Optional Math Subject Classification
    license: str  # Default: arXiv.org perpetual non-exclusive license
    status: str  # "pending", "submitted", "error"
    arxiv_id: str  # Filled after submission
    error_message: str

    def to_dict(self):
        return asdict(self)


# =============================================================================
# DOCUMENT DETECTION AND DEDUPLICATION
# =============================================================================

def get_document_files(folder: str = ".") -> list[Path]:
    """Find all document files in folder"""
    extensions = {".docx", ".pdf", ".tex", ".md"}
    folder_path = Path(folder)
    files = []
    for ext in extensions:
        files.extend(folder_path.glob(f"*{ext}"))
    return sorted(files)


def normalize_filename(filepath: Path) -> str:
    """
    Normalize filename for deduplication.
    Strips extension, lowercases, removes common suffixes like _v1, _final, etc.
    """
    stem = filepath.stem.lower()
    # Remove version suffixes
    stem = re.sub(r'[_\-]?v\d+[_\-]?\d*', '', stem)
    stem = re.sub(r'[_\-]?(final|draft|revised|edit|copy)$', '', stem)
    # Remove trailing numbers/dates
    stem = re.sub(r'[_\-]?\d{4,}$', '', stem)
    # Normalize separators
    stem = re.sub(r'[_\-\s]+', '_', stem)
    return stem.strip('_')


def deduplicate_documents(files: list[Path]) -> list[Path]:
    """
    Group documents by normalized name, keep highest priority format.
    Returns list of unique documents (one per logical paper).
    """
    groups: dict[str, list[Path]] = {}
    
    for f in files:
        key = normalize_filename(f)
        if key not in groups:
            groups[key] = []
        groups[key].append(f)
    
    result = []
    for key, paths in groups.items():
        # Sort by format priority
        paths.sort(key=lambda p: (
            FORMAT_PRIORITY.index(p.suffix.lower()) 
            if p.suffix.lower() in FORMAT_PRIORITY 
            else len(FORMAT_PRIORITY)
        ))
        result.append(paths[0])
        if len(paths) > 1:
            print(f"  Dedup: keeping {paths[0].name}, skipping {[p.name for p in paths[1:]]}")
    
    return sorted(result, key=lambda p: p.name)


# =============================================================================
# DOCUMENT TEXT EXTRACTION
# =============================================================================

def extract_text_from_file(filepath: Path, max_chars: int = 50000) -> str:
    """Extract text content from document for metadata analysis"""
    ext = filepath.suffix.lower()
    
    try:
        if ext == ".md":
            return filepath.read_text(encoding='utf-8')[:max_chars]
        
        elif ext == ".tex":
            return filepath.read_text(encoding='utf-8')[:max_chars]
        
        elif ext == ".txt":
            return filepath.read_text(encoding='utf-8')[:max_chars]
        
        elif ext == ".pdf":
            # Try pdftotext
            import subprocess
            result = subprocess.run(
                ["pdftotext", "-l", "5", str(filepath), "-"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout[:max_chars]
            return f"[PDF extraction failed: {result.stderr}]"
        
        elif ext == ".docx":
            # Try pandoc
            import subprocess
            result = subprocess.run(
                ["pandoc", str(filepath), "-t", "plain"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout[:max_chars]
            return f"[DOCX extraction failed: {result.stderr}]"
        
        else:
            return f"[Unsupported format: {ext}]"
    
    except Exception as e:
        return f"[Extraction error: {e}]"


# =============================================================================
# CLAUDE API METADATA EXTRACTION
# =============================================================================

def extract_metadata_with_claude(filepath: Path, text_content: str, api_key: str) -> PaperMetadata:
    """Use Claude API to extract paper metadata from content"""
    
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this academic paper and extract metadata for arXiv submission.

FILENAME: {filepath.name}

CONTENT (first ~50k chars):
{text_content}

---

Return a JSON object with these fields:
{{
    "title": "Full paper title",
    "abstract": "Complete abstract (usually 150-300 words)",
    "authors": ["Author One", "Author Two"],
    "category": "Primary arXiv category (e.g., cs.AI, cs.LG, quant-ph, physics.soc-ph)",
    "secondary_categories": ["optional", "secondary", "categories"],
    "comments": "e.g., '15 pages, 3 figures' or empty string",
    "acm_class": "ACM classification if applicable, else empty",
    "msc_class": "Math Subject Classification if applicable, else empty"
}}

IMPORTANT:
- For category, choose from: cs.AI, cs.LG, cs.CL, cs.CV, cs.NE, quant-ph, physics.soc-ph, stat.ML, math.OC, etc.
- If this appears to be about AI safety/alignment, use cs.AI
- If about ethics/philosophy + computation, consider cs.AI or cs.CY
- If about quantum cognition or quantum-like models, consider quant-ph or physics.soc-ph
- Extract the FULL abstract, not a summary
- For authors, use full names as written in the paper

Return ONLY the JSON object, no other text."""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON (handle potential markdown code blocks)
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json?\n?', '', response_text)
            response_text = re.sub(r'\n?```$', '', response_text)
        
        data = json.loads(response_text)
        
        return PaperMetadata(
            filepath=str(filepath),
            title=data.get("title", filepath.stem),
            abstract=data.get("abstract", ""),
            authors=data.get("authors", [AUTHOR_NAME]),
            category=data.get("category", DEFAULT_CATEGORY),
            secondary_categories=data.get("secondary_categories", []),
            comments=data.get("comments", ""),
            journal_ref="",
            doi="",
            report_num="",
            acm_class=data.get("acm_class", ""),
            msc_class=data.get("msc_class", ""),
            license="arXiv.org perpetual, non-exclusive license",
            status="pending",
            arxiv_id="",
            error_message=""
        )
    
    except json.JSONDecodeError as e:
        print(f"  JSON parse error for {filepath.name}: {e}")
        return create_fallback_metadata(filepath)
    
    except Exception as e:
        print(f"  Claude API error for {filepath.name}: {e}")
        return create_fallback_metadata(filepath)


def create_fallback_metadata(filepath: Path) -> PaperMetadata:
    """Create metadata with placeholders when extraction fails"""
    return PaperMetadata(
        filepath=str(filepath),
        title=filepath.stem.replace("_", " ").replace("-", " ").title(),
        abstract="[ABSTRACT EXTRACTION FAILED - PLEASE FILL MANUALLY]",
        authors=[AUTHOR_NAME],
        category=DEFAULT_CATEGORY,
        secondary_categories=[],
        comments="",
        journal_ref="",
        doi="",
        report_num="",
        acm_class="",
        msc_class="",
        license="arXiv.org perpetual, non-exclusive license",
        status="needs_review",
        arxiv_id="",
        error_message="Metadata extraction failed"
    )


# =============================================================================
# MANIFEST GENERATION
# =============================================================================

def generate_manifest(papers: list[PaperMetadata], output_file: str = "arxiv_manifest.json"):
    """Save all paper metadata to a JSON manifest for review"""
    manifest = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "author_defaults": {
            "name": AUTHOR_NAME,
            "email": AUTHOR_EMAIL,
            "affiliation": AFFILIATION,
            "department": DEPARTMENT,
            "address": ADDRESS,
            "country": COUNTRY
        },
        "papers": [p.to_dict() for p in papers]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest saved to: {output_file}")
    print(f"Review and edit this file, then run with --submit to begin submission.")
    return output_file


def load_manifest(manifest_file: str) -> tuple[dict, list[PaperMetadata]]:
    """Load manifest from JSON file"""
    with open(manifest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    author_defaults = data.get("author_defaults", {})
    papers = []
    for p in data.get("papers", []):
        papers.append(PaperMetadata(**p))
    
    return author_defaults, papers


# =============================================================================
# SELENIUM SUBMISSION
# =============================================================================

def setup_browser(headless: bool = False):
    """Initialize Selenium WebDriver"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Try to find chromedriver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        # Try with explicit service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    
    driver.implicitly_wait(WAIT_TIMEOUT)
    return driver


def arxiv_login(driver, username: str, password: str):
    """Log into arXiv"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    driver.get("https://arxiv.org/login")
    
    # Wait for login form
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.clear()
    username_field.send_keys(username)
    
    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(password)
    
    # Submit
    login_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
    login_button.click()
    
    # Wait for redirect
    time.sleep(3)
    
    # Check if login succeeded
    if "login" in driver.current_url.lower():
        raise Exception("Login failed - check credentials")
    
    print("  Logged into arXiv successfully")


def submit_paper_to_arxiv(driver, paper: PaperMetadata, author_defaults: dict) -> bool:
    """
    Fill out arXiv submission form for a single paper.
    Returns True if ready for user to click submit, False on error.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    try:
        # Start new submission
        driver.get("https://arxiv.org/submit")
        time.sleep(2)
        
        # Click "Start New Submission" or similar
        try:
            new_sub_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(),'Start')] | //button[contains(text(),'New')]")
            ))
            new_sub_btn.click()
            time.sleep(2)
        except:
            pass  # May already be on submission page
        
        # === LICENSE SELECTION ===
        try:
            # Look for license radio buttons or dropdown
            license_options = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@name,'license')]")
            if license_options:
                # Select perpetual non-exclusive (usually first option)
                license_options[0].click()
            
            # Continue button
            continue_btn = driver.find_element(By.XPATH, "//input[@value='Continue'] | //button[contains(text(),'Continue')]")
            continue_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"    License step issue: {e}")
        
        # === FILE UPLOAD ===
        try:
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(os.path.abspath(paper.filepath))
            time.sleep(3)
            
            # Click upload/continue
            upload_btn = driver.find_element(By.XPATH, 
                "//input[@type='submit'] | //button[contains(text(),'Upload')] | //button[contains(text(),'Continue')]"
            )
            upload_btn.click()
            time.sleep(5)  # Wait for processing
        except Exception as e:
            print(f"    File upload issue: {e}")
        
        # === METADATA FORM ===
        # Title
        try:
            title_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@name='title'] | //textarea[@name='title']")
            ))
            title_field.clear()
            title_field.send_keys(paper.title)
        except:
            pass
        
        # Authors
        try:
            authors_field = driver.find_element(By.XPATH, "//textarea[@name='authors'] | //input[@name='authors']")
            authors_field.clear()
            authors_field.send_keys(", ".join(paper.authors))
        except:
            pass
        
        # Abstract
        try:
            abstract_field = driver.find_element(By.XPATH, "//textarea[@name='abstract']")
            abstract_field.clear()
            abstract_field.send_keys(paper.abstract)
        except:
            pass
        
        # Category
        try:
            category_select = Select(driver.find_element(By.XPATH, "//select[@name='category']"))
            category_select.select_by_value(paper.category)
        except:
            try:
                # Try text input for category
                cat_field = driver.find_element(By.XPATH, "//input[@name='category']")
                cat_field.clear()
                cat_field.send_keys(paper.category)
            except:
                pass
        
        # Comments (optional)
        if paper.comments:
            try:
                comments_field = driver.find_element(By.XPATH, "//input[@name='comments'] | //textarea[@name='comments']")
                comments_field.clear()
                comments_field.send_keys(paper.comments)
            except:
                pass
        
        # ACM Class (optional)
        if paper.acm_class:
            try:
                acm_field = driver.find_element(By.XPATH, "//input[@name='acm_class']")
                acm_field.clear()
                acm_field.send_keys(paper.acm_class)
            except:
                pass
        
        # MSC Class (optional)
        if paper.msc_class:
            try:
                msc_field = driver.find_element(By.XPATH, "//input[@name='msc_class']")
                msc_field.clear()
                msc_field.send_keys(paper.msc_class)
            except:
                pass
        
        print(f"\n{'='*60}")
        print(f"READY TO SUBMIT: {paper.title[:50]}...")
        print(f"Category: {paper.category}")
        print(f"File: {paper.filepath}")
        print(f"{'='*60}")
        print("\n>>> Review the form and CLICK SUBMIT when ready <<<")
        print(">>> Press ENTER in this terminal after submitting (or 's' to skip) <<<\n")
        
        return True
    
    except Exception as e:
        print(f"    Error filling form: {e}")
        paper.status = "error"
        paper.error_message = str(e)
        return False


def run_submission_loop(manifest_file: str, arxiv_user: str, arxiv_pass: str):
    """Main submission loop - process each paper in manifest"""
    
    author_defaults, papers = load_manifest(manifest_file)
    pending_papers = [p for p in papers if p.status == "pending"]
    
    if not pending_papers:
        print("No pending papers to submit.")
        return
    
    print(f"\nFound {len(pending_papers)} papers to submit.")
    print("Starting browser...")
    
    driver = setup_browser(headless=BROWSER_HEADLESS)
    
    try:
        # Login once
        print("Logging into arXiv...")
        arxiv_login(driver, arxiv_user, arxiv_pass)
        
        for i, paper in enumerate(pending_papers):
            print(f"\n[{i+1}/{len(pending_papers)}] Processing: {paper.title[:50]}...")
            
            success = submit_paper_to_arxiv(driver, paper, author_defaults)
            
            if success:
                # Wait for user to click submit
                user_input = input().strip().lower()
                
                if user_input == 's':
                    print("  Skipped.")
                    paper.status = "skipped"
                else:
                    print("  Marked as submitted (verify on arXiv).")
                    paper.status = "submitted"
                
                # Save progress
                save_manifest_progress(manifest_file, papers)
            else:
                print(f"  Failed to prepare submission.")
                user_input = input("Press ENTER to continue to next paper, or 'q' to quit: ").strip().lower()
                if user_input == 'q':
                    break
    
    finally:
        # Save final state
        save_manifest_progress(manifest_file, papers)
        
        print("\nClosing browser...")
        driver.quit()
        
        # Summary
        submitted = len([p for p in papers if p.status == "submitted"])
        skipped = len([p for p in papers if p.status == "skipped"])
        errors = len([p for p in papers if p.status == "error"])
        print(f"\nSummary: {submitted} submitted, {skipped} skipped, {errors} errors")


def save_manifest_progress(manifest_file: str, papers: list[PaperMetadata]):
    """Update manifest with current status"""
    with open(manifest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data["papers"] = [p.to_dict() for p in papers]
    data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="arXiv Semi-Automated Submission Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Step 1: Generate manifest (extract metadata from papers)
  python arxiv_submitter.py --api-key sk-ant-xxx --scan

  # Step 2: Review/edit arxiv_manifest.json

  # Step 3: Submit papers
  python arxiv_submitter.py --arxiv-user myuser --arxiv-pass mypass --submit

  # Or do everything:
  python arxiv_submitter.py --api-key sk-ant-xxx --arxiv-user myuser --arxiv-pass mypass --scan --submit
        """
    )
    
    parser.add_argument("--api-key", help="Anthropic API key for metadata extraction")
    parser.add_argument("--arxiv-user", help="arXiv username")
    parser.add_argument("--arxiv-pass", help="arXiv password")
    parser.add_argument("--email", help=f"Override author email (default: {AUTHOR_EMAIL})")
    parser.add_argument("--folder", default=".", help="Folder to scan for papers (default: current)")
    parser.add_argument("--manifest", default="arxiv_manifest.json", help="Manifest file path")
    parser.add_argument("--scan", action="store_true", help="Scan folder and generate/update manifest")
    parser.add_argument("--submit", action="store_true", help="Begin submission process")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    args = parser.parse_args()
    
    # Update globals from args
    global AUTHOR_EMAIL, BROWSER_HEADLESS
    if args.email:
        AUTHOR_EMAIL = args.email
    if args.headless:
        BROWSER_HEADLESS = True
    
    if not args.scan and not args.submit:
        parser.print_help()
        print("\nError: Must specify --scan and/or --submit")
        sys.exit(1)
    
    # === SCAN MODE ===
    if args.scan:
        if not args.api_key:
            print("Error: --api-key required for --scan mode")
            sys.exit(1)
        
        print(f"Scanning folder: {args.folder}")
        files = get_document_files(args.folder)
        print(f"Found {len(files)} document files")
        
        files = deduplicate_documents(files)
        print(f"After dedup: {len(files)} unique papers")
        
        if not files:
            print("No papers found.")
            sys.exit(0)
        
        print("\nExtracting metadata via Claude API...")
        papers = []
        for i, f in enumerate(files):
            print(f"  [{i+1}/{len(files)}] {f.name}")
            text = extract_text_from_file(f)
            metadata = extract_metadata_with_claude(f, text, args.api_key)
            papers.append(metadata)
            print(f"    -> {metadata.title[:50]}... [{metadata.category}]")
        
        manifest_path = generate_manifest(papers, args.manifest)
        print(f"\n✓ Manifest created: {manifest_path}")
        print(f"  Review and edit this file, then run with --submit")
    
    # === SUBMIT MODE ===
    if args.submit:
        if not args.arxiv_user or not args.arxiv_pass:
            print("Error: --arxiv-user and --arxiv-pass required for --submit mode")
            sys.exit(1)
        
        if not os.path.exists(args.manifest):
            print(f"Error: Manifest not found: {args.manifest}")
            print("Run with --scan first to generate manifest.")
            sys.exit(1)
        
        run_submission_loop(args.manifest, args.arxiv_user, args.arxiv_pass)


if __name__ == "__main__":
    main()
