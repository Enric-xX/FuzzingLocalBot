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

; ============================================================
; BUILD GUI
; ============================================================
BuildGUI:
    Gui, Main:Destroy
    Gui, Main:New, +AlwaysOnTop +LabelMain., FuzzingLocalBot v%AppVersion%
    Gui, Main:Color, %ColorBG%, %ColorPanel%
    Gui, Main:Font, s9 c%ColorText%, Segoe UI

    ; HEADER
    Gui, Main:Add, Text, x20 y20 w460 h30 Center c%ColorAccent%, FUZZINGLOCALBOT v%AppVersion%

    ; TARGET
    Gui, Main:Add, Text, x20 y60 w80 h20 c%ColorGray%, TARGET
    Gui, Main:Add, Edit, x110 y57 w370 h28 vDomainInput, https://example.com

    ; SPEED
    Gui, Main:Add, Text, x20 y100 w80 h20 c%ColorGray%, SPEED
    Gui, Main:Add, Radio, x110 y98 w160 h20 c%ColorText% vSpeedSlow, Slow (10 threads)
    Gui, Main:Add, Radio, x280 y98 w160 h20 c%ColorText% Checked vSpeedNormal, Normal (50 threads)
    Gui, Main:Add, Radio, x110 y118 w160 h20 c%ColorText% vSpeedFast, Fast (100 threads)
    Gui, Main:Add, Radio, x280 y118 w80 h20 c%ColorText% vSpeedCustom, Custom
    Gui, Main:Add, Edit, x340 y116 w40 h20 vCustomThreads Limit3 Number, 50

    ; WORDLIST
    Gui, Main:Add, Text, x20 y150 w80 h20 c%ColorGray%, WORDLIST
    Gui, Main:Add, DropDownList, x110 y147 w280 vWordlistDropDown gWordlistChanged, Loading...
    Gui, Main:Add, Button, x395 y146 w85 h24 gRefreshWordlists, Refresh
    Gui, Main:Add, Text, x110 y172 w370 h16 c%ColorLightGray% vWordlistInfo, Select a wordlist

    ; OPTIONS
    Gui, Main:Add, Text, x20 y200 w80 h20 c%ColorGray%, OPTIONS
    Gui, Main:Add, Checkbox, x110 y200 w200 h20 c%ColorText% vVPNCheck Checked, I am using a VPN

    ; BUTTONS
    Gui, Main:Add, Button, x20 y240 w180 h40 gStartScan vStartBtn, START SCAN
    Gui, Main:Add, Button, x210 y240 w180 h40 gStopScan vStopBtn Disabled, STOP SCAN
    Gui, Main:Add, Button, x400 y240 w80 h40 gOpenOutput, Output

    ; PROGRESS
    Gui, Main:Add, Progress, x20 y295 w460 h6 c%ColorAccent% vScanProgress, 0
    Gui, Main:Add, Text, x20 y308 w460 h20 Center c%ColorGray% vStatusText, Ready

    ; FOOTER
    Gui, Main:Font, s7 c%ColorLightGray%
    Gui, Main:Add, Text, x20 y335 w460 h16 Center, Only for authorized pentesting · Use a VPN

    Gui, Main:Show, w500 h365
    Gosub, LoadWordlists
return

; ============================================================
; LOAD WORDLISTS
; ============================================================
LoadWordlists:
    GuiControl, Main:, WordlistDropDown, |
    
    If FileExist(RootWordlist)
        GuiControl, Main:, WordlistDropDown, extensiones.txt (42,000 routes)
    
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
    
    if InStr(SelectedWordlist, "extensiones.txt")
    {
        GuiControl, Main:, WordlistInfo, 42,000 routes · Full scan dictionary
        SelectedWordlist := RootWordlist
    }
    else
    {
        wordlistPath := WordlistDir . "\" . SelectedWordlist
        If FileExist(wordlistPath)
        {
            FileRead, content, %wordlistPath%
            lines := 0
            Loop, Parse, content, `n, `r
            {
                if (A_LoopField != "")
                    lines++
            }
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
    if (!Dominio || Dominio == "https://example.com")
    {
        MsgBox, 48, Error, Please enter a valid target domain.
        return
    }
    
    if (!InStr(Dominio, "http://") && !InStr(Dominio, "https://"))
        Dominio := "https://" . Dominio

    if (SelectedWordlist = "" || SelectedWordlist = "Loading...")
    {
        MsgBox, 48, Error, Please select a wordlist.
        return
    }

    if (!VPNCheck)
    {
        MsgBox, 52, Security, Please confirm you are using a VPN.
        return
    }

    threads := 50
    if (SpeedSlow)
        threads := 10
    else if (SpeedFast)
        threads := 100
    else if (SpeedCustom)
        threads := CustomThreads

    GuiControl, Main:Disable, StartBtn
    GuiControl, Main:Enable, StopBtn
    GuiControl, Main:Disable, DomainInput
    GuiControl, Main:Disable, WordlistDropDown
    
    RunScan(Dominio, SelectedWordlist, threads)
return

; ============================================================
; RUN SCAN
; ============================================================
RunScan(dominio, wordlist, threads)
{
    global FuzzingActivo, PythonScript, ScanPID
    
    FuzzingActivo := true
    GuiControl, Main:, ScanProgress, 0
    GuiControl, Main:, StatusText, Scanning %dominio%...
    
    FileCreateDir, %A_ScriptDir%\output
    
    if FileExist(PythonScript)
        Run, python "%PythonScript%", , Hide, ScanPID
    else
    {
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
    if (!FuzzingActivo)
    {
        SetTimer, CheckScan, Off
        return
    }
    
    Process, Exist, %ScanPID%
    if (ErrorLevel == 0)
    {
        SetTimer, CheckScan, Off
        ScanFinished()
    }
return

; ============================================================
; STOP SCAN
; ============================================================
StopScan:
    if (FuzzingActivo && ScanPID)
    {
        Process, Close, %ScanPID%
        ScanFinished()
    }
return

; ============================================================
; SCAN FINISHED
; ============================================================
ScanFinished()
{
    global FuzzingActivo
    
    FuzzingActivo := false
    GuiControl, Main:, ScanProgress, 100
    GuiControl, Main:, StatusText, Scan completed
    
    GuiControl, Main:Enable, StartBtn
    GuiControl, Main:Disable, StopBtn
    GuiControl, Main:Enable, DomainInput
    GuiControl, Main:Enable, WordlistDropDown
    
    reporteHTML := ""
    Loop, Files, %A_ScriptDir%\output\report_*.html
    {
        reporteHTML := A_LoopFileFullPath
        break
    }
    
    if (reporteHTML != "")
    {
        MsgBox, 4, FuzzingLocalBot, Scan complete. Open report?
        IfMsgBox Yes
            Run, %reporteHTML%
    }
    else
        MsgBox, 64, FuzzingLocalBot, Scan complete. Results in output/
    
    GuiControl, Main:, ScanProgress, 0
    GuiControl, Main:, StatusText, Ready
}

; ============================================================
; CLOSE
; ============================================================
MainClose:
MainEscape:
    if (FuzzingActivo)
    {
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
