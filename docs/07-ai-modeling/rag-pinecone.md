# RAG · Pinecone

[← AI Modeling 홈](README.md) · [데이터 파이프라인](../02-architecture/data-pipeline.md)

구현: `common/vector_search.py`

## 개요

사용설명서 PDF/텍스트를 청크 단위로 임베딩해 Pinecone에 저장하고, 사용자 질의와 유사한 페이지를 검색해 LLM 답변 근거로 사용합니다.

### 오프라인 적재 (노트북)

| 경로 | 역할 |
|------|------|
| `products/data/embedding/pdfdown.ipynb` | 매뉴얼 PDF 수집 |
| `products/data/embedding/embedding.ipynb` | 청킹·임베딩 |
| `products/data/embedding/pinecone_uploader.ipynb` | Pinecone `user_manual` 업로드 |

→ [데이터 파이프라인 §4](../02-architecture/data-pipeline.md#4-매뉴얼-rag-pinecone)

## 설정

| 환경 변수 | 용도 |
|-----------|------|
| `OPENAI_API_KEY` | 임베딩 생성 |
| `PINECONE_API_KEY` | 인덱스 접근 |
| `PINECONE_HOST` | Index host |

## search_manual()

```python
search_manual(product_type: str, query: str) -> list[dict]
```

| 단계 | 동작 |
|------|------|
| 1 | `text-embedding-3-small`으로 `query` 임베딩 |
| 2 | Pinecone `query`, namespace=`user_manual`, `top_k=5` |
| 3 | 필터 `product_code_header == product_type` (TVT/ACT/…) |
| 4 | `(product_code, page_number)` 중복 제거 |
| 5 | `get_page()`로 페이지 전체 텍스트 조립 |

### 반환 형식

```python
[
  {
    "product_code": "WMT...",
    "page_number": 42,
    "content": "해당 페이지 본문 ..."
  },
  ...
]
```

## get_page()

`fetch_by_metadata`로 동일 `product_code`·`page_number` 청크를 모아 `index` 메타 순 정렬 후 `content` 결합.

## LangGraph 연동

1. `intent_router`가 `vector_search` 슬롯(질의문) 추출
2. `db_search` 이후 `answer_with_result`에서 `manual_results`와 DB 결과를 함께 프롬프트에 주입
3. 답변에 매뉴얼 페이지·제품 코드 인용

## 예시 질의

| 입력 | 기대 |
|------|------|
| 「세탁기 UE 에러가 뭐야?」 | WMT + RAG → 에러 설명 |
| 「에어컨 필터 청소 방법」 | ACT + 단계 안내 |

→ [채팅 기능](../08-features/chat-lgneer.md)

## 관련 문서

- [LangGraph 플로우](langgraph-flow.md)
- [개발 환경 — .env](../01-getting-started/development-environment.md#환경-변수-env)
