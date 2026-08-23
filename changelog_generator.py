#!/usr/bin/env python3
"""
changelog_generator.py
=======================

Genera automáticamente un archivo CHANGELOG.md a partir del historial de
commits de un repositorio Git local, clasificando los mensajes según su
prefijo convencional (feat:, fix:, docs:, etc.).

No requiere dependencias externas: usa el binario `git` a través del
módulo estándar `subprocess`.

Licencia: MIT
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


# --------------------------------------------------------------------------- #
# Configuración de categorías
# --------------------------------------------------------------------------- #

# Orden en el que aparecerán las categorías en el changelog final,
# junto con su título y emoji correspondiente.
CATEGORIAS: "OrderedDict[str, str]" = OrderedDict([
    ("feat", "✨ Nuevas funcionalidades"),
    ("fix", "🐛 Correcciones de errores"),
    ("docs", "📚 Documentación"),
    ("style", "💄 Estilo y formato"),
    ("refactor", "♻️ Refactorización"),
    ("perf", "⚡ Mejoras de rendimiento"),
    ("test", "✅ Pruebas"),
    ("build", "🏗️ Build y dependencias"),
    ("ci", "👷 Integración continua"),
    ("chore", "🔧 Tareas varias"),
    ("otros", "📦 Otros cambios"),
])


@dataclass
class Commit:
    """Representa un commit individual con la información relevante."""
    hash_corto: str
    autor: str
    fecha: str
    mensaje: str
    categoria: str


# --------------------------------------------------------------------------- #
# Interacción con Git
# --------------------------------------------------------------------------- #

def _validar_repositorio(ruta_repo: str) -> Path:
    """
    Verifica que la ruta dada sea un repositorio Git válido.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        ValueError: Si la ruta no es un repositorio Git.
    """
    path = Path(ruta_repo).resolve()

    if not path.exists():
        raise FileNotFoundError(f"La ruta del repositorio no existe: '{path}'")

    resultado = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )

    if resultado.returncode != 0:
        raise ValueError(f"'{path}' no es un repositorio Git válido.")

    return path


def obtener_commits(ruta_repo: str, cantidad: int) -> List[Commit]:
    """
    Obtiene los últimos N commits del repositorio indicado.

    Args:
        ruta_repo: Ruta al repositorio Git local.
        cantidad: Número máximo de commits a analizar.

    Returns:
        Lista de objetos Commit, del más reciente al más antiguo.

    Raises:
        FileNotFoundError: Si la ruta no existe.
        ValueError: Si no es un repositorio válido o no hay commits.
        RuntimeError: Si el comando git falla inesperadamente.
    """
    path = _validar_repositorio(ruta_repo)

    # Separador poco común para evitar colisiones con el texto del commit.
    separador = "<<>>"
    formato = f"%h{separador}%an{separador}%ad{separador}%s"

    comando = [
        "git", "-C", str(path), "log",
        f"-n{cantidad}",
        f"--pretty=format:{formato}",
        "--date=short",
    ]

    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Error al ejecutar git log: {error.stderr.strip()}") from error
    except FileNotFoundError as error:
        raise RuntimeError(
            "No se encontró el ejecutable 'git'. Asegúrate de tenerlo instalado."
        ) from error

    lineas = [linea for linea in resultado.stdout.splitlines() if linea.strip()]

    if not lineas:
        raise ValueError("El repositorio no tiene commits (o el rango solicitado está vacío).")

    commits: List[Commit] = []
    for linea in lineas:
        partes = linea.split(separador)
        if len(partes) != 4:
            continue  # Línea malformada, se ignora de forma segura.

        hash_corto, autor, fecha, mensaje = partes
        categoria = _clasificar_mensaje(mensaje)
        commits.append(Commit(hash_corto, autor, fecha, mensaje, categoria))

    return commits


def _clasificar_mensaje(mensaje: str) -> str:
    """Determina la categoría de un commit según su prefijo convencional."""
    mensaje_normalizado = mensaje.strip().lower()

    for prefijo in CATEGORIAS:
        if prefijo == "otros":
            continue
        # Admite variantes con "scope", ej: "feat(cli): agregar comando"
        if mensaje_normalizado.startswith(f"{prefijo}:") or mensaje_normalizado.startswith(f"{prefijo}("):
            return prefijo

    return "otros"


# --------------------------------------------------------------------------- #
# Generación del Markdown
# --------------------------------------------------------------------------- #

def agrupar_por_categoria(commits: List[Commit]) -> Dict[str, List[Commit]]:
    """Agrupa los commits por su categoría, preservando el orden definido."""
    grupos: Dict[str, List[Commit]] = {clave: [] for clave in CATEGORIAS}

    for commit in commits:
        grupos[commit.categoria].append(commit)

    return grupos


def generar_markdown(commits: List[Commit], nombre_repo: str) -> str:
    """Construye el contenido completo del CHANGELOG.md en formato Markdown."""
    grupos = agrupar_por_categoria(commits)
    fecha_generacion = datetime.now().strftime("%Y-%m-%d")

    lineas: List[str] = []
    lineas.append(f"# 📝 Changelog — {nombre_repo}")
    lineas.append("")
    lineas.append(f"> Generado automáticamente el {fecha_generacion} "
                   f"a partir de los últimos {len(commits)} commit(s).")
    lineas.append("")

    hubo_contenido = False

    for clave, titulo in CATEGORIAS.items():
        commits_categoria = grupos[clave]
        if not commits_categoria:
            continue

        hubo_contenido = True
        lineas.append(f"## {titulo}")
        lineas.append("")
        for commit in commits_categoria:
            lineas.append(
                f"- `{commit.hash_corto}` {commit.mensaje} "
                f"*(por {commit.autor}, {commit.fecha})*"
            )
        lineas.append("")

    if not hubo_contenido:
        lineas.append("_No se encontraron commits para mostrar._")
        lineas.append("")

    lineas.append("---")
    lineas.append("_Generado con `changelog_generator.py` 🚀_")

    return "\n".join(lineas)


def escribir_changelog(contenido: str, ruta_salida: str) -> None:
    """Escribe el contenido del changelog en el archivo de salida indicado."""
    path = Path(ruta_salida)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def construir_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos del generador de changelog."""
    parser = argparse.ArgumentParser(
        prog="changelog_generator.py",
        description="📝 Genera un CHANGELOG.md a partir del historial de commits de Git.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-n", "--count", type=int, default=50,
        help="Cantidad de commits recientes a analizar"
    )
    parser.add_argument(
        "-r", "--repo", default=".",
        help="Ruta al repositorio Git local"
    )
    parser.add_argument(
        "-o", "--output", default="CHANGELOG.md",
        help="Ruta del archivo Markdown de salida"
    )
    return parser


def main() -> int:
    """Punto de entrada principal del script. Devuelve el código de salida."""
    parser = construir_parser()
    args = parser.parse_args()

    if args.count <= 0:
        print("❌ Error de validación: --count debe ser un número mayor que 0.", file=sys.stderr)
        return 1

    try:
        commits = obtener_commits(args.repo, args.count)
        nombre_repo = Path(args.repo).resolve().name
        contenido = generar_markdown(commits, nombre_repo)
        escribir_changelog(contenido, args.output)

    except FileNotFoundError as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"❌ Error de validación: {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"❌ Error de Git: {error}", file=sys.stderr)
        return 1
    except PermissionError as error:
        print(f"❌ Error de permisos: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"❌ Error inesperado: {error}", file=sys.stderr)
        return 1

    print(f"✅ Changelog generado con {len(commits)} commit(s) en: '{args.output}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
