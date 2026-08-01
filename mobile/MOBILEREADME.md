# FuzzingLocalBot Mobile v1.0

Lightweight web fuzzer for Android devices via Termux.

![Termux](https://img.shields.io/badge/Termux-green)
![Git](https://img.shields.io/badge/Git-orange)
![Python](https://img.shields.io/badge/Python-3.6+-yellow)
![License](https://img.shields.io/badge/License-GPL%20v3-red)

---

<img width="1200" height="400" alt="image" src="https://github.com/user-attachments/assets/13f34eb4-c550-487c-8695-755b497fa6c1" />

---

## What is FuzzingLocalBot Mobile?

A lightweight version of [FuzzingLocalBot](https://github.com/Enric-xX/FuzzingLocalBot) optimized for Android devices. Scan websites directly from your phone.

---

## Requirements

- [Termux]([https://f-droid.org/en/packages/com.termux/](https://play.google.com/store/apps/details?id=com.termux&hl=es_419)) (Android)
- Python 3.6+

---

## Installation

```bash
pkg update && pkg upgrade
```
```
pkg install python git
```
```
git clone https://github.com/Enric-xX/FuzzingLocalBot.git
```
```
cd FuzzingLocalBot/mobile
```
```
pip install requests
```
---

# Use

## From Termux terminal

```
cd FuzzingLocalBot/mobile
```
```
python mobilefuzzingbot.py
```

### The tool will ask you:

- Target domain (e.g. https://example.com)

- Wordlist (5 curated lists)

- Scan speed (Slow/Normal/Fast)

---

## Wordlists

| # | File | Lines | Use Case |
|---|------|-------|----------|
| 1 | api.txt| 101 | API endpoints |
| 2 | common.txt | 202 | General directories |
| 3 | wordpress.txt | 88 | WordPress paths |
| 4 | extensions.txt | 102 | File extensions |
| 5 | backup.txt | 90 | Backup files |

---

## Scan Modes

| Mode | Threads | Use Case | 
|------|---------|----------|
| Slow | 3 | Battery saving, stealth |
| Normal | 5 | Balanced|
| Fast | 10 | Maximum speed |

---

## Differences from Desktop Version

| Feature | Desktop | Mobile |
|---------|---------|--------|
| Max threads | 200 | 10 |
| Wordlists | 15 | 5 |
| Reports | MD + HTML | TXT only |
| GUI | Autohotkey ( Windows only ) | Terminal only |

---

## Security Warning

### USE A VPN BEFORE RUNNING THIS TOOL.

This tool is exclusively for authorized pentesting.

---

## License

GNU General Public License v3.0

--- 

## Author

Enric-xX
GitHub: [@Enric-xX](https://github.com/Enric-xX/)

