#!/bin/sh
# Instala el comando `lyric` para el usuario actual, sin sudo (Linux, macOS y WSL).
#   Desde una copia del repositorio:  ./install.sh
#   Directo desde GitHub:             curl -fsSL https://raw.githubusercontent.com/USUARIO/lyric/main/install.sh | sh
set -e

REPO="https://github.com/USUARIO/lyric"
DESTINO="${XDG_DATA_HOME:-$HOME/.local/share}/lyric"
BIN="$HOME/.local/bin"

# Código a instalar: la carpeta del script si es una copia de lyric; si no, el zip de GitHub
ORIGEN="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
grep -qs '^name = "lyric"' "$ORIGEN/pyproject.toml" || ORIGEN="$REPO/archive/refs/heads/main.zip"

command -v python3 >/dev/null || { echo "Falta python3." >&2; exit 1; }

echo "Creando entorno en $DESTINO ..."
python3 -m venv --clear "$DESTINO" || {
    echo "No se pudo crear el entorno virtual. En Ubuntu/Debian: sudo apt install python3-venv" >&2
    exit 1
}
echo "Instalando lyric y pygame ..."
"$DESTINO/bin/pip" install --quiet --disable-pip-version-check "$ORIGEN"

mkdir -p "$BIN"
ln -sf "$DESTINO/bin/lyric" "$BIN/lyric"
echo "Listo: $BIN/lyric"

case ":$PATH:" in
    *":$BIN:"*) echo "Prueba:  lyric --help" ;;
    *)
        echo "Añade esta línea a tu ~/.bashrc o ~/.zshrc y abre una consola nueva:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac
