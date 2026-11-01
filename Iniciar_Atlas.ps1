param([int]$Puerto = 8765)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & '.\Preparar_Entorno.ps1'
}
if (-not (Test-Path -LiteralPath 'data\processed\meteorites.csv')) {
    & '.\.venv\Scripts\python.exe' scripts\prepare_data.py
}
Write-Host "Atlas de meteoritos: http://127.0.0.1:$Puerto"
Write-Host 'Abrí esa dirección en el navegador. Para detenerlo, presioná Ctrl+C.'
& '.\.venv\Scripts\python.exe' -m shiny run --host 127.0.0.1 --port $Puerto app.py
