# 개발 환경

[문서 홈](../README.md) · [실행과 운영](run-and-operations.md)

## 사전 준비

| 항목 | 기준 |
|---|---|
| Python | Django 6 계열을 사용할 수 있는 Python 3.12 이상 |
| Python 의존성 | [requirements.txt](../../requirements.txt)의 고정 버전 |
| Node.js·npm | [Tailwind 패키지](../../theme/static_src/package.json)의 의존성을 지원하는 환경; 저장소에 런타임 버전 고정 파일 없음 |
| 외부 서비스 | OpenAI API, Pinecone 인덱스와 접근 권한 |
| 노트북 | 데이터 재적재 시 Jupyter 실행 환경; Jupyter 자체는 requirements에 없음 |
| 브라우저 | 재수집 시 Chrome과 Selenium 실행 환경 |

웹 의존성에는 Django 6.0.5, django-tailwind 4.4.2, Pillow, LangGraph, LangChain, OpenAI와 Pinecone SDK가 포함됩니다. requirements의 Optional 주석 아래 패키지도 주석 처리된 항목이 아니므로 `pip install -r`에 함께 설치됩니다.

## Python 설치

다음 PowerShell 명령은 `manage.py`가 있는 디렉터리에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

활성화가 제한된 환경에서는 `.venv\Scripts\python.exe`로 각 명령을 직접 실행할 수 있습니다.

## 환경변수

루트 `.env` 또는 실행 프로세스 환경에 다음 이름을 설정합니다. 실제 값은 개인 환경에서 입력하고 저장소에 포함하지 않습니다.

| 이름 | 용도 |
|---|---|
| `OPENAI_API_KEY` | 채팅 모델과 질의 임베딩 |
| `PINECONE_API_KEY` | 벡터 인덱스 인증 |
| `PINECONE_HOST` | 사용할 인덱스의 host |

[settings.py](../../config/settings.py)가 `load_dotenv()`를 호출합니다. [vector_search.py](../../common/vector_search.py)는 import 시 클라이언트와 인덱스를 생성합니다. URL 검사 과정에서도 해당 모듈을 불러오므로 `migrate`, `check`, 서버 시작 전에 설정이 필요할 수 있습니다. 키 없는 별도 실행 모드는 구현되어 있지 않습니다.

## Tailwind 빌드

```powershell
Set-Location theme/static_src
npm install
npm run build
Set-Location ../..
```

빌드 결과는 `theme/static/css/dist/styles.css`입니다. 개발 중에는 별도 터미널의 `theme/static_src`에서 `npm run dev`를 실행합니다. npm 잠금 파일이 없으므로 설치 시점의 버전 해석 결과를 확인해야 합니다.

### NPM_BIN_PATH

Django 설정은 Windows의 npm 실행 경로를 지정합니다. django-tailwind 명령을 사용할 때는 설치된 **npm 실행 파일** 경로와 맞춰야 합니다. 위의 직접 `npm run build`는 셸에서 찾은 npm을 사용합니다. 다른 OS에서 `node` 바이너리 경로를 npm 경로처럼 복사하지 않습니다.

## 데이터 준비

```powershell
python manage.py migrate
```

마이그레이션은 테이블만 만듭니다. 상품은 [database CSV](../../data/products/database/)와 [loaddata.ipynb](../../notebooks/data/loaddata.ipynb)로 별도 적재합니다. 이 노트북은 `Path.cwd().parents[1]`로 저장소 루트를 찾으므로 **커널 작업 디렉터리를 `notebooks/data/`로 맞춥니다**. 루트의 Django 설정·모델을 불러오고 `data/products/database/`의 CSV를 읽습니다.

노트북에는 기존 상품을 삭제하는 셀이 있습니다. 기존 DB를 보존해야 한다면 복사본에서 적재하고, 해상도 마스터와 TV 외래키 순서를 유지합니다. CSV, DB, Pinecone은 자동 동기화되지 않습니다. 설명서 데이터 준비는 [데이터 흐름](../02-architecture/data-flow.md)과 [RAG](../07-ai-modeling/rag-pinecone.md)를 따릅니다.

## 노트북 작업 디렉터리

Jupyter 환경에서 파일을 열 때 아래 폴더를 커널의 작업 디렉터리로 사용합니다. 파일 위치와 커널 작업 디렉터리가 다를 수 있으므로 실행 전에 `Path.cwd()`를 확인합니다.

| 노트북 | 커널 작업 디렉터리 | 입력·출력 기준 |
|---|---|---|
| `loaddata.ipynb` | `notebooks/data/` | 저장소 루트의 `data/products/database/` CSV → SQLite |
| `llm_frame.ipynb` | `notebooks/evaluation/` | 평가 입력 CSV와 결과 CSV를 같은 폴더에서 읽고 저장 |
| 수집·전처리 노트북 | 해당 `data/products/raw/data_crawling/<제품군>/` 또는 `data/products/preprocessing/<제품군>/` | 동일 폴더의 CSV·HTML·링크 파일, 해상도 입력은 `../TV/` |
| PDF·임베딩·업로드 노트북 | `data/products/embedding/` | 상품 CSV는 `../database/`, 중간 파일은 `manual_pdf/`, `res/`, `index/` |

평가 입력 `fall_case_label_test_50.csv`, `subsequence_router_label_test_50.csv`, `product_classification_label_test_50.csv`는 별도 준비가 필요합니다. 임베딩 중간 CSV·PDF·출력 디렉터리 역시 자동으로 준비되지 않습니다. 폴더 이동은 데이터나 외부 인덱스를 생성하지 않습니다.
