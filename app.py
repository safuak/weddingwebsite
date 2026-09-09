from datetime import datetime
from pathlib import Path
import ast
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import tempfile
import unicodedata
import zipfile
from functools import wraps
from flask import Flask, abort, jsonify, redirect, render_template_string, request, send_file, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR / "engagement-site"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
RSVP_TEXT_FILE = UPLOAD_DIR / "rsvp_submissions.txt"
RSVP_JSONL_FILE = UPLOAD_DIR / "rsvp_submissions.jsonl"
TMP_DOWNLOAD_DIR = BASE_DIR / "tmp" / "downloads"
TMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file(BASE_DIR / ".env")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD must be set in .env or environment variables.")
if not FLASK_SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY must be set in .env or environment variables.")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "heic",
    "heif",
    "mp4",
    "webm",
    "mov",
    "avi",
    "mkv",
}
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1 GB
PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic", "heif"}
VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv"}
TRANSLITERATION_MAP = str.maketrans(
    {
        "ı": "i",
        "İ": "I",
        "ş": "s",
        "Ş": "S",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sht",
        "ъ": "a",
        "ь": "",
        "ю": "yu",
        "я": "ya",
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "Y",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Sht",
        "Ъ": "A",
        "Ь": "",
        "Ю": "Yu",
        "Я": "Ya",
    }
)

app = Flask(
    __name__,
    static_folder=str(SITE_DIR),
    static_url_path="",
    template_folder=str(SITE_DIR),
)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = FLASK_SECRET_KEY


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_storage_summary() -> dict:
    files = [path for path in UPLOAD_DIR.rglob("*") if path.is_file()]
    total_size = sum(path.stat().st_size for path in files)
    disk = shutil.disk_usage(BASE_DIR)
    return {
        "file_count": len(files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
    }


def file_category(filename: str) -> str:
    extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if extension in PHOTO_EXTENSIONS:
        return "photo"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    return "other"


def safe_guest_folder(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name.strip().translate(TRANSLITERATION_MAP))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    folder = re.sub(r"[^A-Za-z0-9_-]+", "_", ascii_name).strip("_")
    return folder[:80] or "guest"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def protect_admin_posts():
    if not request.path.startswith("/admin/") or request.method != "POST":
        return None
    if request.endpoint == "admin_login":
        return None
    csrf_token = session.get("admin_csrf_token", "")
    submitted = request.form.get("csrf_token", "")
    if not csrf_token or not hmac.compare_digest(csrf_token, submitted):
        abort(403)
    return None


def admin_csrf_token() -> str:
    token = session.get("admin_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["admin_csrf_token"] = token
    return token


def parse_guest_count(value: str, status: str) -> int:
    value = str(value or "").strip()
    if value.endswith("+"):
        value = value[:-1]
    try:
        count = int(value)
    except ValueError:
        count = 1
    return max(count, 0)


def normalize_rsvp(raw: dict) -> dict:
    status = (raw.get("status") or "").strip()
    if status not in {"coming", "not-coming"}:
        status = "coming"
    guests = parse_guest_count(raw.get("guests", ""), status)
    return {
        "received_at": raw.get("received_at", ""),
        "name": (raw.get("name") or "").strip(),
        "guests": guests,
        "status": status,
        "note": (raw.get("note") or "").strip(),
    }


def rsvp_row_id(row: dict) -> str:
    data = {
        "received_at": row.get("received_at", ""),
        "name": row.get("name", ""),
        "guests": row.get("guests", 0),
        "status": row.get("status", ""),
        "note": row.get("note", ""),
    }
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def load_rsvps() -> list[dict]:
    rows = []
    seen = set()

    def add_row(raw):
        row = normalize_rsvp(raw)
        row["id"] = rsvp_row_id(row)
        key = row["id"]
        if key not in seen:
            seen.add(key)
            rows.append(row)

    if RSVP_JSONL_FILE.exists():
        with RSVP_JSONL_FILE.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    add_row(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if RSVP_TEXT_FILE.exists():
        with RSVP_TEXT_FILE.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    add_row(ast.literal_eval(line))
                except (SyntaxError, ValueError):
                    continue

    return sorted(rows, key=lambda item: item["received_at"], reverse=True)


def save_rsvps(rows: list[dict]) -> None:
    RSVP_JSONL_FILE.parent.mkdir(exist_ok=True)
    with RSVP_JSONL_FILE.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = {key: row[key] for key in ("received_at", "name", "guests", "status", "note")}
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    with RSVP_TEXT_FILE.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = {key: row[key] for key in ("received_at", "name", "guests", "status", "note")}
            handle.write(f"{payload}\n")


def rsvp_summary(rows: list[dict]) -> dict:
    coming = [row for row in rows if row["status"] == "coming"]
    not_coming = [row for row in rows if row["status"] == "not-coming"]
    return {
        "total_responses": len(rows),
        "coming_responses": len(coming),
        "not_coming_responses": len(not_coming),
        "coming_people": sum(row["guests"] for row in coming),
        "not_coming_people": sum(row["guests"] or 1 for row in not_coming),
        "notes": sum(1 for row in rows if row["note"]),
    }


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def memory_file_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in {"jpg", "jpeg", "png", "gif", "webp", "heic", "heif"}:
        return "image"
    if suffix in {"mp4", "webm", "mov", "avi", "mkv"}:
        return "video"
    return "file"


def load_memory_uploads() -> dict:
    ignored_files = {RSVP_TEXT_FILE.name, RSVP_JSONL_FILE.name}
    grouped = {}
    total_files = 0
    total_size = 0

    for path in sorted(UPLOAD_DIR.rglob("*"), key=lambda item: item.stat().st_mtime, reverse=True):
        if not path.is_file() or path.name in ignored_files:
            continue
        rel_path = path.relative_to(UPLOAD_DIR)
        parts = rel_path.parts
        guest = parts[0] if len(parts) > 1 else "Klasorsuz"
        stat = path.stat()
        total_files += 1
        total_size += stat.st_size
        group = grouped.setdefault(
            guest,
            {"guest": guest, "files": [], "file_count": 0, "total_size": 0, "updated_at": ""},
        )
        group["file_count"] += 1
        group["total_size"] += stat.st_size
        updated_at = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        if not group["updated_at"]:
            group["updated_at"] = updated_at
        group["files"].append(
            {
                "name": path.name,
                "relative_path": rel_path.as_posix(),
                "type": memory_file_type(path),
                "size": format_bytes(stat.st_size),
                "updated_at": updated_at,
            }
        )

    groups = sorted(grouped.values(), key=lambda item: item["updated_at"], reverse=True)
    for group in groups:
        group["total_size_label"] = format_bytes(group["total_size"])

    return {
        "groups": groups,
        "summary": {
            "guest_count": len(groups),
            "file_count": total_files,
            "total_size": format_bytes(total_size),
        },
    }


def public_memory_items() -> list[dict]:
    memories = load_memory_uploads()
    items = []
    for group in memories["groups"]:
        for file in group["files"]:
            if file["type"] not in {"image", "video"}:
                continue
            items.append(
                {
                    "guest": group["guest"],
                    "name": file["name"],
                    "relative_path": file["relative_path"],
                    "type": file["type"],
                    "updated_at": file["updated_at"],
                }
            )
    return items


def resolve_upload_path(filename: str) -> Path:
    path = (UPLOAD_DIR / filename).resolve()
    if not path.is_file() or UPLOAD_DIR.resolve() not in path.parents:
        raise FileNotFoundError(filename)
    return path


def selected_upload_paths() -> list[tuple[str, Path]]:
    selected = request.form.getlist("files")
    paths = []
    for filename in selected:
        try:
            path = resolve_upload_path(filename)
        except FileNotFoundError:
            continue
        paths.append((filename, path))
    return paths


def zip_arcname(filename: str, path: Path) -> str:
    rel = Path(filename)
    if len(rel.parts) > 1:
        return rel.as_posix()
    return f"Klasorsuz/{path.name}"


def cleanup_empty_upload_parent(path: Path) -> None:
    parent = path.parent
    try:
        if parent != UPLOAD_DIR and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    except OSError:
        pass


@app.route("/")
def index():
    return send_from_directory(SITE_DIR, "index.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password, ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            session["admin_csrf_token"] = secrets.token_urlsafe(32)
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        error = "Sifre hatali."

    return render_template_string(
        """
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Admin Giris</title>
          <style>
            body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f8f1e7;color:#3d2b1f;font-family:Arial,sans-serif}
            form{width:min(420px,calc(100vw - 32px));background:#fffaf3;border:1px solid #dfc38b;border-radius:18px;padding:28px;box-shadow:0 24px 60px rgba(73,45,20,.14)}
            h1{margin:0 0 18px;font-family:Georgia,serif;font-size:38px;color:#8b641f}
            label{display:grid;gap:10px;font-weight:700}
            input{border:1px solid #e1cdb5;border-radius:12px;padding:14px 16px;font-size:16px}
            button{margin-top:18px;border:0;border-radius:12px;padding:14px 20px;background:#b8892d;color:white;font-weight:800;cursor:pointer}
            .error{margin:0 0 14px;color:#a33;font-weight:700}
          </style>
        </head>
        <body>
          <form method="post">
            <h1>Admin</h1>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
            <label>Sifre<input type="password" name="password" autocomplete="current-password" required autofocus></label>
            <button type="submit">Giris Yap</button>
          </form>
        </body>
        </html>
        """,
        error=error,
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    active_tab = request.args.get("tab", "rsvp")
    rows = load_rsvps()
    memories = load_memory_uploads()
    storage = upload_storage_summary()
    storage_status = "good"
    storage_message = "Site sagligi iyi gorunuyor."
    if storage["disk_free_gb"] < 5:
        storage_status = "danger"
        storage_message = "Disk alani kritik seviyede, yuklemeler etkilenebilir."
    elif storage["disk_free_gb"] < 20:
        storage_status = "warn"
        storage_message = "Disk alani dusuyor, yakinda temizlik gerekebilir."
    status_filter = request.args.get("status", "all")
    if status_filter in {"coming", "not-coming"}:
        visible_rows = [row for row in rows if row["status"] == status_filter]
    else:
        visible_rows = rows

    return render_template_string(
        """
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Admin Panel</title>
          <style>
            :root{--gold:#b8892d;--ink:#3d2b1f;--muted:#7a6a5f;--line:#ead8bc;--paper:#fffaf3}
            *{box-sizing:border-box}
            body{margin:0;background:#f8f1e7;color:var(--ink);font-family:Arial,sans-serif}
            .wrap{width:min(1180px,calc(100vw - 28px));margin:0 auto;padding:28px 0 52px}
            .top{display:flex;gap:16px;align-items:center;justify-content:space-between;margin-bottom:22px}
            h1{margin:0;font-family:Georgia,serif;font-size:clamp(34px,7vw,58px);color:#7d581c}
            .logout{color:var(--gold);font-weight:800;text-decoration:none}
            .tabs{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 20px}
            .tabs a{border:1px solid var(--line);background:#fff;color:var(--ink);padding:12px 16px;border-radius:999px;text-decoration:none;font-weight:800}
            .tabs a.active{background:var(--gold);border-color:var(--gold);color:#fff}
            .health-card{display:grid;grid-template-columns:1fr auto;gap:14px;align-items:center;margin:0 0 18px;background:rgba(255,250,243,.86);border:1px solid var(--line);border-radius:16px;padding:16px;box-shadow:0 14px 34px rgba(73,45,20,.07)}
            .health-card strong{display:block;font-size:18px;color:#7d581c}
            .health-card p{margin:6px 0 0;color:var(--muted);font-weight:700}
            .health-metrics{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
            .health-metrics span{display:inline-flex;border:1px solid var(--line);border-radius:999px;background:#fff;padding:8px 10px;font-weight:900;color:var(--ink);font-size:12px}
            .health-card.warn{border-color:#d9ad49;background:#fff8e8}
            .health-card.danger{border-color:#dc8c8c;background:#fff0f0}
            .admin-actions{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}
            .admin-actions a{border:1px solid var(--line);background:#fff;color:var(--gold);padding:11px 14px;border-radius:12px;text-decoration:none;font-weight:900}
            .admin-actions a.primary{background:var(--gold);border-color:var(--gold);color:#fff}
            .stats{display:grid;grid-template-columns:repeat(6,minmax(130px,1fr));gap:12px;margin-bottom:18px}
            .stats.memories{grid-template-columns:repeat(3,minmax(160px,1fr))}
            .stat{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 14px 34px rgba(73,45,20,.08)}
            .stat small{display:block;color:var(--muted);font-weight:800;text-transform:uppercase;font-size:11px;letter-spacing:.08em}
            .stat strong{display:block;margin-top:8px;font-size:28px;color:var(--gold)}
            .filters{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
            .filters a{border:1px solid var(--line);background:#fff;color:var(--ink);padding:10px 14px;border-radius:999px;text-decoration:none;font-weight:800}
            .filters a.active{background:var(--gold);color:#fff;border-color:var(--gold)}
            .table-card{overflow:auto;background:rgba(255,250,243,.74);border:1px solid var(--line);border-radius:16px}
            table{width:100%;border-collapse:collapse;min-width:820px}
            th,td{padding:14px 16px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
            th{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#8a6c43;background:#fff7ea}
            tr:last-child td{border-bottom:0}
            .pill{display:inline-flex;border-radius:999px;padding:6px 10px;font-weight:800;font-size:12px}
            .coming{background:#edf8ef;color:#26713a}
            .not-coming{background:#fff0f0;color:#a33}
            .note{max-width:360px;white-space:pre-wrap;line-height:1.55}
            .empty{padding:28px;text-align:center;color:var(--muted);font-weight:700}
            .memory-groups{display:grid;gap:16px}
            .bulk-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 16px;background:rgba(255,250,243,.82);border:1px solid var(--line);border-radius:16px;padding:14px}
            .bulk-actions label{display:flex;gap:8px;align-items:center;font-weight:900;color:var(--ink)}
            .bulk-actions button{border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--gold);padding:10px 14px;font-weight:900;cursor:pointer}
            .bulk-actions .bulk-delete{background:#fff0f0;color:#a33;border-color:#efc4c4}
            .memory-card{background:rgba(255,250,243,.82);border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:0 14px 34px rgba(73,45,20,.07)}
            .memory-head{display:flex;gap:12px;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
            .memory-head h2{margin:0;font-family:Georgia,serif;font-size:24px;color:#7d581c}
            .memory-head p{margin:5px 0 0;color:var(--muted);font-weight:700;font-size:13px}
            .memory-meta{display:flex;gap:12px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
            .group-select{display:flex;gap:8px;align-items:center;border:1px solid var(--line);border-radius:999px;background:#fff;padding:8px 12px;color:var(--gold);font-weight:900;cursor:pointer}
            .group-select .checkmark{width:18px;height:18px;border:2px solid var(--gold);border-radius:5px;background:#fff;display:grid;place-items:center;color:#fff;font-size:12px;line-height:1}
            .group-select.active .checkmark{background:var(--gold)}
            .group-select.partial .checkmark{background:#fff7ea;color:var(--gold)}
            .file-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:10px}
            .file-card{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
            .file-check{display:flex;gap:7px;align-items:center;padding:8px 10px;border-bottom:1px solid var(--line);font-weight:900;color:var(--muted);font-size:13px}
            .file-check input{width:16px;height:16px;accent-color:var(--gold)}
            .preview{height:82px;background:#f0e4d1;display:grid;place-items:center;color:var(--gold);font-weight:900;font-size:13px}
            .preview img,.preview video{width:100%;height:100%;object-fit:cover}
            .file-info{padding:9px}
            .file-info strong{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}
            .file-info small{display:block;margin-top:5px;color:var(--muted);font-size:11px}
            .file-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:9px}
            .file-actions a,.file-actions button{display:grid;place-items:center;min-height:32px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--gold);font-weight:900;text-decoration:none;font-size:12px;cursor:pointer}
            .file-actions .open{background:#fff7ea}
            .file-actions .download{background:#f7efe1}
            .file-actions .delete{background:#fff0f0;color:#a33;border-color:#efc4c4;width:100%}
            .file-actions form{margin:0}
            .row-delete{margin:0}
            .row-delete button{border:1px solid #efc4c4;border-radius:10px;background:#fff0f0;color:#a33;padding:9px 12px;font-weight:900;cursor:pointer}
            @media(max-width:860px){.top{align-items:flex-start;flex-direction:column}.health-card{grid-template-columns:1fr}.health-metrics{justify-content:flex-start}.stats,.stats.memories{grid-template-columns:repeat(2,1fr)}}
          </style>
        </head>
        <body>
          <main class="wrap">
            <div class="top">
              <div>
                <h1>Admin Paneli</h1>
                <p>Katilim cevaplari, notlar ve yuklenen anilar.</p>
              </div>
              <a class="logout" href="{{ url_for('admin_logout') }}">Cikis</a>
            </div>

            <nav class="tabs">
              <a class="{{ 'active' if active_tab == 'rsvp' else '' }}" href="{{ url_for('admin_dashboard') }}">Katilim Durumu</a>
              <a class="{{ 'active' if active_tab == 'memories' else '' }}" href="{{ url_for('admin_dashboard', tab='memories') }}">Anilarimizi Saklayalim</a>
            </nav>

            <section class="health-card {{ storage_status }}">
              <div>
                <strong>Site sagligi</strong>
                <p>{{ storage_message }}</p>
              </div>
              <div class="health-metrics">
                <span>Disk bos: {{ storage.disk_free_gb }} GB</span>
                <span>Upload: {{ storage.total_size_mb }} MB</span>
                <span>Dosya: {{ storage.file_count }}</span>
              </div>
            </section>

            <div class="admin-actions">
              <a class="primary" href="{{ url_for('public_memories') }}" target="_blank" rel="noopener">Sizden Gelenler sayfasini ac</a>
              <a href="{{ url_for('health_check') }}" target="_blank" rel="noopener">Health JSON</a>
            </div>

            {% if active_tab == 'memories' %}
            <section class="stats memories">
              <div class="stat"><small>Kisi/Klasor</small><strong>{{ memories.summary.guest_count }}</strong></div>
              <div class="stat"><small>Dosya sayisi</small><strong>{{ memories.summary.file_count }}</strong></div>
              <div class="stat"><small>Toplam boyut</small><strong>{{ memories.summary.total_size }}</strong></div>
            </section>

            <section class="memory-groups">
              {% if memories.groups %}
              <form id="bulkMemoryForm" class="bulk-actions" method="post">
                <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                <label><input id="selectAllMemories" type="checkbox"> Tumunu sec</label>
                <button type="submit" formaction="{{ url_for('admin_bulk_download_uploads') }}">Secilenleri ZIP indir</button>
                <button class="bulk-delete" type="submit" formaction="{{ url_for('admin_bulk_delete_uploads') }}" onclick="return confirm('Secilen dosyalar silinsin mi?')">Secilenleri sil</button>
              </form>
              {% for group in memories.groups %}
              {% set group_id = loop.index0 %}
              <article class="memory-card">
                <div class="memory-head">
                  <div>
                    <h2>{{ group.guest }}</h2>
                    <p>{{ group.file_count }} dosya · {{ group.total_size_label }}</p>
                  </div>
                  <div class="memory-meta">
                    <button class="group-select group-check" type="button" data-group="{{ group_id }}" aria-pressed="false">
                      <span class="checkmark" aria-hidden="true">✓</span>
                      Klasoru sec
                    </button>
                    <p>{{ group.updated_at }}</p>
                  </div>
                </div>
                <div class="file-grid">
                  {% for file in group.files %}
                  <div class="file-card">
                    <label class="file-check">
                      <input class="memory-checkbox" type="checkbox" name="files" value="{{ file.relative_path }}" form="bulkMemoryForm" data-group="{{ group_id }}">
                      Sec
                    </label>
                    <div class="preview">
                      {% if file.type == 'image' %}
                      <img src="{{ url_for('admin_upload_file', filename=file.relative_path) }}" alt="{{ file.name }}" loading="lazy" decoding="async">
                      {% elif file.type == 'video' %}
                      <span>Video</span>
                      {% else %}
                      <span>Dosya</span>
                      {% endif %}
                    </div>
                    <div class="file-info">
                      <strong title="{{ file.name }}">{{ file.name }}</strong>
                      <small>{{ file.size }} · {{ file.updated_at }}</small>
                      <div class="file-actions">
                        <a class="open" href="{{ url_for('admin_upload_file', filename=file.relative_path) }}" target="_blank" rel="noopener">Ac</a>
                        <a class="download" href="{{ url_for('admin_upload_file', filename=file.relative_path, download='1') }}">Indir</a>
                        <form method="post" action="{{ url_for('admin_delete_upload', filename=file.relative_path) }}" onsubmit="return confirm('Bu dosya silinsin mi?')">
                          <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                          <button class="delete" type="submit">Sil</button>
                        </form>
                      </div>
                    </div>
                  </div>
                  {% endfor %}
                </div>
              </article>
              {% endfor %}
              {% else %}
              <div class="empty">Henuz yuklenen ani dosyasi yok.</div>
              {% endif %}
            </section>
            {% else %}
            <section class="stats">
              <div class="stat"><small>Toplam cevap</small><strong>{{ summary.total_responses }}</strong></div>
              <div class="stat"><small>Gelen cevap</small><strong>{{ summary.coming_responses }}</strong></div>
              <div class="stat"><small>Gelmeyen cevap</small><strong>{{ summary.not_coming_responses }}</strong></div>
              <div class="stat"><small>Gelecek kisi</small><strong>{{ summary.coming_people }}</strong></div>
              <div class="stat"><small>Gelmeyen kisi</small><strong>{{ summary.not_coming_people }}</strong></div>
              <div class="stat"><small>Not sayisi</small><strong>{{ summary.notes }}</strong></div>
            </section>

            <nav class="filters">
              <a class="{{ 'active' if status_filter == 'all' else '' }}" href="{{ url_for('admin_dashboard') }}">Tum liste</a>
              <a class="{{ 'active' if status_filter == 'coming' else '' }}" href="{{ url_for('admin_dashboard', status='coming') }}">Gelenler</a>
              <a class="{{ 'active' if status_filter == 'not-coming' else '' }}" href="{{ url_for('admin_dashboard', status='not-coming') }}">Gelmeyenler</a>
            </nav>

            <section class="table-card">
              {% if rows %}
              <table>
                <thead>
                  <tr>
                    <th>Tarih</th>
                    <th>Ad Soyad</th>
                    <th>Durum</th>
                    <th>Kisi</th>
                    <th>Not</th>
                    <th>Islem</th>
                  </tr>
                </thead>
                <tbody>
                  {% for row in rows %}
                  <tr>
                    <td>{{ row.received_at|replace('T', ' ')|replace('Z', '') }}</td>
                    <td><strong>{{ row.name or '-' }}</strong></td>
                    <td><span class="pill {{ row.status }}">{{ 'Geliyor' if row.status == 'coming' else 'Gelmiyor' }}</span></td>
                    <td>{{ row.guests }}</td>
                    <td class="note">{{ row.note or '-' }}</td>
                    <td>
                      <form class="row-delete" method="post" action="{{ url_for('admin_delete_rsvp', row_id=row.id) }}" onsubmit="return confirm('Bu katilim kaydi silinsin mi?')">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                        <button type="submit">Sil</button>
                      </form>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
              {% else %}
              <div class="empty">Henuz kayit yok.</div>
              {% endif %}
            </section>
            {% endif %}
          </main>
          <script>
            const selectAllMemories = document.getElementById('selectAllMemories');
            const memoryCheckboxes = [...document.querySelectorAll('.memory-checkbox')];
            const groupChecks = [...document.querySelectorAll('.group-check')];
            const syncMemoryChecks = () => {
              if(selectAllMemories){
                const selectedCount = memoryCheckboxes.filter(box => box.checked).length;
                selectAllMemories.checked = memoryCheckboxes.length > 0 && selectedCount === memoryCheckboxes.length;
                selectAllMemories.indeterminate = selectedCount > 0 && selectedCount < memoryCheckboxes.length;
              }
              groupChecks.forEach(group => {
                const boxes = memoryCheckboxes.filter(box => box.dataset.group === group.dataset.group);
                const selectedCount = boxes.filter(box => box.checked).length;
                const allSelected = boxes.length > 0 && selectedCount === boxes.length;
                const partiallySelected = selectedCount > 0 && selectedCount < boxes.length;
                group.classList.toggle('active', allSelected);
                group.classList.toggle('partial', partiallySelected);
                group.setAttribute('aria-pressed', allSelected ? 'true' : 'false');
              });
            };
            selectAllMemories?.addEventListener('change', () => {
              memoryCheckboxes.forEach(box => { box.checked = selectAllMemories.checked; });
              syncMemoryChecks();
            });
            groupChecks.forEach(group => group.addEventListener('click', () => {
              const boxes = memoryCheckboxes.filter(box => box.dataset.group === group.dataset.group);
              const shouldSelect = boxes.some(box => !box.checked);
              boxes.forEach(box => { box.checked = shouldSelect; });
              syncMemoryChecks();
            }));
            memoryCheckboxes.forEach(box => box.addEventListener('change', syncMemoryChecks));
            syncMemoryChecks();
          </script>
        </body>
        </html>
        """,
        rows=visible_rows,
        summary=rsvp_summary(rows),
        status_filter=status_filter,
        active_tab=active_tab,
        memories=memories,
        csrf_token=admin_csrf_token(),
        storage=storage,
        storage_status=storage_status,
        storage_message=storage_message,
    )


@app.route("/admin/uploads/<path:filename>")
@admin_required
def admin_upload_file(filename: str):
    resolve_upload_path(filename)
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=request.args.get("download") == "1")


@app.route("/admin/rsvp/<row_id>/delete", methods=["POST"])
@admin_required
def admin_delete_rsvp(row_id: str):
    rows = load_rsvps()
    remaining = [row for row in rows if row.get("id") != row_id]
    if len(remaining) != len(rows):
        save_rsvps(remaining)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/uploads/bulk-download", methods=["POST"])
@admin_required
def admin_bulk_download_uploads():
    paths = selected_upload_paths()
    if not paths:
        return redirect(url_for("admin_dashboard", tab="memories"))

    temp_file = tempfile.NamedTemporaryFile(prefix="shandfi-anilar-", suffix=".zip", dir=TMP_DOWNLOAD_DIR, delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for filename, path in paths:
            archive.write(path, zip_arcname(filename, path))

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    def cleanup_zip():
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass

    response = send_file(
        temp_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"shandfi-anilar-{stamp}.zip",
    )
    response.call_on_close(cleanup_zip)
    return response


@app.route("/admin/uploads/bulk-delete", methods=["POST"])
@admin_required
def admin_bulk_delete_uploads():
    paths = selected_upload_paths()
    for _, path in paths:
        try:
            path.unlink()
            cleanup_empty_upload_parent(path)
        except OSError:
            continue
    return redirect(url_for("admin_dashboard", tab="memories"))


@app.route("/admin/uploads/<path:filename>/delete", methods=["POST"])
@admin_required
def admin_delete_upload(filename: str):
    try:
        path = resolve_upload_path(filename)
    except FileNotFoundError:
        return redirect(url_for("admin_dashboard", tab="memories"))

    try:
        path.unlink()
    except OSError:
        return redirect(url_for("admin_dashboard", tab="memories", delete_error="1"))
    cleanup_empty_upload_parent(path)
    return redirect(url_for("admin_dashboard", tab="memories"))


@app.route("/api/health")
def health_check():
    return jsonify(
        {
            "success": True,
            "status": "ok",
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "uploads": upload_storage_summary(),
        }
    )


@app.route("/api/public-memories")
def public_memories_api():
    items = public_memory_items()
    return jsonify(
        {
            "success": True,
            "count": len(items),
            "items": [
                {
                    "guest": item["guest"],
                    "type": item["type"],
                    "url": url_for("public_upload_file", filename=item["relative_path"]),
                    "updated_at": item["updated_at"],
                }
                for item in items[:12]
            ],
        }
    )


@app.route("/sizden-gelenler")
def public_memories():
    items = public_memory_items()
    return render_template_string(
        """
        <!doctype html>
        <html lang="bg">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="robots" content="noindex, nofollow">
          <title>Sizden Gelenler | Fikrie & Şafak</title>
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600;700;800&family=Noto+Serif+Display:wght@500;600;700&display=swap" rel="stylesheet">
          <style>
            :root{--gold:#b8892d;--gold2:#ddb75b;--ink:#3d2b1f;--muted:#7a6a5f;--line:#ead8bc;--paper:#fffaf3}
            *{box-sizing:border-box}
            html{scroll-behavior:smooth}
            body{margin:0;background:
              radial-gradient(circle at 18% 4%, rgba(255,255,255,.94), transparent 34%),
              linear-gradient(180deg,#fffaf2,#f6ead6 52%,#fff9ee);color:var(--ink);font-family:Inter,Arial,sans-serif;overflow-x:hidden}
            body:before,body:after{content:'';position:fixed;z-index:-1;pointer-events:none;opacity:.34;background:url('/assets/floral-gold-door.webp') center/contain no-repeat}
            body:before{width:360px;height:520px;left:-170px;top:110px;transform:rotate(-4deg)}
            body:after{width:420px;height:600px;right:-220px;bottom:-80px;transform:rotate(8deg)}
            .topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px clamp(16px,4vw,42px);background:rgba(255,250,243,.9);border-bottom:1px solid rgba(222,196,148,.58);backdrop-filter:blur(16px)}
            .logo{font-family:'Noto Serif Display',Georgia,serif;font-size:28px;color:#6f4d1c;text-decoration:none;font-weight:700;letter-spacing:0}
            .logo span,.hero h1 span{color:var(--gold)}
            .nav{display:flex;gap:18px;align-items:center}
            .nav a{color:#6f4d1c;text-decoration:none;font-weight:800;font-size:14px}
            .actions{display:flex;gap:10px;align-items:center}
            .lang-switch{display:flex;gap:4px;padding:5px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.72)}
            .lang-switch button{border:0;border-radius:999px;background:transparent;color:#6f4d1c;padding:8px 10px;font-weight:900;cursor:pointer}
            .lang-switch button.active{background:linear-gradient(135deg,var(--gold),var(--gold2));color:#fff}
            .btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;border:1px solid rgba(184,137,45,.3);border-radius:14px;padding:12px 16px;background:rgba(255,255,255,.86);color:#6f4d1c;text-decoration:none;font-weight:900;cursor:pointer}
            .btn.primary{background:linear-gradient(135deg,var(--gold),var(--gold2));color:#fff;border-color:transparent}
            .hero{position:relative;min-height:440px;display:grid;place-items:center;text-align:center;padding:70px 18px 58px;overflow:hidden}
            .hero:before{content:'';position:absolute;inset:0;background:
              linear-gradient(180deg,rgba(48,31,20,.26),rgba(255,248,235,.58)),
              url('/assets/hero-arkaplan2.webp') center/cover no-repeat;opacity:.9}
            .hero-inner{position:relative;width:min(760px,100%);color:#fff;text-shadow:0 2px 18px rgba(45,28,18,.22)}
            .eyebrow{margin:0 0 12px;color:#d8ad45;font-weight:900;text-transform:uppercase;letter-spacing:.28em;font-size:12px}
            h1{margin:0;font-family:'Noto Serif Display',Georgia,serif;font-size:clamp(48px,10vw,90px);line-height:.92;color:#fff8eb}
            .hero p:not(.eyebrow){max-width:650px;margin:18px auto 0;line-height:1.7;font-weight:700}
            .hero-stats{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:26px}
            .hero-stats span,.hero-stats a{min-width:118px;border:1px solid rgba(255,255,255,.42);border-radius:14px;background:rgba(255,255,255,.18);padding:12px 14px;color:#fff;font-weight:900;backdrop-filter:blur(12px);text-decoration:none}
            .hero-stats .memory-count{color:#ffe2a0;border-color:rgba(221,183,91,.62);background:rgba(184,137,45,.22)}
            .hero-stats .share-btn{background:rgba(255,250,243,.9);color:#80591b;border-color:rgba(255,255,255,.68)}
            .wrap{width:min(1160px,calc(100vw - 28px));margin:0 auto;padding:44px 0 70px}
            .section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:22px}
            .section-head h2{margin:0;font-family:'Noto Serif Display',Georgia,serif;font-size:clamp(36px,7vw,66px);line-height:1;color:#7d581c}
            .section-head p{max-width:430px;margin:0;color:var(--muted);line-height:1.6;font-weight:700}
            .gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}
            .item{position:relative;display:grid;border:1px solid rgba(184,137,45,.28);border-radius:10px;overflow:hidden;background:#fffaf3;box-shadow:0 16px 34px rgba(73,45,20,.1);min-height:230px;cursor:pointer}
            .item img,.item video{width:100%;height:100%;aspect-ratio:4/5;object-fit:cover;display:block;filter:sepia(.08) contrast(.97) saturate(.95)}
            .item video{background:#2a201b}
            .caption{position:absolute;left:8px;right:8px;bottom:8px;border-radius:8px;background:rgba(255,250,243,.9);padding:8px 10px;color:#6f4d1c;font-size:12px;font-weight:900;backdrop-filter:blur(8px)}
            .caption small{display:block;color:var(--muted);font-weight:700;margin-top:3px}
            .empty{max-width:560px;margin:0 auto;padding:34px;border:1px solid var(--line);border-radius:14px;background:rgba(255,250,243,.86);text-align:center;color:var(--muted);font-weight:800}
            .lightbox{position:fixed;inset:0;z-index:50;display:none;place-items:center;padding:22px;background:rgba(28,20,17,.84);backdrop-filter:blur(10px)}
            .lightbox.open{display:grid}
            .lightbox img,.lightbox video{max-width:min(96vw,980px);max-height:84vh;border-radius:10px;box-shadow:0 24px 70px rgba(0,0,0,.35);background:#111}
            .lightbox img{display:block}.lightbox video{display:none}
            .lightbox.media-video img{display:none}.lightbox.media-video video{display:block}
            .close,.navbtn{position:fixed;border:1px solid rgba(255,255,255,.4);background:rgba(255,255,255,.88);color:#5a3b1c;border-radius:999px;width:44px;height:44px;font-size:28px;cursor:pointer}
            .close{top:18px;right:18px}.prev{left:18px}.next{right:18px}.navbtn{top:50%;transform:translateY(-50%)}
            @media(max-width:760px){.topbar{display:grid;grid-template-columns:auto 1fr;align-items:center;padding:12px 14px}.nav{grid-column:1/-1;display:flex;justify-content:center;gap:8px;order:3;margin-top:10px}.nav a{font-size:12px;padding:8px 10px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.72)}.actions{justify-content:flex-end}.logo{font-size:25px}.hero{min-height:360px;padding-top:38px}.section-head{display:block}.section-head p{margin-top:10px}.gallery{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.item{min-height:170px}.caption{font-size:11px}.lang-switch button{padding:7px 8px;font-size:12px}.hero-stats span,.hero-stats a{min-width:132px}.hero-stats{margin-top:20px}}
          </style>
        </head>
        <body>
          <header class="topbar">
            <a class="logo" href="/">F<span>&</span>Ş</a>
            <nav class="nav" aria-label="Navigation">
              <a href="/" data-i18n="navInvite">Покана</a>
              <a href="/?share=memories" data-i18n="navShare">Сподели спомени</a>
            </nav>
            <div class="actions">
              <div class="lang-switch" aria-label="Language selector">
                <button type="button" data-lang="bg">🇧🇬 BG</button>
                <button type="button" data-lang="tr">🇹🇷 TR</button>
                <button type="button" data-lang="en">🇬🇧 EN</button>
              </div>
            </div>
          </header>

          <section class="hero">
            <div class="hero-inner">
              <p class="eyebrow" data-i18n="kicker">От вас</p>
              <h1 data-i18n="heroTitle">Споделени спомени</h1>
              <p data-i18n="heroText">Снимките и видеата, които ни изпратихте, се събират тук като малък албум от нашия ден.</p>
              <div class="hero-stats">
                <span class="memory-count">{{ items|length }} <i data-i18n="countLabel">спомена</i></span>
                <a class="share-btn" href="/?qr=1" data-i18n="shareButton">Споделете спомени</a>
              </div>
            </div>
          </section>

          <main class="wrap" id="gallery">
            <div class="section-head">
              <div>
                <p class="eyebrow" data-i18n="galleryKicker">Галерия</p>
                <h2 data-i18n="galleryTitle">Сизден gelenler</h2>
              </div>
              <p data-i18n="galleryText">Благодарим ви, че споделихте тези красиви моменти с нас.</p>
            </div>
            {% if items %}
            <section class="gallery">
              {% for item in items %}
              <button class="item" type="button" data-media="{{ item.type }}" data-src="{{ url_for('public_upload_file', filename=item.relative_path) }}">
                {% if item.type == 'image' %}
                <img src="{{ url_for('public_upload_file', filename=item.relative_path) }}" alt="{{ item.guest }} anısı" loading="lazy" decoding="async">
                {% else %}
                <video src="{{ url_for('public_upload_file', filename=item.relative_path) }}" preload="metadata" muted playsinline></video>
                {% endif %}
                <div class="caption">{{ item.guest }}<small>{{ item.updated_at }}</small></div>
              </button>
              {% endfor %}
            </section>
            {% else %}
            <div class="empty" data-i18n="empty">Все още няма споделени спомени.</div>
            {% endif %}
          </main>

          <div class="lightbox" id="lightbox" aria-hidden="true">
            <button class="close" id="closeLightbox" type="button" aria-label="Close">×</button>
            <button class="navbtn prev" id="prevMedia" type="button" aria-label="Previous">‹</button>
            <img id="lightboxImg" alt="Memory preview">
            <video id="lightboxVideo" controls playsinline></video>
            <button class="navbtn next" id="nextMedia" type="button" aria-label="Next">›</button>
          </div>

          <script>
            const translations = {
              bg:{navInvite:'Покана',navShare:'Сподели спомени',kicker:'От вас',heroTitle:'Споделени спомени',heroText:'Снимките и видеата, които ни изпратихте, се събират тук като малък албум от нашия ден.',countLabel:'спомена',shareButton:'Споделете спомени',galleryKicker:'Галерия',galleryTitle:'Нашите гости',galleryText:'Благодарим ви, че споделихте тези красиви моменти с нас.',empty:'Все още няма споделени спомени.'},
              tr:{navInvite:'Davetiye',navShare:'Anı Paylaş',kicker:'Sizden gelenler',heroTitle:'Paylaşılan Anılar',heroText:'Bize gönderdiğiniz fotoğraf ve videolar burada küçük bir anı albümü gibi toplanıyor.',countLabel:'anı',shareButton:'Anılarınızı Paylaşın',galleryKicker:'Galeri',galleryTitle:'Sizden Gelenler',galleryText:'Bu güzel anları bizimle paylaştığınız için çok teşekkür ederiz.',empty:'Henüz paylaşılan anı yok.'},
              en:{navInvite:'Invitation',navShare:'Share Memories',kicker:'From you',heroTitle:'Shared Memories',heroText:'The photos and videos you sent us gather here as a small album from our day.',countLabel:'memories',shareButton:'Share Your Memories',galleryKicker:'Gallery',galleryTitle:'From Our Guests',galleryText:'Thank you for sharing these beautiful moments with us.',empty:'No shared memories yet.'}
            };
            let currentLang = localStorage.getItem('siteLang') || 'bg';
            const $ = (selector, root = document) => root.querySelector(selector);
            const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
            function applyLanguage(lang){
              currentLang = translations[lang] ? lang : 'bg';
              localStorage.setItem('siteLang', currentLang);
              document.documentElement.lang = currentLang;
              $$('[data-i18n]').forEach(el => {
                const text = translations[currentLang][el.dataset.i18n];
                if(text) el.textContent = text;
              });
              $$('[data-lang]').forEach(btn => btn.classList.toggle('active', btn.dataset.lang === currentLang));
            }
            $$('[data-lang]').forEach(btn => btn.addEventListener('click', () => applyLanguage(btn.dataset.lang)));
            applyLanguage(currentLang);

            const items = $$('.item');
            const lightbox = $('#lightbox');
            const img = $('#lightboxImg');
            const video = $('#lightboxVideo');
            let active = 0;
            function show(index){
              if(!items.length) return;
              active = (index + items.length) % items.length;
              const item = items[active];
              const isVideo = item.dataset.media === 'video';
              lightbox.classList.toggle('media-video', isVideo);
              if(isVideo){
                img.removeAttribute('src');
                video.src = item.dataset.src;
                video.play().catch(() => {});
              }else{
                video.pause();
                video.removeAttribute('src');
                const itemImg = $('img', item);
                img.src = itemImg.src;
                img.alt = itemImg.alt;
              }
              lightbox.classList.add('open');
              lightbox.setAttribute('aria-hidden','false');
            }
            function close(){
              video.pause();
              video.removeAttribute('src');
              img.removeAttribute('src');
              lightbox.classList.remove('open','media-video');
              lightbox.setAttribute('aria-hidden','true');
            }
            items.forEach((item,index) => item.addEventListener('click', () => show(index)));
            $('#closeLightbox')?.addEventListener('click', close);
            $('#prevMedia')?.addEventListener('click', () => show(active - 1));
            $('#nextMedia')?.addEventListener('click', () => show(active + 1));
            lightbox?.addEventListener('click', event => { if(event.target === lightbox) close(); });
            addEventListener('keydown', event => {
              if(!lightbox?.classList.contains('open')) return;
              if(event.key === 'Escape') close();
              if(event.key === 'ArrowLeft') show(active - 1);
              if(event.key === 'ArrowRight') show(active + 1);
            });
          </script>
        </body>
        </html>
        """,
        items=items,
    )


@app.route("/sizden-gelenler/dosya/<path:filename>")
def public_upload_file(filename: str):
    try:
        resolve_upload_path(filename)
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Not found"}), 404
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/<path:path>")
def serve_path(path: str):
    if path.startswith("api/"):
        return jsonify({"success": False, "error": "Not found"}), 404
    requested = SITE_DIR / path
    if requested.exists() and requested.is_file():
        return send_from_directory(SITE_DIR, path)
    return send_from_directory(SITE_DIR, "index.html")


@app.route("/api/memories/upload", methods=["POST"])
def upload_memories():
    if "memories" not in request.files:
        return jsonify({"success": False, "error": "No files provided."}), 400

    files = request.files.getlist("memories")
    if not files:
        return jsonify({"success": False, "error": "No files provided."}), 400

    for file in files:
        filename = secure_filename(file.filename)
        if not filename or not allowed_file(filename):
            return jsonify({"success": False, "error": "Invalid file type."}), 400

    guest_name = request.form.get("guestName", "").strip() or "guest"
    safe_folder = safe_guest_folder(guest_name)
    guest_dir = UPLOAD_DIR / safe_folder
    guest_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for index, file in enumerate(files, start=1):
        filename = secure_filename(file.filename)
        if not filename or not allowed_file(filename):
            return jsonify({"success": False, "error": "Invalid file type."}), 400

        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        destination = guest_dir / f"{stamp}_{index}_{filename}"
        file.save(destination)
        try:
            saved_files.append(str(destination.relative_to(BASE_DIR)))
        except ValueError:
            saved_files.append(str(destination.relative_to(UPLOAD_DIR)))

    return jsonify({"success": True, "files": saved_files})


@app.route("/api/rsvp", methods=["POST"])
def rsvp():
    payload = request.form.to_dict(flat=True)
    payload["received_at"] = datetime.utcnow().isoformat() + "Z"
    payload = normalize_rsvp(payload)
    with RSVP_JSONL_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    with RSVP_TEXT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"{payload}\n")
    return jsonify({"success": True, "payload": payload})


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"success": False, "error": "Upload exceeded the maximum allowed size."}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
