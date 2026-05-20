# AI / Modeling 파트 문서

[← Docs 홈](../README.md)

**담당**: 윤정연, 정영일  
**스택**: LangGraph, LangChain, OpenAI, Pinecone

## 문서 목록

| 문서 | 내용 |
|------|------|
| [langgraph-flow.md](langgraph-flow.md) | 노드·라우팅·상태 |
| [rag-pinecone.md](rag-pinecone.md) | 매뉴얼 벡터 검색 |

## 코드 위치

| 파일 | 역할 |
|------|------|
| `common/llm.py` | `GraphState`, 노드, `graph_instance`, `add_chat()` |
| `common/llm_agent.py` | 프롬프트·structured output 호출 |
| `common/vector_search.py` | `search_manual`, `get_page` |
| `debug.py` | 그래프 단독 실행 |

## 모델·외부 서비스

| 용도 | 모델/서비스 |
|------|-------------|
| 대화·분류·슬롯 | `gpt-4o-mini` |
| 임베딩 | `text-embedding-3-small` |
| 벡터 DB | Pinecone index, namespace `user_manual` |

## 연관 기능

- [채팅 LGneer](../08-features/chat-lgneer.md)
- [데이터 파이프라인](../02-architecture/data-pipeline.md)
