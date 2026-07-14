#NoEnv
#SingleInstance, Force
SetWorkingDir %A_ScriptDir%
SetBatchLines, -1

global ExtensionesFile := A_ScriptDir . "\extensiones.txt"
global Dominio := ""
global Navegador := ""
global PythonScript := A_ScriptDir . "\fuzz_backend.py"
global Directorios := []
global Extensiones := []
global RutasCompletas := []
global Velocidad := "Rápida"

FuzzBotMenu:
    Gui, FuzzBot:Destroy
    Gui, FuzzBot:New, +AlwaysOnTop, Fuzzing Bot
    Gui, FuzzBot:Color, 0x0d1117
    Gui, FuzzBot:Font, s10 cWhite, Segoe UI

    Gui, FuzzBot:Add, Text, x10 y10 w380 h30 Center c00ff41, ⚡ Fuzzing Bot ⚡
    
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

CargarExtensiones:
    global ExtensionesFile, Directorios, Extensiones, RutasCompletas
    
    Directorios := []
    Extensiones := []
    RutasCompletas := []
    
    if !FileExist(ExtensionesFile) {
        GuiControl, FuzzBot:, EstadoExtensiones, Estado: extensiones.txt no encontrado
        return
    }
    
    GuiControl, FuzzBot:, EstadoExtensiones, Estado: Cargando 18.000 líneas...
    
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
    
    estado := "Estado: " . Directorios.MaxIndex() . " directorios + " . Extensiones.MaxIndex() . " ext = " . RutasCompletas.MaxIndex() . " combinaciones"
    GuiControl, FuzzBot:, EstadoExtensiones, %estado%
return

SeleccionarExtensiones:
    FileSelectFile, archivo, 3, , Selecciona extensiones, Text Documents (*.txt)
    if archivo {
        ExtensionesFile := archivo
        GuiControl, FuzzBot:, ExtFileReadOnly, %ExtensionesFile%
        Gosub, CargarExtensiones
    }
return

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

    if RutasCompletas.MaxIndex() == 0 {
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

    totalRutas := RutasCompletas.MaxIndex()
    MsgBox, 4, , ⚠️ FUZZING ⚠️`n`nObjetivo: %Dominio%`nRutas: %totalRutas%`nNavegador: %NavSel%`n`n🚀 NO TOQUES EL TECLADO.
    IfMsgBox No
        return

    EjecutarFuzzing(Navegador, Dominio, RutasCompletas)
return

EjecutarFuzzing(navegador, dominio, rutas) {
    global
    
    ; Abrir navegador
    Run, %navegador%
    Sleep, 2000
    
    ; Nueva pestaña y cargar dominio
    Send, ^n
    Sleep, 500
    Send, ^l
    Sleep, 300
    Send, %dominio%
    Sleep, 200
    Send, {Enter}
    Sleep, 1500
    
    total := rutas.MaxIndex()
    contador := 0
    
    FormatTime, timestamp,, yyyy-MM-dd_HH-mm-ss
    resultadosFile := A_ScriptDir . "\fuzz_results_" . timestamp . ".txt"
    FileAppend, Resultados fuzzing en %dominio%`n`n, %resultadosFile%
    
    ; Iniciar Python backend (rápido, en paralelo)
    if FileExist(PythonScript) {
        Run, python "%PythonScript%" "%dominio%" "%ExtensionesFile%" "%resultadosFile%",, Hide
    }
    
    ; Velocidad máxima
    SetKeyDelay, 0, 0
    
    for index, ruta in rutas {
        contador++
        
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
        
        ; Escribir URL (muy rápido)
        SendInput, %url%
        Sleep, 50
        Send, {Enter}
        Sleep, 300
        
        ; Cerrar pestaña
        Send, ^w
        Sleep, 30
        
        ; Guardar registro
        if Mod(contador, 50) == 0 {
            FileAppend, %contador%: %url%`n, %resultadosFile%
            porcentaje := Round(contador / total * 100)
            TrayTip, Fuzzing, %porcentaje%% (%contador%/%total%), 1
        }
    }
    
    MsgBox, ✅ COMPLETADO!`n`n%total% rutas probadas en %dominio%.`nResultados: %resultadosFile%
}
