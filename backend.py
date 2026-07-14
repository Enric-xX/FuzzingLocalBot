#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

TIMEOUT = 10
THREADS = 20
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def log(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def cargar_extensiones(archivo):
    directorios = []
    extensiones = []
    
    if not os.path.exists(archivo):
        log(f"ERROR: Archivo {archivo} no encontrado.")
        return [], []
    
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            
            if "." in linea and "/" not in linea and "\\" not in linea:
                if not linea.startswith("*"):
                    extensiones.append(linea)
            else:
                directorios.append(linea)
    
    return directorios, extensiones

def generar_combinaciones(directorios, extensiones):
    if directorios and extensiones:
        return [d + e for d in directorios for e in extensiones]
    elif directorios:
        return directorios.copy()
    elif extensiones:
        return extensiones.copy()
    return []

def probar_url(url, timeout=TIMEOUT):
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        return {
            "url": url,
            "status": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "content_length": len(response.content),
            "redirect": response.url if response.history else None,
            "exists": response.status_code < 400
        }
    except requests.exceptions.Timeout:
        return {"url": url, "status": "timeout", "exists": False}
    except requests.exceptions.ConnectionError:
        return {"url": url, "status": "connection_error", "exists": False}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e), "exists": False}

def main():
    if len(sys.argv) < 4:
        log("Uso: python fuzz_backend.py <dominio> <extensiones.txt> <resultados.txt>")
        sys.exit(1)
    
    dominio = sys.argv[1]
    ext_file = sys.argv[2]
    results_file = sys.argv[3]
    
    log(f"Iniciando backend para {dominio}")
    
    directorios, extensiones = cargar_extensiones(ext_file)
    rutas = generar_combinaciones(directorios, extensiones)
    
    log(f"Directorios: {len(directorios)}, Extensiones: {len(extensiones)}, Total: {len(rutas)}")
    
    resultados = []
    log(f"Probando {len(rutas)} rutas con {THREADS} threads...")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(probar_url, urljoin(dominio, ruta)): ruta for ruta in rutas}
        
        for i, future in enumerate(as_completed(futures), 1):
            resultado = future.result()
            resultados.append(resultado)
            
            if resultado.get("exists", False):
                with open(results_file, "a", encoding="utf-8") as f:
                    f.write(f"[{resultado['status']}] {resultado['url']}\n")
            
            if i % 50 == 0:
                log(f"Progreso: {i}/{len(rutas)}")
    
    json_file = results_file.replace(".txt", ".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    encontrados = [r for r in resultados if r.get("exists", False)]
    log(f"✅ Completado: {len(encontrados)}/{len(rutas)} rutas encontradas")
    log(f"Resultados guardados en {json_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrumpido por el usuario.")
    except Exception as e:
        log(f"ERROR: {e}")
