# FuzzingLocalBot v3.0

Automation of directory and extension fuzzing, featuring intelligent analysis and professional reporting for authorized penetration testing.

![Linux](https://img.shields.io/badge/Linux-purple)
![Windows](https://img.shields.io/badge/Windows-blue)
![Termux](https://img.shields.io/badge/Termux-green)
![Git](https://img.shields.io/badge/Git-orange)
![License](https://img.shields.io/badge/License-GPL%20v3-red)
![Python](https://img.shields.io/badge/Python-3.6+-yellow)
![AutoHotKey](https://img.shields.io/badge/AutoHotkey-1.1+-green)

---

<img width="1200" height="400" alt="image" src="https://github.com/user-attachments/assets/9421c603-84a2-4985-9022-0c5dff58f78c" />


---

## Dependencies

Before installing, you need to have installed:

| Program | Download | Is it required?|
|----------|----------|---------------|
| **Python 3.6+** | [python.org/downloads](https://www.python.org/downloads/) | ✅ Yes |
| **Git** | [git-scm.com/install](https://git-scm.com/install) | ✅ Yes |
| **AutoHotkey 1.1+** | [autohotkey.com/download](https://www.autohotkey.com/download/) | ⚠️ Only for GUI (Windows) |

---

## Installation

### Linux 

```
git clone https://github.com/Enric-xX/FuzzingLocalBot.git
```
```
cd FuzzingLocalBot
```
```
pip install -r requirements.txt
```
### Windows

```
git clone https://github.com/Enric-xX/FuzzingLocalBot.git
```
```
cd FuzzingLocalBot
```
```
pip install -r requirements.txt
```

---

## Use

### With GUI (Windows)

- Run bot.ahk with AutoHotkey

- Select the browser

- Enter the target domain (e.g., https://example.com)
  
- Click START FUZZING

### From terminal (Linux / Windows)

```
cd FuzzingLocalBot
```
```
python fuzzingbot.py
```

---

## Update repository

```
cd FuzzingLocalBot
```
```
git pull
```
---

## What does it do?

1. **Fuzzing** → Scans routes against the target domain with configurable threads (10-200)
2. **Wordlist selection** → Choose from 15 curated dictionaries (APIs, WordPress, Jira, LFI, etc.)
3. **Analysis** → Detects technologies (WordPress, Apache, PHP...), directory listing, exposed backups, config files, Git exposed, and more
4. **Report** → Generates a professional report in Markdown and HTML with findings classified by severity

---

## Features

- **15 curated dictionaries**: General, APIs, WordPress, Jira, Path Traversal, IIS, and more
- **Interactive wordlist selector**: Browse and choose from available dictionaries
- **42k lines full scan dictionary** included
- **Configurable scan speed**: Slow (10 threads, stealth), Normal (50 threads), Fast (100 threads), or Custom
- **Stealth mode**: Random delays between requests to evade detection
- **User-Agent rotation**: 6 different User-Agents to avoid fingerprinting
- **Response analyzer**: Detects technologies and classifies findings by severity
- **Professional reports**: Generates Markdown and HTML reports
- **Technologies fingerprinting**: WordPress, Apache, Nginx, PHP, Laravel, Django, and more

---

## Scan Modes

| Mode | Threads | User-Agent | Delay | Use Case |
|------|---------|------------|-------|----------|
| Slow | 10 | Rotating (6) | 1-3s | Stealth, evading WAF/IDS |
| Normal | 50 | Rotating (6) | 0.5-1s | Balanced pentesting |
| Fast | 100 | Rotating (6) | None | CTFs, authorized speed tests |
| Custom | Any | Rotating (6) | Configurable | Full control

---

## Findings Classification

| Severity | What It Detects|
|-------|-------------|
| Critical | Directory listing, exposed PHP info, SQL dumps, exposed Git |
| High | Backups, configuration files, server errors |
| Medium | 403 Forbidden, 401 Unauthorized, error disclosure |
| Low | Login redirects |
| Info | Detected technologies, fingerprints |

---

## Directory Structure

```
FuzzingLocalBot/
├── LICENSE                                                                  GPL v3 License
├── README.md                                                                This file
├── CREDITS.md                                                               Wordlist authors credits
├── config.ini                                                               Configuration file
├── requirements.txt                                                         Python dependencies
├── extensiones.txt                                                          42k paths dictionary 
├── fuzzingbot.py                                                            Main fuzzing engine 
├── analyzer.py                                                              HTTP response analyzer
├── reporter.py                                                              Report generator
├── bot.ahk                                                                  Graphical interface 
├── dictionaries/                                                            Curated wordlist collection
│   ├── top.txt                                                              General directories 
│   ├── api.txt                                                              API endpoints 
│   ├── wp-fuzz.txt                                                          WordPress paths 
│   ├── jira-fuzz.txt                                                        Jira/Atlassian paths
│   ├── JHADDIX_LFI.txt                                                      Path traversal payloads
│   ├── iis.txt                                                              IIS/Windows paths
│   ├── extensions.txt                                                       File extensions
│   ├── common-ms-httpd-log-locations.txt                                    Windows log paths
│   ├── common-unix-httpd-log-locations.txt                                  Unix log paths
│   ├── alt-extensions-asp.txt                                               ASP extensions
│   ├── alt-extensions-jsp.txt                                               JSP extensions
│   ├── alt-extensions-php.txt                                               PHP extensions
│   ├── MimeTypes.txt                                                        MIME types
│   └── param.txt                                                            Parameter names
└── output/                                                                  Results folder
    ├── scan_*.txt                                                           Raw results
    ├── scan_*.json                                                          JSON results
    ├── report_*.md                                                          Markdown report
    └── report_*.html                                                        HTML report
```
---

## Security Warning

### USE A VPN BEFORE RUNNING THIS TOOL.

This tool is exclusively for authorized pentesting. Do not use it against systems without the explicit permission of their owner.

---

## Mobile Version

A lightweight version for Android (Termux) is available at:
[FuzzingLocalBot-Mobile](https://github.com/Enric-xX/FuzzingLocalBot/blob/main/mobile/MOBILEREADME.md)

---

## License

GNU General Public License v3.0 - See [LICENSE](https://github.com/Enric-xX/FuzzingLocalBot/blob/main/LICENSE)

---

## Credits

### Wordlists

The wordlists in this project come from the following open source repositories, to see that vsit the [CREDITS.md](https://github.com/Enric-xX/FuzzingLocalBot/edit/main/CREDITS.md)

---

## Author

### Enric-xX

GitHub: [@Enric-xX](https://github.com/Enric-xX)



