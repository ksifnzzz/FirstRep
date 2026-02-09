# CursorProject

Python 프로젝트 템플릿입니다. (환경: Windows, PowerShell)

## 설정

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 실행

```powershell
python -m src.main
```

## 테스트

```powershell
pip install pytest
pytest tests/
```

## 한글 깨짐 방지 (UTF-8)

- **이 프로젝트**: Cursor에서 터미널을 열면 기본으로 UTF-8 프로필이 적용됩니다.
- **한 번에 실행만 UTF-8로**:  
  `.\scripts\run-with-utf8.ps1 python -m src.stock_data`  
  `.\scripts\run-with-utf8.ps1 pytest tests/ -v`
- **PowerShell 전체에 적용**:  
  `.\scripts\setup-utf8-profile.ps1` 실행 후 새 PowerShell 창부터 적용됩니다.

## 프로젝트 계획

자세한 단계는 [PLAN.md](PLAN.md)를 참고하세요.
