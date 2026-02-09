# PowerShell 프로필에 UTF-8 설정 추가 (한글 깨짐 방지)
# 한 번만 실행하면 이후 새 PowerShell 창에서 자동 적용됩니다.
# 실행: .\scripts\setup-utf8-profile.ps1

$utf8Lines = @"

# UTF-8 인코딩 (한글 깨짐 방지) - CursorProject
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
`$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
"@

$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath

if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

if (Test-Path $profilePath) {
    $content = Get-Content $profilePath -Raw
    if ($content -match "chcp 65001") {
        Write-Host "이미 UTF-8 설정이 프로필에 있습니다: $profilePath"
        exit 0
    }
}

Add-Content -Path $profilePath -Value $utf8Lines
Write-Host "UTF-8 설정을 프로필에 추가했습니다: $profilePath"
Write-Host "새 PowerShell 창을 열면 적용됩니다."
