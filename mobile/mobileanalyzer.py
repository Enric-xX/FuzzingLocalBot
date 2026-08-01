#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FuzzingLocalBot - Analyzer Module
Analyzes HTTP responses and classifies findings by severity.
"""

import re


# ============================================================
# SIGNATURES
# ============================================================

TECH_SIGNATURES = {
    # CMS
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
    
    # Frameworks
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
    
    # Languages
    "PHP": ["X-Powered-By: PHP", "PHPSESSID", ".php"],
    "Python": ["python", "werkzeug", "flask"],
    "Ruby": ["ruby", "rails"],
    "Node.js": ["node.js", "express", "koa"],
    "Java": ["Java", "Servlet", "JSP", "JSESSIONID", "tomcat"],
    "Go": ["go", "golang"],
    "C#": ["ASP.NET", "X-AspNet-Version"],
    
    # Servers
    "Apache": ["Apache", "Server: Apache"],
    "Nginx": ["nginx", "Server: nginx"],
    "IIS": ["Microsoft-IIS", "Server: Microsoft"],
    "Tomcat": ["Apache Tomcat", "JSESSIONID", "Apache-Coyote"],
    "Caddy": ["Caddy", "Server: Caddy"],
    "LiteSpeed": ["LiteSpeed", "Server: LiteSpeed"],
    "OpenResty": ["openresty", "Server: OpenResty"],
    
    # Cloud / CDN
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
    
    # DevOps / Monitoring
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
}

RISK_PATTERNS = {
    "directory_listing": ["Index of /", "Parent Directory", "[DIR]", "Directory Listing"],
    "phpinfo": ["phpinfo", "PHP Version", "PHP Credits"],
    "sql_dump": ["INSERT INTO", "CREATE TABLE", "DROP TABLE", "BEGIN TRANSACTION", "ALTER TABLE"],
    "backup_file": [".bak", ".backup", ".old", ".sql.gz", ".tar.gz", ".zip", ".7z", ".rar", ".dump"],
    "config_file": [".env", "wp-config", "config.php", "settings.py", "application.properties", "database.yml", "credentials.json"],
    "login_form": ["password", "login", "username", "<form", "signin", "sign_in"],
    "error_disclosure": ["Fatal error", "Warning:", "Notice:", "Stack trace", "on line", "in /", "Traceback", "Exception in"],
    "git_exposed": [".git/HEAD", "refs/heads", ".gitignore", ".git/config"],
    "api_key": ["api_key", "apikey", "secret_key", "access_token", "Bearer", "Authorization:", "sk-", "AKIA"],
    "debug_mode": ["debug", "DEBUG=True", "APP_DEBUG", "WP_DEBUG", "development mode", "dev mode"],
    "swagger": ["swagger", "openapi", "api-docs", "Swagger UI"],
    "graphql": ["graphql", "GraphQL", "graphiql"],
    "actuator": ["actuator", "heapdump", "env", "mappings", "beans", "autoconfig"],
    "php_errors": ["PHP Parse error", "PHP Warning", "PHP Notice", "PHP Fatal error", "unexpected", "syntax error"],
    "sql_errors": ["SQL syntax", "mysql_fetch", "pg_query", "ORA-", "ODBC", "SQLite error", "SQLSTATE"],
    "cors_misconfig": ["Access-Control-Allow-Origin: *", "Access-Control-Allow-Credentials: true"],
    "clickjacking": ["X-Frame-Options: DENY", "X-Frame-Options: SAMEORIGIN"],
    "hsts_missing": ["Strict-Transport-Security"],
    "csp_missing": ["Content-Security-Policy"],
    "sensitive_files": ["id_rsa", "id_dsa", "known_hosts", "shadow", "passwd", ".htpasswd", ".htaccess", "wp-config.php"],
    "exposed_panels": ["admin panel", "control panel", "cpanel", "webmail", "phpmyadmin", "adminer"],
    "outdated_software": ["Apache/2.2", "Apache/2.4.0", "PHP/5.", "PHP/7.0", "PHP/7.1", "nginx/1.0", "nginx/1.1"],
    "aws_credentials": ["AKIA", "ASIA", "aws_access_key", "aws_secret_key", "amazonaws.com"],
    "jwt_token": ["eyJ", "JWT", "jsonwebtoken"],
    "oauth_config": ["oauth", "openid", "client_secret", "client_id", "redirect_uri"],
    "firebase": ["firebaseio.com", "firebaseapp.com", ".firebaseio.com"],
    "s3_bucket": ["s3.amazonaws.com", "s3-us-", ".s3.", "amazonaws.com/"],
    "docker_api": ["/containers/json", "/images/json", "Docker/", "/var/run/docker.sock"],
    "kubernetes_api": ["/api/v1/pods", "/api/v1/namespaces", "kubernetes"],
    "jenkins_script": ["/script", "/manage", "/configure", "Jenkins-Crumb"],
    "wordpress_backup": ["wp-content/backups", "wp-content/backup-db", "wp-content/ai1wm-backups", "wp-content/updraft"],
    "laravel_debug": ["Whoops", "laravel-debugbar", "APP_DEBUG", "laravel.log"],
    "django_debug": ["DEBUG=True", "django_debug", "settings.py", "wsgi.py"],
    "ruby_debug": ["Rails.root:", "Application Trace", "Framework Trace", "params:", "session:"],
}

# WAF / IDS signatures
WAF_SIGNATURES = {
    "Cloudflare WAF": ["cf-ray", "cloudflare-nginx", "__cf_bm", "cf-chl-bypass"],
    "AWS WAF": ["x-amzn-waf", "aws-waf", "x-amzn-RequestId"],
    "ModSecurity": ["mod_security", "Mod_Security", "modsecurity"],
    "F5 BIG-IP": ["BigIP", "F5", "BIG-IP", "BIGipServer"],
    "Imperva": ["imperva", "incapsula", "Imperva", "X-Iinfo"],
    "Akamai": ["akamai", "X-Akamai", "X-Akamai-Transformed"],
    "Sucuri": ["sucuri", "cloudproxy", "Sucuri/Cloudproxy"],
    "Fortinet": ["fortinet", "FortiGate", "fortigate"],
    "Palo Alto": ["Palo Alto", "PAN-OS", "panos"],
    "Barracuda": ["barracuda", "Barracuda"],
    "Citrix": ["citrix", "Citrix", "Netscaler", "ns_af"],
    "F5 ASM": ["asm", "Application Security Manager", "f5-as"],
    "Wordfence": ["wordfence", "Wordfence"],
    "Sucuri WAF": ["sucuri", "cloudproxy", "Sucuri/Cloudproxy", "x-sucuri-id"],
    "Cloudbric": ["cloudbric", "Cloudbric"],
    "Wallarm": ["wallarm", "Wallarm"],
}

STATUS_CLASSIFICATION = {
    200: "found",
    201: "created",
    204: "no_content",
    301: "redirect_permanent",
    302: "redirect_temporary",
    304: "not_modified",
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    429: "rate_limited",
    500: "server_error",
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout",
}


class Analyzer:
    """Analyzes HTTP responses and classifies findings."""

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
        self.total_urls_analyzed += 1

        # 1. False positive check
        if status == 200 and self.baseline_length and content_length == self.baseline_length:
            return {"url": url, "risk": "false_positive", "score": 0, "findings": ["Same length as baseline (likely false positive)"]}

        # 2. Detect technologies
        for tech, signatures in TECH_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in content.lower() or sig.lower() in str(headers).lower():
                    self.technologies.add(tech)
                    findings.append(f"Technology: {tech}")
                    risk_score += 1
                    break

        # 3. Detect WAF
        for waf, signatures in WAF_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in str(headers).lower() or sig.lower() in content.lower():
                    self.wafs.add(waf)
                    findings.append(f"WAF detected: {waf}")
                    risk_score += 2
                    break

        # 4. Detect security headers
        security_headers = {
            "Strict-Transport-Security": "HSTS enabled",
            "Content-Security-Policy": "CSP enabled",
            "X-Frame-Options": "Clickjacking protection",
            "X-Content-Type-Options": "MIME sniffing protection",
            "X-XSS-Protection": "XSS filter enabled",
        }
        for header, description in security_headers.items():
            if header in headers:
                findings.append(f"Security: {description}")
            else:
                findings.append(f"Missing: {header}")
                risk_score += 3

        # 5. Detect risks
        if status == 200:
            for pattern in RISK_PATTERNS["directory_listing"]:
                if pattern in content:
                    findings.append("Directory listing enabled")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["phpinfo"]:
                if pattern in content:
                    findings.append("PHP info exposed")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["sql_dump"]:
                if pattern in content:
                    findings.append("SQL dump exposed")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["git_exposed"]:
                if pattern in content or pattern in url:
                    findings.append("Git repository exposed")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["api_key"]:
                if pattern in content:
                    findings.append("Possible API key or secret exposed")
                    risk_score += 40
                    break

            for pattern in RISK_PATTERNS["aws_credentials"]:
                if pattern in content:
                    findings.append("AWS credentials exposed")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["debug_mode"]:
                if pattern in content:
                    findings.append("Debug mode enabled")
                    risk_score += 30
                    break

            for pattern in RISK_PATTERNS["backup_file"]:
                if pattern in url.lower():
                    findings.append("Backup file exposed")
                    risk_score += 30
                    break

            for pattern in RISK_PATTERNS["config_file"]:
                if pattern in url.lower():
                    findings.append("Config file exposed")
                    risk_score += 30
                    break

            for pattern in RISK_PATTERNS["error_disclosure"]:
                if pattern in content:
                    findings.append("Error messages disclosed")
                    risk_score += 20
                    break

            for pattern in RISK_PATTERNS["php_errors"]:
                if pattern in content:
                    findings.append("PHP errors disclosed")
                    risk_score += 25
                    break

            for pattern in RISK_PATTERNS["sql_errors"]:
                if pattern in content:
                    findings.append("SQL errors disclosed")
                    risk_score += 25
                    break

            for pattern in RISK_PATTERNS["swagger"]:
                if pattern in content.lower() or pattern in url.lower():
                    findings.append("API documentation exposed (Swagger/OpenAPI)")
                    risk_score += 15
                    break

            for pattern in RISK_PATTERNS["graphql"]:
                if pattern in url.lower():
                    findings.append("GraphQL endpoint found")
                    risk_score += 10
                    break

            for pattern in RISK_PATTERNS["actuator"]:
                if pattern in url.lower():
                    findings.append("Spring Actuator endpoint found")
                    risk_score += 20
                    break

            for pattern in RISK_PATTERNS["sensitive_files"]:
                if pattern in url.lower():
                    findings.append("Sensitive file exposed")
                    risk_score += 40
                    break

            for pattern in RISK_PATTERNS["exposed_panels"]:
                if pattern in content.lower() or pattern in url.lower():
                    findings.append("Admin panel or management interface exposed")
                    risk_score += 25
                    break

            for pattern in RISK_PATTERNS["docker_api"]:
                if pattern in url.lower():
                    findings.append("Docker API exposed")
                    risk_score += 40
                    break

            for pattern in RISK_PATTERNS["kubernetes_api"]:
                if pattern in url.lower():
                    findings.append("Kubernetes API exposed")
                    risk_score += 40
                    break

            for pattern in RISK_PATTERNS["outdated_software"]:
                if pattern in str(headers) or pattern in content:
                    findings.append("Outdated software version detected")
                    risk_score += 20
                    break

            has_form = any(p in content.lower() for p in RISK_PATTERNS["login_form"])
            if has_form:
                findings.append("Login form detected")
                risk_score += 5

        elif status in [301, 302]:
            redirect_url = result.get("redirect", "")
            if "login" in redirect_url.lower():
                findings.append("Redirects to login page")
                risk_score += 5
            else:
                findings.append(f"Redirect to: {redirect_url}")

        elif status == 403:
            findings.append("Access forbidden (resource exists)")
            risk_score += 10

        elif status == 401:
            findings.append("Authentication required")
            risk_score += 10

        elif status == 429:
            findings.append("Rate limited (429)")
            risk_score += 5

        elif status >= 500:
            findings.append(f"Server error ({status})")
            risk_score += 25

        # 6. Fingerprinting from headers
        server = headers.get("Server", "")
        powered_by = headers.get("X-Powered-By", "")
        x_generator = headers.get("X-Generator", "")

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
                    # Check outdated
                    if ver.startswith("2.2") or ver.startswith("2.4.0"):
                        findings.append("CRITICAL: Apache version is severely outdated")
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
                    findings.append("CRITICAL: PHP version is end-of-life")
                    risk_score += 30

        if x_generator:
            findings.append(f"Generator: {x_generator}")

        # 7. Check cookies
        set_cookie = headers.get("Set-Cookie", "")
        if set_cookie:
            if "HttpOnly" not in set_cookie:
                findings.append("Cookie missing HttpOnly flag")
                risk_score += 10
            if "Secure" not in set_cookie:
                findings.append("Cookie missing Secure flag")
                risk_score += 10
            if "SameSite" not in set_cookie:
                findings.append("Cookie missing SameSite attribute")
                risk_score += 5

        # 8. Determine risk level
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

        # 9. Store finding
        finding = {
            "url": url,
            "status": status,
            "risk": risk_level,
            "score": risk_score,
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
    print("[*] Analyzer module loaded successfully.")
    print("[*] Use: from analyzer import Analyzer")
