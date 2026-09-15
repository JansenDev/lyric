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
  python letras_sync.py ejemplo.lrc --audio cancion.mp3   (reproduce la música a la vez)

Para --audio hace falta pygame:  pip install pygame
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

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")  # sin el saludo de pygame
try:
    import pygame  # opcional: solo hace falta con --audio
except ImportError:
    pygame = None

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


def reloj_audio(musica, inicio):
    """Reloj basado en la posición real del audio; devuelve None cuando termina."""
    def ahora():
        if not musica.get_busy():
            return None
        return inicio + musica.get_pos() / 1000  # get_pos no incluye el inicio
    return ahora


def reproducir(lineas, modo="karaoke", inicio=0.0, reloj=None):
    if reloj is None:
        # Reloj de referencia: todas las esperas se calculan contra t0,
        # así los pequeños retrasos de print/sleep NO se acumulan.
        t0 = time.monotonic() - inicio
        reloj = lambda: time.monotonic() - t0
    primera = next((i for i, (t, _) in enumerate(lineas) if t >= inicio), len(lineas))

    for idx in range(primera, len(lineas)):
        t, letra = lineas[idx]
        # Esperas cortas volviendo a consultar el reloj: con audio, el tiempo
        # lo marca la canción y puede no ir exacto al reloj del sistema.
        while (ahora := reloj()) is not None and ahora < t:
            time.sleep(min(t - ahora, 0.05))
        if ahora is None:
            return  # el audio terminó antes que la letra
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
    p.add_argument("--audio", help="archivo de audio (mp3, ogg, wav) para reproducir a la vez")
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

    musica = None
    if args.audio:
        if pygame is None:
            sys.exit("Para reproducir audio instala pygame:  pip install pygame")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(args.audio)
        except (pygame.error, OSError) as e:
            sys.exit(f"Error al cargar el audio: {e}")
        musica = pygame.mixer.music

    titulo = f"{meta.get('ar', '?')} — {meta.get('ti', '?')}"
    print(f"{VERDE}♫ {titulo}{RESET}")
    if musica:
        print("Reproduciendo... (Ctrl+C para salir)")
    else:
        # Margen para darle al play en el reproductor externo
        print("Empieza en 3 segundos... (Ctrl+C para salir)")
        time.sleep(3)

    try:
        reloj = None
        if musica:
            musica.play(start=args.inicio)
            reloj = reloj_audio(musica, args.inicio)
        reproducir(lineas, args.modo, args.inicio, reloj)
        while musica and musica.get_busy():  # deja sonar el final de la canción
            time.sleep(0.1)
        print(f"\n{VERDE}♫ Fin{RESET}")
    except KeyboardInterrupt:
        print(f"{RESET}\nDetenido.")
    finally:
        if musica:
            pygame.mixer.quit()


if __name__ == "__main__":
    main()
