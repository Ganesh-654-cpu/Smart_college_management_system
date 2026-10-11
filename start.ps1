$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = if (Test-Path '.venv\Scripts\python.exe') { '.venv\Scripts\python.exe' } else { 'python' }
if (-not (Test-Path 'db.sqlite3') -and $env:DB_ENGINE -ne 'mysql') {
    & $python manage.py migrate
}
Write-Host 'Smart Campus is starting at http://127.0.0.1:8000'
& $python manage.py runserver 127.0.0.1:8000
