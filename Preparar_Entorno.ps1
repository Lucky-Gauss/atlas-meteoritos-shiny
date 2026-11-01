$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno de Python.' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar todas las dependencias.' }
& '.\.venv\Scripts\python.exe' scripts\prepare_data.py
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron preparar los datos locales.' }
Write-Host 'Entorno listo. Ejecutá .\Iniciar_Atlas.ps1 para abrir el atlas.'
