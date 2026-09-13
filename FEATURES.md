# FuzzingLocalBot - Features

Complete feature list for FuzzingLocalBot v3.4.

---

## Core Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Multi-threaded scanning** | Configurable threads (1-200) for parallel fuzzing |
| 2 | **16+ curated dictionaries** | General, APIs, WordPress, Jira, LFI, IIS, and more |
| 3 | **42k lines full scan dictionary** | Massive built-in wordlist for deep scans |
| 4 | **Interactive wordlist selector** | Browse and choose dictionaries by number |
| 5 | **Real-time progress** | Live progress bar with speed and ETA |
| 6 | **Ctrl+C graceful shutdown** | Saves report automatically on interrupt |
| 7 | **Output in multiple formats** | TXT, JSON, Markdown, HTML, CSV |
| 8 | **Professional reports** | Severity classification with CWE mapping |

---

## Scan Modes

| Mode | Threads | User-Agent | Delay | Use Case |
|------|---------|------------|-------|----------|
| **Slow** | 10 | Rotating (40+) | 1-3s | Stealth, evading WAF/IDS |
| **Normal** | 50 | Rotating (40+) | 0.5-1s | Balanced pentesting |
| **Fast** | 100 | Rotating (40+) | None | CTFs, authorized speed tests |
| **Custom** | Any | Rotating (40+) | Configurable | Full control |

---

## User-Agent Pool (40+ agents)

See [USER_AGENTS.md](USER_AGENTS.md) for the full list.

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

---

## Technologies Detected (200+)

### CMS
| Technology | Detection |
|------------|-----------|
| WordPress | wp-content, wp-json, wp-includes |
| Joomla | joomla, com_content |
| Drupal | drupal, sites/default |
| Moodle | moodle, course/view.php |
| Magento | magento, Mage.Cookies |
| PrestaShop | prestashop |
| Shopify | shopify, myshopify |
| WooCommerce | woocommerce |
| Ghost | ghost |
| TYPO3 | typo3 |
| Craft CMS | craftcms |
| Umbraco | umbraco |
| Sitecore | sitecore |
| Squarespace | squarespace |
| Wix | wix |
| Webflow | webflow |
| Bitrix | bitrix |
| OpenCart | opencart |
| MediaWiki | mediawiki |
| phpBB | phpbb |
| vBulletin | vbulletin |
| XenForo | xenforo |
| Discourse | discourse |

### Frameworks
| Technology | Detection |
|------------|-----------|
| Laravel | laravel, XSRF-TOKEN |
| Django | django, csrftoken |
| Ruby on Rails | rails, _session_id |
| ASP.NET | ASP.NET, __RequestVerificationToken |
| Spring Boot | spring, actuator |
| Flask | flask, werkzeug |
| Express.js | express, x-powered-by |
| Next.js | next, __next |
| Nuxt.js | nuxt, __nuxt |
| Gatsby | gatsby |
| Angular | angular, ng-version |
| React | react, react-root |
| Vue.js | vue, data-v- |
| Svelte | svelte |
| FastAPI | fastapi |
| Phoenix | phoenix |
| Symfony | symfony |
| CakePHP | cakephp |
| CodeIgniter | codeigniter |
| NestJS | nestjs |
| Strapi | strapi |
| Directus | directus |

### Servers
| Technology | Detection |
|------------|-----------|
| Apache | Server: Apache |
| Nginx | Server: nginx |
| IIS | Microsoft-IIS |
| Tomcat | Apache Tomcat, JSESSIONID |
| Caddy | Server: Caddy |
| LiteSpeed | Server: LiteSpeed |
| OpenResty | Server: OpenResty |
| Jetty | jetty |
| Gunicorn | gunicorn |
| uWSGI | uwsgi |
| Traefik | traefik |
| HAProxy | haproxy |
| Envoy | envoy |
| Istio | istio |

### Cloud / CDN
| Technology | Detection |
|------------|-----------|
| Cloudflare | cf-ray, __cfduid |
| AWS | x-amz-request-id, CloudFront |
| Google Cloud | appspot.com, firebase |
| Azure | azurewebsites.net |
| DigitalOcean | digitalocean |
| Heroku | herokuapp |
| Vercel | vercel, x-vercel-id |
| Netlify | netlify, x-nf-request-id |
| Fastly | fastly, x-served-by |
| Akamai | akamai, X-Akamai |
| BunnyCDN | bunnycdn |
| Fly.io | fly.io |
| Render | render.com |
| Railway | railway |

### DevOps / Tools
| Technology | Detection |
|------------|-----------|
| Jenkins | jenkins, Jenkins-Crumb |
| GitLab | gitlab, _gitlab_session |
| GitHub | github |
| Kubernetes | kubernetes, k8s |
| Docker | docker, Docker/ |
| Grafana | grafana |
| Prometheus | prometheus |
| Kibana | kibana |
| Elasticsearch | elasticsearch |
| MongoDB | mongodb |
| Redis | redis |
| PostgreSQL | postgresql |
| MySQL | mysql |
| PHPMyAdmin | phpmyadmin |
| Adminer | adminer |
| RabbitMQ | rabbitmq |
| Kafka | kafka |
| Vault | vault |
| Consul | consul |
| Terraform | terraform |
| Ansible | ansible |
| ArgoCD | argocd |

### JavaScript Libraries
| Technology | Detection |
|------------|-----------|
| jQuery | jquery |
| Bootstrap | bootstrap |
| Tailwind CSS | tailwind |
| Font Awesome | font-awesome |
| Lodash | lodash |
| Moment.js | moment |
| Axios | axios |
| D3.js | d3.js |
| Three.js | three.js |
| Chart.js | chart.js |
| Alpine.js | alpine |
| HTMX | htmx |

### Analytics / Marketing
| Technology | Detection |
|------------|-----------|
| Google Analytics | google-analytics, gtag |
| Google Tag Manager | googletagmanager, GTM- |
| Facebook Pixel | facebook.net, fbq( |
| Hotjar | hotjar |
| Mixpanel | mixpanel |
| Segment | segment |
| Matomo | matomo |
| Plausible | plausible |
| Fathom | fathom |

### Payment / E-commerce
| Technology | Detection |
|------------|-----------|
| Stripe | stripe |
| PayPal | paypal |
| Square | square |
| Braintree | braintree |
| Adyen | adyen |
| Mollie | mollie |
| Klarna | klarna |

### Security
| Technology | Detection |
|------------|-----------|
| reCAPTCHA | recaptcha, g-recaptcha |
| hCaptcha | hcaptcha, h-captcha |
| Cloudflare Turnstile | turnstile, cf-turnstile |
| Auth0 | auth0 |
| Okta | okta |
| Keycloak | keycloak |
| Firebase Auth | firebase |
| Supabase | supabase |
| Clerk | clerk |
| NextAuth | next-auth |

---

## WAF/IDS Detected (25+)

| WAF | Detection |
|-----|-----------|
| Cloudflare | cf-ray, __cf_bm |
| AWS WAF | x-amzn-waf |
| ModSecurity | mod_security |
| F5 BIG-IP | BigIP, F5 |
| Imperva | imperva, visid_incap_ |
| Akamai | akamai, X-Akamai |
| Sucuri | sucuri, cloudproxy |
| Fortinet | fortinet, FortiGate |
| Palo Alto | PAN-OS |
| Barracuda | barracuda |
| Citrix | citrix, Netscaler |
| Wordfence | wordfence, wfvt_ |
| Wallarm | wallarm |
| Cloudbric | cloudbric |
| AWS Shield | x-amz-shield |
| Google Cloud Armor | GCP Armor |
| Azure WAF | azure-waf |
| Radware | radware |
| F5 ASM | Application Security Manager |
| Distil | distil |
| Reblaze | reblaze |
| Bitninja | bitninja |
| StackPath | stackpath |
| Fastly | fastly |
| Section.io | section.io |

---

## Risk Patterns Detected (60+)

### Critical (Score 50)
| Pattern | CWE | Description |
|---------|-----|-------------|
| Directory listing | CWE-548 | Index of /, Parent Directory |
| phpinfo | CWE-200 | PHP Version, PHP Credits |
| SQL dump | CWE-200 | INSERT INTO, CREATE TABLE |
| Git exposed | CWE-527 | .git/HEAD, refs/heads |
| AWS credentials | CWE-798 | AKIA, ASIA |
| .env file | CWE-200 | DB_PASSWORD=, SECRET_KEY= |
| Private key | CWE-798 | BEGIN RSA PRIVATE KEY |

### High (Score 30-40)
| Pattern | CWE | Description |
|---------|-----|-------------|
| API key | CWE-798 | api_key, secret_key |
| Docker API | CWE-200 | /containers/json |
| Kubernetes API | CWE-200 | /api/v1/pods |
| Sensitive files | CWE-200 | id_rsa, shadow, passwd |
| Debug mode | CWE-489 | DEBUG=True, APP_DEBUG |
| Backup file | CWE-530 | .bak, .backup, .old |
| Config file | CWE-200 | .env, wp-config, config.php |
| Laravel debug | CWE-489 | Whoops, laravel-debugbar |
| CORS misconfig | CWE-942 | Access-Control-Allow-Origin: * |

### Medium (Score 15-25)
| Pattern | CWE | Description |
|---------|-----|-------------|
| Error disclosure | CWE-209 | Fatal error, Stack trace |
| PHP errors | CWE-209 | PHP Parse error, PHP Warning |
| SQL errors | CWE-209 | SQL syntax, mysql_fetch |
| Exposed panels | CWE-200 | admin panel, cpanel |
| Outdated software | CWE-1104 | Apache/2.2, PHP/5. |
| Actuator | CWE-200 | actuator, heapdump |
| Swagger | CWE-200 | swagger, openapi |
| Jenkins script | CWE-200 | /script, Jenkins-Crumb |
| WordPress backup | CWE-530 | wp-content/backups |
| Firebase | CWE-200 | firebaseio.com |
| S3 bucket | CWE-200 | s3.amazonaws.com |
| JWT token | CWE-200 | eyJ, JWT |
| GraphQL | CWE-200 | graphql, graphiql |

### Low (Score 5)
| Pattern | CWE | Description |
|---------|-----|-------------|
| Login form | N/A | password, login, username |

---

## Security Headers Checked

| Header | Description |
|--------|-------------|
| Strict-Transport-Security | HSTS |
| Content-Security-Policy | CSP |
| X-Frame-Options | Clickjacking protection |
| X-Content-Type-Options | MIME sniffing protection |
| Referrer-Policy | Referrer policy |
| Permissions-Policy | Permissions policy |
| Cross-Origin-Opener-Policy | COOP |
| Cross-Origin-Resource-Policy | CORP |
| Cross-Origin-Embedder-Policy | COEP |

---

## Output Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| Text | .txt | Raw scan results |
| JSON | .json | Structured data |
| Markdown | .md | Human-readable report |
| HTML | .html | Professional styled report |
| CSV | .csv | Spreadsheet-compatible |

---

## Scan Modes Comparison

| Mode | Threads | User-Agent | Delay | Use Case |
|------|---------|------------|-------|----------|
| Slow | 10 | Rotating | 1-3s | Stealth, evading WAF/IDS |
| Normal | 50 | Rotating | 0.5-1s | Balanced pentesting |
| Fast | 100 | Rotating | None | CTFs, speed tests |
| Custom | 1-200 | Rotating | Configurable | Full control |

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✅ Full | Native support |
| Windows | ✅ Full | With AutoHotkey GUI |
| macOS | ✅ Full | Native support |
| Termux (Android) | ✅ Full | Mobile version available |
| Docker | ⚠️ Partial | Community support |

---

## CLI vs GUI

| Feature | CLI | GUI (Windows) |
|---------|-----|---------------|
| Fuzzing | ✅ | ✅ |
| Wordlist selection | ✅ | ✅ |
| Scan modes | ✅ | ✅ |
| Stealth mode | ✅ | ✅ |
| Real-time progress | ✅ | ✅ |
| Report generation | ✅ | ✅ |
| Ctrl+C handling | ✅ | ✅ |

---

## Performance

| Metric | Value |
|--------|-------|
| Max threads | 200 |
| Requests per second | Up to 500+ |
| Memory usage | < 100 MB |
| CPU usage | Low |
| Startup time | < 1s |

---

## Security Features

| Feature | Description |
|---------|-------------|
| TLS verification bypass | Optional (for testing) |
| Stealth mode | Random delays |
| User-Agent rotation | 40+ agents |
| Realistic headers | Browser-like behavior |
| CWE mapping | Vulnerability classification |
| Severity scoring | Risk-based classification |

---

## Limitations

| Limitation | Notes |
|------------|-------|
| No POST fuzzing | Only GET requests |
| No authentication | No login support |
| No proxy rotation | Manual VPN recommended |
| No JS rendering | Static HTML only |
| No WebSocket | HTTP/HTTPS only |

---

## Roadmap (v3.5+)

| Feature | Status |
|---------|--------|
| POST/PUT/DELETE fuzzing | Planned |
| Authentication support | Planned |
| Proxy rotation | Planned |
| JS rendering | Planned |
| WebSocket support | Planned |
| GraphQL fuzzing | Planned |
| API fuzzing | Planned |
| Machine learning analysis | Planned |

---

*Part of FuzzingLocalBot v3.4 - See main README for full documentation.*
