; ============================================================
; FuzzingLocalBot v3.1 - Windows GUI
; Minimal · Light/Dark Mode · Professional · Expanded
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
global AppVersion := "3.1.0"
global DarkMode := false
global CveHunterMode := false
global StealthMode := false

; ============================================================
; THEME
; ============================================================
SetTheme(mode) {
    global
    if (mode) {
        ColorBG := "1E1E1E"
        ColorPanel := "252525"
        ColorAccent := "4A90D9"
        ColorText := "FFFFFF"
        ColorGray := "AAAAAA"
        ColorLightGray := "888888"
        ColorBorder := "333333"
        ColorBtn := "333333"
        ColorProgress := "333333"
        ColorRed := "FF4444"
        ColorGreen := "44FF44"
    } else {
        ColorBG := "FFFFFF"
        ColorPanel := "FAFAFA"
        ColorAccent := "1A1A1A"
        ColorText := "1A1A1A"
        ColorGray := "666666"
        ColorLightGray := "999999"
        ColorBorder := "E5E5E5"
        ColorBtn := "F0F0F0"
        ColorProgress := "F0F0F0"
        ColorRed := "CC0000"
        ColorGreen := "00AA00"
    }
    Gosub, BuildGUI
}

; ============================================================
; BUILD GUI
; ============================================================
BuildGUI:
    Gui, Main:Destroy
    Gui, Main:New, -Caption +Border, FuzzingLocalBot
    Gui, Main:Color, %ColorBG%, %ColorPanel%
    Gui, Main:Font, s9 c%ColorText%, Segoe UI

    ; Title Bar
    Gui, Main:Add, Text, x15 y12 w420 h20 c%ColorText%, FUZZINGLOCALBOT v%AppVersion%
    Gui, Main:Add, Text, x440 y12 w20 h20 gToggleTheme c%ColorGray%, ☀
    Gui, Main:Add, Text, x465 y12 w20 h20 gMainClose c%ColorGray%, ✕

    ; Separator
    Gui, Main:Add, Text, x0 y38 w500 h1 c%ColorBorder%

    ; === TARGET ===
    Gui, Main:Add, Text, x20 y50 w460 h14 c%ColorGray%, TARGET URL
    Gui, Main:Add, Edit, x20 y67 w460 h32 vDomainInput c%ColorText% Background%ColorPanel%, https://example.com

    ; === SCAN MODE ===
    Gui, Main:Add, Text, x20 y108 w220 h14 c%ColorGray%, SCAN MODE
    Gui, Main:Add, Text, x250 y108 w230 h14 c%ColorGray%, STEALTH

    Gui, Main:Add, Radio, x20 y125 w110 h20 c%ColorText% Checked vModeNormal, Normal
    Gui, Main:Add, Radio, x140 y125 w110 h20 c%ColorText% vModeCveHunter, CVE Hunter

    Gui, Main:Add, Checkbox, x250 y125 w230 h20 c%ColorText% vStealthCheck gToggleStealth, Enable Stealth Mode
    Gui, Main:Add, Text, x250 y148 w230 h28 c%ColorLightGray% vStealthInfo, Random delays · User-Agent rotation · WAF evasion

    ; === SPEED ===
    Gui, Main:Add, Text, x20 y170 w460 h14 c%ColorGray%, SPEED
    Gui, Main:Add, Radio, x20 y187 w90 h20 c%ColorText% vSpeedSlow, Slow
    Gui, Main:Add, Radio, x115 y187 w90 h20 c%ColorText% Checked vSpeedNormal, Normal
    Gui, Main:Add, Radio, x210 y187 w80 h20 c%ColorText% vSpeedFast, Fast
    Gui, Main:Add, Radio, x295 y187 w60 h20 c%ColorText% vSpeedCustom, Custom
    Gui, Main:Add, Edit, x355 y185 w50 h22 vCustomThreads Limit3 Number c%ColorText% Background%ColorPanel%, 50
    Gui, Main:Add, Text, x410 y188 w70 h14 c%ColorLightGray%, threads

    ; === WORDLIST ===
    Gui, Main:Add, Text, x20 y218 w460 h14 c%ColorGray%, WORDLIST
    Gui, Main:Add, DropDownList, x20 y235 w390 vWordlistDropDown gWordlistChanged c%ColorText% Background%ColorPanel%, Loading...
    Gui, Main:Add, Text, x415 y238 w65 h20 gRefreshWordlists c%ColorAccent%, ↻ Refresh
    Gui, Main:Add, Text, x20 y261 w460 h14 c%ColorLightGray% vWordlistInfo, Select a wordlist

    ; === OPTIONS ===
    Gui, Main:Add, Text, x20 y285 w220 h14 c%ColorGray%, OPTIONS
    Gui, Main:Add, Text, x250 y285 w230 h14 c%ColorGray%, OUTPUT FORMAT

    Gui, Main:Add, Checkbox, x20 y302 w220 h20 c%ColorText% vVPNCheck Checked, I am using a VPN
    Gui, Main:Add, Checkbox, x20 y322 w220 h20 c%ColorText% vAutoOpenCheck Checked, Auto-open report when done

    Gui, Main:Add, Checkbox, x250 y302 w110 h20 c%ColorText% Checked vMdCheck, Markdown
    Gui, Main:Add, Checkbox, x250 y322 w110 h20 c%ColorText% Checked vHtmlCheck, HTML
    Gui, Main:Add, Checkbox, x365 y302 w110 h20 c%ColorText% Checked vJsonCheck, JSON

    ; === BUTTONS ===
    Gui, Main:Add, Progress, x20 y355 w460 h2 c%ColorBorder% Background%ColorBorder%, 100

    Gui, Main:Add, Button, x20 y370 w150 h40 gStartScan vStartBtn c%ColorBG% Background%ColorAccent%, START SCAN
    Gui, Main:Add, Button, x180 y370 w100 h40 gStopScan vStopBtn Disabled c%ColorText% Background%ColorBtn%, STOP
    Gui, Main:Add, Button, x290 y370 w90 h40 gPauseScan vPauseBtn Disabled c%ColorText% Background%ColorBtn%, PAUSE
    Gui, Main:Add, Button, x390 y370 w90 h40 gOpenOutput c%ColorText% Background%ColorBtn%, Output

    ; === PROGRESS ===
    Gui, Main:Add, Progress, x20 y422 w460 h4 c%ColorAccent% Background%ColorProgress% vScanProgress, 0
    Gui, Main:Add, Text, x20 y432 w230 h16 c%ColorGray% vStatusText, Ready
    Gui, Main:Add, Text, x250 y432 w230 h16 Right c%ColorLightGray% vStatsText,

    ; === FOOTER ===
    Gui, Main:Font, s7 c%ColorLightGray%
    Gui, Main:Add, Text, x20 y455 w230 h14, Only for authorized pentesting
    Gui, Main:Add, Text, x250 y455 w230 h14 Right, github.com/Enric-xX

    Gui, Main:Show, w500 h478
    Gosub, LoadWordlists
return

; ============================================================
; TOGGLE THEME
; ============================================================
ToggleTheme:
    DarkMode := !DarkMode
    SetTheme(DarkMode)
return

; ============================================================
; TOGGLE STEALTH
; ============================================================
ToggleStealth:
    Gui, Main:Submit, NoHide
    if (StealthCheck) {
        GuiControl, Main:, StealthInfo, Random delays · User-Agent rotation · WAF evasion
    } else {
        GuiControl, Main:, StealthInfo,
    }
return

; ============================================================
; TOGGLE CVE HUNTER
; ============================================================
ToggleCveHunter:
    Gui, Main:Submit, NoHide
    CveHunterMode := ModeCveHunter
return

; ============================================================
; LOAD WORDLISTS
; ============================================================
LoadWordlists:
    GuiControl, Main:, WordlistDropDown, |
    If FileExist(RootWordlist)
        GuiControl, Main:, WordlistDropDown, extensiones.txt (42k routes)
    If FileExist(WordlistDir)
    {
        Loop, Files, %WordlistDir%\*.txt
            GuiControl, Main:, WordlistDropDown, % A_LoopFileName
    }
    GuiControl, Main:, StatusText, Ready · Wordlists loaded
return

; ============================================================
; WORDLIST CHANGED
; ============================================================
WordlistChanged:
    Gui, Main:Submit, NoHide
    SelectedWordlist := WordlistDropDown
    if (SelectedWordlist = "" || SelectedWordlist = "Loading...")
        return
    if InStr(SelectedWordlist, "extensiones.txt") {
        GuiControl, Main:, WordlistInfo, 42,000 routes · Full scan
        SelectedWordlist := RootWordlist
    } else {
        wordlistPath := WordlistDir . "\" . SelectedWordlist
        If FileExist(wordlistPath) {
            FileRead, content, %wordlistPath%
            lines := 0
            Loop, Parse, content, `n, `r
                if (A_LoopField != "")
                    lines++
            GuiControl, Main:, WordlistInfo, %lines% routes
            SelectedWordlist := wordlistPath
        }
    }
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
    If !FileExist(outputDir)
        FileCreateDir, %outputDir%
    Run, explorer %outputDir%
return

; ============================================================
; START SCAN
; ============================================================
StartScan:
    Gui, Main:Submit, NoHide
    Dominio := Trim(DomainInput)
    if (!Dominio || Dominio == "https://example.com") {
        MsgBox, 48, Error, Please enter a valid target domain.
        return
    }
    if (!InStr(Dominio, "http://") && !InStr(Dominio, "https://"))
        Dominio := "https://" . Dominio
    if (SelectedWordlist = "" || SelectedWordlist = "Loading...") {
        MsgBox, 48, Error, Please select a wordlist.
        return
    }
    if (!VPNCheck) {
        MsgBox, 52, Security, Please confirm you are using a VPN.
        return
    }
    threads := SpeedSlow ? 10 : SpeedFast ? 100 : SpeedCustom ? CustomThreads : 50
    StealthMode := StealthCheck
    
    GuiControl, Main:Disable, StartBtn
    GuiControl, Main:Enable, StopBtn
    GuiControl, Main:Enable, PauseBtn
    GuiControl, Main:Disable, DomainInput
    GuiControl, Main:Disable, WordlistDropDown
    GuiControl, Main:, StatsText, 0 / 0 found
    
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
    FileCreateDir, %A_ScriptDir%\output
    if FileExist(PythonScript)
        Run, python "%PythonScript%", , Hide, ScanPID
    else {
        MsgBox, 16, Error, Python script not found.
        ScanFinished()
        return
    }
    SetTimer, CheckScan, 500
}

; ============================================================
; CHECK SCAN
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
; PAUSE SCAN
; ============================================================
PauseScan:
    if (FuzzingActivo && ScanPID) {
        Process, Suspend, %ScanPID%
        GuiControl, Main:, StatusText, Paused
        GuiControl, Main:, PauseBtn, RESUME
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
    GuiControl, Main:, PauseBtn, PAUSE
    
    GuiControl, Main:Enable, StartBtn
    GuiControl, Main:Disable, StopBtn
    GuiControl, Main:Disable, PauseBtn
    GuiControl, Main:Enable, DomainInput
    GuiControl, Main:Enable, WordlistDropDown
    
    if (AutoOpenCheck) {
        reporteHTML := ""
        Loop, Files, %A_ScriptDir%\output\report_*.html {
            reporteHTML := A_LoopFileFullPath
            break
        }
        if (reporteHTML != "")
            Run, %reporteHTML%
    } else {
        MsgBox, 64, FuzzingLocalBot, Scan complete. Results in output/
    }
    
    GuiControl, Main:, ScanProgress, 0
    GuiControl, Main:, StatsText,
    GuiControl, Main:, StatusText, Ready
}

; ============================================================
; CLOSE
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
; INIT
; ============================================================
Gosub, BuildGUI
return
