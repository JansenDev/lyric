# Instalación de lyric

Esta guía explica cómo instalar el comando `lyric` en Linux, macOS, WSL y Windows.

El instalador no necesita `sudo` ni permisos de administrador: crea un entorno de Python solo para lyric
(con [pygame](https://www.pygame.org) para el audio), así que no toca el Python de tu sistema.

## 1. Requisitos

- **Python 3.8 o superior**
- **Conexión a internet**: se descargan lyric y pygame

Comprueba si tienes Python:

| Sistema | Comprobar | Si no lo tienes |
|---------|-----------|-----------------|
| Ubuntu, Debian y WSL | `python3 --version` | `sudo apt install python3 python3-venv curl` |
| macOS | `python3 --version` | Descárgalo de [python.org](https://www.python.org/downloads/) o usa `brew install python` |
| Windows | `py --version` | Descárgalo de [python.org](https://www.python.org/downloads/) (incluye el lanzador `py`) |

En Ubuntu, Debian y WSL también hace falta el paquete `python3-venv`: sin él, el instalador no puede crear el entorno.

## 2. Instalación rápida (recomendada)

### Linux, macOS y WSL

Abre una terminal y ejecuta:

```sh
curl -fsSL https://raw.githubusercontent.com/JansenDev/lyric/main/install.sh | sh
```

Si no tienes `curl`, puedes usar `wget`:

```sh
wget -qO- https://raw.githubusercontent.com/JansenDev/lyric/main/install.sh | sh
```

### Windows

Abre **PowerShell** (no CMD) y ejecuta:

```powershell
irm https://raw.githubusercontent.com/JansenDev/lyric/main/install.ps1 | iex
```

Una vez instalado, `lyric` funciona en PowerShell, CMD y Windows Terminal.

### Qué verás

```
Creando entorno en ...
Instalando lyric y pygame ...
Listo: .../lyric
Prueba:  lyric --help
```

## 3. Instalación desde el código fuente

Útil si quieres modificar lyric: el instalador usa el código de la carpeta clonada, así que instala también tus cambios.

```sh
git clone https://github.com/JansenDev/lyric.git
cd lyric
```

Y después, según tu sistema:

```sh
./install.sh                                            # Linux, macOS y WSL
powershell -ExecutionPolicy Bypass -File install.ps1    # Windows
```

## 4. Comprobar que funciona

Abre una **consola nueva** (para que lea el PATH actualizado) y ejecuta:

```sh
lyric --help
```

Para probarlo con la letra de ejemplo, descárgala y ábrela:

```sh
# Linux, macOS y WSL
curl -fsSLO https://raw.githubusercontent.com/JansenDev/lyric/main/ejemplo.lrc
lyric ejemplo.lrc
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/JansenDev/lyric/main/ejemplo.lrc -OutFile ejemplo.lrc
lyric ejemplo.lrc
```

O descarga directamente la letra de una canción: `lyric --buscar "Artista" "Canción"`.

## 5. Dónde se instala

| | Linux, macOS y WSL | Windows |
|-|--------------------|---------|
| Entorno de Python | `~/.local/share/lyric` | `%LOCALAPPDATA%\lyric` |
| Comando | `~/.local/bin/lyric` | `%USERPROFILE%\.local\bin\lyric.exe` |

En Windows, el instalador añade `%USERPROFILE%\.local\bin` al PATH de tu usuario si no estaba.
En Linux y macOS, si `~/.local/bin` no está en tu PATH, el instalador te muestra la línea que debes añadir.

## 6. Actualizar

Vuelve a ejecutar el mismo comando de instalación: recrea el entorno con la última versión.

## 7. Desinstalar

**Linux, macOS y WSL**

```sh
rm -rf ~/.local/share/lyric ~/.local/bin/lyric
```

**Windows (PowerShell)**

```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\lyric", "$env:USERPROFILE\.local\bin\lyric.exe"
```

## 8. Problemas frecuentes

**`lyric: command not found` o «lyric no se reconoce como un comando»**
Cierra la consola y abre una nueva: el PATH solo se lee al abrirla. Si sigue sin funcionar:
- Linux y macOS: añade `export PATH="$HOME/.local/bin:$PATH"` al final de tu `~/.bashrc` o `~/.zshrc`.
- Windows: comprueba que `%USERPROFILE%\.local\bin` está en el PATH de tu usuario.

**«No se pudo crear el entorno virtual»** (Ubuntu, Debian y WSL)
Instala el paquete que falta con `sudo apt install python3-venv` y repite la instalación.

**`error: externally-managed-environment`**
Aparece si instalas con `pip install` directamente en el Python del sistema. Usa el instalador de esta guía,
que crea su propio entorno y evita ese error.

**Windows: «No se encontró Python»**
Instala Python desde [python.org](https://www.python.org/downloads/). Si al escribir `python` se abre
Microsoft Store, es un acceso directo de Windows y no un Python real: instálalo desde python.org igualmente.

**Windows: «la ejecución de scripts está deshabilitada en este sistema»**
Sucede al ejecutar `.\install.ps1` directamente. Usa `powershell -ExecutionPolicy Bypass -File install.ps1`.
La instalación rápida (`irm ... | iex`) no tiene este problema.

**No se oye el audio en WSL**
WSL necesita WSLg para el sonido (Windows 11, o Windows 10 con WSL actualizado mediante `wsl --update`).
Como alternativa, instala lyric en Windows y úsalo desde PowerShell.

**Falla la instalación de pygame**
pygame publica paquetes listos para las versiones de Python más usadas. Si tu Python es muy reciente,
pip puede intentar compilarlo y fallar: prueba con una versión de Python anterior.
