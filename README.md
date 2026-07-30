# FuzzingLocalBot v2.0

Automation of directory and extension fuzzing, featuring intelligent analysis and professional reporting for authorized penetration testing.

![Linux](https://img.shields.io/badge/Linux-orange)
![Windows](https://img.shields.io/badge/Windows-blue)
![Python](https://img.shields.io/badge/Python-3.6+-yellow)
![License](https://img.shields.io/badge/License-GPL%20v3-red)
![AutoHotKey](https://img.shields.io/badge/AutoHotkey-1.1+-green)

---

<img width="1200" height="400" alt="image" src="https://github.com/user-attachments/assets/9421c603-84a2-4985-9022-0c5dff58f78c" />


---

## Dependencies

Before installing, you need to have installed:

| Program | Download | Is it required?|
|----------|----------|---------------|
| **Python 3.6+** | [python.org/downloads](https://www.python.org/downloads/) | ✅ Yes |
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
python fuzzingbot.py https://ejemplo.com extensiones.txt resultados.txt
```

---

## What does it do?

- Fuzzing → Scans 42,000 paths against the target domain using 50 parallel threads

- Analysis → Detects technologies (WordPress, Apache, PHP...), directory listing, exposed backups, configurations, exposed Git, and more

- Reporting → Generates a professional Markdown and HTML report with findings classified by severity

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

## Estructura

```
FuzzingLocalBot/
├── LICENSE                 GPL v3 License
├── README.md               This file
├── config.ini              Configuration file
├── requirements.txt        Python dependencies
├── extensiones.txt         42k paths dictionary
├── fuzzingbot.py           Main fuzzing engine
├── analyzer.py             HTTP response analyzer
├── reporter.py             Report generator
├── bot.ahk                 Graphical interface (AutoHotkey)
└── output/                 Results folder
    ├── scan_*.txt          Raw results
    ├── scan_*.json         JSON results
    ├── report_*.md         Markdown report
    └── report_*.html       HTML report
```
---

## Security Warning

### USE A VPN BEFORE RUNNING THIS TOOL.

This tool is exclusively for authorized pentesting. Do not use it against systems without the explicit permission of their owner.

---

## License

GNU General Public License v3.0 - See [LICENSE](https://github.com/Enric-xX/FuzzingLocalBot/blob/main/LICENSE)

---

## Author

### Enric-xX

GitHub: [@Enric-xX](https://github.com/Enric-xX)



