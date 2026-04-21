# Wordlist Generator

Herramienta de línea de comandos para generar diccionarios de contraseñas personalizados basados en información personal del objetivo. Útil para auditorías de seguridad y pentesting.

**Uso exclusivamente ético y legal. Solo en cuentas propias o con autorización explícita.**

---

## Cómo funciona

El script hace un cuestionario interactivo donde se ingresan datos del objetivo: nombre, apellidos, fechas, DNI, mascotas, ciudad, gustos, etc. Los campos que se dejan en blanco son ignorados.

Con esa información genera combinaciones aplicando:

- Variantes de capitalización (minúsculas, mayúsculas, capitalizado)
- Texto invertido
- Leetspeak (a→4, e→3, o→0, s→$, etc.)
- Combinaciones de pares de tokens con separadores (_, ., -, @, #)
- Sufijos y prefijos comunes (123, !, 666, 2024, @, etc.)

Las fechas se parsean automáticamente y generan múltiples fragmentos: día, mes, año, combinaciones (ddmm, mmddyyyy, etc.).

La generación escribe directamente al disco sin acumular datos en memoria, por lo que funciona sin importar la cantidad de tokens ingresados.

---

## Requisitos

- Python 3.6 o superior
- No requiere librerías externas

---

## Uso

```bash
python3 wordlist_gen.py
```

El script guía el proceso paso a paso. Al final pregunta el nombre del archivo de salida y los filtros de longitud mínima y máxima.

---

## Deduplicar el resultado

El archivo generado puede contener duplicados. Para eliminarlos:

En Linux / Mac:
```bash
sort -u wordlist.txt -o wordlist.txt
```

En Windows:
```cmd
sort /unique wordlist.txt > wordlist_limpio.txt
```

---

## Ejemplo de salida

Con nombre `Dylan` y fecha de nacimiento `19/08/2001` el diccionario incluye entradas como:

```
dylan
DYLAN
dylan123
dylan_2001
2001_dylan
dylan.1908
19082001dylan
dy14n_2001
nalyD@123
```
