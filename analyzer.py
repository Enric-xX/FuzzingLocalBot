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
    "WordPress": ["wp-content", "wp-json", "wp-includes", "wordpress"],
    "Joomla": ["joomla", "com_content"],
    "Drupal": ["drupal", "sites/default"],
    "Moodle": ["moodle", "course/view.php"],
    "Jenkins": ["jenkins", "Dashboard"],
    "Jira": ["jira", "atlassian"],
    "Confluence": ["confluence"],
    "PHP": ["X-Powered-By: PHP", "PHPSESSID", ".php"],
    "Apache": ["Apache", "Server: Apache"],
    "Nginx": ["nginx", "Server: nginx"],
    "IIS": ["Microsoft-IIS", "Server: Microsoft"],
    "Laravel": ["laravel", "XSRF-TOKEN"],
    "Django": ["django", "csrftoken"],
    "Ruby on Rails": ["rails", "_session_id"],
    "ASP.NET": ["ASP.NET", "__RequestVerificationToken"],
    "Tomcat": ["Apache Tomcat", "JSESSIONID"],
    "Node.js": ["node.js", "express"],
    "Cloudflare": ["cloudflare", "__cfduid"],
    "AWS": ["aws", "x-amz-request-id"],
    "Google Cloud": ["appspot.com", "firebase"],
    "Azure": ["azurewebsites.net", "x-azure-ref"],
}

RISK_PATTERNS = {
    "directory_listing": ["Index of /", "Parent Directory", "[DIR]"],
    "phpinfo": ["phpinfo", "PHP Version"],
    "sql_dump": ["INSERT INTO", "CREATE TABLE", "DROP TABLE", "BEGIN TRANSACTION"],
    "backup_file": [".bak", ".backup", ".old", ".sql.gz", ".tar.gz", ".zip", ".7z"],
    "config_file": [".env", "wp-config", "config.php", "settings.py", "application.properties"],
    "login_form": ["password", "login", "username", "<form"],
    "error_disclosure": ["Fatal error", "Warning:", "Notice:", "Stack trace", "on line"],
    "git_exposed": [".git/HEAD", "refs/heads"],
    "api_key": ["api_key", "apikey", "secret_key", "access_token", "Bearer"],
    "debug_mode": ["debug", "DEBUG=True", "APP_DEBUG", "WP_DEBUG"],
    "swagger": ["swagger", "openapi", "api-docs"],
    "graphql": ["graphql", "GraphQL"],
    "actuator": ["actuator", "health", "heapdump", "env"],
}

# WAF / IDS signatures
WAF_SIGNATURES = {
    "Cloudflare WAF": ["cf-ray", "cloudflare-nginx", "__cf_bm"],
    "AWS WAF": ["x-amzn-waf", "aws-waf"],
    "ModSecurity": ["mod_security", "Mod_Security"],
    "F5 BIG-IP": ["BigIP", "F5"],
    "Imperva": ["imperva", "incapsula"],
    "Akamai": ["akamai", "X-Akamai"],
    "Sucuri": ["sucuri", "cloudproxy"],
}

STATUS_CLASSIFICATION = {
    200: "found",
    201: "created",
    301: "redirect",
    302: "redirect",
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    429: "rate_limited",
    500: "server_error",
    502: "bad_gateway",
    503: "service_unavailable",
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

        # 1. False positive check
        if status == 200 and self.baseline_length and content_length == self.baseline_length:
            return {"url": url, "risk": "false_positive", "score": 0, "findings": ["Same length as baseline"]}

        # 2. Detect technologies
        for tech, signatures in TECH_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in content.lower() or sig in str(headers):
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

        # 4. Detect risks
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
                if pattern in content:
                    findings.append("Git repository exposed")
                    risk_score += 50
                    break

            for pattern in RISK_PATTERNS["api_key"]:
                if pattern in content:
                    findings.append("Possible API key or secret exposed")
                    risk_score += 40
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

            for pattern in RISK_PATTERNS["swagger"]:
                if pattern in content.lower() or pattern in url.lower():
                    findings.append("API documentation exposed")
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

        elif status >= 500:
            findings.append(f"Server error ({status})")
            risk_score += 25

        # 5. Fingerprinting from headers
        server = headers.get("Server", "")
        powered_by = headers.get("X-Powered-By", "")

        if server:
            findings.append(f"Server: {server}")
            risk_score += 5
            if "Apache" in server:
                self.technologies.add("Apache")
                version_match = re.search(r"Apache/([\d.]+)", server)
                if version_match:
                    findings.append(f"Apache version: {version_match.group(1)}")
                    risk_score += 15
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
                findings.append(f"PHP version: {version_match.group(1)}")
                risk_score += 15

        # 6. Determine risk level
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

        # 7. Store finding
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
            "technologies": list(self.technologies),
            "wafs": list(self.wafs),
        }

    def get_findings(self):
        return self.findings


if __name__ == "__main__":
    print("[*] Analyzer module loaded successfully.")
    print("[*] Use: from analyzer import Analyzer")
