# 개발 환경 설정

[← Docs 홈](../README.md) · [실행 및 운영](run-and-operations.md)

## 사전 요구사항

| 항목 | 버전·비고 |
|------|-----------|
| Python | 3.12+ |
| Node.js / npm | Tailwind 빌드 (`theme/static_src`) |
| OpenAI API Key | 챗봇·임베딩 |
| Pinecone API Key & Host | 사용설명서 RAG |
| Chrome + WebDriver | 크롤링 파이프라인만 필요 |

## 저장소·디렉터리

```powershell
cd 4th_project
```

프로젝트 루트는 `manage.py`가 있는 `4th_project/` 디렉터리입니다.

## Python 가상환경

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

주요 패키지: `Django`, `django-tailwind`, `langgraph`, `langchain-openai`, `pinecone`, `python-dotenv` — 전체 목록은 [requirements.txt](../../requirements.txt).

## Tailwind (theme)

```powershell
cd theme\static_src
npm install
npm run build
cd ..\..
```

스타일 개발 중에는 별도 터미널에서:

```powershell
cd theme\static_src
npm run dev
```

## 환경 변수 (`.env`)

프로젝트 루트에 `.env` 파일을 생성합니다. `config/settings.py`의 `load_dotenv()`가 로드합니다.

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_HOST=...
```

> `.env`는 Git에 커밋하지 않습니다.

## 데이터베이스 초기화

```powershell
python manage.py migrate
```

상품 데이터는 다음 중 하나로 준비합니다.

- 팀 제공 `db.sqlite3` 사용 (`.gitignore` — 로컬만 유지)
- `products/data/database/` CSV → `products/loaddata.ipynb`로 SQLite 적재
- 처음부터 구축 시: `products/data/raw/data_crawling/` 수집 → `products/data/preprocessing/` 전처리 → 위 CSV 생성

크롤링·적재·RAG 적재 절차는 [데이터 파이프라인](../02-architecture/data-pipeline.md) · [디렉터리 구조](../02-architecture/directory-structure.md)를 참고하세요.

## IDE·로컬 팁

| 항목 | 권장 |
|------|------|
| Django 설정 모듈 | `config.settings` (`manage.py` 기본) |
| LangGraph 단독 테스트 | `debug.py`, `common/llm.py`의 `graph_instance` |
| 정적 파일 | `static/`, Tailwind 빌드 결과는 `theme/static/` |

## 다음 단계

- [실행 및 일상 운영](run-and-operations.md)
- [디렉터리 구조](../02-architecture/directory-structure.md)
