# 📝 Git Changelog Generator

Un script de Python que genera automáticamente un archivo `CHANGELOG.md`
bien formateado a partir del historial de commits de un repositorio Git,
clasificando cada commit según su prefijo convencional (`feat:`, `fix:`,
`docs:`, etc.).

---

## ✨ Características

- 🔍 Lee los últimos **N** commits de cualquier repositorio Git local.
- 🏷️ Clasifica automáticamente los commits en categorías: `feat`, `fix`,
  `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` y `otros`.
- 📄 Exporta un `CHANGELOG.md` limpio, agrupado y con emojis por categoría.
- ⚙️ Opciones configurables por CLI: cantidad de commits, ruta del repo y
  archivo de salida.
- 🪶 **Cero dependencias externas** (usa `subprocess` + el binario `git`).
- 🧩 Código modular, tipado y documentado según PEP 8.

---

## 📦 Requisitos

- Python 3.8 o superior
- Tener `git` instalado y disponible en el `PATH` del sistema
- No requiere librerías externas (ver `requirements.txt`)

---

## 🚀 Instalación

```bash
# 1. Clona o descarga este proyecto
cd proyecto2-git-changelog

# 2. (Opcional) Crea un entorno virtual
python3 -m venv venv
source venv/bin/activate     # En Windows: venv\Scripts\activate

# 3. No hay dependencias que instalar, pero si quieres revisar:
pip install -r requirements.txt
```

---

## 🖥️ Uso

### Uso básico (repositorio actual, últimos 50 commits)

```bash
python changelog_generator.py
```

### Especificar cantidad de commits

```bash
python changelog_generator.py -n 100
```

### Especificar la ruta de otro repositorio

```bash
python changelog_generator.py -r /ruta/a/mi/repositorio
```

### Cambiar el nombre/ruta del archivo de salida

```bash
python changelog_generator.py -o docs/CHANGELOG.md
```

### Combinando opciones

```bash
python changelog_generator.py -r ../mi-proyecto -n 30 -o CHANGELOG.md
```

### Ver ayuda completa

```bash
python changelog_generator.py --help
```

---

## 🏷️ Convención de prefijos reconocidos

| Prefijo      | Categoría                     |
|--------------|--------------------------------|
| `feat:`      | ✨ Nuevas funcionalidades      |
| `fix:`       | 🐛 Correcciones de errores     |
| `docs:`      | 📚 Documentación                |
| `style:`     | 💄 Estilo y formato            |
| `refactor:`  | ♻️ Refactorización              |
| `perf:`      | ⚡ Mejoras de rendimiento       |
| `test:`      | ✅ Pruebas                      |
| `build:`     | 🏗️ Build y dependencias         |
| `ci:`        | 👷 Integración continua         |
| `chore:`     | 🔧 Tareas varias                |
| *(sin prefijo o desconocido)* | 📦 Otros cambios |

> También reconoce prefijos con *scope*, ej: `feat(cli): agregar comando merge`.

---

## ⚠️ Manejo de errores

- ❌ Ruta de repositorio inexistente.
- ❌ Ruta que no es un repositorio Git válido.
- ❌ Repositorio sin commits.
- ❌ `git` no instalado o no encontrado en el `PATH`.
- ❌ Valor inválido para `--count` (debe ser mayor que 0).

---

## 🗂️ Estructura del proyecto

```
proyecto2-git-changelog/
├── changelog_generator.py   # Script principal
├── requirements.txt          # Dependencias (ninguna externa)
└── README.md                 # Este archivo
```

---

## 📝 Licencia

MIT — libre para usar y modificar.
