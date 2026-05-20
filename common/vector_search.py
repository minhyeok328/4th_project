"""
사용설명서 벡터 검색(Pinecone + OpenAI embedding).

- llm.intent_router_node에서 vector_search 문자열이 있을 때 search_manual 호출
- namespace user_manual, product_code_header로 제품군 필터
"""

from openai import OpenAI
from pinecone import Pinecone

import os

# 환경 변수로 Pinecone 인덱스·OpenAI 클라이언트 초기화(모듈 로드 시 1회)
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_host = os.getenv("PINECONE_HOST")
pc = Pinecone(api_key=pinecone_key)
index = pc.Index(host=pinecone_host)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def search_manual(product_type:str, query:str) -> list[dict]:
    """
    질의 문장을 임베딩해 유사 매뉴얼 청크를 검색하고 페이지 본문을 합친다.

    Args:
        product_type: 제품군 코드(ACT/REF 등) — Pinecone metadata 필터
        query: LLM이 추출한 vector_search 문장

    Returns:
        product_code, page_number, content 딕셔너리 목록(동일 페이지 중복 제거)
    """
    global index, client

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    query_vector = response.data[0].embedding

    result = index.query(
        namespace="user_manual",
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        filter={"product_code_header": {"$eq": product_type}}
    )

    matches = []
    for match in result["matches"]:
        matches.append(match["metadata"])

    # top_k 매치 중 (product_code, page_number) 쌍이 겹치지 않게 1건만 유지
    buff = []
    for m in matches:
        valid = True
        data = (m["product_code"], m["page_number"])

        for b in buff:
            if b[0] == data[0] and b[1] == data[1]:
                valid = False

        if valid:
            buff.append(data)

    return [
        {
            "product_code": b[0],
            "page_number": b[1],
            "content": get_page(b[0], b[1])
        } for b in buff
    ]

def get_page(product_code:str, page_number:int) -> str:
    """한 매뉴얼 페이지에 해당하는 청크 metadata를 index 순으로 이어 붙인다."""
    global index

    result = index.fetch_by_metadata(
        filter={
            "$and": [
                {"product_code": {"$eq": product_code}},
                {"page_number": {"$eq": page_number}}
            ]
        },
        namespace="user_manual",
        limit=20
    )

    vectors = result.get("vectors", {})

    metadatas = [vec.get("metadata", {}) for vec in vectors.values()]
    metadatas.sort(key=lambda x: x.get("index", 0))

    contents = [md.get("content", "") for md in metadatas]

    return " ".join(contents)