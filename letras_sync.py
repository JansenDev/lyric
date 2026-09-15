#!/usr/bin/env python3
"""
Letras sincronizadas en consola (estilo Spotify).

Lee letras en formato LRC:   [mm:ss.xx] texto de la línea

Uso:
  python letras_sync.py ejemplo.lrc
  python letras_sync.py ejemplo.lrc --modo simple
  python letras_sync.py ejemplo.lrc --inicio 30          (empezar en el segundo 30)
  python letras_sync.py --buscar "Artista" "Canción"      (descarga de LRCLIB)
  python letras_sync.py --buscar "Artista" "Canción" --guardar cancion.lrc
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TIME_TAG = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
META_TAG = re.compile(r"^\[(ar|ti|al|by|offset|length):(.*)\]$", re.IGNORECASE)

GRIS, BLANCO, VERDE, RESET = "\033[90m", "\033[1;97m", "\033[92m", "\033[0m"


def parse_lrc(texto):
    """Devuelve (metadatos, [(segundos, letra), ...]) ordenado por tiempo."""
    meta, lineas, offset = {}, [], 0.0
    for raw in texto.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        m = META_TAG.match(raw)
        if m:
            clave, valor = m.group(1).lower(), m.group(2).strip()
            meta[clave] = valor
            if clave == "offset":  # en milisegundos; positivo = la letra sale antes
                try:
                    offset = int(valor) / 1000
                except ValueError:
                    pass
            continue
        tiempos = TIME_TAG.findall(raw)
        if not tiempos:
            continue
        letra = TIME_TAG.sub("", raw).strip()
        # Una línea puede tener varias marcas (ej. un coro que se repite)
        for mm, ss in tiempos:
            lineas.append((int(mm) * 60 + float(ss), letra))
    lineas.sort(key=lambda x: x[0])
    lineas = [(max(0.0, t - offset), l) for t, l in lineas]
    return meta, lineas


def buscar_lrclib(artista, cancion):
    """Descarga la letra sincronizada desde la API pública de LRCLIB."""
    params = urllib.parse.urlencode({"artist_name": artista, "track_name": cancion})
    req = urllib.request.Request(
        f"https://lrclib.net/api/get?{params}",
        headers={"User-Agent": "letras-sync/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        datos = json.load(r)
    if not datos.get("syncedLyrics"):
        raise ValueError("La canción existe pero no tiene letra sincronizada.")
    return datos["syncedLyrics"]


def fmt(seg):
    return f"{int(seg // 60):02d}:{seg % 60:05.2f}"


def dibujar(lineas, actual, contexto=3):
    """Modo karaoke: redibuja la pantalla con la línea actual resaltada."""
    salida = ["\033[2J\033[H"]  # limpiar pantalla y mover cursor arriba
    for j in range(actual - contexto, actual + contexto + 1):
        if 0 <= j < len(lineas):
            texto = lineas[j][1] or "♪"
            if j == actual:
                salida.append(f"  {BLANCO}▶ {texto}{RESET}")
            else:
                salida.append(f"    {GRIS}{texto}{RESET}")
        else:
            salida.append("")
    print("\n".join(salida), flush=True)


def reproducir(lineas, modo="karaoke", inicio=0.0):
    # Reloj de referencia: todas las esperas se calculan contra t0,
    # así los pequeños retrasos de print/sleep NO se acumulan.
    t0 = time.monotonic() - inicio
    primera = next((i for i, (t, _) in enumerate(lineas) if t >= inicio), len(lineas))

    for idx in range(primera, len(lineas)):
        t, letra = lineas[idx]
        espera = t - (time.monotonic() - t0)
        if espera > 0:
            time.sleep(espera)
        if modo == "karaoke":
            dibujar(lineas, idx)
        else:
            print(f"{GRIS}[{fmt(t)}]{RESET} {letra or '♪'}", flush=True)


def main():
    if os.name == "nt":
        os.system("")  # activa los colores ANSI en la consola de Windows

    p = argparse.ArgumentParser(description="Letras sincronizadas en consola")
    p.add_argument("archivo", nargs="?", help="archivo .lrc")
    p.add_argument("--buscar", nargs=2, metavar=("ARTISTA", "CANCION"))
    p.add_argument("--guardar", help="guardar la letra descargada en este .lrc")
    p.add_argument("--modo", choices=["karaoke", "simple"], default="karaoke")
    p.add_argument("--inicio", type=float, default=0.0, help="segundo de inicio")
    args = p.parse_args()

    try:
        if args.buscar:
            texto = buscar_lrclib(*args.buscar)
            if args.guardar:
                with open(args.guardar, "w", encoding="utf-8") as f:
                    f.write(texto)
        elif args.archivo:
            with open(args.archivo, encoding="utf-8") as f:
                texto = f.read()
        else:
            p.error("Indica un archivo .lrc o usa --buscar")
    except urllib.error.HTTPError as e:
        sys.exit("No se encontró la canción en LRCLIB." if e.code == 404 else f"Error HTTP {e.code}")
    except (OSError, ValueError) as e:
        sys.exit(f"Error: {e}")

    meta, lineas = parse_lrc(texto)
    if not lineas:
        sys.exit("El archivo no tiene líneas con marcas de tiempo.")

    titulo = f"{meta.get('ar', '?')} — {meta.get('ti', '?')}"
    print(f"{VERDE}♫ {titulo}{RESET}")
    print("Empieza en 3 segundos... (Ctrl+C para salir)")
    time.sleep(3)

    try:
        reproducir(lineas, args.modo, args.inicio)
        print(f"\n{VERDE}♫ Fin{RESET}")
    except KeyboardInterrupt:
        print(f"{RESET}\nDetenido.")


if __name__ == "__main__":
    main()
