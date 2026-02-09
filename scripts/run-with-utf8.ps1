# UTF-8 인코딩 설정 후 명령 실행 (한글 깨짐 방지)
# 사용: .\scripts\run-with-utf8.ps1 python -m src.stock_data
# 사용: .\scripts\run-with-utf8.ps1 pytest tests/ -v

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

if ($args.Count -eq 0) {
    Write-Host "사용법: .\scripts\run-with-utf8.ps1 <명령> [인자...]"
    Write-Host "예: .\scripts\run-with-utf8.ps1 python -m src.stock_data"
    exit 0
}

# 첫 번째 인자를 명령, 나머지를 인자로 실행 (공백으로 묶이지 않도록)
$cmd = $args[0]
$cmdArgs = @()
if ($args.Count -gt 1) {
    $cmdArgs = $args[1..($args.Count - 1)]
}
# 가상환경 python 우선 사용 (프로젝트 루트에서 실행 시)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if ($cmd -eq "python" -and (Test-Path $venvPython)) {
    $cmd = $venvPython
}
& $cmd @cmdArgs
