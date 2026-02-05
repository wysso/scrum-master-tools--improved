@echo off
REM PowerShell Launcher for better compatibility

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& {
    # Move to script directory
    Set-Location -Path '%~dp0'
    
    # Clear screen
    Clear-Host
    
    Write-Host '=========================================' -ForegroundColor Cyan
    Write-Host '   ScrumMaster Tools 2.11.1 (SMT)' -ForegroundColor Cyan
    Write-Host '=========================================' -ForegroundColor Cyan
    Write-Host ''
    
    # Activate virtual environment
    Write-Host 'Activating virtual environment...' -ForegroundColor Yellow
    
    if (Test-Path 'venv\Scripts\Activate.ps1') {
        & 'venv\Scripts\Activate.ps1'
        
        Write-Host 'Starting ScrumMaster Tools...' -ForegroundColor Green
        Write-Host ''
        python smt.py
    } else {
        Write-Host ''
        Write-Host 'ERROR: Virtual environment not found!' -ForegroundColor Red
        Write-Host 'Please run: python -m venv venv' -ForegroundColor Yellow
        Write-Host ''
    }
    
    Write-Host ''
    Write-Host 'Program finished. Press any key to close...' -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}"