#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FuzzingLocalBot - Analyzer Module
Analiza las respuestas HTTP y clasifica los hallazgos por gravedad.
"""

import re

# ============================================================
# CONFIGURACIÓN DE FIRMAS
# ============================================================

# Tecnologías detectables
TECH_SIGNATURES = {
    "WordPress": ["wp-content", "wp-json", "wp-includes", "wordpress"],
    "Joomla": ["joomla", "com_content"],
    "Drupal": ["drupal", "sites/default"],
    "PHP": ["X-Powered-By: PHP", "PHPSESSID", ".php"],
    "Apache": ["Apache", "Server: Apache"],
    "Nginx": ["nginx", "Server: nginx"],
    "IIS": ["Microsoft-IIS", "Server: Microsoft"],
    "Laravel": ["laravel", "XSRF-TOKEN"],
    "Django": ["django", "csrftoken"],
}

# Patrones de riesgo
RISK_PATTERNS = {
    "directory_listing": ["Index of /", "Parent Directory", "[DIR]"],
    "phpinfo": ["phpinfo", "PHP Version"],
    "sql_dump": ["INSERT INTO", "CREATE TABLE", "DROP TABLE"],
    "backup_file": [".bak", ".backup", ".old", ".sql.gz", ".tar.gz", ".zip"],
    "config_file": [".env", "wp-config", "config.php", "settings.py"],
    "login_form": ["password", "login", "username", "<form"],
    "error_disclosure": ["Fatal error", "Warning:", "Notice:", "Stack trace"],
    "git_exposed": [".git/HEAD", "refs/heads"],
}

# Clasificación por status code
STATUS_CLASSIFICATION = {
    200: "found",
    301: "redirect",
    302: "redirect",
    403: "forbidden",
    401: "unauthorized",
    500: "server_error",
    502: "bad_gateway",
    503: "service_unavailable",
    429: "rate_limited",
}


class Analyzer:
    """Analiza respuestas HTTP y clasifica hallazgos."""

    def __init__(self):
        self.findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": [],
        }
        self.technologies = set()
        self.baseline_length = None

    def set_baseline(self, length):
        """Establece la longitud de respuesta baseline (página de error genérica)."""
        self.baseline_length = length

    def analyze(self, result):
        """
        Analiza un resultado y devuelve la clasificación.
        
        Args:
            result: dict con 'url', 'status', 'content_type', 'content_length', 
                    'redirect', 'content' (opcional)
        
        Returns:
            dict con la clasificación del hallazgo
        """
        url = result.get("url", "")
        status = result.get("status", 0)
        content_type = result.get("content_type", "")
        content_length = result.get("content_length", 0)
        content = result.get("content", "")
        headers = result.get("headers", {})

        findings = []
        risk_level = "info"

        # 1. Clasificar por status code
        status_type = STATUS_CLASSIFICATION.get(status, "unknown")

        # 2. Ignorar falsos positivos
        if status == 200 and self.baseline_length and content_length == self.baseline_length:
            return {"url": url, "risk": "false_positive", "findings": ["Misma longitud que baseline"]}

        # 3. Detectar tecnologías
        for tech, signatures in TECH_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in content.lower() or sig in headers.get("Server", ""):
                    self.technologies.add(tech)
                    findings.append(f"Technology: {tech}")

        # 4. Detectar riesgos
        if status == 200:
            # Directory listing
            for pattern in RISK_PATTERNS["directory_listing"]:
                if pattern in content:
                    findings.append("Directory listing enabled")
                    risk_level = "critical"
                    break

            # PHP Info
            for pattern in RISK_PATTERNS["phpinfo"]:
                if pattern in content:
                    findings.append("PHP info exposed")
                    risk_level = "critical"
                    break

            # SQL dump
            for pattern in RISK_PATTERNS["sql_dump"]:
                if pattern in content:
                    findings.append("SQL dump exposed")
                    risk_level = "critical"
                    break

            # Backup files
            for pattern in RISK_PATTERNS["backup_file"]:
                if pattern in url.lower():
                    findings.append("Backup file exposed")
                    risk_level = "high"
                    break

            # Config files
            for pattern in RISK_PATTERNS["config_file"]:
                if pattern in url.lower():
                    findings.append("Config file exposed")
                    risk_level = "high"
                    break

            # Git exposed
            for pattern in RISK_PATTERNS["git_exposed"]:
                if pattern in content:
                    findings.append("Git repository exposed")
                    risk_level = "critical"
                    break

            # Error disclosure
            for pattern in RISK_PATTERNS["error_disclosure"]:
                if pattern in content:
                    findings.append("Error messages disclosed")
                    risk_level = "medium"
                    break

            # Login form
            has_form = False
            for pattern in RISK_PATTERNS["login_form"]:
                if pattern in content.lower():
                    has_form = True
            if has_form:
                findings.append("Login form detected")

        elif status in [301, 302]:
            redirect_url = result.get("redirect", "")
            if "login" in redirect_url.lower():
                findings.append("Redirects to login page")
                risk_level = "low"
            else:
                findings.append(f"Redirect to: {redirect_url}")
                risk_level = "info"

        elif status == 403:
            findings.append("Access forbidden (resource exists)")
            risk_level = "medium"

        elif status == 401:
            findings.append("Authentication required")
            risk_level = "medium"

        elif status >= 500:
            findings.append(f"Server error ({status})")
            risk_level = "high"

        # 5. Fingerprinting por headers
        server = headers.get("Server", "")
        powered_by = headers.get("X-Powered-By", "")

        if server:
            findings.append(f"Server: {server}")
            if "Apache" in server:
                self.technologies.add("Apache")
                # Extraer versión si está expuesta
                version_match = re.search(r"Apache/([\d.]+)", server)
                if version_match:
                    findings.append(f"Apache version: {version_match.group(1)}")
            elif "nginx" in server:
                self.technologies.add("Nginx")

        if powered_by:
            findings.append(f"X-Powered-By: {powered_by}")
            self.technologies.add("PHP")

        # 6. Determinar nivel de riesgo final
        if not findings:
            risk_level = "info"
            findings.append("No significant findings")

        # 7. Almacenar en la categoría correspondiente
        finding = {
            "url": url,
            "status": status,
            "risk": risk_level,
            "findings": findings,
            "content_length": content_length,
        }

        if risk_level == "critical":
            self.findings["critical"].append(finding)
        elif risk_level == "high":
            self.findings["high"].append(finding)
        elif risk_level == "medium":
            self.findings["medium"].append(finding)
        elif risk_level == "low":
            self.findings["low"].append(finding)
        else:
            self.findings["info"].append(finding)

        return finding

    def get_summary(self):
        """Devuelve un resumen de los hallazgos."""
        return {
            "critical": len(self.findings["critical"]),
            "high": len(self.findings["high"]),
            "medium": len(self.findings["medium"]),
            "low": len(self.findings["low"]),
            "info": len(self.findings["info"]),
            "technologies": list(self.technologies),
        }

    def get_findings(self):
        """Devuelve todos los hallazgos categorizados."""
        return self.findings


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[*] Analyzer module loaded successfully.")
    print("[*] Use: from analyzer import Analyzer")
