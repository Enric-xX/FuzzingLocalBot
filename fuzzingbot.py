#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import signal
import threading
import urllib3
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
TIMEOUT = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
MAX_RETRIES = 2
FOUND = 0
TOTAL = 0
THREADS = 50
LOCK = threading.Lock()
START_TIME = time.time()
LAST_UPDATE = time.time()

# ============================================================
# UTILITIES
# ============================================================
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def show_progress():
    global FOUND, TOTAL, START_TIME, LAST_UPDATE
    if time.time() - LAST_UPDATE < 2:
        return
    LAST_UPDATE = time.time()
    elapsed = time.time() - START_TIME
    if elapsed > 0 and TOTAL > 0:
        speed = FOUND / elapsed
        eta = (TOTAL - FOUND) / (speed + 0.001)
        log(f"Progress: {FOUND}/{TOTAL} found | Speed: {speed:.1f}/s | ETA: {eta:.0f}s")

def show_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗   ██╗███████╗███████╗██╗███╗   ██╗ ██████╗   ║
║   ██╔════╝██║   ██║╚══███╔╝╚══███╔╝██║████╗  ██║██╔════╝   ║
║   █████╗  ██║   ██║  ███╔╝   ███╔╝ ██║██╔██╗ ██║██║  ███╗  ║
║   ██╔══╝  ██║   ██║ ███╔╝   ███╔╝  ██║██║╚██╗██║██║   ██║  ║
║   ██║     ╚██████╔╝███████╗███████╗██║██║ ╚████║╚██████╔╝  ║
║   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝   ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDATION: USE A VPN BEFORE RUNNING THIS              ║
║  Only for authorized pentesting                             ║
╚══════════════════════════════════════════════════════════════╝
""")

def show_help():
    print("""
Usage: python fuzzingbot.py <domain> <wordlist.txt> <results.txt>

Example:
    python fuzzingbot.py https://example.com wordlist.txt results.txt

Parameters:
    domain      - Target URL (e.g. https://example.com)
    wordlist.txt - File with directories and extensions
    results.txt  - File where results will be saved
""")

def configure_scan():
    """Ask user for scan speed and return thread count."""
    print("\n[*] Select scan speed:")
    print("    1. Slow (10 threads, stealth)")
    print("    2. Normal (50 threads)")
    print("    3. Fast (100 threads)")
    print("    4. Custom")
    
    choice = input("\n[*] Choose (1-4, Enter=2): ").strip() or "2"
    
    if choice == "1":
        return 10
    elif choice == "2":
        return 50
    elif choice == "3":
        return 100
    elif choice == "4":
        try:
            custom = int(input("[*] Number of threads: "))
            return max(1, min(200, custom))
        except:
            return 50
    else:
        return 50

# ============================================================
# LOAD WORDLIST
# ============================================================
def load_wordlist(filepath):
    directories = []
    extensions = []
    
    if not os.path.exists(filepath):
        log(f"ERROR: File {filepath} not found.")
        return [], []
    
    log(f"Loading {filepath}...")
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "." in line and "/" not in line and "\\" not in line:
                if not line.startswith("*"):
                    extensions.append(line)
            else:
                directories.append(line)
    
    log(f"Loaded: {len(directories)} directories, {len(extensions)} extensions")
    return directories, extensions

def generate_routes(directories, extensions):
    if directories and extensions:
        total = len(directories) * len(extensions)
        log(f"Generating {total} combinations...")
        return [d + e for d in directories for e in extensions]
    elif directories:
        return directories.copy()
    elif extensions:
        return extensions.copy()
    return []

# ============================================================
# TEST URL
# ============================================================
def test_url(url, timeout=TIMEOUT):
    headers = {"User-Agent": USER_AGENT}
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
                "content": response.text[:5000],
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
# MAIN
# ============================================================
def main():
    global FOUND, TOTAL, START_TIME, THREADS
    
    show_banner()
    
    if len(sys.argv) < 4:
        show_help()
        sys.exit(1)
    
    domain = sys.argv[1]
    wordlist_file = sys.argv[2]
    results_file = sys.argv[3]
    
    log(f"Starting backend for {domain}")
    
    # Configure scan speed
    THREADS = configure_scan()
    log(f"Using {THREADS} threads")
    
    directories, extensions = load_wordlist(wordlist_file)
    if not directories and not extensions:
        log("ERROR: Could not load directories or extensions.")
        sys.exit(1)
    
    routes = generate_routes(directories, extensions)
    TOTAL = len(routes)
    
    if TOTAL == 0:
        log("ERROR: No routes generated.")
        sys.exit(1)
    
    log(f"Total routes to test: {TOTAL}")
    
    START_TIME = time.time()
    results = []
    FOUND = 0
    progress_thread = threading.Thread(target=show_periodic_progress, args=(TOTAL, FOUND, START_TIME), daemon=True)
    progress_thread.start()
    
    log(f"Testing with {THREADS} threads...")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(test_url, urljoin(domain, route)): route for route in routes}
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            
            if result.get("exists", False):
                FOUND += 1
                with open(results_file, "a", encoding="utf-8") as f:
                    f.write(f"[{result['status']}] {result['url']}\n")
                log(f"FOUND: {result['status']} {result['url']}")
            
            if i % 100 == 0:
                show_progress()
    
    json_file = results_file.replace(".txt", ".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - START_TIME
    log("=" * 50)
    log(f"COMPLETED")
    log(f"   Total routes: {TOTAL}")
    log(f"   Found: {FOUND}")
    log(f"   Time: {elapsed:.1f}s")
    log(f"   Speed: {TOTAL/elapsed:.1f} routes/s")
    log(f"   Results: {results_file}")
    log(f"   JSON: {json_file}")
    log("=" * 50)
    
    # ============================================================
    # ANALYSIS AND REPORT
    # ============================================================
    try:
        from analyzer import Analyzer
        from reporter import Reporter
        
        log("\nAnalyzing results...")
        analyzer = Analyzer()
        
        if results:
            lengths = [r.get("content_length", 0) for r in results if r.get("status") == 200]
            if lengths:
                baseline = max(set(lengths), key=lengths.count)
                analyzer.set_baseline(baseline)
        
        for r in results:
            if r.get("exists", False) or r.get("status") in [401, 403, 500]:
                analyzer.analyze(r)
        
        log("Generating reports...")
        reporter = Reporter(domain, analyzer)
        
        md_file = reporter.save_markdown(TOTAL, elapsed, output_dir="output")
        html_file = reporter.save_html(TOTAL, elapsed, output_dir="output")
        
        summary = analyzer.get_summary()
        log(f"   Critical: {summary['critical']}")
        log(f"   High: {summary['high']}")
        log(f"   Medium: {summary['medium']}")
        log(f"   Low: {summary['low']}")
        log(f"   Info: {summary['info']}")
        log(f"   MD Report: {md_file}")
        log(f"   HTML Report: {html_file}")
        
    except ImportError:
        log("analyzer.py or reporter.py not found. Reports not generated.")
    except Exception as e:
        log(f"Error generating reports: {e}")

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        main()
    except KeyboardInterrupt:
        log("Interrupted by user.")
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
