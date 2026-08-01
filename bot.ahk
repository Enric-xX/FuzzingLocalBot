; ============================================================
; FuzzingLocalBot v3.0 - Windows GUI
; Minimalist · Professional · Auto-close
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
global PythonScript := A_ScriptDir . "\fuzzingbot.py"
global FuzzingActivo := false
global SelectedWordlist := ""
global WordlistDir := A_ScriptDir . "\dictionaries"
global RootWordlist := A_ScriptDir . "\extensiones.txt"
global ScanPID := 0
global AppVersion := "3.0.0"

; ============================================================
; COLORS
; ============================================================
global ColorBG := "FFFFFF"
global ColorPanel := "F8F9FA"
global ColorAccent := "2563EB"
global ColorText := "333333"
global ColorGray := "6B7280"
global ColorLightGray := "9CA3AF"
global ColorBorder := "E5E7EB"
global ColorGreen := "10B981"
global ColorRed := "EF4444"

; ============================================================
; STARTUP
; ============================================================
Gosub, BuildGUI
return

; ============================================================
; BUILD GUI
; ============================================================
BuildGUI:
    Gui, Main:Destroy
    Gui, Main:New, +AlwaysOnTop +LabelMain., FuzzingLocalBot v%AppVersion%
    Gui, Main:Color, %ColorBG%, %ColorPanel%
    Gui, Main:Font, s9 c%ColorText%, Segoe UI

    ; ============================================================
    ; HEADER
    ; ============================================================
    Gui, Main:Add, Picture, x20 y20 w32 h32, logo.png
    Gui, Main:Add, Text, x60 y24 w200 h24 c%ColorAccent% vTitleText, FUZZINGLOCALBOT
    Gui, Main:Font, s7 c%ColorLightGray%
    Gui, Main:Add, Text, x60 y48 w200 h16, Web Fuzzing Tool v%AppVersion%
    Gui, Main:Font, s9 c%ColorText%

    ; ============================================================
    ; TARGET SECTION
    ; ============================================================
    Gui, Main:Add, Text, x20 y85 w460 h1 c%ColorBorder% 0x7
    Gui, Main:Add, Text, x20 y95 w80 h20 c%ColorGray%, TARGET
    Gui, Main:Add, Edit, x110 y92 w370 h28 vDomainInput gDomainChanged, https://example.com

    ; ============================================================
    ; SCAN SPEED SECTION
    ; ============================================================
    Gui, Main:Add, Text, x20 y135 w460 h1 c%ColorBorder% 0x7
    Gui, Main:Add, Text, x20 y145 w80 h20 c%ColorGray%, SPEED
    Gui, Main:Add, Radio, x110 y143 w160 h20 c%ColorText% vSpeedSlow gSpeedChanged, Slow (10 threads)
    Gui, Main:Add, Radio, x280 y143 w160 h20 c%ColorText% Checked vSpeedNormal gSpeedChanged, Normal (50 threads)
    Gui, Main:Add, Radio, x110 y165 w160 h20 c%ColorText% vSpeedFast gSpeedChanged, Fast (100 threads)
    Gui, Main:Add, Radio, x280 y165 w80 h20 c%ColorText% vSpeedCustom gSpeedChanged, Custom
    Gui, Main:Add, Edit, x340 y163 w40 h20 vCustomThreads Limit3 Number gCustomChanged, 50
    Gui, Main:Add, UpDown, vThreadUpDown Range1-200, 50

    ; ============================================================
    ; WORDLIST SECTION
    ; ============================================================
    Gui, Main:Add, Text, x20 y200 w460 h1 c%ColorBorder% 0x7
    Gui, Main:Add, Text, x20 y210 w80 h20 c%ColorGray%, WORDLIST
    Gui, Main:Add, DropDownList, x110 y207 w280 vWordlistDropDown gWordlistChanged, Loading...
    Gui, Main:Add, Button, x395 y206 w85 h24 gRefreshWordlists, Refresh
    Gui, Main:Add, Text, x110 y232 w370 h16 c%ColorLightGray% vWordlistInfo, Select a wordlist

    ; ============================================================
    ; OPTIONS
    ; ============================================================
    Gui, Main:Add, Text, x20 y260 w460 h1 c%ColorBorder% 0x7
    Gui, Main:Add, Text, x20 y270 w80 h20 c%ColorGray%, OPTIONS
    Gui, Main:Add, Checkbox, x110 y270 w200 h20 c%ColorText% vStealthCheck gStealthChanged, Stealth mode (random delays)
    Gui, Main:Add, Checkbox, x110 y290 w200 h20 c%ColorText% vVPNCheck Checked, I am using a VPN

    ; ============================================================
    ; ACTION BUTTONS
    ; ============================================================
    Gui, Main:Add, Text, x20 y325 w460 h1 c%ColorBorder% 0x7
    
    Gui, Main:Add, Button, x20 y340 w180 h40 gStartScan vStartBtn, START SCAN
    Gui, Main:Add, Button, x210 y340 w180 h40 gStopScan vStopBtn Disabled, STOP SCAN
    Gui, Main:Add, Button, x400 y340 w80 h40 gOpenOutput, Output

    ; ============================================================
    ; PROGRESS
    ; ============================================================
    Gui, Main:Add, Progress, x20 y395 w460 h6 c%ColorAccent% vScanProgress, 0
    Gui, Main:Add, Text, x20 y408 w460 h20 Center c%ColorGray% vStatusText, Ready

    ; ============================================================
    ; FOOTER
    ; ============================================================
    Gui, Main:Font, s7 c%ColorLightGray%
    Gui, Main:Add, Text, x20 y435 w460 h16 Center, FuzzingLocalBot v%AppVersion% · Only for authorized pentesting · Use a VPN

    ; ============================================================
    ; SHOW
    ; ============================================================
    Gui, Main:Show, w500 h460
    Gosub, LoadWordlists
return

; ============================================================
; LOAD WORDLISTS
; ============================================================
LoadWordlists:
    GuiControl, Main:, WordlistDropDown, |
    
    If FileExist(RootWordlist) {
        GuiControl, Main:, WordlistDropDown, extensiones.txt (42,000 routes)
    }
    
    If FileExist(WordlistDir) {
        Loop, Files, %WordlistDir%\*.txt
        {
            GuiControl, Main:, WordlistDropDown, % A_LoopFileName
        }
    }
    
    GuiControl, Main:, StatusText, Ready · Wordlists loaded
return

; ============================================================
; WORDLIST CHANGED
; ============================================================
WordlistChanged:
    Gui, Main:Submit, NoHide
    SelectedWordlist := WordlistDropDown
    
    if (SelectedWordlist = "" || SelectedWordlist = "Loading...") {
        return
    }
    
    if InStr(SelectedWordlist, "extensiones.txt") {
        GuiControl, Main:, WordlistInfo, 42,000 routes · Full scan dictionary
        SelectedWordlist := RootWordlist
    } else {
        wordlistPath := WordlistDir . "\" . SelectedWordlist
        If FileExist(wordlistPath) {
            FileRead, content, %wordlistPath%
            lines := 0
            Loop, Parse, content, `n, `r
            {
                if (A_LoopField != "")
                    lines++
            }
            FileGetSize, size, %wordlistPath%, K
            GuiControl, Main:, WordlistInfo, %lines% routes · %size% KB
            SelectedWordlist := wordlistPath
        }
    }
return

; ============================================================
; DOMAIN CHANGED
; ============================================================
DomainChanged:
    Gui, Main:Submit, NoHide
    if (DomainInput != "" && DomainInput != "https://example.com") {
        GuiControl, Main:, StatusText, Target set · Ready to scan
    }
return

; ============================================================
; SPEED CHANGED
; ============================================================
SpeedChanged:
    Gui, Main:Submit, NoHide
    if (SpeedCustom) {
        GuiControl, Main:Enable, CustomThreads
    } else {
        GuiControl, Main:Disable, CustomThreads
    }
return

; ============================================================
; CUSTOM THREADS CHANGED
; ============================================================
CustomChanged:
    Gui, Main:Submit, NoHide
    if (CustomThreads < 1) {
        GuiControl, Main:, CustomThreads, 1
    }
    if (CustomThreads > 200) {
        GuiControl, Main:, CustomThreads, 200
    }
return

; ============================================================
; STEALTH CHANGED
; ============================================================
StealthChanged:
    ; Just update internal state
return

; ============================================================
; REFRESH WORDLISTS
; ============================================================
RefreshWordlists:
    Gosub, LoadWordlists
return

; ============================================================
; OPEN OUTPUT FOLDER
; ============================================================
OpenOutput:
    outputDir := A_ScriptDir . "\output"
    If !FileExist(outputDir) {
        FileCreateDir, %outputDir%
    }
    Run, explorer %outputDir%
return

; ============================================================
; START SCAN
; ============================================================
StartScan:
    Gui, Main:Submit, NoHide

    ; Validate domain
    Dominio := Trim(DomainInput)
    if (!Dominio || Dominio == "https://example.com") {
        MsgBox, 48, Validation Error, Please enter a valid target domain.
        return
    }
    
    if (!InStr(Dominio, "http://") && !InStr(Dominio, "https://")) {
        Dominio := "https://" . Dominio
    }

    ; Validate wordlist
    if (SelectedWordlist = "" || SelectedWordlist = "Loading...") {
        MsgBox, 48, Validation Error, Please select a wordlist.
        return
    }

    ; Validate VPN
    if (!VPNCheck) {
        MsgBox, 52, Security Warning, Please confirm you are using a VPN before scanning. Continue?
        IfMsgBox No
            return
    }

    ; Get threads
    threads := 50
    if (SpeedSlow) { threads := 10 }
    else if (SpeedFast) { threads := 100 }
    else if (SpeedCustom) { threads := CustomThreads }

    ; Confirmation
    wordlistName := SelectedWordlist
    StringGetPos, pos, wordlistName, \, R1
    if (pos >= 0) {
        StringTrimLeft, wordlistName, wordlistName, pos + 1
    }
    
    MsgBox, 4, FuzzingLocalBot v%AppVersion%,
    (
    SCAN CONFIGURATION
    
    Target: %Dominio%
    Wordlist: %wordlistName%
    Threads: %threads%
    Stealth: %StealthCheck%
    
    Start scan?
    )
    IfMsgBox No
        return

    ; Disable controls
    GuiControl, Main:Disable, StartBtn
    GuiControl, Main:Enable, StopBtn
    GuiControl, Main:Disable, DomainInput
    GuiControl, Main:Disable, WordlistDropDown
    
    RunScan(Dominio, SelectedWordlist, threads)
return

; ============================================================
; RUN SCAN
; ============================================================
RunScan(dominio, wordlist, threads) {
    global FuzzingActivo, PythonScript, ScanPID
    
    FuzzingActivo := true
    GuiControl, Main:, ScanProgress, 0
    GuiControl, Main:, StatusText, Scanning %dominio%...
    
    ; Create output folder
    FileCreateDir, %A_ScriptDir%\output
    
    ; Launch Python backend
    if FileExist(PythonScript) {
        Run, python "%PythonScript%" , , Hide, ScanPID
    } else {
        MsgBox, 16, Error, Python script not found: %PythonScript%
        ScanFinished()
        return
    }
    
    ; Monitor process
    SetTimer, CheckScan, 500
}

; ============================================================
; CHECK SCAN STATUS
; ============================================================
CheckScan:
    if (!FuzzingActivo) {
        SetTimer, CheckScan, Off
        return
    }
    
    Process, Exist, %ScanPID%
    if (ErrorLevel == 0) {
        SetTimer, CheckScan, Off
        ScanFinished()
    }
return

; ============================================================
; STOP SCAN
; ============================================================
StopScan:
    if (FuzzingActivo && ScanPID) {
        Process, Close, %ScanPID%
        ScanFinished()
    }
return

; ============================================================
; SCAN FINISHED
; ============================================================
ScanFinished() {
    global FuzzingActivo
    
    FuzzingActivo := false
    GuiControl, Main:, ScanProgress, 100
    GuiControl, Main:, StatusText, Scan completed
    
    ; Enable controls
    GuiControl, Main:Enable, StartBtn
    GuiControl, Main:Disable, StopBtn
    GuiControl, Main:Enable, DomainInput
    GuiControl, Main:Enable, WordlistDropDown
    
    ; Find report
    reporteHTML := ""
    Loop, Files, %A_ScriptDir%\output\report_*.html
    {
        reporteHTML := A_LoopFileFullPath
        break
    }
    
    if (reporteHTML != "") {
        MsgBox, 4, FuzzingLocalBot v%AppVersion%, 
        (
        SCAN COMPLETED
        
        Report: %reporteHTML%
        
        Open report?
        )
        IfMsgBox Yes
        {
            Run, %reporteHTML%
        }
    } else {
        MsgBox, 64, FuzzingLocalBot v%AppVersion%,
        (
        SCAN COMPLETED
        
        Results saved to output/
        )
    }
    
    GuiControl, Main:, ScanProgress, 0
    GuiControl, Main:, StatusText, Ready · Waiting for next scan
}

; ============================================================
; CLOSE HANDLER
; ============================================================
MainClose:
MainEscape:
    if (FuzzingActivo) {
        MsgBox, 4, FuzzingLocalBot, Scan in progress. Stop and exit?
        IfMsgBox No
            return
        Process, Close, %ScanPID%
    }
    ExitApp
return

; ============================================================
; KEYBOARD SHORTCUTS
; ============================================================
^Enter::
    Gosub, StartScan
return

^S::
    Gosub, StopScan
return

^O::
    Gosub, OpenOutput
return

; ============================================================
; INIT
; ============================================================
Gosub, BuildGUI
return
