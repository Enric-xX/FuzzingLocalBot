## User-Agent Pool (40 agents)

| # | Browser | Version | OS |
|---|---------|---------|-----|
| 1 | Chrome | 131 | Windows 10/11 |
| 2 | Chrome | 130 | Windows 10/11 |
| 3 | Chrome | 129 | Windows 10/11 |
| 4 | Chrome | 128 | Windows 10/11 |
| 5 | Chrome | 131 | macOS 10.15 |
| 6 | Chrome | 130 | macOS 14.5 |
| 7 | Chrome | 129 | macOS 13.6 |
| 8 | Chrome | 131 | Linux x86_64 |
| 9 | Chrome | 130 | Ubuntu Linux |
| 10 | Chrome | 129 | Fedora Linux |
| 11 | Firefox | 133 | Windows 10/11 |
| 12 | Firefox | 132 | Windows 10/11 |
| 13 | Firefox | 131 | Windows 10/11 |
| 14 | Firefox | 133 | macOS 10.15 |
| 15 | Firefox | 132 | macOS 14.5 |
| 16 | Firefox | 133 | Linux x86_64 |
| 17 | Firefox | 132 | Ubuntu Linux |
| 18 | Safari | 18.1 | macOS 10.15 |
| 19 | Safari | 17.6 | macOS 10.15 |
| 20 | Safari | 18.0 | macOS 14.5 |
| 21 | Safari | 18.1 | iOS 18.1 (iPhone) |
| 22 | Safari | 17.6 | iOS 17.6 (iPhone) |
| 23 | Safari | 18.1 | iPadOS 18.1 (iPad) |
| 24 | Chrome | 131 | Android 14 (Samsung) |
| 25 | Chrome | 130 | Android 14 (Pixel 8 Pro) |
| 26 | Chrome | 129 | Android 13 (Samsung A53) |
| 27 | Chrome | 131 | Android 14 (OnePlus 11) |
| 28 | Edge | 131 | Windows 10/11 |
| 29 | Edge | 130 | Windows 10/11 |
| 30 | Edge | 129 | Windows 10/11 |
| 31 | Opera | 115 | Windows 10/11 |
| 32 | Opera | 114 | Windows 10/11 |
| 33 | Brave | 131 | Windows 10/11 |
| 34 | Brave | 130 | macOS 10.15 |
| 35 | Vivaldi | 7.0 | Windows 10/11 |
| 36 | Samsung Internet | 27.0 | Android 14 (Samsung) |
| 37 | PlayStation Browser | 2.26 | PlayStation 5 |
| 38 | Xbox Browser | - | Xbox Series X |
| 39 | Googlebot | 2.1 | Bot |
| 40 | Bingbot | 2.0 | Bot |
| 41 | Chrome | 109 | Windows 7/8.1 (Legacy) |
| 42 | Firefox | 109 | Windows 7/8.1 (Legacy) |

All 40+ User-Agents rotate randomly on each request. Combined with realistic headers 
(Accept, Accept-Language, Sec-Fetch-*, Upgrade-Insecure-Requests), FuzzingLocalBot 
mimics real browser behavior to evade basic fingerprinting and WAF detection.

### Categories

| Category | Count | Examples |
|----------|-------|----------|
| Chrome | 10 | Windows, macOS, Linux, Android |
| Firefox | 6 | Windows, macOS, Linux |
| Safari | 6 | macOS, iOS, iPadOS |
| Edge | 3 | Windows |
| Opera | 2 | Windows |
| Brave | 2 | Windows, macOS |
| Vivaldi | 1 | Windows |
| Samsung Internet | 1 | Android |
| Consoles | 2 | PS5, Xbox Series X |
| Bots | 2 | Googlebot, Bingbot |
| Legacy | 2 | Chrome 109, Firefox 109 |

### Why rotate User-Agents?

- **Evade fingerprinting** → Each request looks like a different real browser
- **Bypass basic WAF rules** → Some WAFs block repeated User-Agents
- **Mimic legitimate traffic** → Harder to distinguish from real users
- **Reduce detection** → Less likely to be rate-limited or blocked

### Realistic headers included

Each request also sends:

- `Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8`
- `Accept-Language: en-US,en;q=0.5`
- `Accept-Encoding: gzip, deflate`
- `Connection: keep-alive`
- `Upgrade-Insecure-Requests: 1`
- `Sec-Fetch-Dest: document`
- `Sec-Fetch-Mode: navigate`
- `Sec-Fetch-Site: none`
- `Sec-Fetch-User: ?1`
- `Cache-Control: max-age=0`

This combination makes each request look like a real browser navigation, not a bot.

---

*Part of FuzzingLocalBot v3.4 - See main README for full documentation.*
