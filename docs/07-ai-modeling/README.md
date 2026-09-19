# AI 구현

[문서 홈](../README.md)

## 구성

| 구현 | 기능 |
|---|---|
| [llm.py](../../common/llm.py) | GraphState·노드·조건 병합·라우팅·대화 저장 연결 |
| [llm_agent.py](../../common/llm_agent.py) | 프롬프트·Pydantic 구조화 출력·LLM 호출 |
| [vector_search.py](../../common/vector_search.py) | 질의 임베딩·Pinecone 검색·페이지 복원 |
| [llm_frame.ipynb](../../notebooks/evaluation/llm_frame.ipynb) | 노드별 평가 |
| [embedding 노트북](../../data/products/embedding/) | 사용설명서 오프라인 준비 |

대화·분류·조건 추출은 `gpt-4o-mini`, 임베딩은 `text-embedding-3-small`을 지정합니다. 모델 이름은 코드 설정이며 실제 서비스 접근 가능 여부는 실행 환경에서 확인해야 합니다.

## 처리 계약

범위 밖 질문 판정 → 현재 상태에 따른 제품군·후속 질문 판정 → 조건 추출 → 선택적 매뉴얼 검색 → ORM 검색 → 결과 개수별 응답 순서입니다. 검색 결과가 0건이면 최근 조건을 반영하지 않고 안내하고, 1~5건이면 모델 답변, 5건 초과면 추가 조건을 요청합니다.

`from_favorites`와 `vector_search`는 추출된 제어 필드이며 ORM에 직접 넘기지 않습니다. 해당 결과에서 `product_code_in` 조건을 만들어 이전 슬롯과 병합합니다. 매뉴얼 검색은 답변 생성 후가 아니라 조건 추출 노드에서 수행됩니다.

## 상태와 실행 의존성

대화 상태는 `Chatroom.agent_state`에 저장합니다. LangGraph 자체의 별도 체크포인터는 사용하지 않으며 요청마다 대화 문자열을 DB에서 복원합니다. OpenAI·Pinecone 설정은 [개발 환경](../01-getting-started/development-environment.md), 상태 전이는 [LangGraph 상세](langgraph-flow.md), metadata는 [RAG 상세](rag-pinecone.md)에 있습니다.

## 검증 해석

[과거 모델 평가](../10-quality/model-evaluation-history.md)는 범위·후속·제품군 노드만 평가했습니다. 슬롯 추출, 전체 추천 적합성, 설명서 인용 정확도, 찜 범위 제한, 외부 장애 대응까지 검증한 수치가 아닙니다. 모델 출력과 정답 라벨 정의는 별도 확인해야 합니다.
