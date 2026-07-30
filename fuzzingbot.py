#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import signal
import threading
import urllib3
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("[!] Instala requests: pip install requests")
    sys.exit(1)

# ============================================================
# CONFIGURACIÓN
# ============================================================
TIMEOUT = 3
THREADS = 50
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
MAX_RETRIES = 2
ENCONTRADOS = 0
TOTAL = 0
LOCK = threading.Lock()
INICIO = time.time()
ULTIMA_ACTUALIZACION = time.time()

# ============================================================
# UTILIDADES
# ============================================================
def log(mensaje):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def mostrar_progreso():
    global ENCONTRADOS, TOTAL, INICIO, ULTIMA_ACTUALIZACION
    if time.time() - ULTIMA_ACTUALIZACION < 2:
        return
    ULTIMA_ACTUALIZACION = time.time()
    elapsed = time.time() - INICIO
    if elapsed > 0 and TOTAL > 0:
        velocidad = ENCONTRADOS / elapsed
        estimado = (TOTAL - ENCONTRADOS) / (velocidad + 0.001)
        log(f"Progreso: {ENCONTRADOS}/{TOTAL} encontrados | Vel: {velocidad:.1f}/s | Est: {estimado:.0f}s")

def mostrar_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗   ██╗███████╗███████╗██╗███╗   ██╗ ██████╗   ║
║   ██╔════╝██║   ██║╚══███╔╝╚══███╔╝██║████╗  ██║██╔════╝   ║
║   █████╗  ██║   ██║  ███╔╝   ███╔╝ ██║██╔██╗ ██║██║  ███╗  ║
║   ██╔══╝  ██║   ██║ ███╔╝   ███╔╝  ██║██║╚██╗██║██║   ██║  ║
║   ██║     ╚██████╔╝███████╗███████╗██║██║ ╚████║╚██████╔╝  ║
║   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝   ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  RECOMENDACION: USA UNA VPN ANTES DE EJECUTAR ESTO          ║
║  Solo para pentesting autorizado                            ║
╚══════════════════════════════════════════════════════════════╝
""")

def mostrar_ayuda():
    print("""
Uso: python fuzzingbot.py <dominio> <extensiones.txt> <resultados.txt>

Ejemplo:
    python fuzzingbot.py https://ejemplo.com extensiones.txt resultados.txt

Parametros:
    dominio         - URL objetivo (ej: https://ejemplo.com)
    extensiones.txt - Archivo con directorios y extensiones
    resultados.txt  - Archivo donde se guardaran los resultados
""")

# ============================================================
# CARGA DE EXTENSIONES
# ============================================================
def cargar_extensiones(archivo):
    directorios = []
    extensiones = []
    
    if not os.path.exists(archivo):
        log(f"ERROR: Archivo {archivo} no encontrado.")
        return [], []
    
    log(f"Cargando {archivo}...")
    
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
    
    log(f"Cargados: {len(directorios)} directorios, {len(extensiones)} extensiones")
    return directorios, extensiones

def generar_rutas(directorios, extensiones):
    if directorios and extensiones:
        total = len(directorios) * len(extensiones)
        log(f"Generando {total} combinaciones...")
        return [d + e for d in directorios for e in extensiones]
    elif directorios:
        return directorios.copy()
    elif extensiones:
        return extensiones.copy()
    return []

# ============================================================
# PROBAR URL
# ============================================================
def probar_url(url, timeout=TIMEOUT):
    headers = {"User-Agent": USER_AGENT}
    for intento in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                allow_redirects=True,
                verify=False
            )
            return {
                "url": url,
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(response.content),
                "redirect": response.url if response.history else None,
                "exists": response.status_code < 400,
                "content": response.text[:5000],
                "headers": dict(response.headers)
            }
        except requests.exceptions.Timeout:
            if intento < MAX_RETRIES:
                continue
            return {"url": url, "status": "timeout", "exists": False}
        except requests.exceptions.ConnectionError:
            if intento < MAX_RETRIES:
                continue
            return {"url": url, "status": "connection_error", "exists": False}
        except Exception as e:
            return {"url": url, "status": "error", "error": str(e), "exists": False}
    return {"url": url, "status": "error", "exists": False}

# ============================================================
# PROGRESO EN TIEMPO REAL
# ============================================================
def mostrar_progreso_periodico(total, encontrados, inicio):
    global ULTIMA_ACTUALIZACION
    while True:
        time.sleep(5)
        elapsed = time.time() - inicio
        if total > 0 and elapsed > 0:
            velocidad = encontrados / elapsed
            restante = total - encontrados
            estimado = restante / (velocidad + 0.001) if velocidad > 0 else 0
            log(f"Progreso: {encontrados}/{total} | Vel: {velocidad:.1f}/s | Est: {estimado:.0f}s")

# ============================================================
# MAIN
# ============================================================
def main():
    global ENCONTRADOS, TOTAL, INICIO
    
    # Mostrar banner y recomendacion
    mostrar_banner()
    
    # Verificar argumentos
    if len(sys.argv) < 4:
        mostrar_ayuda()
        sys.exit(1)
    
    dominio = sys.argv[1]
    ext_file = sys.argv[2]
    results_file = sys.argv[3]
    
    log(f"Iniciando backend para {dominio}")
    
    # Cargar extensiones
    directorios, extensiones = cargar_extensiones(ext_file)
    if not directorios and not extensiones:
        log("ERROR: No se cargaron directorios ni extensiones.")
        sys.exit(1)
    
    # Generar rutas
    rutas = generar_rutas(directorios, extensiones)
    TOTAL = len(rutas)
    
    if TOTAL == 0:
        log("ERROR: No se generaron rutas.")
        sys.exit(1)
    
    log(f"Total de rutas a probar: {TOTAL}")
    
    # Inicio
    INICIO = time.time()
    resultados = []
    ENCONTRADOS = 0
    hilo_progreso = threading.Thread(target=mostrar_progreso_periodico, args=(TOTAL, ENCONTRADOS, INICIO), daemon=True)
    hilo_progreso.start()
    
    # Probar en paralelo
    log(f"Probando con {THREADS} threads...")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(probar_url, urljoin(dominio, ruta)): ruta for ruta in rutas}
        
        for i, future in enumerate(as_completed(futures), 1):
            resultado = future.result()
            resultados.append(resultado)
            
            if resultado.get("exists", False):
                ENCONTRADOS += 1
                with open(results_file, "a", encoding="utf-8") as f:
                    f.write(f"[{resultado['status']}] {resultado['url']}\n")
                log(f"ENCONTRADO: {resultado['status']} {resultado['url']}")
            
            # Progreso cada 100
            if i % 100 == 0:
                mostrar_progreso()
    
    # Guardar resultados completos en JSON
    json_file = results_file.replace(".txt", ".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    # Resumen final
    elapsed = time.time() - INICIO
    log("=" * 50)
    log(f"COMPLETADO")
    log(f"   Total rutas: {TOTAL}")
    log(f"   Encontradas: {ENCONTRADOS}")
    log(f"   Tiempo: {elapsed:.1f}s")
    log(f"   Velocidad: {TOTAL/elapsed:.1f} rutas/s")
    log(f"   Resultados: {results_file}")
    log(f"   JSON: {json_file}")
    log("=" * 50)
    
    # ============================================================
    # ANALISIS Y REPORTE
    # ============================================================
    try:
        from analyzer import Analyzer
        from reporter import Reporter
        
        log("\nAnalizando resultados...")
        analyzer = Analyzer()
        
        # Establecer baseline (longitud de la pagina de error generica)
        if resultados:
            lengths = [r.get("content_length", 0) for r in resultados if r.get("status") == 200]
            if lengths:
                baseline = max(set(lengths), key=lengths.count)
                analyzer.set_baseline(baseline)
        
        # Analizar cada resultado
        for r in resultados:
            if r.get("exists", False) or r.get("status") in [401, 403, 500]:
                analyzer.analyze(r)
        
        # Generar reportes
        log("Generando reportes...")
        reporter = Reporter(dominio, analyzer)
        
        md_file = reporter.save_markdown(TOTAL, elapsed, output_dir="output")
        html_file = reporter.save_html(TOTAL, elapsed, output_dir="output")
        
        summary = analyzer.get_summary()
        log(f"   Criticos: {summary['critical']}")
        log(f"   Altos: {summary['high']}")
        log(f"   Medios: {summary['medium']}")
        log(f"   Bajos: {summary['low']}")
        log(f"   Info: {summary['info']}")
        log(f"   Reporte MD: {md_file}")
        log(f"   Reporte HTML: {html_file}")
        
    except ImportError:
        log("analyzer.py o reporter.py no encontrados. Reportes no generados.")
    except Exception as e:
        log(f"Error generando reportes: {e}")

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        main()
    except KeyboardInterrupt:
        log("Interrumpido por el usuario.")
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
