from openai import OpenAI
from pinecone import Pinecone

import os

# index table과의 연결
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_host = os.getenv("PINECONE_HOST")
pc = Pinecone(api_key=pinecone_key)
index = pc.Index(host=pinecone_host)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def search_manual(product_type:str, query:str) -> list[dict]:
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