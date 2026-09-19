# 사용설명서 RAG와 Pinecone

[AI 구현](README.md) · [데이터 흐름](../02-architecture/data-flow.md)

## 오프라인 준비

| 노트북 | 내용 |
|---|---|
| [pdfdown.ipynb](../../data/products/embedding/pdfdown.ipynb) | 매뉴얼 URL에서 PDF 수집, 페이지 텍스트와 청크 준비 |
| [embedding.ipynb](../../data/products/embedding/embedding.ipynb) | 청크를 `text-embedding-3-small`로 임베딩 |
| [pinecone_uploader.ipynb](../../data/products/embedding/pinecone_uploader.ipynb) | 벡터와 metadata를 `user_manual`에 업로드 |

노트북 커널 작업 디렉터리는 `data/products/embedding/`입니다. PDF 수집 입력은 `../database/ProductTV.csv`, PDF 저장은 `manual_pdf/manual_TV_pdf/`, 중간 입력·출력은 `res/`, `index/` 아래 카테고리별 CSV를 사용합니다. 모든 중간 자료가 저장소에 포함된 것으로 가정하지 말고 셀의 파일 경로와 코드 접두를 확인합니다. 업로드 노트북은 100개 단위 배치를 사용합니다. 재실행 전 대상 인덱스·ID 정책·기존 벡터 범위를 확인해야 합니다.

## 런타임 검색

[vector_search.py](../../common/vector_search.py)의 `search_manual(product_type, query)`:

1. OpenAI `text-embedding-3-small`로 질의를 임베딩합니다.
2. Pinecone `user_manual`에서 `top_k=5`, `include_metadata=True`로 검색합니다.
3. `product_code_header`가 제품군 코드와 같은 metadata만 대상으로 합니다.
4. 동일 `(product_code, page_number)`를 중복 제거합니다.
5. `get_page`로 같은 제품·페이지 청크를 다시 읽고 `index` 순으로 정렬해 본문을 합칩니다.

```python
[{"product_code": "WMT_EXAMPLE", "page_number": 42, "content": "페이지 본문"}]
```

위는 응답 구조 예시입니다. 실제 제품 코드와 페이지 값은 업로드된 metadata에 따릅니다.

## 필수 metadata

| 키 | 용도 |
|---|---|
| `product_code_header` | TVT·ACT·REF·VAC·WMT 제품군 필터 |
| `product_code` | SQLite 상품 코드 연결·페이지 재조회 |
| `page_number` | 동일 페이지 청크 조회 |
| `index` | 페이지 내부 정렬 |
| `content` | 모델에 전달할 본문 |

인덱스 벡터 차원은 실제 임베딩 출력과 같아야 합니다. 런타임은 인덱스를 생성하지 않습니다. 연결에 사용하는 환경변수 이름은 `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_HOST`입니다.

## 그래프 연결과 한계

검색은 `intent_router`에서 실행됩니다. 검색된 상품 코드는 ORM 필터에 결합되고, 결과가 1~5건일 때 `answer_with_result`가 상품 정보와 매뉴얼 본문을 프롬프트에 전달합니다.

검색 필터는 정확한 모델 코드가 아닌 제품군 수준입니다. `get_page`의 `fetch_by_metadata`는 최대 20개 벡터만 가져오며 페이지네이션이 없어 긴 페이지는 일부 청크만 복원될 수 있습니다. 최저 유사도 임계값·별도 reranker·인용 검증기는 구현되어 있지 않습니다. 페이지 반환이 곧 정확한 사용법이나 전체 매뉴얼 검증을 의미하지 않습니다.

[LangGraph](langgraph-flow.md) · [검증과 한계](../10-quality/verification-and-limitations.md)
