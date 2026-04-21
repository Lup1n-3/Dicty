#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║           WORDLIST GENERATOR - Diccionario Personalizado      ║
║                  Herramienta OSINT / Pentesting               ║
╚══════════════════════════════════════════════════════════════╝
ADVERTENCIA: Solo para uso ético y legal.
"""

import itertools
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SEPARADORES = ["", "_", ".", "-", "@", "#"]

SUFIJOS_PREFIJOS = [
    "1", "12", "123", "1234", "12345", "123456",
    "!", "!!", "0", "00",
    "69", "666", "777", "99", "2024", "2025",
    "@", "#", "*", "007",
]

LEET_MAP = {
    'a': ['a', '4'], 'e': ['e', '3'], 'i': ['i', '1'],
    'o': ['o', '0'], 's': ['s', '$'], 't': ['t', '7'],
}

def leet_variations(word):
    options = [LEET_MAP.get(c, [c]) for c in word.lower()]
    return {''.join(combo) for combo in itertools.product(*options)}

def transformaciones(token):
    base = token.strip()
    if not base:
        return set()
    v = set()
    v.add(base.lower())
    v.add(base.upper())
    v.add(base.capitalize())
    v.add(base[::-1].lower())
    v.add(base[::-1].capitalize())
    v.update(leet_variations(base))
    return v

# ─────────────────────────────────────────────
# FECHAS
# ─────────────────────────────────────────────
CAMPOS_FECHA = {'fecha_nacimiento', 'fecha_aniversario', 'fecha_especial'}

def parsear_fecha(fecha_str):
    fecha_str = fecha_str.strip().replace("-", "/").replace(".", "/")
    for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%y", "%d%m%Y", "%Y%m%d"]:
        try:
            f = datetime.strptime(fecha_str, fmt)
            d, m, Y, y = f.strftime("%d"), f.strftime("%m"), f.strftime("%Y"), f.strftime("%y")
            return list(set([d, m, Y, y, f"{d}{m}", f"{m}{d}",
                             f"{d}{m}{Y}", f"{d}{m}{y}", f"{Y}{m}{d}"]))
        except ValueError:
            continue
    return [fecha_str.replace("/", "")]

# ─────────────────────────────────────────────
# CUESTIONARIO
# ─────────────────────────────────────────────
def preguntar(pregunta, ejemplo=""):
    prompt = f"  → {pregunta}" + (f" [{ejemplo}]" if ejemplo else "") + ": "
    return input(prompt).strip()

def cuestionario():
    print("\n" + "═"*62)
    print("  INFORMACIÓN DEL OBJETIVO")
    print("  (Dejá en blanco los campos que no apliquen)")
    print("═"*62 + "\n")
    datos = {}
    print("── DATOS PERSONALES ──────────────────────────────────────")
    datos['nombre']           = preguntar("Nombre",             "Dylan")
    datos['segundo_nombre']   = preguntar("Segundo nombre",     "Matías")
    datos['apellido']         = preguntar("Apellido",           "García")
    datos['segundo_apellido'] = preguntar("Segundo apellido",   "López")
    datos['apodo']            = preguntar("Apodo / Nickname",   "dyl")
    print("\n── FECHAS ────────────────────────────────────────────────")
    datos['fecha_nacimiento']  = preguntar("Fecha de nacimiento",  "19/08/2001")
    datos['fecha_aniversario'] = preguntar("Fecha de aniversario", "14/02/2019")
    datos['fecha_especial']    = preguntar("Otra fecha importante", "25/12/2000")
    print("\n── DOCUMENTOS E IDENTIFICADORES ─────────────────────────")
    datos['dni']           = preguntar("DNI / Cédula",     "12345678")
    datos['telefono']      = preguntar("Teléfono",         "1155667788")
    datos['email_usuario'] = preguntar("Usuario de email", "dylan123")
    print("\n── LUGAR ─────────────────────────────────────────────────")
    datos['ciudad'] = preguntar("Ciudad",           "BuenosAires")
    datos['barrio'] = preguntar("Barrio / Colonia", "Palermo")
    datos['pais']   = preguntar("País",             "Argentina")
    print("\n── FAMILIA Y ENTORNO ─────────────────────────────────────")
    datos['pareja']   = preguntar("Nombre pareja/ex",   "Valentina")
    datos['madre']    = preguntar("Nombre madre",       "María")
    datos['padre']    = preguntar("Nombre padre",       "Carlos")
    datos['hijos']    = preguntar("Nombre/s hijo/s",    "Luca, Emma")
    datos['mascotas'] = preguntar("Nombre/s mascota/s", "Thor, Luna")
    print("\n── GUSTOS E INTERESES ────────────────────────────────────")
    datos['equipo']         = preguntar("Equipo de fútbol",    "Boca")
    datos['banda_pelicula'] = preguntar("Banda/Película fav.", "Nirvana")
    datos['videojuego']     = preguntar("Videojuego fav.",     "Minecraft")
    datos['palabra_fav']    = preguntar("Palabra/frase fav.",  "freedom")
    print("\n── TRABAJO / ESTUDIO ─────────────────────────────────────")
    datos['empresa']     = preguntar("Empresa / Institución", "Google")
    datos['profesion']   = preguntar("Profesión / Carrera",   "developer")
    datos['usuario_red'] = preguntar("Usuario en redes",      "dylan_arg")
    print("\n── EXTRA ─────────────────────────────────────────────────")
    datos['numero_suerte']   = preguntar("Número de la suerte", "7")
    datos['palabra_extra_1'] = preguntar("Palabra extra 1")
    datos['palabra_extra_2'] = preguntar("Palabra extra 2")
    datos['palabra_extra_3'] = preguntar("Palabra extra 3")
    return datos

def procesar_datos(datos):
    tokens, vistos = [], set()
    for campo, valor in datos.items():
        if not valor:
            continue
        partes = parsear_fecha(valor) if campo in CAMPOS_FECHA else [p.strip() for p in valor.split(',') if p.strip()]
        for t in partes:
            if t.lower() not in vistos:
                vistos.add(t.lower())
                tokens.append(t)
    return tokens

# ─────────────────────────────────────────────
# GENERACIÓN STREAMING PURA — sin RAM acumulada
# ─────────────────────────────────────────────
def generar_y_escribir(tokens, archivo, min_len, max_len):
    """
    Escribe directamente al archivo, línea por línea.
    NO usa ningún set en memoria → uso de RAM constante y mínimo.
    Los duplicados se pueden eliminar después con: sort -u archivo.txt -o archivo.txt
    """
    escritas = 0
    BUFFER_SIZE = 50_000  # líneas en buffer antes de flush

    def es_valida(p):
        return min_len <= len(p) <= max_len

    print("[*] Calculando variantes por token...")
    variantes = {t: sorted(transformaciones(t)) for t in tokens}
    total_var = sum(len(v) for v in variantes.values())
    print(f"    Tokens: {len(tokens)} | Variantes individuales: {total_var}")

    buffer = []

    def flush(f):
        nonlocal buffer
        f.write('\n'.join(buffer) + '\n')
        buffer = []

    with open(archivo, 'w', encoding='utf-8', buffering=1_048_576) as f:

        # ── Paso 1: variantes individuales + afijos ──
        print("[*] [1/2] Variantes individuales + afijos...")
        for t in tokens:
            for v in variantes[t]:
                if es_valida(v):
                    buffer.append(v); escritas += 1
                for afijo in SUFIJOS_PREFIJOS:
                    p1 = v + afijo
                    p2 = afijo + v
                    if es_valida(p1): buffer.append(p1); escritas += 1
                    if es_valida(p2): buffer.append(p2); escritas += 1
                if len(buffer) >= BUFFER_SIZE:
                    flush(f)
        flush(f)
        mb = os.path.getsize(archivo) / 1_048_576
        print(f"    {escritas:,} entradas | {mb:.1f} MB")

        # ── Paso 2: combinaciones de pares ──
        token_lista = list(tokens)
        total_pares = len(token_lista) * (len(token_lista) - 1)
        pares_ok = 0
        print(f"[*] [2/2] Combinaciones de pares ({total_pares} pares)...")

        for i, t1 in enumerate(token_lista):
            vars1 = variantes[t1]
            for j, t2 in enumerate(token_lista):
                if i == j:
                    continue
                vars2 = variantes[t2]

                for v1 in vars1:
                    for sep in SEPARADORES:
                        for v2 in vars2:
                            combo = f"{v1}{sep}{v2}"
                            if es_valida(combo):
                                buffer.append(combo); escritas += 1
                    # Afijos solo en combo sin separador (evita explosión)
                    for v2 in vars2:
                        base_combo = f"{v1}{v2}"
                        for afijo in SUFIJOS_PREFIJOS:
                            p1 = base_combo + afijo
                            p2 = afijo + base_combo
                            if es_valida(p1): buffer.append(p1); escritas += 1
                            if es_valida(p2): buffer.append(p2); escritas += 1

                    if len(buffer) >= BUFFER_SIZE:
                        flush(f)

                pares_ok += 1
                if pares_ok % 5 == 0 or pares_ok == total_pares:
                    mb = os.path.getsize(archivo) / 1_048_576
                    print(f"    Par {pares_ok}/{total_pares} | {escritas:,} líneas | {mb:.0f} MB", end='\r')

        flush(f)
        print()

    return escritas

# ─────────────────────────────────────────────
# DEDUPLICAR (opcional, usa sort externo)
# ─────────────────────────────────────────────
def deduplicar(archivo):
    """Usa sort del SO para deduplicar sin cargar el archivo en RAM."""
    import subprocess
    print(f"[*] Deduplicando con sort (puede tardar)...")
    tmp = archivo + ".tmp"
    ret = subprocess.run(
        ["sort", "-u", archivo, "-o", tmp],
        capture_output=True
    )
    if ret.returncode == 0:
        os.replace(tmp, archivo)
        print(f"    Deduplicación completada.")
        return True
    else:
        print(f"    [!] sort no disponible (Windows). El archivo puede tener duplicados.")
        print(f"        Para deduplicar manualmente: sort /unique archivo.txt > limpio.txt")
        if os.path.exists(tmp):
            os.remove(tmp)
        return False

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        WORDLIST GENERATOR — Diccionario Personalizado        ║
║                    Solo uso ético / legal                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    print("  ⚠  ADVERTENCIA LEGAL")
    print("  Esta herramienta es para uso en cuentas propias o")
    print("  con autorización explícita del propietario.\n")
    if input("  ¿Confirmás que usarás esto de forma ética? [s/N]: ").strip().lower() != 's':
        print("\n  Saliendo."); sys.exit(0)

    datos = cuestionario()
    tokens = procesar_datos(datos)
    if not tokens:
        print("\n[!] No se ingresaron datos."); sys.exit(1)

    print(f"\n[*] Tokens ({len(tokens)}): {', '.join(tokens[:12])}{'...' if len(tokens)>12 else ''}")

    print("\n" + "═"*62)
    print("  OPCIONES DE SALIDA")
    print("═"*62)
    nombre = input("  → Nombre del archivo [wordlist.txt]: ").strip() or "wordlist.txt"
    if not nombre.endswith(".txt"):
        nombre += ".txt"
    s = input("  → Longitud mínima [4]: ").strip()
    min_len = int(s) if s.isdigit() else 4
    s = input("  → Longitud máxima [32]: ").strip()
    max_len = int(s) if s.isdigit() else 32
    ded = input("  → ¿Deduplicar al final? (requiere sort) [s/N]: ").strip().lower() == 's'

    print(f"\n[*] Generando → '{nombre}' | Escritura directa al disco | RAM mínima\n")
    inicio = datetime.now()
    total = generar_y_escribir(tokens, nombre, min_len, max_len)

    if ded:
        deduplicar(nombre)

    duracion = (datetime.now() - inicio).total_seconds()
    mb = os.path.getsize(nombre) / 1_048_576

    # Contar líneas reales del archivo
    with open(nombre, 'rb') as f:
        lineas = sum(1 for _ in f)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                     GENERACIÓN COMPLETA                      ║
╠══════════════════════════════════════════════════════════════╣
║  Archivo:     {nombre:<46}║
║  Entradas:    {f"{lineas:,}":<46}║
║  Tamaño:      {f"{mb:.2f} MB":<46}║
║  Tiempo:      {f"{duracion:.1f} segundos":<46}║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
