; ============================================================
; FuzzingLocalBot - AutoHotkey Interface
; Version: 2.0
; ============================================================

#NoEnv
#SingleInstance, Force
SetWorkingDir %A_ScriptDir%
SetBatchLines, -1
SetKeyDelay, 0, 0
SendMode, Input

; ============================================================
; CONFIGURACION GLOBAL
; ============================================================
global ExtensionesFile := A_ScriptDir . "\extensiones.txt"
global Dominio := ""
global Navegador := ""
global PythonScript := A_ScriptDir . "\fuzzingbot.py"
global Directorios := []
global Extensiones := []
global RutasCompletas := []
global TotalRutas := 0
global FuzzingActivo := false

; ============================================================
; MENU PRINCIPAL
; ============================================================
FuzzBotMenu:
    Gui, FuzzBot:Destroy
    Gui, FuzzBot:New, +AlwaysOnTop, FuzzingLocalBot v2.0
    Gui, FuzzBot:Color, 0x0d1117
    Gui, FuzzBot:Font, s10 cWhite, Segoe UI

    Gui, FuzzBot:Add, Text, x10 y10 w380 h30 Center c00ff41, FUZZINGLOCALBOT v2.0
    
    Gui, FuzzBot:Add, Text, x10 y50 w120 h20 c8892b0, Navegador:
    Gui, FuzzBot:Add, DropDownList, x130 y48 w250 vNavSel, Chrome|Edge|Firefox|Brave|Opera

    Gui, FuzzBot:Add, Text, x10 y80 w120 h20 c8892b0, Dominio:
    Gui, FuzzBot:Add, Edit, x130 y78 w250 vDominioInput, https://ejemplo.com

    Gui, FuzzBot:Add, Text, x10 y110 w120 h20 c8892b0, Extensiones:
    Gui, FuzzBot:Add, Edit, x130 y108 w200 vExtFileReadOnly ReadOnly, %ExtensionesFile%
    Gui, FuzzBot:Add, Button, x335 y108 w45 h20 gSeleccionarExtensiones, ...

    Gui, FuzzBot:Add, Text, x10 y140 w370 h20 c8892b0 vEstadoExtensiones, Estado: Cargando...

    Gui, FuzzBot:Add, Button, x10 y170 w370 h40 gIniciarFuzzing, INICIAR FUZZING

    Gui, FuzzBot:Add, Progress, x10 y220 w370 h20 c00ff41 vBarraProgreso, 0

    Gui, FuzzBot:Add, Text, x10 y250 w370 h30 Center cFF5555 vTextoEstado, Listo para empezar.

    Gui, FuzzBot:Show, w390 h300
    Gosub, CargarExtensiones
return

; ============================================================
; CARGAR EXTENSIONES
; ============================================================
CargarExtensiones:
    global ExtensionesFile, Directorios, Extensiones, RutasCompletas, TotalRutas
    
    Directorios := []
    Extensiones := []
    RutasCompletas := []
    
    if !FileExist(ExtensionesFile) {
        GuiControl, FuzzBot:, EstadoExtensiones, Estado: extensiones.txt no encontrado
        return
    }
    
    GuiControl, FuzzBot:, EstadoExtensiones, Estado: Cargando...
    
    lineas := []
    Loop, Read, %ExtensionesFile%
    {
        linea := Trim(A_LoopReadLine)
        if (linea != "" && SubStr(linea, 1, 1) != "#") {
            lineas.Push(linea)
        }
    }
    
    for i, linea in lineas {
        if InStr(linea, ".") && !InStr(linea, "/") && !InStr(linea, "\") {
            if !InStr(linea, "*") {
                Extensiones.Push(linea)
            }
        } else {
            Directorios.Push(linea)
        }
    }
    
    if Directorios.MaxIndex() > 0 && Extensiones.MaxIndex() > 0 {
        for i, dir in Directorios {
            for j, ext in Extensiones {
                RutasCompletas.Push(dir . ext)
            }
        }
    } else if Directorios.MaxIndex() > 0 {
        RutasCompletas := Directorios.Clone()
    } else {
        RutasCompletas := Extensiones.Clone()
    }
    
    TotalRutas := RutasCompletas.MaxIndex()
    estado := "Estado: " . Directorios.MaxIndex() . " dirs + " . Extensiones.MaxIndex() . " ext = " . TotalRutas . " combinaciones"
    GuiControl, FuzzBot:, EstadoExtensiones, %estado%
return

; ============================================================
; SELECCIONAR ARCHIVO
; ============================================================
SeleccionarExtensiones:
    FileSelectFile, archivo, 3, , Selecciona extensiones, Text Documents (*.txt)
    if archivo {
        ExtensionesFile := archivo
        GuiControl, FuzzBot:, ExtFileReadOnly, %ExtensionesFile%
        Gosub, CargarExtensiones
    }
return

; ============================================================
; INICIO DEL FUZZING
; ============================================================
IniciarFuzzing:
    Gui, FuzzBot:Submit, NoHide

    Dominio := Trim(DominioInput)
    if !Dominio || Dominio == "https://ejemplo.com" {
        MsgBox, 16, Error, Introduce un dominio valido.
        return
    }
    
    if !InStr(Dominio, "http://") && !InStr(Dominio, "https://") {
        Dominio := "https://" . Dominio
    }

    if TotalRutas == 0 {
        MsgBox, 16, Error, No hay rutas cargadas.
        return
    }

    if NavSel = "Chrome" {
        Navegador := "chrome.exe"
    } else if NavSel = "Edge" {
        Navegador := "msedge.exe"
    } else if NavSel = "Firefox" {
        Navegador := "firefox.exe"
    } else if NavSel = "Brave" {
        Navegador := "brave.exe"
    } else if NavSel = "Opera" {
        Navegador := "opera.exe"
    } else {
        MsgBox, 16, Error, Selecciona un navegador.
        return
    }

    MsgBox, 4, FuzzingLocalBot v2.0, 
    (
    CONFIGURACION DEL ESCANEO:
    
    Objetivo: %Dominio%
    Rutas: %TotalRutas%
    Navegador: %NavSel%
    
    El backend Python hara el fuzzing real.
    La ventana de CMD mostrara el progreso.
    
    DESEA CONTINUAR?
    )
    IfMsgBox No
        return

    EjecutarFuzzing(Navegador, Dominio, RutasCompletas)
return

; ============================================================
; EJECUCION DEL FUZZING
; ============================================================
EjecutarFuzzing(navegador, dominio, rutas) {
    global TotalRutas, FuzzingActivo, PythonScript, ExtensionesFile
    
    FuzzingActivo := true
    GuiControl, FuzzBot:, TextoEstado, Iniciando backend Python...
    GuiControl, FuzzBot:, BarraProgreso, 0
    
    FormatTime, timestamp,, yyyy-MM-dd_HH-mm-ss
    resultadosFile := A_ScriptDir . "\output\scan_" . timestamp . ".txt"
    
    ; Crear carpeta output si no existe
    FileCreateDir, %A_ScriptDir%\output
    
    ; Iniciar Python backend en una ventana visible de CMD
    if FileExist(PythonScript) {
        GuiControl, FuzzBot:, TextoEstado, Backend Python ejecutandose. Mira la ventana CMD.
        Run, cmd /k python "%PythonScript%" "%dominio%" "%ExtensionesFile%" "%resultadosFile%", , , PID
    } else {
        MsgBox, 16, Error, No se encontro %PythonScript%
        FuzzingActivo := false
        GuiControl, FuzzBot:, TextoEstado, Error: Script no encontrado.
        return
    }
    
    ; Esperar a que termine el proceso Python
    Sleep, 2000
    GuiControl, FuzzBot:, TextoEstado, Escaneando... Espera a que termine la ventana CMD.
    
    loop {
        Process, Exist, %PID%
        if (ErrorLevel == 0) {
            break
        }
        Sleep, 1000
    }
    
    FuzzingActivo := false
    GuiControl, FuzzBot:, BarraProgreso, 100
    GuiControl, FuzzBot:, TextoEstado, Escaneo completado.
    
    ; Buscar reportes generados
    reporteHTML := ""
    Loop, Files, %A_ScriptDir%\output\report_*.html
    {
        reporteHTML := A_LoopFileFullPath
    }
    
    if reporteHTML != "" {
        MsgBox, 4, FuzzingLocalBot v2.0,
        (
        ESCANEO COMPLETADO!
        
        Resultados: %resultadosFile%
        Reporte: %reporteHTML%
        
        DESEA ABRIR EL REPORTE?
        )
        IfMsgBox Yes
        {
            Run, %reporteHTML%
        }
    } else {
        MsgBox, 64, FuzzingLocalBot v2.0,
        (
        ESCANEO COMPLETADO!
        
        Resultados guardados en: %resultadosFile%
        )
    }
    
    GuiControl, FuzzBot:, TextoEstado, Listo para otro escaneo.
    GuiControl, FuzzBot:, BarraProgreso, 0
}

; ============================================================
; ATALLO DE TECLADO
; ============================================================
^!F::
    Gosub, FuzzBotMenu
return

; ============================================================
; CIERRE
; ============================================================
FuzzBotGuiClose:
    if FuzzingActivo {
        MsgBox, 4, FuzzingLocalBot, Hay un escaneo en curso. Desea salir?
        IfMsgBox No
            return
    }
    ExitApp
return

Gosub, FuzzBotMenu
