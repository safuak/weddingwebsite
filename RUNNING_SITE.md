# Running the Site

Double-click:

```text
start-site.bat
```

Or run manually from PowerShell:

```powershell
cd C:\Users\Administrator\Desktop\davetiye
.\start-site.ps1
```

Public URL:

```text
https://shandfi.com
```

Admin panel:

```text
https://shandfi.com/admin
```

Admin password:

```text
Set in .env as ADMIN_PASSWORD.
```

The Flask session secret is also set in `.env` as `FLASK_SECRET_KEY`.
Do not commit `.env` to GitHub.

What it starts:

- Python/Waitress app on `127.0.0.1:5000`
- Caddy HTTPS proxy on ports `80` and `443`

Logs:

- `waitress.out.log`
- `waitress.err.log`
- `caddy.out.log`
- `caddy.err.log`
