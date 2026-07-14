; ============================================================
; Fuzzing Bot - AutoHotkey
; ============================================================

#NoEnv
#SingleInstance, Force
SetWorkingDir %A_ScriptDir%
SetBatchLines, -1
SetKeyDelay, 0, 0
SendMode, Input

; ============================================================
; CONFIGURACIÓN GLOBAL
; ============================================================
global ExtensionesFile := A_ScriptDir . "\extensiones.txt"
global Dominio := ""
global Navegador := ""
global PythonScript := A_ScriptDir . "\fuzz_backend.py"
global Directorios := []
global Extensiones := []
global RutasCompletas := []
global TotalRutas := 0
global Progreso := 0

; ============================================================
; MENÚ PRINCIPAL
; ============================================================
FuzzBotMenu:
    Gui, FuzzBot:Destroy
    Gui, FuzzBot:New, +AlwaysOnTop, Fuzzing Bot
    Gui, FuzzBot:Color, 0x0d1117
    Gui, FuzzBot:Font, s10 cWhite, Segoe UI

    Gui, FuzzBot:Add, Text, x10 y10 w380 h30 Center c00ff41, ⚡ FUZZING BOT ⚡
    
    Gui, FuzzBot:Add, Text, x10 y50 w120 h20 c8892b0, Navegador:
    Gui, FuzzBot:Add, DropDownList, x130 y48 w250 vNavSel, Chrome|Edge|Firefox|Brave|Opera

    Gui, FuzzBot:Add, Text, x10 y80 w120 h20 c8892b0, Dominio:
    Gui, FuzzBot:Add, Edit, x130 y78 w250 vDominioInput, https://ejemplo.com

    Gui, FuzzBot:Add, Text, x10 y110 w120 h20 c8892b0, Extensiones:
    Gui, FuzzBot:Add, Edit, x130 y108 w200 vExtFileReadOnly ReadOnly, %ExtensionesFile%
    Gui, FuzzBot:Add, Button, x335 y108 w45 h20 gSeleccionarExtensiones, ...

    Gui, FuzzBot:Add, Text, x10 y140 w370 h20 c8892b0 vEstadoExtensiones, Estado: Cargando...

    Gui, FuzzBot:Add, Button, x10 y170 w370 h40 gIniciarFuzzing, 🚀 INICIAR FUZZING

    Gui, FuzzBot:Add, Text, x10 y220 w370 h30 Center cFF5555, ⚠️ NO TOQUES EL TECLADO ⚠️

    Gui, FuzzBot:Show, w390 h270
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
    
    ; Leer todas las líneas del archivo
    lineas := []
    Loop, Read, %ExtensionesFile%
    {
        linea := Trim(A_LoopReadLine)
        if (linea != "" && SubStr(linea, 1, 1) != "#") {
            lineas.Push(linea)
        }
    }
    
    ; Clasificar directorios y extensiones
    for i, linea in lineas {
        if InStr(linea, ".") && !InStr(linea, "/") && !InStr(linea, "\") {
            if !InStr(linea, "*") {
                Extensiones.Push(linea)
            }
        } else {
            Directorios.Push(linea)
        }
    }
    
    ; Generar combinaciones
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
        MsgBox, Introduce un dominio válido.
        return
    }
    
    if !InStr(Dominio, "http://") && !InStr(Dominio, "https://") {
        Dominio := "https://" . Dominio
    }

    if TotalRutas == 0 {
        MsgBox, No hay rutas cargadas.
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
        MsgBox, Selecciona un navegador.
        return
    }

    MsgBox, 4, , ⚠️ FUZZING ⚠️`n`nObjetivo: %Dominio%`nRutas: %TotalRutas%`nNavegador: %NavSel%`n`n🚀 NO TOQUES EL TECLADO.
    IfMsgBox No
        return

    EjecutarFuzzing(Navegador, Dominio, RutasCompletas)
return

; ============================================================
; EJECUCIÓN DEL FUZZING
; ============================================================
EjecutarFuzzing(navegador, dominio, rutas) {
    global TotalRutas, Progreso
    
    ; Abrir navegador
    Run, %navegador%
    Sleep, 2000
    
    ; Nueva pestaña
    Send, ^n
    Sleep, 500
    Send, ^l
    Sleep, 300
    Send, %dominio%
    Sleep, 200
    Send, {Enter}
    Sleep, 1500
    
    Progreso := 0
    
    FormatTime, timestamp,, yyyy-MM-dd_HH-mm-ss
    resultadosFile := A_ScriptDir . "\fuzz_results_" . timestamp . ".txt"
    FileAppend, Resultados fuzzing en %dominio%`n`n, %resultadosFile%
    
    ; Iniciar Python backend
    if FileExist(PythonScript) {
        Run, python "%PythonScript%" "%dominio%" "%ExtensionesFile%" "%resultadosFile%",, Hide
    }
    
    ; Bucle principal
    for index, ruta in rutas {
        Progreso := index
        
        ; Abrir pestaña
        Send, ^n
        Sleep, 50
        
        ; Enfocar barra
        Send, ^l
        Sleep, 30
        
        ; Construir URL
        if InStr(ruta, ".") {
            url := dominio . "/" . ruta
        } else {
            url := dominio . "/" . ruta . "/"
        }
        
        ; Escribir URL
        SendInput, %url%
        Sleep, 50
        Send, {Enter}
        Sleep, 300
        
        ; Cerrar pestaña
        Send, ^w
        Sleep, 30
        
        ; Guardar cada 100
        if Mod(index, 100) == 0 {
            FileAppend, %index%: %url%`n, %resultadosFile%
            porcentaje := Round(index / TotalRutas * 100)
            TrayTip, Fuzzing, %porcentaje%% (%index%/%TotalRutas%), 1
        }
    }
    
    MsgBox, ✅ COMPLETADO!`n`n%TotalRutas% rutas probadas en %dominio%.`nResultados: %resultadosFile%
}

; ============================================================
; ATALLO DE TECLADO
; ============================================================
^!F::  ; Ctrl+Alt+F
    Gosub, FuzzBotMenu
return

; ============================================================
; CIERRE
; ============================================================
FuzzBotGuiClose:
    ExitApp
return

Gosub, FuzzBotMenu
