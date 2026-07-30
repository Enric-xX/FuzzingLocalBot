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
; GLOBAL CONFIGURATION
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
; MAIN MENU
; ============================================================
FuzzBotMenu:
    Gui, FuzzBot:Destroy
    Gui, FuzzBot:New, +AlwaysOnTop, FuzzingLocalBot v2.0
    Gui, FuzzBot:Color, 0x0d1117
    Gui, FuzzBot:Font, s10 cWhite, Segoe UI

    Gui, FuzzBot:Add, Text, x10 y10 w380 h30 Center c00ff41, FUZZINGLOCALBOT v2.0
    
    Gui, FuzzBot:Add, Text, x10 y50 w120 h20 c8892b0, Browser:
    Gui, FuzzBot:Add, DropDownList, x130 y48 w250 vNavSel, Chrome|Edge|Firefox|Brave|Opera

    Gui, FuzzBot:Add, Text, x10 y80 w120 h20 c8892b0, Domain:
    Gui, FuzzBot:Add, Edit, x130 y78 w250 vDominioInput, https://example.com

    Gui, FuzzBot:Add, Text, x10 y110 w120 h20 c8892b0, Wordlist:
    Gui, FuzzBot:Add, Edit, x130 y108 w200 vExtFileReadOnly ReadOnly, %ExtensionesFile%
    Gui, FuzzBot:Add, Button, x335 y108 w45 h20 gSeleccionarExtensiones, ...

    Gui, FuzzBot:Add, Text, x10 y140 w370 h20 c8892b0 vEstadoExtensiones, Status: Loading...

    Gui, FuzzBot:Add, Button, x10 y170 w370 h40 gIniciarFuzzing, START FUZZING

    Gui, FuzzBot:Add, Progress, x10 y220 w370 h20 c00ff41 vBarraProgreso, 0

    Gui, FuzzBot:Add, Text, x10 y250 w370 h30 Center cFF5555 vTextoEstado, Ready to start.

    Gui, FuzzBot:Show, w390 h300
    Gosub, CargarExtensiones
return

; ============================================================
; LOAD WORDLIST
; ============================================================
CargarExtensiones:
    global ExtensionesFile, Directorios, Extensiones, RutasCompletas, TotalRutas
    
    Directorios := []
    Extensiones := []
    RutasCompletas := []
    
    if !FileExist(ExtensionesFile) {
        GuiControl, FuzzBot:, EstadoExtensiones, Status: extensiones.txt not found
        return
    }
    
    GuiControl, FuzzBot:, EstadoExtensiones, Status: Loading...
    
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
    estado := "Status: " . Directorios.MaxIndex() . " dirs + " . Extensiones.MaxIndex() . " ext = " . TotalRutas . " combinations"
    GuiControl, FuzzBot:, EstadoExtensiones, %estado%
return

; ============================================================
; SELECT FILE
; ============================================================
SeleccionarExtensiones:
    FileSelectFile, archivo, 3, , Select wordlist, Text Documents (*.txt)
    if archivo {
        ExtensionesFile := archivo
        GuiControl, FuzzBot:, ExtFileReadOnly, %ExtensionesFile%
        Gosub, CargarExtensiones
    }
return

; ============================================================
; START FUZZING
; ============================================================
IniciarFuzzing:
    Gui, FuzzBot:Submit, NoHide

    Dominio := Trim(DominioInput)
    if !Dominio || Dominio == "https://example.com" {
        MsgBox, 16, Error, Enter a valid domain.
        return
    }
    
    if !InStr(Dominio, "http://") && !InStr(Dominio, "https://") {
        Dominio := "https://" . Dominio
    }

    if TotalRutas == 0 {
        MsgBox, 16, Error, No routes loaded.
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
        MsgBox, 16, Error, Select a browser.
        return
    }

    MsgBox, 4, FuzzingLocalBot v2.0, 
    (
    SCAN CONFIGURATION:
    
    Target: %Dominio%
    Routes: %TotalRutas%
    Browser: %NavSel%
    
    Python backend will do the real fuzzing.
    The CMD window will show the progress.
    
    DO YOU WANT TO CONTINUE?
    )
    IfMsgBox No
        return

    EjecutarFuzzing(Navegador, Dominio, RutasCompletas)
return

; ============================================================
; RUN FUZZING
; ============================================================
EjecutarFuzzing(navegador, dominio, rutas) {
    global TotalRutas, FuzzingActivo, PythonScript, ExtensionesFile
    
    FuzzingActivo := true
    GuiControl, FuzzBot:, TextoEstado, Starting Python backend...
    GuiControl, FuzzBot:, BarraProgreso, 0
    
    FormatTime, timestamp,, yyyy-MM-dd_HH-mm-ss
    resultadosFile := A_ScriptDir . "\output\scan_" . timestamp . ".txt"
    
    ; Create output folder if not exists
    FileCreateDir, %A_ScriptDir%\output
    
    ; Start Python backend in visible CMD window
    if FileExist(PythonScript) {
        GuiControl, FuzzBot:, TextoEstado, Python backend running. Check the CMD window.
        Run, cmd /k python "%PythonScript%" "%dominio%" "%ExtensionesFile%" "%resultadosFile%", , , PID
    } else {
        MsgBox, 16, Error, %PythonScript% not found.
        FuzzingActivo := false
        GuiControl, FuzzBot:, TextoEstado, Error: Script not found.
        return
    }
    
    ; Wait for Python process to finish
    Sleep, 2000
    GuiControl, FuzzBot:, TextoEstado, Scanning... Wait for the CMD window to finish.
    
    loop {
        Process, Exist, %PID%
        if (ErrorLevel == 0) {
            break
        }
        Sleep, 1000
    }
    
    FuzzingActivo := false
    GuiControl, FuzzBot:, BarraProgreso, 100
    GuiControl, FuzzBot:, TextoEstado, Scan completed.
    
    ; Search for generated reports
    reporteHTML := ""
    Loop, Files, %A_ScriptDir%\output\report_*.html
    {
        reporteHTML := A_LoopFileFullPath
    }
    
    if reporteHTML != "" {
        MsgBox, 4, FuzzingLocalBot v2.0,
        (
        SCAN COMPLETED!
        
        Results: %resultadosFile%
        Report: %reporteHTML%
        
        DO YOU WANT TO OPEN THE REPORT?
        )
        IfMsgBox Yes
        {
            Run, %reporteHTML%
        }
    } else {
        MsgBox, 64, FuzzingLocalBot v2.0,
        (
        SCAN COMPLETED!
        
        Results saved to: %resultadosFile%
        )
    }
    
    GuiControl, FuzzBot:, TextoEstado, Ready for another scan.
    GuiControl, FuzzBot:, BarraProgreso, 0
}

; ============================================================
; KEYBOARD SHORTCUT
; ============================================================
^!F::
    Gosub, FuzzBotMenu
return

; ============================================================
; CLOSE
; ============================================================
FuzzBotGuiClose:
    if FuzzingActivo {
        MsgBox, 4, FuzzingLocalBot, A scan is in progress. Do you want to exit?
        IfMsgBox No
            return
    }
    ExitApp
return

Gosub, FuzzBotMenu
