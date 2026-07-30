# FuzzingLocalBot v2.0
![Uploading image.png…]()


Automatización de fuzzing de directorios y extensiones con análisis inteligente y reportes profesionales para pentesting autorizado.


![Python](https://img.shields.io/badge/Python-3.6+-blue)
![License](https://img.shields.io/badge/License-GPL%20v3-orange)
---

## Dependencias

Antes de instalar, necesitas tener instalado:

| Programa | Descarga | ¿Obligatorio? |
|----------|----------|---------------|
| **Python 3.6+** | [python.org/downloads](https://www.python.org/downloads/) | ✅ Sí |
| **AutoHotkey 1.1+** | [autohotkey.com/download](https://www.autohotkey.com/download/) | ⚠️ Solo para GUI (Windows) |

---

## Instalación

### Linux 

```
git clone https://github.com/Enric-xX/FuzzingLocalBot.git
```
```
cd FuzzingLocalBot
```
```
pip install -r requirements.txt
```
### Windows

```
git clone https://github.com/Enric-xX/FuzzingLocalBot.git
```
```
cd FuzzingLocalBot
```
```
pip install -r requirements.txt
```

---

## Uso

### Con interfaz gráfica (Windows)

- Ejecuta bot.ahk con AutoHotkey

- Selecciona el navegador

- Introduce el dominio objetivo (ej: https://ejemplo.com)

- Haz clic en INICIAR FUZZING

### Desde terminal (Linux / Windows)

```
python fuzzingbot.py https://ejemplo.com extensiones.txt resultados.txt
```

---

## ¿Qué hace?

- Fuzzing → Escanea 42.000 rutas contra el dominio objetivo con 50 threads en paralelo

- Análisis → Detecta tecnologías (WordPress, Apache, PHP...), directory listing, backups expuestos, configuraciones, Git expuesto y más

- Reporte → Genera un informe profesional en Markdown y HTML con los hallazgos clasificados por gravedad

---

## Clasificación de hallazgos

| Nivel | Qué Detecta |
|-------|-------------|
| Crítico | Directory listing, PHP info expuesto, SQL dumps, Git expuesto |
| Alto | Backups, archivos de configuración, errores de servidor |
| Medio | 403 Forbidden, 401 Unauthorized, error disclosure |
| Bajo | Redirecciones a login |
| Info | Tecnologías detectadas, fingerprints |

---

## Estructura

```
FuzzingLocalBot/
├── LICENSE                 Licencia GPL v3
├── README.md               Este archivo
├── config.ini              Configuración
├── requirements.txt        Dependencias Python
├── extensiones.txt         Diccionario de 42k rutas
├── fuzzingbot.py           Motor principal de fuzzing
├── analyzer.py             Analizador de respuestas HTTP
├── reporter.py             Generador de informes
├── bot.ahk                 Interfaz gráfica (AutoHotkey)
└── output/                 Carpeta de resultados
    ├── scan_*.txt           Resultados brutos
    ├── scan_*.json          Resultados en JSON
    ├── report_*.md          Informe en Markdown
    └── report_*.html        Informe en HTML

```
---

## Aviso de seguridad

### USA UNA VPN ANTES DE EJECUTAR ESTA HERRAMIENTA.

Esta herramienta es exclusivamente para pentesting autorizado. No la uses contra sistemas sin el permiso explícito de su propietario.

---

## Licencia

GNU General Public License v3.0 - Ver [LICENSE](https://github.com/Enric-xX/FuzzingLocalBot/blob/main/LICENSE)

---

## Autor

### Enric-xX

GitHub: [@Enric-xX](https://github.com/Enric-xX)



