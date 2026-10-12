# SpamDeleter

CLI tool que elimina automáticamente correos de la carpeta SPAM vía IMAP. Soporta Gmail, Outlook, Yahoo y cualquier servidor IMAP con autenticación básica u OAuth2.

[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![CI](https://github.com/bi0punk/SpamDeleter/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/SpamDeleter/actions)

## Contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack](#stack)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Instalación](#instalación)
- [Uso](#uso)
- [Configuración](#configuración)
- [Tests / CI](#tests--ci)
- [Logs](#logs)
- [Roadmap](#roadmap)
- [Licencia](#licencia)

## Características

- **Multi-proveedor**: Gmail, Outlook, Yahoo, IMAP genérico
- **Autenticación flexible**: básica (app password) u OAuth2 (Google, Microsoft)
- **Modo dry-run**: simula la operación sin eliminar nada
- **Ejecución programada**: intervalo configurable vía CLI (`--interval`)
- **Logging detallado**: registro de cada acción con timestamp
- **Dry-run seguro**: lista correos sin borrarlos

## Arquitectura

```mermaid
flowchart TD
  CLI[python -m spam_deleter] --> C[config.py: args + .env]
  CLI --> S[scheduler.py: loop con schedule / modo once]
  S --> CL[cleaner.py]
  CL --> CN[connector.py]
  CN -->|básica: imaplib.login| IMAP[Servidor IMAP 993 TLS]
  CN -->|XOAUTH2: Google o Microsoft| IMAP
  IMAP -->|search ALL en carpeta SPAM| CL
  CL -->|BODY.PEEK header FROM/SUBJECT| L[logger.py]
  L --> LOG[spam_deleter.log + consola]
  CL -->|dry_run o +FLAGS Deleted + expunge| IMAP
```

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| IMAP | `imaplib` (stdlib) |
| Scheduling | `schedule` |
| OAuth2 (opt) | `google-auth-oauthlib`, `msal` |
| Testing | pytest |

## Estructura del repositorio

```
SpamDeleter/
├── spam_deleter/
│   ├── __init__.py
│   ├── __main__.py          # Entry point CLI
│   ├── cleaner.py           # Lógica de eliminación
│   ├── config.py            # Parseo de args + env
│   ├── connector.py         # Conexión IMAP
│   ├── logger.py            # Logger formateado
│   └── scheduler.py         # Loop con schedule
├── tests/
│   └── test_smoke.py
├── .env.example
├── .github/workflows/
│   └── ci.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Instalación

```bash
pip install -r requirements.txt
```

Para OAuth2 (opcional):

```bash
pip install google-auth-oauthlib    # Google
pip install msal                     # Microsoft
```

Requisitos: Python 3.10+, servidor IMAP accesible desde la red y, para OAuth2, credenciales de aplicación en Google/Microsoft.

## Uso

```bash
# Ejecutar una sola vez
python -m spam_deleter --once

# Modo dry-run (solo lista, no borra)
python -m spam_deleter --once --dry-run

# Cada 30 minutos
python -m spam_deleter --interval 30m

# Cada 6 horas
python -m spam_deleter --interval 6h

# Forzar proveedor distinto al del .env
python -m spam_deleter --provider outlook
```

También se instala el ejecutable `spam-deleter` definido en `pyproject.toml`.

## Configuración

Copia `.env.example` a `.env` y completa tus credenciales:

### Autenticación básica

```env
PROVIDER=gmail
EMAIL=tu@email.com
PASSWORD=tu_contraseña_o_app_password
```

### OAuth2 (alternativa más segura)

```env
OAUTH2_ENABLED=true
OAUTH2_PROVIDER=google       # google | microsoft
OAUTH2_CLIENT_ID=xxx
OAUTH2_CLIENT_SECRET=xxx
OAUTH2_REFRESH_TOKEN=xxx
```

Otras variables opcionales: `INTERVAL` (intervalo por defecto, ej. `1h`), `IMAP_SERVER`/`IMAP_PORT` (si `PROVIDER=custom`), `SPAM_FOLDER` (por defecto Gmail `[Gmail]/Spam`, Outlook `Junk`, Yahoo `Bulk Mail`), `LOG_FILE`.

## Tests / CI

```bash
pip install pytest
pytest tests/ -v
```

GitHub Actions ejecuta lint (Ruff) y tests (pytest) en cada push/PR a main/master.

## Logs

Cada acción se registra en `spam_deleter.log`:

```
2026-05-28 10:00:00 | DELETE  | gmail | spam@scam.com       | Gane dinero facil
2026-05-28 10:00:01 | SUMMARY | gmail | Eliminados: 12 correos en 0.30s
```

## Roadmap

- [x] Soporte multi-proveedor (Gmail, Outlook, Yahoo, IMAP)
- [x] OAuth2 para Google y Microsoft
- [x] Modo dry-run
- [ ] Filtros por remitente/asunto
- [ ] Modo servidor (daemon con systemd)
- [ ] Notificaciones (webhook, email)
- [ ] Estadísticas semanales
- [ ] UI web básica

## Licencia

MIT