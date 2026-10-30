$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
& $python -m poc3 --entrada '.\dados_ficticios' --saida '.\saida_demo'
if ($LASTEXITCODE -ne 0) { throw 'Falha na POC 03' }
Write-Host "Abra o arquivo .\saida_demo\RELATORIO_VISUAL.html no navegador" -ForegroundColor Green
