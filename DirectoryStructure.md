# FuzzingLocalBot - Directory Structure

Complete project structure for FuzzingLocalBot v3.4.

---

## Project Tree

```
FuzzingLocalBot/
│
├── LICENSE
├── README.md
├── UserAgentsPool.md
├── FEATURES.md
├── STRUCTURE.md
├── CREDITS.md
│
├── config.ini
├── requirements.txt
│
├── fuzzingbot.py
├── analyzer.py
├── reporter.py
├── gui.ahk
│
├── extensiones.txt
├── output.txt
│
├── dictionaries/
│   ├── top.txt
│   ├── api.txt
│   ├── wp-fuzz.txt
│   ├── jira-fuzz.txt
│   ├── JHADDIX_LFI.txt
│   ├── iis.txt
│   ├── extensions.txt
│   ├── backendfiles.txt
│   ├── common-ms-httpd-log-locations.txt
│   ├── common-unix-httpd-log-locations.txt
│   ├── alt-extensions-asp.txt
│   ├── alt-extensions-jsp.txt
│   ├── alt-extensions-php.txt
│   ├── MimeTypes.txt
│   └── param.txt
│
├── mobile/
│   ├── MOBILEREADME.md
│   ├── mobilefuzzingbot.py
│   ├── mobileanalyzer.py
│   ├── mobilereporter.py
│   ├── requirements.txt
│   ├── output.txt
│   └── mobile wordlists/
│       ├── api.txt
│       ├── backup.txt
│       ├── common.txt
│       ├── extensions.txt
│       └── wordpress.txt
│
└── output/
    ├── scan_*.txt
    ├── scan_*.json
    ├── report_*.md
    ├── report_*.html
    └── report_*.csv

```

---


- `fuzzingbot.py` imports both `analyzer.py` and `reporter.py`
- `analyzer.py` is independent
- `reporter.py` uses data from `analyzer.py`

---

## Adding New Files

### New dictionary

1. Add `.txt` file to `dictionaries/`
2. It will appear automatically in the wordlist selector

### New mobile dictionary

1. Add `.txt` file to `mobile/mobile wordlists/`
2. It will appear automatically in the mobile selector

### New module

1. Create `.py` file in root
2. Import it in `fuzzingbot.py`
3. Document it in this file

### New report format

1. Add method to `reporter.py`
2. Call it from `save_interrupt_report()`
3. Document it in this file

---

*Part of FuzzingLocalBot v3.4 - See main README for full documentation.*
