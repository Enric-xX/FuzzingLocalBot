#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
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
TIMEOUT = 3
MAX_RETRIES = 2
FOUND = 0
TOTAL = 0
THREADS = 50
LOCK = threading.Lock()
START_TIME = time.time()
LAST_UPDATE = time.time()

# User-Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

# Stealth delays
STEALTH_DELAYS = {
    "slow": (1, 3),
    "normal": (0.5, 1),
    "fast": (0, 0.5),
}
STEALTH_MODE = False
STEALTH_SPEED = "normal"

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
╔═════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                         ║
║   ███████╗██╗   ██╗███████╗███████╗██╗      ██████╗  ██████╗ █████╗ ██╗     ██████╗  ██████╗ ████████╗  ║
║   ██╔════╝██║   ██║╚══███╔╝╚══███╔╝██║     ██╔═══██╗██╔════╝██╔══██╗██║     ██╔══██╗██╔═══██╗╚══██╔══╝  ║
║   █████╗  ██║   ██║  ███╔╝   ███╔╝ ██║     ██║   ██║██║     ███████║██║     ██████╔╝██║   ██║   ██║     ║
║   ██╔══╝  ██║   ██║ ███╔╝   ███╔╝  ██║     ██║   ██║██║     ██╔══██║██║     ██╔══██╗██║   ██║   ██║     ║
║   ██║     ╚██████╔╝███████╗███████╗███████╗╚██████╔╝╚██████╗██║  ██║███████╗██████╔╝╚██████╔╝   ██║     ║
║  ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝    ╚═╝      ║
║                                                                                                         ║
╠═════════════════════════════════════════════════════════════════════════════════════════════════════════╣
                    ║  RECOMMENDATION: USE A VPN BEFORE RUNNING THIS              ║
                    ║  Only for authorized pentesting                             ║
                    ╚═════════════════════════════════════════════════════════════╝
""")

def configure_scan():
    """Ask user for scan speed, stealth mode, and return thread count."""
    global STEALTH_MODE, STEALTH_SPEED
    
    print("\n[*] Select scan speed:")
    print("    1. Slow (10 threads, stealth)")
    print("    2. Normal (50 threads, stealth)")
    print("    3. Fast (100 threads)")
    print("    4. Custom")
    
    choice = input("\n[*] Choose (1-4, Enter=2): ").strip() or "2"
    
    if choice == "1":
        threads = 10
        STEALTH_MODE = True
        STEALTH_SPEED = "slow"
    elif choice == "2":
        threads = 50
        STEALTH_MODE = True
        STEALTH_SPEED = "normal"
    elif choice == "3":
        threads = 100
        STEALTH_MODE = False
    elif choice == "4":
        try:
            custom = int(input("[*] Number of threads: "))
            threads = max(1, min(200, custom))
        except:
            threads = 50
        stealth = input("[*] Enable stealth mode? (y/n, Enter=n): ").strip().lower()
        STEALTH_MODE = stealth == "y"
        if STEALTH_MODE:
            speed = input("[*] Stealth speed (slow/normal/fast, Enter=normal): ").strip().lower() or "normal"
            STEALTH_SPEED = speed if speed in STEALTH_DELAYS else "normal"
    else:
        threads = 50
    
    if STEALTH_MODE:
        log(f"Stealth mode enabled ({STEALTH_SPEED})")
    
    return threads

def select_wordlist():
    """Show available wordlists and let user pick one."""
    wordlist_dir = "wordlists"
    
    all_wordlists = []
    
    if os.path.exists("extensiones.txt"):
        all_wordlists.append("extensiones.txt (42k full scan)")
    
    if os.path.exists(wordlist_dir):
        files = sorted([f for f in os.listdir(wordlist_dir) if f.endswith(".txt")])
        for f in files:
            all_wordlists.append(f"{wordlist_dir}/{f}")
    
    if not all_wordlists:
        log("No wordlists found. Using extensiones.txt")
        return "extensiones.txt"
    
    print(f"\n[*] Available wordlists:\n")
    for wl in all_wordlists:
        print(f"    {wl}")
    
    print(f"\n[*] Type the filename (Enter=extensiones.txt):")
    choice = input("> ").strip()
    
    if choice == "":
        return "extensiones.txt"
    
    for wl in all_wordlists:
        if choice in wl:
            return wl.split(" ")[0]
    
    log(f"'{choice}' not found. Using extensiones.txt")
    return "extensiones.txt"

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
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    if STEALTH_MODE:
        delay_min, delay_max = STEALTH_DELAYS.get(STEALTH_SPEED, (0.5, 1))
        time.sleep(random.uniform(delay_min, delay_max))
    
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
    
    # Interactive mode
    domain = input("[*] Target domain (e.g. https://example.com): ").strip()
    if not domain:
        log("ERROR: No domain provided.")
        sys.exit(1)
    if not domain.startswith("http"):
        domain = "https://" + domain
    
    wordlist_file = select_wordlist()
    results_file = f"output/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
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
