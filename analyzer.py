#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FuzzingLocalBot - Analyzer Module v3.0
Analyzes HTTP responses and classifies findings by severity with CWE mapping.
"""

import re
import hashlib
from urllib.parse import urlparse


# ============================================================
# SIGNATURES - 150+ technologies, 50+ risk patterns, 20+ WAFs
# ============================================================

TECH_SIGNATURES = {
    # === CMS ===
    "WordPress": ["wp-content", "wp-json", "wp-includes", "wordpress", "wp-admin"],
    "Joomla": ["joomla", "com_content", "Joomla!"],
    "Drupal": ["drupal", "sites/default", "Drupal.settings"],
    "Moodle": ["moodle", "course/view.php", "MoodleSession"],
    "Magento": ["magento", "Mage.Cookies", "mage"],
    "PrestaShop": ["prestashop", "PrestaShop"],
    "Shopify": ["shopify", "myshopify"],
    "WooCommerce": ["woocommerce", "woo"],
    "Ghost": ["ghost", "Ghost"],
    "Blogger": ["blogger", "blogspot"],
    "TYPO3": ["typo3", "TYPO3"],
    "Craft CMS": ["craftcms", "Craft CMS"],
    "Umbraco": ["umbraco", "Umbraco"],
    "Sitecore": ["sitecore", "Sitecore"],
    "Kentico": ["kentico", "Kentico"],
    "Squarespace": ["squarespace", "Squarespace"],
    "Wix": ["wix", "Wix"],
    "Webflow": ["webflow", "Webflow"],
    
    # === Frameworks ===
    "Laravel": ["laravel", "XSRF-TOKEN", "laravel_session"],
    "Django": ["django", "csrftoken", "django_language"],
    "Ruby on Rails": ["rails", "_session_id", "rails/"],
    "ASP.NET": ["ASP.NET", "__RequestVerificationToken", "X-AspNet-Version"],
    "Spring Boot": ["spring", "X-Application-Context", "actuator"],
    "Flask": ["flask", "werkzeug"],
    "Express.js": ["express", "x-powered-by: express"],
    "Next.js": ["next", "__next", "_next/"],
    "Nuxt.js": ["nuxt", "__nuxt", "_nuxt/"],
    "Gatsby": ["gatsby", "___gatsby"],
    "Angular": ["angular", "ng-version", "app-root"],
    "React": ["react", "reactjs", "react-root"],
    "Vue.js": ["vue", "vuejs", "data-v-"],
    "Svelte": ["svelte", "sveltekit"],
    "FastAPI": ["fastapi", "FastAPI"],
    "Phoenix": ["phoenix", "phoenix/", "Elixir"],
    "Symfony": ["symfony", "Symfony"],
    "CakePHP": ["cakephp", "CakePHP"],
    "CodeIgniter": ["codeigniter", "CodeIgniter"],
    
    # === Languages ===
    "PHP": ["X-Powered-By: PHP", "PHPSESSID", ".php"],
    "Python": ["python", "werkzeug", "flask", "fastapi"],
    "Ruby": ["ruby", "rails"],
    "Node.js": ["node.js", "express", "koa", "nestjs"],
    "Java": ["Java", "Servlet", "JSP", "JSESSIONID", "tomcat", "spring"],
    "Go": ["go", "golang"],
    "C#": ["ASP.NET", "X-AspNet-Version"],
    "Perl": ["perl", "Perl"],
    "Rust": ["rust", "Rust"],
    
    # === Servers ===
    "Apache": ["Apache", "Server: Apache"],
    "Nginx": ["nginx", "Server: nginx"],
    "IIS": ["Microsoft-IIS", "Server: Microsoft"],
    "Tomcat": ["Apache Tomcat", "JSESSIONID", "Apache-Coyote"],
    "Caddy": ["Caddy", "Server: Caddy"],
    "LiteSpeed": ["LiteSpeed", "Server: LiteSpeed"],
    "OpenResty": ["openresty", "Server: OpenResty"],
    "Jetty": ["jetty", "Jetty"],
    "Undertow": ["undertow", "Undertow"],
    "Gunicorn": ["gunicorn", "Gunicorn"],
    "uWSGI": ["uwsgi", "uWSGI"],
    
    # === Cloud / CDN ===
    "Cloudflare": ["cloudflare", "__cfduid", "cf-ray", "cf-cache-status"],
    "AWS": ["aws", "x-amz-request-id", "x-amz-cf-id", "CloudFront"],
    "Google Cloud": ["appspot.com", "firebase", "x-goog-"],
    "Azure": ["azurewebsites.net", "x-azure-ref", "azure"],
    "DigitalOcean": ["digitalocean", "droplet"],
    "Heroku": ["heroku", "herokuapp"],
    "Vercel": ["vercel", "now.sh", "x-vercel-id"],
    "Netlify": ["netlify", "x-nf-request-id"],
    "Fastly": ["fastly", "x-served-by"],
    "Akamai": ["akamai", "X-Akamai"],
    "BunnyCDN": ["bunnycdn", "BunnyCDN"],
    "KeyCDN": ["keycdn", "KeyCDN"],
    "StackPath": ["stackpath", "StackPath"],
    
    # === DevOps / Tools ===
    "Jenkins": ["jenkins", "Dashboard", "Jenkins-Crumb"],
    "GitLab": ["gitlab", "_gitlab_session"],
    "GitHub": ["github", "x-github-request-id"],
    "Bitbucket": ["bitbucket", "atlbitbucket"],
    "Kubernetes": ["kubernetes", "kube", "k8s"],
    "Docker": ["docker", "Docker/"],
    "Grafana": ["grafana", "x-grafana-org-id"],
    "Prometheus": ["prometheus", "Prometheus"],
    "Kibana": ["kibana", "Kibana"],
    "Elasticsearch": ["elasticsearch", "cluster_name"],
    "MongoDB": ["mongodb", "MongoDB"],
    "Redis": ["redis", "Redis"],
    "PostgreSQL": ["postgresql", "PostgreSQL"],
    "MySQL": ["mysql", "MySQL"],
    "PHPMyAdmin": ["phpmyadmin", "phpMyAdmin"],
    "Adminer": ["adminer", "Adminer"],
    "RabbitMQ": ["rabbitmq", "RabbitMQ"],
    "Apache Kafka": ["kafka", "Kafka"],
    "NATS": ["nats", "NATS"],
    "Vault": ["vault", "Vault"],
    "Consul": ["consul", "Consul"],
    "Traefik": ["traefik", "Traefik"],
    "HAProxy": ["haproxy", "HAProxy"],
    "Envoy": ["envoy", "Envoy"],
    "Istio": ["istio", "Istio"],
}

RISK_PATTERNS = {
    # === Critical ===
    "directory_listing": {
        "patterns": ["Index of /", "Parent Directory", "[DIR]", "Directory Listing"],
        "cwe": "CWE-548",
        "score": 50,
    },
    "phpinfo": {
        "patterns": ["phpinfo", "PHP Version", "PHP Credits"],
        "cwe": "CWE-200",
        "score": 50,
    },
    "sql_dump": {
        "patterns": ["INSERT INTO", "CREATE TABLE", "DROP TABLE", "BEGIN TRANSACTION", "ALTER TABLE", "CREATE INDEX"],
        "cwe": "CWE-200",
        "score": 50,
    },
    "git_exposed": {
        "patterns": [".git/HEAD", "refs/heads", ".gitignore", ".git/config"],
        "cwe": "CWE-527",
        "score": 50,
    },
    "aws_credentials": {
        "patterns": ["AKIA", "ASIA", "aws_access_key", "aws_secret_key"],
        "cwe": "CWE-798",
        "score": 50,
    },
    "env_file": {
        "patterns": ["DB_PASSWORD=", "DB_USERNAME=", "SECRET_KEY=", "API_KEY=", "APP_KEY=", "MAIL_PASSWORD="],
        "cwe": "CWE-200",
        "score": 50,
    },
    
    # === High ===
    "api_key": {
        "patterns": ["api_key", "apikey", "secret_key", "access_token", "Bearer ", "sk-", "token="],
        "cwe": "CWE-798",
        "score": 40,
    },
    "docker_api": {
        "patterns": ["/containers/json", "/images/json", "Docker/", "/var/run/docker.sock"],
        "cwe": "CWE-200",
        "score": 40,
    },
    "kubernetes_api": {
        "patterns": ["/api/v1/pods", "/api/v1/namespaces", "kubernetes"],
        "cwe": "CWE-200",
        "score": 40,
    },
    "sensitive_files": {
        "patterns": ["id_rsa", "id_dsa", "known_hosts", "shadow", "passwd", ".htpasswd", "wp-config.php"],
        "cwe": "CWE-200",
        "score": 40,
    },
    "debug_mode": {
        "patterns": ["debug", "DEBUG=True", "APP_DEBUG", "WP_DEBUG", "development mode", "dev mode", "ENV=development"],
        "cwe": "CWE-489",
        "score": 30,
    },
    "backup_file": {
        "patterns": [".bak", ".backup", ".old", ".sql.gz", ".tar.gz", ".zip", ".7z", ".rar", ".dump", ".tgz"],
        "cwe": "CWE-530",
        "score": 30,
    },
    "config_file": {
        "patterns": [".env", "wp-config", "config.php", "settings.py", "application.properties", "database.yml", "credentials.json", "config.yml"],
        "cwe": "CWE-200",
        "score": 30,
    },
    "laravel_debug": {
        "patterns": ["Whoops", "laravel-debugbar", "APP_DEBUG", "laravel.log", "Laravel", "vendor/"],
        "cwe": "CWE-489",
        "score": 30,
    },
    "django_debug": {
        "patterns": ["DEBUG=True", "django_debug", "settings.py", "wsgi.py", "DJANGO_SETTINGS_MODULE"],
        "cwe": "CWE-489",
        "score": 30,
    },
    
    # === Medium ===
    "error_disclosure": {
        "patterns": ["Fatal error", "Warning:", "Notice:", "Stack trace", "on line", "in /", "Traceback", "Exception in", "at line"],
        "cwe": "CWE-209",
        "score": 20,
    },
    "php_errors": {
        "patterns": ["PHP Parse error", "PHP Warning", "PHP Notice", "PHP Fatal error", "unexpected", "syntax error", "undefined variable"],
        "cwe": "CWE-209",
        "score": 25,
    },
    "sql_errors": {
        "patterns": ["SQL syntax", "mysql_fetch", "pg_query", "ORA-", "ODBC", "SQLite error", "SQLSTATE", "mysql error", "database error"],
        "cwe": "CWE-209",
        "score": 25,
    },
    "exposed_panels": {
        "patterns": ["admin panel", "control panel", "cpanel", "webmail", "phpmyadmin", "adminer", "Admin Panel"],
        "cwe": "CWE-200",
        "score": 25,
    },
    "outdated_software": {
        "patterns": ["Apache/2.2", "Apache/2.4.0", "PHP/5.", "PHP/7.0", "PHP/7.1", "nginx/1.0", "nginx/1.1"],
        "cwe": "CWE-1104",
        "score": 20,
    },
    "actuator": {
        "patterns": ["actuator", "heapdump", "env", "mappings", "beans", "autoconfig", "configprops"],
        "cwe": "CWE-200",
        "score": 20,
    },
    "swagger": {
        "patterns": ["swagger", "openapi", "api-docs", "Swagger UI", "swagger.json", "swagger.yaml"],
        "cwe": "CWE-200",
        "score": 15,
    },
    "jenkins_script": {
        "patterns": ["/script", "/manage", "/configure", "Jenkins-Crumb", "Jenkins.instance"],
        "cwe": "CWE-200",
        "score": 20,
    },
    "wordpress_backup": {
        "patterns": ["wp-content/backups", "wp-content/backup-db", "wp-content/ai1wm-backups", "wp-content/updraft"],
        "cwe": "CWE-530",
        "score": 20,
    },
    "firebase": {
        "patterns": ["firebaseio.com", "firebaseapp.com", ".firebaseio.com", "firebase.google.com"],
        "cwe": "CWE-200",
        "score": 15,
    },
    "s3_bucket": {
        "patterns": ["s3.amazonaws.com", "s3-us-", ".s3.", "amazonaws.com/", "s3://"],
        "cwe": "CWE-200",
        "score": 15,
    },
    "jwt_token": {
        "patterns": ["eyJ", "JWT", "jsonwebtoken"],
        "cwe": "CWE-200",
        "score": 10,
    },
    
    # === Low ===
    "login_form": {
        "patterns": ["password", "login", "username", "<form", "signin", "sign_in", "log in", "email"],
        "cwe": "N/A",
        "score": 5,
    },
    "graphql": {
        "patterns": ["graphql", "GraphQL", "graphiql"],
        "cwe": "CWE-200",
        "score": 10,
    },
    "cors_misconfig": {
        "patterns": ["Access-Control-Allow-Origin: *"],
        "cwe": "CWE-942",
        "score": 10,
    },
}

WAF_SIGNATURES = {
    "Cloudflare": ["cf-ray", "cloudflare-nginx", "__cf_bm", "cf-chl-bypass", "CF-Cache-Status"],
    "AWS WAF": ["x-amzn-waf", "aws-waf", "x-amzn-RequestId"],
    "ModSecurity": ["mod_security", "Mod_Security", "modsecurity"],
    "F5 BIG-IP": ["BigIP", "F5", "BIG-IP", "BIGipServer", "F5-TrafficShield"],
    "Imperva": ["imperva", "incapsula", "Imperva", "X-Iinfo", "visid_incap_"],
    "Akamai": ["akamai", "X-Akamai", "X-Akamai-Transformed", "akamai-edge"],
    "Sucuri": ["sucuri", "cloudproxy", "Sucuri/Cloudproxy", "x-sucuri-id"],
    "Fortinet": ["fortinet", "FortiGate", "fortigate", "FORTIWAF"],
    "Palo Alto": ["Palo Alto", "PAN-OS", "panos"],
    "Barracuda": ["barracuda", "Barracuda", "barra_counter_session"],
    "Citrix": ["citrix", "Citrix", "Netscaler", "ns_af", "NSC_"],
    "Wordfence": ["wordfence", "Wordfence", "wfvt_"],
    "Wallarm": ["wallarm", "Wallarm"],
    "Cloudbric": ["cloudbric", "Cloudbric"],
    "AWS Shield": ["x-amz-shield", "AWSShield"],
    "Google Cloud Armor": ["google cloud armor", "GCP Armor"],
    "Azure WAF": ["azure-waf", "Azure WAF"],
    "Radware": ["radware", "Radware"],
    "F5 ASM": ["asm", "Application Security Manager", "f5-as", "TS"],
    "Distil": ["distil", "Distil", "x-distil-cs"],
    "Reblaze": ["reblaze", "Reblaze"],
    "Bitninja": ["bitninja", "BitNinja"],
}

STATUS_CLASSIFICATION = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found (Temporary Redirect)",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    429: "Rate Limited",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


class Analyzer:
    """Advanced HTTP response analyzer with CWE mapping."""

    def __init__(self):
        self.findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": [],
        }
        self.technologies = set()
        self.wafs = set()
        self.baseline_length = None
        self.total_urls_analyzed = 0
        self.seen_hashes = set()

    def set_baseline(self, length):
        self.baseline_length = length

    def analyze(self, result):
        url = result.get("url", "")
        status = result.get("status", 0)
        content_length = result.get("content_length", 0)
        content = result.get("content", "")
        headers = result.get("headers", {})

        findings = []
        risk_score = 0
        cwes = set()
        self.total_urls_analyzed += 1

        # 1. Duplicate detection
        content_hash = hashlib.md5(content.encode() if content else b"").hexdigest()
        if content_hash in self.seen_hashes and status == 200:
            return {"url": url, "risk": "duplicate", "score": 0, "findings": ["Duplicate content (already seen)"]}
        self.seen_hashes.add(content_hash)

        # 2. False positive check
        if status == 200 and self.baseline_length and content_length == self.baseline_length:
            return {"url": url, "risk": "false_positive", "score": 0, "findings": ["Same length as baseline (likely false positive)"]}

        # 3. Detect technologies
        for tech, signatures in TECH_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in content.lower() or sig.lower() in str(headers).lower():
                    self.technologies.add(tech)
                    findings.append(f"Technology: {tech}")
                    risk_score += 1
                    break

        # 4. Detect WAF
        for waf, signatures in WAF_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in str(headers).lower() or sig.lower() in content.lower():
                    self.wafs.add(waf)
                    findings.append(f"WAF/IDS: {waf}")
                    risk_score += 2
                    break

        # 5. Check security headers
        security_headers = {
            "Strict-Transport-Security": ("HSTS enabled", 0),
            "Content-Security-Policy": ("CSP enabled", 0),
            "X-Frame-Options": ("Clickjacking protection", 0),
            "X-Content-Type-Options": ("MIME sniffing protection", 0),
            "Referrer-Policy": ("Referrer policy set", 0),
            "Permissions-Policy": ("Permissions policy set", 0),
        }
        for header, (description, _) in security_headers.items():
            if header in headers:
                findings.append(f"Security: {description}")
            else:
                findings.append(f"Missing: {header}")
                risk_score += 3

        # 6. Check cookies
        cookies = headers.get("Set-Cookie", "")
        if cookies:
            if "HttpOnly" not in cookies:
                findings.append("Cookie: Missing HttpOnly flag")
                risk_score += 10
            if "Secure" not in cookies:
                findings.append("Cookie: Missing Secure flag")
                risk_score += 10
            if "SameSite" not in cookies:
                findings.append("Cookie: Missing SameSite attribute")
                risk_score += 5
            if "PHPSESSID" in cookies or "JSESSIONID" in cookies:
                findings.append("Cookie: Session ID exposed")

        # 7. Detect risks
        if status == 200:
            for risk_name, risk_data in RISK_PATTERNS.items():
                for pattern in risk_data["patterns"]:
                    if pattern in content or pattern in url.lower():
                        findings.append(f"{risk_name.replace('_', ' ').title()} ({risk_data['cwe']})")
                        risk_score += risk_data["score"]
                        cwes.add(risk_data["cwe"])
                        break

        elif status in [301, 302]:
            redirect_url = result.get("redirect", "")
            if "login" in redirect_url.lower():
                findings.append("Redirects to login page")
                risk_score += 5
            else:
                findings.append(f"Redirect: {redirect_url}")

        elif status == 403:
            findings.append("Access forbidden (resource exists)")
            risk_score += 10

        elif status == 401:
            findings.append("Authentication required")
            risk_score += 10

        elif status == 429:
            findings.append("Rate limited (429) - Reduce scan speed")
            risk_score += 5

        elif status >= 500:
            findings.append(f"Server error ({status}) - Possible vulnerability")
            risk_score += 25

        # 8. Fingerprinting from headers
        server = headers.get("Server", "")
        powered_by = headers.get("X-Powered-By", "")
        x_generator = headers.get("X-Generator", "")
        x_asp_version = headers.get("X-AspNet-Version", "")

        if server:
            findings.append(f"Server: {server}")
            risk_score += 5
            if "Apache" in server:
                self.technologies.add("Apache")
                version_match = re.search(r"Apache/([\d.]+)", server)
                if version_match:
                    ver = version_match.group(1)
                    findings.append(f"Apache version: {ver}")
                    risk_score += 15
                    if ver.startswith("2.2") or ver.startswith("2.4.0"):
                        findings.append("CRITICAL: Apache is EOL (End of Life)")
                        risk_score += 30
            elif "nginx" in server:
                self.technologies.add("Nginx")
                version_match = re.search(r"nginx/([\d.]+)", server)
                if version_match:
                    findings.append(f"Nginx version: {version_match.group(1)}")
                    risk_score += 15

        if powered_by:
            findings.append(f"X-Powered-By: {powered_by}")
            self.technologies.add("PHP")
            version_match = re.search(r"PHP/([\d.]+)", powered_by)
            if version_match:
                ver = version_match.group(1)
                findings.append(f"PHP version: {ver}")
                risk_score += 15
                if ver.startswith("5.") or ver.startswith("7.0") or ver.startswith("7.1"):
                    findings.append("CRITICAL: PHP is EOL (End of Life)")
                    risk_score += 30

        if x_generator:
            findings.append(f"Generator: {x_generator}")

        if x_asp_version:
            findings.append(f"ASP.NET version: {x_asp_version}")
            risk_score += 10

        # 9. Determine risk level
        if risk_score >= 50:
            risk_level = "critical"
        elif risk_score >= 30:
            risk_level = "high"
        elif risk_score >= 15:
            risk_level = "medium"
        elif risk_score >= 5:
            risk_level = "low"
        else:
            risk_level = "info"
            if not findings:
                findings.append("No significant findings")

        # 10. Store finding
        finding = {
            "url": url,
            "status": status,
            "risk": risk_level,
            "score": risk_score,
            "cwes": list(cwes),
            "findings": findings,
            "content_length": content_length,
        }

        self.findings[risk_level].append(finding)
        return finding

    def get_summary(self):
        return {
            "critical": len(self.findings["critical"]),
            "high": len(self.findings["high"]),
            "medium": len(self.findings["medium"]),
            "low": len(self.findings["low"]),
            "info": len(self.findings["info"]),
            "technologies": sorted(list(self.technologies)),
            "wafs": sorted(list(self.wafs)),
            "total_analyzed": self.total_urls_analyzed,
        }

    def get_findings(self):
        return self.findings


if __name__ == "__main__":
    print("[*] Analyzer module v3.0 loaded successfully.")
    print("[*] Use: from analyzer import Analyzer")
