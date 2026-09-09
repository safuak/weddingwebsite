# HTTPS Setup

Recommended production shape:

1. Run the Flask app internally with Waitress:

```powershell
.\run-site.ps1
```

2. Run Caddy from this folder:

```powershell
caddy run --config .\Caddyfile
```

Caddy will listen on ports 80 and 443, request a Let's Encrypt certificate for `shandfi.com`, and proxy traffic to the local Python app.

Requirements:

- DNS A record for `shandfi.com` points to this server IP.
- DNS A record for `www.shandfi.com` points to this server IP.
- Windows Firewall allows inbound TCP 80 and 443.
- No other service uses ports 80 or 443.
