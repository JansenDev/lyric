# Instala el comando `lyric` en Windows para el usuario actual (sin administrador).
#   Desde una copia del repositorio:  powershell -ExecutionPolicy Bypass -File install.ps1
#   Directo desde GitHub:             irm https://raw.githubusercontent.com/USUARIO/lyric/main/install.ps1 | iex
# Mensajes sin tildes a proposito: PowerShell 5.1 lee los .ps1 sin BOM como ANSI.
$ErrorActionPreference = "Stop"

$Repo = "https://github.com/USUARIO/lyric"
$Destino = Join-Path $env:LOCALAPPDATA "lyric"
$Bin = Join-Path $env:USERPROFILE ".local\bin"

# Codigo a instalar: la carpeta del script si es una copia de lyric; si no, el zip de GitHub
$Proyecto = if ($PSScriptRoot) { Join-Path $PSScriptRoot "pyproject.toml" } else { "" }
if ($Proyecto -and (Test-Path $Proyecto) -and (Select-String -Quiet '^name = "lyric"' $Proyecto)) {
    $Origen = $PSScriptRoot
} else {
    $Origen = "$Repo/archive/refs/heads/main.zip"
}

if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }
else { throw "No se encontro Python. Instalalo desde https://www.python.org/downloads/" }

Write-Host "Creando entorno en $Destino ..."
& $Python -m venv --clear $Destino
if ($LASTEXITCODE) { throw "No se pudo crear el entorno virtual." }

Write-Host "Instalando lyric y pygame ..."
& "$Destino\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check $Origen
if ($LASTEXITCODE) { throw "Fallo la instalacion con pip." }

# El lyric.exe que genera pip apunta al Python del entorno, asi que funciona copiado
New-Item -ItemType Directory -Force $Bin | Out-Null
Copy-Item "$Destino\Scripts\lyric.exe" $Bin -Force
Write-Host "Listo: $Bin\lyric.exe"

$PathUsuario = [Environment]::GetEnvironmentVariable("Path", "User")
if (($PathUsuario -split ";") -notcontains $Bin) {
    [Environment]::SetEnvironmentVariable("Path", "$PathUsuario;$Bin", "User")
    Write-Host "Se anadio $Bin al PATH. Abre una consola nueva y prueba:  lyric --help"
} else {
    Write-Host "Prueba:  lyric --help"
}
