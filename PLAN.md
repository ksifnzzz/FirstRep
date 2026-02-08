# CursorProject — 새 Python 프로젝트 & 기존 GitHub 저장소 연결 계획

## 1단계: 로컬 프로젝트 구조 만들기 ✅

- [x] 표준 Python 프로젝트 폴더 구조
- [x] `requirements.txt` (의존성 관리)
- [x] `.gitignore` (Python/GitHub용)
- [x] `README.md` (프로젝트 설명)

**폴더 구조:**
```
CursorProject/
├── src/              # 소스 코드
├── tests/            # 테스트
├── docs/             # 문서 (선택)
├── requirements.txt
├── README.md
├── .gitignore
└── PLAN.md
```

---

## 2단계: 가상 환경 설정

```powershell
# 프로젝트 폴더에서
python -m venv .venv

# 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

`.venv`는 이미 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다.

---

## 3단계: Git 저장소 초기화

```powershell
git init
git add .
git commit -m "Initial commit: Python project setup"
```

---

## 4단계: 기존 GitHub 저장소에 연결

1. **기존 저장소 URL 확인**
   - GitHub 저장소 페이지 → **Code** 버튼 → URL 복사  
   - HTTPS: `https://github.com/USERNAME/REPO_NAME.git`  
   - SSH: `git@github.com:USERNAME/REPO_NAME.git`

2. **로컬과 원격 연결**

   ```powershell
   git remote add origin https://github.com/USERNAME/REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

   `USERNAME`과 `REPO_NAME`을 본인 저장소 정보로 바꾸세요.

3. **원격에 이미 커밋이 있을 때** (README 등으로 비어 있지 않을 때)
   - 먼저 가져온 뒤 합치기:
   ```powershell
   git pull origin main --allow-unrelated-histories
   # 충돌 있으면 해결 후
   git push -u origin main
   ```
   - 또는 로컬 내용으로 원격을 덮어쓰기 (**원격 내용이 사라지므로 주의**):
   ```powershell
   git push -u origin main --force
   ```

4. **SSH 사용 시**
   ```powershell
   git remote add origin git@github.com:USERNAME/REPO_NAME.git
   ```

---

## 5단계: 이후 개발 흐름

- 코드 수정 → `git add .` → `git commit -m "메시지"` → `git push`
- 새 패키지 설치 시: `pip install 패키지명` 후 `pip freeze > requirements.txt`
- 테스트: `tests/`에 테스트 작성 후 `pytest` 실행

---

## 체크리스트

| 단계 | 내용 | 완료 |
|------|------|------|
| 1 | 프로젝트 구조 생성 | ✅ |
| 2 | 가상 환경 생성 및 활성화 | ⬜ |
| 3 | `git init` 및 첫 커밋 | ⬜ |
| 4 | 기존 GitHub 저장소 연결 | ⬜ |
| 5 | `remote` 추가 및 `push` | ⬜ |
