#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FuzzingLocalBot Mobile v1.0
Lightweight web fuzzer for Termux (Android).
"""

import os
import sys
import time
import signal
import threading
import urllib3
import random
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("[!] Install requests: pip install requests")
    sys.exit(1)

# ============================================================
# CONFIGURATION
# ============================================================
TIMEOUT = 5
MAX_RETRIES = 1
MAX_THREADS = 10  # Mobile limit
FOUND = 0
TOTAL = 0
THREADS = 5
LOCK = threading.Lock()
START_TIME = time.time()
LAST_UPDATE = time.time()
SCAN_RESULTS = []
CURRENT_RESULTS_FILE = ""

# User-Agents (mobile-focused)
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

STEALTH_MODE = True
STEALTH_SPEED = "slow"

# ============================================================
# UTILITIES
# ============================================================
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def show_progress():
    global FOUND, TOTAL, START_TIME, LAST_UPDATE
    if time.time() - LAST_UPDATE < 3:
        return
    LAST_UPDATE = time.time()
    elapsed = time.time() - START_TIME
    if elapsed > 0 and TOTAL > 0:
        speed = FOUND / elapsed
        eta = (TOTAL - FOUND) / (speed + 0.001) if speed > 0 else 0
        log(f"Progress: {FOUND}/{TOTAL} found | Speed: {speed:.1f}/s | ETA: {eta:.0f}s")

def show_banner():
    print("""
╔══════════════════════════════════════════════╗
║                                              ║
║   FuzzingLocalBot Mobile v1.0                ║
║   Lightweight Web Fuzzer for Termux          ║
║                                              ║
╠══════════════════════════════════════════════╣
║  USE A VPN BEFORE RUNNING THIS               ║
║  Only for authorized pentesting              ║
╚══════════════════════════════════════════════╝
""")

def configure_scan():
    """Ask user for scan speed (mobile-optimized)."""
    global STEALTH_MODE, STEALTH_SPEED
    
    print("\n[*] Select scan speed (Mobile):")
    print("    1. Slow (3 threads, stealth)")
    print("    2. Normal (5 threads)")
    print("    3. Fast (10 threads)")
    
    choice = input("\n[*] Choose (1-3, Enter=2): ").strip() or "2"
    
    if choice == "1":
        threads = 3
        STEALTH_MODE = True
        STEALTH_SPEED = "slow"
    elif choice == "2":
        threads = 5
        STEALTH_MODE = False
    elif choice == "3":
        threads = 10
        STEALTH_MODE = False
    else:
        threads = 5
    
    if STEALTH_MODE:
        log(f"Stealth mode enabled (slow)")
    
    return threads

def select_wordlist():
    """Show available mobile wordlists."""
    wordlist_dir = "wordlists"
    
    if not os.path.exists(wordlist_dir):
        log("ERROR: wordlists/ folder not found.")
        sys.exit(1)
    
    files = sorted([f for f in os.listdir(wordlist_dir) if f.endswith(".txt")])
    
    if not files:
        log("ERROR: No wordlists found.")
        sys.exit(1)
    
    print(f"\n[*] Available wordlists:\n")
    for i, f in enumerate(files, 1):
        print(f"    {i}. {f}")
    
    print(f"\n[*] Choose a number (Enter=1):")
    choice = input("> ").strip()
    
    if choice == "":
        return f"{wordlist_dir}/{files[0]}"
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(files):
            return f"{wordlist_dir}/{files[index]}"
    except:
        pass
    
    return f"{wordlist_dir}/{files[0]}"

# ============================================================
# LOAD WORDLIST
# ============================================================
def load_wordlist(filepath):
    """Load wordlist treating all lines as complete routes."""
    standalone = []
    
    if not os.path.exists(filepath):
        log(f"ERROR: File {filepath} not found.")
        return []
    
    log(f"Loading {filepath}...")
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                standalone.append(line)
    
    log(f"Loaded: {len(standalone)} routes")
    return standalone

# ============================================================
# TEST URL
# ============================================================
def test_url(url, timeout=TIMEOUT):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    # Always use light stealth on mobile
    if STEALTH_MODE:
        time.sleep(random.uniform(1, 2))
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                allow_redirects=True,
                verify=False
            )
            return {
                "url": url,
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(response.content),
                "redirect": response.url if response.history else None,
                "exists": response.status_code < 400,
                "content": response.text[:3000],  # Less content for mobile RAM
                "headers": dict(response.headers)
            }
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                continue
            return {"url": url, "status": "timeout", "exists": False}
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                continue
            return {"url": url, "status": "connection_error", "exists": False}
        except Exception as e:
            return {"url": url, "status": "error", "error": str(e), "exists": False}
    return {"url": url, "status": "error", "exists": False}

# ============================================================
# REAL-TIME PROGRESS
# ============================================================
def show_periodic_progress(total, found, start_time):
    global LAST_UPDATE
    while True:
        time.sleep(5)
        elapsed = time.time() - start_time
        if total > 0 and elapsed > 0:
            speed = found / elapsed
            remaining = total - found
            eta = remaining / (speed + 0.001) if speed > 0 else 0
            log(f"Progress: {found}/{total} | Speed: {speed:.1f}/s | ETA: {eta:.0f}s")

# ============================================================
# SAVE REPORT
# ============================================================
def save_interrupt_report():
    """Generate TXT report with current results."""
    global SCAN_RESULTS, CURRENT_RESULTS_FILE
    
    if not SCAN_RESULTS:
        log("\nNo results to save.")
        return
    
    log("\nGenerating report...")
    
    try:
        from analyzer import Analyzer
        from reporter import Reporter
        
        analyzer = Analyzer()
        
        lengths = [r.get("content_length", 0) for r in SCAN_RESULTS if r.get("status") == 200]
        if lengths:
            baseline = max(set(lengths), key=lengths.count)
            analyzer.set_baseline(baseline)
        
        for r in SCAN_RESULTS:
            if r.get("exists", False) or r.get("status") in [401, 403, 500]:
                analyzer.analyze(r)
        
        domain = "unknown"
        if SCAN_RESULTS:
            first_url = SCAN_RESULTS[0].get("url", "")
            if "://" in first_url:
                domain = first_url.split("://")[1].split("/")[0]
        
        reporter = Reporter(domain, analyzer)
        elapsed = time.time() - START_TIME
        found_count = sum(1 for r in SCAN_RESULTS if r.get("exists", False))
        
        txt_file = reporter.save_txt(found_count, elapsed, output_dir="output")
        
        summary = analyzer.get_summary()
        log(f"   Critical: {summary['critical']}")
        log(f"   High: {summary['high']}")
        log(f"   Medium: {summary['medium']}")
        log(f"   Report: {txt_file}")
        log("Report saved!")
        
    except Exception as e:
        log(f"Could not generate report: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n")
    log("Interrupted. Saving results...")
    save_interrupt_report()
    sys.exit(0)

# ============================================================
# MAIN
# ============================================================
def main():
    global FOUND, TOTAL, START_TIME, THREADS, SCAN_RESULTS, CURRENT_RESULTS_FILE
    
    signal.signal(signal.SIGINT, signal_handler)
    
    show_banner()
    
    domain = input("[*] Target domain (e.g. https://example.com): ").strip()
    if not domain:
        log("ERROR: No domain provided.")
        sys.exit(1)
    if not domain.startswith("http"):
        domain = "https://" + domain
    
    wordlist_file = select_wordlist()
    CURRENT_RESULTS_FILE = f"output/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    log(f"Starting scan for {domain}")
    
    THREADS = configure_scan()
    log(f"Using {THREADS} threads")
    
    routes = load_wordlist(wordlist_file)
    if not routes:
        log("ERROR: Could not load wordlist.")
        sys.exit(1)
    
    TOTAL = len(routes)
    log(f"Total routes to test: {TOTAL}")
    
    START_TIME = time.time()
    SCAN_RESULTS = []
    FOUND = 0
    progress_thread = threading.Thread(target=show_periodic_progress, args=(TOTAL, FOUND, START_TIME), daemon=True)
    progress_thread.start()
    
    log(f"Testing with {THREADS} threads...")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(test_url, urljoin(domain, route)): route for route in routes}
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            SCAN_RESULTS.append(result)
            
            if result.get("exists", False):
                FOUND += 1
                with open(CURRENT_RESULTS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{result['status']}] {result['url']}\n")
                log(f"FOUND: {result['status']} {result['url']}")
            
            if i % 50 == 0:
                show_progress()
    
    elapsed = time.time() - START_TIME
    log("=" * 50)
    log(f"COMPLETED")
    log(f"   Total routes: {TOTAL}")
    log(f"   Found: {FOUND}")
    log(f"   Time: {elapsed:.1f}s")
    log(f"   Results: {CURRENT_RESULTS_FILE}")
    log("=" * 50)
    
    save_interrupt_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrupted by user.")
    except Exception as e:
        log(f"ERROR: {e}")
