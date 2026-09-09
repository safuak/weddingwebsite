# Fikrie & Safak Engagement Website

Digital engagement invitation website for https://shandfi.com.

## Run Locally

```powershell
cd C:\Users\Administrator\Desktop\davetiye
.\start-site.ps1
```

Or double-click `start-site.bat`.

## Environment

Create `.env` from `.env.example`:

```text
ADMIN_PASSWORD=your-admin-password
FLASK_SECRET_KEY=your-long-random-secret
```

`.env`, uploads, backups, logs, local Caddy data, and temporary browser files are ignored by Git.

## URLs

- Site: https://shandfi.com
- Admin: https://shandfi.com/admin
- Hidden guest gallery: https://shandfi.com/sizden-gelenler
- Health: https://shandfi.com/api/health

## Notes

- Uploaded guest memories are stored under `uploads/<guest-name>/`.
- Admin bulk downloads are created as temporary ZIP files and removed after download.
- Large audio/video files should be compressed with ffmpeg before publishing.
