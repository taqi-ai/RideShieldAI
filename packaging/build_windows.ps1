# Builds the Windows desktop app and zips it for release.
#
#   powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
#
# Needs the project's virtual environment (.venv) with the requirements installed. PyInstaller is installed
# into it if missing. Prints the file size and SHA-256 to paste into web\src\config\download.ts.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { throw "Create the virtual environment first: python -m venv .venv ; .venv\Scripts\pip install -r requirements.txt" }

& $py -m pip install --quiet pyinstaller
& $py -m PyInstaller packaging\RideShield.spec --noconfirm --distpath "$root\dist" --workpath "$root\build"

$zip = Join-Path $root 'dist\RideShield-Windows.zip'
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "$root\dist\RideShield" -DestinationPath $zip -CompressionLevel Optimal

$size = (Get-Item $zip).Length
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
$unpacked = (Get-ChildItem "$root\dist\RideShield" -Recurse -File | Measure-Object Length -Sum).Sum
"`nBuilt $zip"
"sizeMiB:     {0:N0}" -f ($size / 1MB)
"unpackedGiB: {0:N2}" -f ($unpacked / 1GB)
"sha256:      $hash"
