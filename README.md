# SpamDeleter

Elimina automáticamente correos de la carpeta SPAM via IMAP.
Soporta Gmail, Outlook, Yahoo y cualquier servidor IMAP.

## Instalación

```bash
pip install -r requirements.txt
```

Para OAuth2 (opcional):

```bash
pip install google-auth-oauthlib    # Google
pip install msal                     # Microsoft
```

## Configuración

Copia `.env.example` a `.env` y completa tus credenciales:

```bash
cp .env.example .env
```

### Autenticación básica

```env
PROVIDER=gmail
EMAIL=tu@email.com
PASSWORD=tu_app_password
```

### OAuth2 (alternativa más segura)

```env
OAUTH2_ENABLED=true
OAUTH2_PROVIDER=google
OAUTH2_CLIENT_ID=xxx
OAUTH2_CLIENT_SECRET=xxx
OAUTH2_REFRESH_TOKEN=xxx
```

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

## Logs

Cada acción se registra en `spam_deleter.log`:

```
2026-05-28 10:00:00 | DELETE  | gmail | spam@scam.com       | Gane dinero facil
2026-05-28 10:00:01 | SUMMARY | gmail | Eliminados: 12 correos en 0.30s
```

## Licencia

MIT
