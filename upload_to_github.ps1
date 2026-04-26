$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/Vitali22/snake-python.git"
$git = "git"

Set-Location $PSScriptRoot

Write-Host "Preparando el repositorio local..."

& $git config --global --add safe.directory ($PSScriptRoot -replace "\\", "/")

if (-not (Test-Path ".git")) {
    & $git init
}

& $git add snake.py README.md .gitignore

$hasCommit = $true
& $git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) {
    $hasCommit = $false
}

$hasChanges = $false
& $git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    $hasChanges = $true
}

if ($hasChanges -or -not $hasCommit) {
    & $git commit -m "Crear juego de Snake"
}
else {
    Write-Host "No hay cambios nuevos para guardar."
}

& $git branch -M master

$remoteExists = $true
& $git remote get-url origin *> $null
if ($LASTEXITCODE -ne 0) {
    $remoteExists = $false
}

if ($remoteExists) {
    & $git remote set-url origin $repoUrl
}
else {
    & $git remote add origin $repoUrl
}

Write-Host "Subiendo a GitHub..."
& $git push -u origin master

Write-Host "Listo. Revisa tu repositorio en: $repoUrl"
