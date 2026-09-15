# lyric

Letras sincronizadas en la consola, estilo Spotify. Lee archivos [LRC](https://es.wikipedia.org/wiki/LRC_(formato_de_archivo)),
los descarga de [LRCLIB](https://lrclib.net) y puede reproducir la canción a la vez.

```
♫ lyric — Canción de ejemplo

    Esta es una letra de ejemplo
  ▶ para probar lyric en tu consola
    cada línea sale justo a su tiempo
```

## Instalación

Necesitas Python 3.8 o superior. El instalador crea un entorno propio (con pygame para el audio)
y deja el comando `lyric` disponible en cualquier consola, sin sudo ni permisos de administrador.

**Linux, macOS y WSL**

```sh
curl -fsSL https://raw.githubusercontent.com/JansenDev/lyric/main/install.sh | sh
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/JansenDev/lyric/main/install.ps1 | iex
```

También puedes clonar el repositorio y ejecutar `./install.sh` o
`powershell -ExecutionPolicy Bypass -File install.ps1`. Para actualizar, vuelve a ejecutar el instalador.

## Uso

```sh
lyric ejemplo.lrc                              # modo karaoke
lyric ejemplo.lrc --modo simple                # una línea detrás de otra
lyric cancion.lrc --audio cancion.mp3          # reproduce la música a la vez (mp3, ogg, wav)
lyric --buscar "Artista" "Canción"             # descarga la letra de LRCLIB
lyric --buscar "Artista" "Canción" --guardar cancion.lrc
lyric cancion.lrc --inicio 30                  # empieza en el segundo 30
lyric cancion.lrc --desfase 0.3                # la letra sale 0,3 s más tarde
```

Si la letra no va a la par de la música, mientras suena:

| Tecla | Acción |
|-------|--------|
| `Espacio` | Púlsala justo cuando empiece a cantar una línea: la letra se sincroniza ahí |
| `←` / `→` | Adelanta / retrasa la letra 0,1 s |
| `Ctrl+C` | Salir |

Al terminar te indica el `--desfase` que puedes usar la próxima vez.

## Desinstalar

- Linux, macOS y WSL: `rm -rf ~/.local/share/lyric ~/.local/bin/lyric`
- Windows: borra `%LOCALAPPDATA%\lyric` y `%USERPROFILE%\.local\bin\lyric.exe`
