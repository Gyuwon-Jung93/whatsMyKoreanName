# 영어 이름 → 한국어 이름 추천 서비스 (Project 3D2Z)

## 개요

영어 이름을 입력하면 트렌드와 발음을 고려해 맞춤 한국어 이름을 추천해 주는 웹 서비스입니다. React SPA(프론트엔드)와 Flask API(백엔드)로 구성되며, Vercel CDN + Serverless Functions로 배포됩니다.

## 폴더 구조

```
KoreanName/
├── frontend/      # React + Vite 소스 코드
├── backend/       # Flask API 소스 코드
├── .github/       # GitHub Actions 워크플로
└── README.md      # 현재 문서
```

## 빠른 시작

### 1. 필수 도구

-   Node.js 20.x LTS
-   Python 3.11+
-   pnpm 8.x (권장) 또는 npm/yarn
-   (선택) direnv: `.envrc` 자동 로딩

### 2. 프로젝트 클론

```bash
$ git clone <repo-url> && cd KoreanName
```

### 3. 환경 변수 설정

루트에 `.env` 파일을 만들고 다음 값을 채워 주세요.

```
# 공용
VITE_SENTRY_DSN=
PYTHON_ENV=development
SENTRY_DSN=
```

### 4. 의존성 설치

프론트엔드와 백엔드 각각 설치합니다.

```bash
# frontend
$ cd frontend
$ pnpm install

# backend
$ cd ../backend
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
```

### 5. 로컬 개발 서버 실행

터미널 2개를 열어 다음 명령을 각각 실행하세요.

```bash
# 터미널 1 - frontend
$ cd frontend
$ pnpm dev

# 터미널 2 - backend
$ cd backend
$ source .venv/bin/activate
$ python app.py
```

프론트엔드는 `http://localhost:5173`, 백엔드는 `http://localhost:5000` 에서 실행됩니다.

## 테스트 & 린트

```bash
# frontend
$ pnpm test          # vitest 유닛 테스트
$ pnpm lint          # eslint + prettier 체크
$ pnpm cy:open       # cypress e2e 테스트 (UI)

# backend
$ pytest             # 파이썬 단위 테스트
$ ruff .             # 파이썬 린트
```

## 배포

### Vercel

`vercel.json` 파일과 `vercel` CLI 또는 GitHub Actions(Vercel 제공)으로 자동 배포됩니다. `main` 브랜치에 푸시 시 프로덕션으로, 기타 브랜치에는 프리뷰 배포가 생성됩니다.

### GitHub Actions

`.github/workflows/ci.yml` 워크플로가 다음을 수행합니다.

1. 프론트엔드 의존성 설치 및 테스트
2. 백엔드 의존성 설치 및 테스트
3. 코드 린트 및 타입 체크
4. (통과 시) Vercel 프로덕션/프리뷰 배포 트리거

## 모니터링

-   **Sentry**: 프론트·백엔드 오류 및 성능 데이터 수집.
-   **GitHub Issues**: 버그/기능 요청 관리.

## 기여 가이드

1. `main` 브랜치 → 배포 브랜치. PR 기반 개발.
2. 이슈를 먼저 생성하고 태스크를 연결한 뒤 브랜치를 생성해 주세요.
3. 커밋 메시지는 Conventional Commits 규칙을 따릅니다. (`feat:`, `fix:` 등)
4. PR 템플릿을 활용해 변경 내역·테스트 결과를 명시합니다.

---

> 문의: 프로젝트 슬랙 채널 #korean-name 또는 GitHub Discussions를 이용해 주세요.
