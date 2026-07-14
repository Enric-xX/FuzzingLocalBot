; ============================================================
; Bot de Fuzzing v3.0
; ============================================================

#NoEnv
#SingleInstance, Force
SetWorkingDir %A_ScriptDir%
SetBatchLines, -1

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

; ============================================================
; MENÚ PRINCIPAL
; ============================================================
FuzzBotMenu:
    Gui, FuzzBot:Destroy
    Gui, FuzzBot:New, +AlwaysOnTop, Bot de Fuzzing
    Gui, FuzzBot:Color, 0x0d1117
    Gui, FuzzBot:Font, s10 cWhite, Segoe UI

    Gui, FuzzBot:Add, Text, x10 y10 w380 h30 Center c00ff41, ⚡ Bot de Fuzzing ⚡
    
    Gui, FuzzBot:Add, Text, x10 y50 w120 h20 c8892b0, Navegador:
    Gui, FuzzBot:Add, DropDownList, x130 y48 w250 vNavSel gGuardarNavegador, Chrome|Edge|Firefox|Brave|Opera

    Gui, FuzzBot:Add, Text, x10 y80 w120 h20 c8892b0, Dominio:
    Gui, FuzzBot:Add, Edit, x130 y78 w250 vDominioInput gGuardarDominio, https://ejemplo.com

    Gui, FuzzBot:Add, Text, x10 y110 w120 h20 c8892b0, Extensiones:
    Gui, FuzzBot:Add, Edit, x130 y108 w200 vExtFileReadOnly ReadOnly, %ExtensionesFile%
    Gui, FuzzBot:Add, Button, x335 y108 w45 h20 gSeleccionarExtensiones, ...

    Gui, FuzzBot:Add, Text, x10 y140 w370 h20 c8892b0 vEstadoExtensiones, Estado: Cargando...

    Gui, FuzzBot:Add, Button, x10 y170 w370 h40 gIniciarFuzzing, 🚀 INICIAR FUZZING

    Gui, FuzzBot:Add, Text, x10 y220 w370 h30 Center cFF5555, ⚠️ NO TOQUES EL TECLADO MIENTRAS FUZZEA ⚠️

    Gui, FuzzBot:Show, w390 h270
    Gosub, CargarExtensiones
return

GuardarNavegador:
    GuiControlGet, NavSel
return

GuardarDominio:
    GuiControlGet, DominioInput
return

; ============================================================
; CARGAR EXTENSIONES
; ============================================================
CargarExtensiones:
    global ExtensionesFile, Directorios, Extensiones, RutasCompletas
    
    Directorios := []
    Extensiones := []
    RutasCompletas := []
    
    if !FileExist(ExtensionesFile) {
        GuiControl, FuzzBot:, EstadoExtensiones, Estado: Archivo no encontrado (se creará)
        Gosub, CrearArchivoExtensiones
        return
    }
    
    estado := "Estado: Cargando..."
    GuiControl, FuzzBot:, EstadoExtensiones, %estado%
    
    totalLineas := 0
    Loop, Read, %ExtensionesFile%
        totalLineas++
    
    lineaIndex := 0
    Loop, Read, %ExtensionesFile%
    {
        lineaIndex++
        linea := Trim(A_LoopReadLine)
        
        if (linea == "" || SubStr(linea, 1, 1) == "#")
            continue
            
        if InStr(linea, ".") && !InStr(linea, "/") && !InStr(linea, "\") {
            if !InStr(linea, "*") {
                Extensiones.Push(linea)
            }
        } else {
            Directorios.Push(linea)
        }
        
        if Mod(lineaIndex, 10) == 0 {
            GuiControl, FuzzBot:, EstadoExtensiones, Estado: Cargando %lineaIndex% de %totalLineas%...
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
    
    estado := "Estado: " . Directorios.MaxIndex() . " directorios + " . Extensiones.MaxIndex() . " extensiones = " . RutasCompletas.MaxIndex() . " combinaciones"
    GuiControl, FuzzBot:, EstadoExtensiones, %estado%
    
    RegistrarAccion("Cargadas " . RutasCompletas.MaxIndex() . " rutas desde extensiones.txt")
return

; ============================================================
; CREAR ARCHIVO DE EXTENSIONES
; ============================================================
CrearArchivoExtensiones:
    global ExtensionesFile
    
    FileDelete, %ExtensionesFile%
    FileAppend,
    (LTrim
        # Directorios y extensiones para fuzzing
        # Las líneas con # son comentarios
        # Las líneas vacías se ignoran
        
        # Directorios comunes
        admin
        login
        wp-admin
        wp-login.php
        dashboard
        cpanel
        webmail
        api
        v1
        v2
        v3
        docs
        help
        support
        about
        contact
        shop
        store
        cart
        checkout
        account
        profile
        settings
        config
        backup
        backups
        tmp
        temp
        cache
        logs
        debug
        tests
        testing
        stage
        staging
        dev
        development
        old
        new
        legacy
        
        # Archivos comunes
        index.php
        index.html
        index.htm
        default.php
        default.html
        home.php
        home.html
        main.php
        main.html
        wp-config.php
        wp-config.php.bak
        .env
        .git
        .gitignore
        .htaccess
        .htpasswd
        robots.txt
        sitemap.xml
        phpinfo.php
        info.php
        test.php
        test.html
        shell.php
        upload.php
        dump.sql
        backup.sql
        database.sql
        db.sql
        backup.zip
        
        # Extensiones
        .php
        .html
        .htm
        .txt
        .xml
        .json
        .yml
        .yaml
        .ini
        .conf
        .config
        .bak
        .backup
        .old
        .sql
        .db
        .log
        .tmp
        .css
        .js
        .zip
        .tar
        .gz
        .rar
        .7z
        
        # Directorios de CMS
        wp-admin/
        wp-includes/
        wp-content/
        wp-content/uploads/
        wp-content/plugins/
        wp-content/themes/
        wp-content/languages/
        wp-content/upgrade/
        wp-content/backup-db/
        wp-content/backup/
        wp-content/cache/
        
        # Directorios de frameworks
        vendor/
        node_modules/
        dist/
        build/
        src/
        lib/
        app/
        public/
        resources/
        routes/
        database/
        migrations/
        storage/
        bootstrap/
        config/
        lang/
        
        # Otros
        .aws/
        .ssh/
        .docker/
        .vscode/
        .github/
        Dockerfile
        docker-compose.yml
        Makefile
        composer.json
        composer.lock
        package.json
        package-lock.json
        yarn.lock
        Gemfile
        requirements.txt
        Pipfile
        setup.py
        go.mod
        go.sum
    ), %ExtensionesFile%
    
    Gosub, CargarExtensiones
return

; ============================================================
; SELECCIONAR ARCHIVO DE EXTENSIONES
; ============================================================
SeleccionarExtensiones:
    FileSelectFile, archivo, 3, , Selecciona el archivo de extensiones, Text Documents (*.txt)
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

    if RutasCompletas.MaxIndex() == 0 {
        MsgBox, No hay rutas cargadas. Revisa el archivo extensiones.txt
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
    MsgBox, 4, , ⚠️ FUZZING AVANZADO⚠️`n`nObjetivo: %Dominio%`nRutas a probar: %totalRutas%`nNavegador: %NavSel%`n`n🚀 NO TOQUES EL TECLADO.`n`n¿Quieres continuar?
    IfMsgBox No
        return

    RegistrarAccion("Iniciando fuzzing en " . Dominio . " con " . totalRutas . " rutas")
    
    EjecutarFuzzing(Navegador, Dominio, RutasCompletas)

return

; ============================================================
; EJECUCIÓN DEL FUZZING
; ============================================================
EjecutarFuzzing(navegador, dominio, rutas) {
    global
    
    Run, %navegador%
    Sleep, 3000
    
    Send, ^n
    Sleep, 1500
    
    Send, ^l
    Sleep, 500
    
    Send, %dominio%
    Sleep, 300
    Send, {Enter}
    Sleep, 3000
    
    total := rutas.MaxIndex()
    contador := 0
    
    FormatTime, timestamp,, yyyy-MM-dd_HH-mm-ss
    resultadosFile := A_ScriptDir . "\fuzz_results_" . timestamp . ".txt"
    FileAppend, Resultados de fuzzing en %dominio%`n`n, %resultadosFile%
    
    if FileExist(PythonScript) {
        Run, python "%PythonScript%" "%dominio%" "%ExtensionesFile%" "%resultadosFile%",, Hide
        RegistrarAccion("Backend Python iniciado")
    }
    
    for index, ruta in rutas {
        contador++
        
        Send, ^n
        Sleep, 1000
        
        Send, ^l
        Sleep, 400
        
        if InStr(ruta, ".") {
            url := dominio . "/" . ruta
        } else {
            url := dominio . "/" . ruta . "/"
        }
        
        for i, char in StrSplit(url) {
            Send, %char%
            Random, delay, 5, 15
            Sleep, %delay%
        }
        Sleep, 200
        
        Send, {Enter}
        Sleep, 2000
        
        Send, ^w
        Sleep, 500
        
        FileAppend, %contador%: %url%`n, %resultadosFile%
        
        if Mod(contador, 10) == 0 {
            porcentaje := Round(contador / total * 100)
            TrayTip, Bot, Progreso: %porcentaje%% (%contador%/%total%), 2
        }
        
        Random, delay, 800, 2500
        Sleep, %delay%
    }
    
    RegistrarAccion("Fuzzing completado. " . total . " rutas probadas.")
    MsgBox, ✅ FUZZING COMPLETADO!`n`nSe probaron %total% rutas en %dominio%.`n`nResultados guardados en:%resultadosFile%
}

; ============================================================
; REGISTRO DE ACCIONES
; ============================================================
RegistrarAccion(mensaje) {
    FormatTime, ahora,, yyyy-MM-dd HH:mm:ss
    FileAppend, %ahora% - %mensaje%`n, %A_ScriptDir%\bot.log
}

; ============================================================
; ATALLO DE TECLADO
; ============================================================
^!F::  ; Ctrl+Alt+F para abrir el menú
    Gosub, FuzzBotMenu
return

; ============================================================
; CIERRE
; ============================================================
FuzzBotGuiClose:
    ExitApp
return

Gosub, FuzzBotMenu
