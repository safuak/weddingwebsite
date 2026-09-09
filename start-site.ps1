$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

function Test-Port {
  param([int]$Port)
  $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port $Port -WarningAction SilentlyContinue
  return [bool]$connection.TcpTestSucceeded
}

if (-not (Test-Path -LiteralPath ".\.venv\Scripts\waitress-serve.exe")) {
  Write-Host "Creating Python virtual environment..."
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

if (-not (Test-Port 5000)) {
  Write-Host "Starting Python app on http://127.0.0.1:5000 ..."
  Start-Process -FilePath ".\.venv\Scripts\waitress-serve.exe" `
    -ArgumentList @("--host=127.0.0.1", "--port=5000", "--threads=16", "--connection-limit=200", "--channel-timeout=1800", "app:app") `
    -WorkingDirectory $Root `
    -RedirectStandardOutput ".\waitress.out.log" `
    -RedirectStandardError ".\waitress.err.log" `
    -WindowStyle Hidden
} else {
  Write-Host "Python app already listens on port 5000."
}

Start-Sleep -Seconds 2

if (-not (Test-Port 443)) {
  Write-Host "Starting Caddy HTTPS proxy..."
  .\caddy.exe start --config Caddyfile
} else {
  Write-Host "HTTPS proxy already listens on port 443."
}

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Site should be available at:"
Write-Host "https://shandfi.com"
Write-Host "Admin panel:"
Write-Host "https://shandfi.com/admin"
Write-Host ""
Write-Host "Local checks:"
Write-Host "Python app port 5000: $(Test-Port 5000)"
Write-Host "HTTPS port 443: $(Test-Port 443)"
