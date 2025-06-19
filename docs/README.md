# 영어→한국어 이름 추천 서비스 문서

## 1. 서비스 흐름

1. 사용자가 영어 이름을 입력합니다.
2. 프론트엔드가 **POST /api/convert** 로 요청하여 한국어 이름 후보 3개를 받습니다.
3. 사용자는 마음에 드는 이름을 **💾 저장** 할 수 있습니다.
4. 저장 시 LocalStorage 및 **POST /api/history/save** 로 백엔드에 기록됩니다.
5. _내 이름 모아보기_ 탭에서 저장 내역을 조회·삭제할 수 있습니다. (`GET /api/history`, `DELETE /api/history/{id}`)

## 2. 로컬 개발 환경

```bash
# 1) 저장소 클론
$ git clone <repo> && cd KoreanName

# 2) 프론트엔드
$ cd frontend && pnpm install && pnpm dev  # http://localhost:5173

# 3) 백엔드
$ cd ../backend && python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
$ python app.py           # http://localhost:5000

# TIP: 프론트+백 동시 실행
$ cd frontend && pnpm dev:full
```

## 3. REST API 명세

### 3.1 이름 추천

| 메서드 | 엔드포인트     | 설명                             |
| ------ | -------------- | -------------------------------- |
| POST   | `/api/convert` | 영어 이름 → 한국어 이름 3개 추천 |

**요청 본문**

```json
{
    "name": "Alice"
}
```

**성공 응답 (200)**

```json
{
    "candidates": [
        { "koreanName": "하린", "meaning": "하늘같이 맑고 밝은", "eraScore": 0.82 },
        { "koreanName": "서연", "meaning": "서로를 연모하는 마음", "eraScore": 0.71 },
        { "koreanName": "다은", "meaning": "모든 이에게 은혜로움", "eraScore": 0.63 }
    ]
}
```

### 3.2 이름 저장

| 메서드 | 엔드포인트          | 설명               |
| ------ | ------------------- | ------------------ |
| POST   | `/api/history/save` | 추천된 이름을 저장 |

**요청 본문**

```json
{
    "englishName": "Alice",
    "koreanName": "하린"
}
```

**성공 응답 (201/200)**

```json
{ "id": 12, "savedAt": "2024-05-13T12:34:56Z" }
```

### 3.3 저장 목록 조회

| 메서드 | 엔드포인트     | 설명                  |
| ------ | -------------- | --------------------- |
| GET    | `/api/history` | 저장된 이름 목록 반환 |

**응답 예시**

```json
[
    {
        "id": 12,
        "englishName": "Alice",
        "koreanName": "하린",
        "savedAt": "2024-05-13T12:34:56Z"
    }
]
```

### 3.4 저장 항목 삭제

| 메서드 | 엔드포인트          | 설명              |
| ------ | ------------------- | ----------------- |
| DELETE | `/api/history/{id}` | 지정 ID 저장 삭제 |

**성공 응답 (200)**

```json
{ "status": "deleted" }
```

## 4. 인증 / 헤더

현재 MVP 단계에서는 로그인 기능이 없으며, `X-User-Id` 헤더를 사용해 임시 사용자 식별 값을 전달할 수 있습니다.

## 5. 오류 코드

| 코드 | 상황               |
| ---- | ------------------ |
| 400  | 필수 파라미터 없음 |
| 404  | 리소스 없음        |
| 500  | 서버 오류          |

## 6. 배포

-   **Vercel**: `main` 브랜치 푸시 시 자동 배포
-   **GitHub Actions**: 테스트·린트·Cypress 통과 후 Vercel 트리거

---

문의: GitHub Issues 또는 슬랙 `#korean-name` 채널
