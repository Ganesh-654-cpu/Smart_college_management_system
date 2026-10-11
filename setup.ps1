$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
}
& '.venv\Scripts\python.exe' -m pip install --upgrade pip
& '.venv\Scripts\python.exe' -m pip install -r requirements.txt
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
& '.venv\Scripts\python.exe' manage.py makemigrations campus
& '.venv\Scripts\python.exe' manage.py migrate
Write-Host ''
Write-Host 'Setup complete. Create an admin with: .venv\Scripts\python.exe manage.py createsuperuser'
Write-Host 'Optional demo data: .venv\Scripts\python.exe manage.py seed_demo'
Write-Host 'Then start the site with: .\start.ps1'
