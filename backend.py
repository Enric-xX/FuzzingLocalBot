#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

TIMEOUT = 3
THREADS = 50
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def cargar_extensiones(archivo):
    dirs, exts = [], []
    if not os.path.exists(archivo):
        return [], []
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if "." in linea and "/" not in linea and "\\" not in linea:
                if not linea.startswith("*"):
                    exts.append(linea)
            else:
                dirs.append(linea)
    return dirs, exts

def generar_rutas(dirs, exts):
    if dirs and exts:
        return [d + e for d in dirs for e in exts]
    return dirs.copy() if dirs else exts.copy()

def probar(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
        return {"url": url, "status": r.status_code, "exists": r.status_code < 400}
    except:
        return {"url": url, "status": "error", "exists": False}

def main():
    if len(sys.argv) < 4:
        log("Uso: python backend.py <dominio> <extensiones.txt> <resultados.txt>")
        sys.exit(1)
    
    dominio = sys.argv[1]
    ext_file = sys.argv[2]
    results_file = sys.argv[3]
    
    log(f"Iniciando backend para {dominio}")
    
    dirs, exts = cargar_extensiones(ext_file)
    rutas = generar_rutas(dirs, exts)
    
    log(f"Total combinaciones: {len(rutas)}")
    
    resultados = []
    encontrados = 0
    
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        futures = {ex.submit(probar, urljoin(dominio, r)): r for r in rutas}
        for i, f in enumerate(as_completed(futures), 1):
            res = f.result()
            resultados.append(res)
            if res.get("exists", False):
                encontrados += 1
                with open(results_file, "a", encoding="utf-8") as out:
                    out.write(f"[{res['status']}] {res['url']}\n")
            if i % 500 == 0:
                log(f"Progreso: {i}/{len(rutas)} | Encontrados: {encontrados}")
    
    with open(results_file.replace(".txt", ".json"), "w") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Completado: {encontrados}/{len(rutas)} encontrados")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrumpido.")
    except Exception as e:
        log(f"ERROR: {e}")
