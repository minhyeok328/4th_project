from operator import add
from typing import Annotated
from typing_extensions import TypedDict
from typing import Literal, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END

from langchain_core.messages import AIMessage, HumanMessage

############################################################
# state definition
############################################################

ConversationState = Literal["initial", "subseq", "context"]

RouteFromStart = Literal[
    "subsequence_router",
    "product_classification",
    "intent_router",
]

RouteFromSubsequenceRouter = Literal[
    "product_classification",
    "intent_router",
]

RouteFromProductClassification = Literal[
    "intent_router",
    "end",
]

RouteFromDBSearch = Literal[
    "answer_with_result",
    "answer_without_result",
]


class GraphState(TypedDict, total=False):
    # 현재 대화 상태
    state: ConversationState
    # 다음 상태
    next_state: ConversationState

    # 채팅 기록 MessageList
    messages: list

    # 제품군 / 슬롯
    product_type: str
    slots: list[dict]

    # 후속 질문 여부
    is_fall_case: bool
    is_subsequence: bool

    # 검색 결과
    search_results: List[Dict[str, Any]]
    result_count: int

    # 최종 답변
    response: str

    # 채팅 기록에는 안들어갈 추가 text
    response_tail: str


############################################################
# node definition
############################################################

def fall_case_node(state: GraphState) -> GraphState:
    """
    챗봇의 역량 밖의 답변을 처리하는 node
    적당한 수준의 사교성 대화나 이전 대화 목록을 참고하는 답변만 하고 이외의 답변은 무시
    """

    # llm implement part
    # 사교성 대화만 한 경우
    is_fall_case = False
    response = "안녕하세요"

    # return value
    rstate = {**state}
    rstate["is_fall_case"] = is_fall_case
    if is_fall_case:
        rstate["next_state"] = rstate["state"]
        rstate["response"] = response
    return rstate

def subsequence_router_node(state: GraphState) -> GraphState:
    """
    후속질문판단 / LLM 분기 노드

    역할:
    - 현재 입력이 직전 검색 결과를 참조하는 후속 질문인지 판단
    - 예: "두 번째 거", "그 제품", "아까 추천한 거", "그건 왜 별로야?"
    """

    # llm implement part
    # 만약 후속 질문 의사가 있을 경우
    is_subsequence = False

    rstate = {**state}
    rstate["is_subsequence"] = is_subsequence
    if not is_subsequence:
        rstate["state"] = "initial"
        rstate["product_type"] = ""
        rstate["slots"] = []
    return rstate


def product_classification_node(state: GraphState) -> GraphState:
    """
    제품군 요청 확인 노드

    역할:
    - 사용자 입력에서 제품군이 명시되었는지 확인
    - 예: 냉장고, 세탁기, 에어컨, 노트북 등
    """

    # llm implement part
    # 총 5개의 가전에 대해서 확인, 결과는 state["product_type"]에 저장
    # TV: "TVT"
    # 에어컨: "ACT"
    # 냉장고: "REF"
    # 청소기: "VAC"
    # 세탁기: "WMT"
    # 요청하지 않았으면: "" < 빈 문자열 + 답변: 먼저 ~~해주세요
    product_type = "ACT"

    rstate = {**state}
    rstate["product_type"] = product_type
    if product_type:
        rstate["state"] = "context"
    else:
        rstate["next_state"] = "initial"
        rstate["response"] = "먼저 검색할 상품군을 지정해주세요\n가능한 상품군 목록:\nTV, 에어컨, 냉장고, 청소기, 세탁기"
    return rstate


def intent_router_node(state: GraphState) -> GraphState:
    """
    Intent Router / 슬롯 추출기 노드

    역할:
    - 사용자 의도 분류
    - 검색 조건 슬롯 추출
    - 기존 context와 새 입력 병합
    """

    # llm implement part
    # models.py 참조해서 모든 필드가 _로 4개의 옵션 받아서 dictionary로 가공
    # slots리스트 맨 마지막에 append
    slot = {}

    rstate = {**state}
    rstate["slots"].append(slot)
    return rstate


def db_search_node(state: GraphState) -> GraphState:
    """
    DB 검색기 노드

    역할:
    - intent와 slots를 기준으로 DB 검색
    - 검색 결과와 검색 결과 수 저장
    """

    # DB 검색해서 결과 길이 확인
    # 충분히 짧으면 검색 결과도 반환
    result_count = 10
    search_result = [{}, {}, {}]

    rstate = {**state}
    rstate["result_count"] = result_count
    rstate["search_result"] = search_result
    return rstate

def reverse_condition(state: GraphState) -> GraphState:
    """
    검색 결과가 0건일 경우

    가장 최신 조건을 삭제하고 답변 생성
    """

    # 답변: 죄송하지만 그 조건에 맞는 결과는 없으니까 이전 단계로 돌아갑니다
    response = "hello"

    rstate = {**state}
    rstate["next_state"] = rstate["state"]
    rstate["response"] = response
    rstate["slots"] = rstate["slots"][:-1]
    return rstate


def answer_with_result_node(state: GraphState) -> GraphState:
    """
    정보 충분 / 답변 생성기 노드

    검색 결과가 적절하게 나온 경우 답변 생성
    """

    # llm implement part

    rstate = {**state}
    return rstate


def answer_without_result_node(state: GraphState) -> GraphState:
    """
    정보 불충분 / 답변 생성기 노드

    검색 결과가 너무 많거나 조건이 부족한 경우 추가 정보 요청
    """

    # 답변: 검색 결과가 너무 많아서 추가 조건이 필요해요
    # 제시할 수 있는 답변 목록

    rstate = {**state}
    return rstate


############################################################
# edge function
############################################################

def route_from_start(state: GraphState) -> RouteFromStart:
    """
    Mermaid 구조:

    start_point -->|state=subseq| subsequence_router
    start_point -->|state=initial| product_classification
    start_point -->|state=context| intent_router
    """
    fall_case = state.get("is_fall_case", False)
    if fall_case:
        return "fall_case"

    current_state = state.get("state", "initial")

    if current_state == "subseq":
        return "subsequence_router"

    if current_state == "context":
        return "intent_router"

    return "product_classification"


def route_from_subsequence_router(state: GraphState) -> RouteFromSubsequenceRouter:
    """
    Mermaid 구조:

    subsequence_router -->|후속 질문 의도 없음| product_classification
    subsequence_router -->|후속 질문 의도 있음| intent_router
    """
    if state.get("is_subsequence", False):
        return "intent_router"

    return "product_classification"


def route_from_product_classification(state: GraphState) -> RouteFromProductClassification:
    """
    Mermaid 구조:

    product_classification -->|제품군 설정| intent_router
    product_classification -->|제품군 설정 안함 next_state=initial state| end_point
    """
    product_type = state.get("product_type", "")

    if product_type:
        return "intent_router"

    return "end"


def route_from_db_search(state: GraphState) -> RouteFromDBSearch:
    """
    Mermaid 구조:

    db_search -->|검색 제품 수 = 0| reverse_condition
    db_search -->|0 < 검색 제품 수 <= n| answer_with_result
    db_search -->|검색 제품 수 > n| answer_without_result
    """
    n = 5
    result_count = state.get("result_count", 0)

    if result_count == 0:
        return "reverse_condition"
    elif 0 < result_count <= n:
        return "answer_with_result"

    return "answer_without_result"


############################################################
# graph builder
############################################################

builder = StateGraph(GraphState)

# Node 등록
builder.add_node("fall_case_node", fall_case_node)
builder.add_node("subsequence_router", subsequence_router_node)
builder.add_node("product_classification", product_classification_node)
builder.add_node("intent_router", intent_router_node)
builder.add_node("db_search", db_search_node)
builder.add_node("reverse_condition", reverse_condition)
builder.add_node("answer_with_result", answer_with_result_node)
builder.add_node("answer_without_result", answer_without_result_node)

# START node
builder.add_edge(START, "fall_case_node")

# fall_case_node 분기
builder.add_conditional_edges(
    fall_case_node,
    route_from_start,
    {
        "subsequence_router": "subsequence_router",
        "product_classification": "product_classification",
        "intent_router": "intent_router",
        "fall_case": END
    },
)


# subsequence_router conditional edge
builder.add_conditional_edges(
    "subsequence_router",
    route_from_subsequence_router,
    {
        "product_classification": "product_classification",
        "intent_router": "intent_router",
    },
)


# product_classification conditional edge
builder.add_conditional_edges(
    "product_classification",
    route_from_product_classification,
    {
        "intent_router": "intent_router",
        "end": END,
    },
)


# 일반 edge
builder.add_edge("intent_router", "db_search")


# db_search conditional edge
builder.add_conditional_edges(
    "db_search",
    route_from_db_search,
    {
        "reverse_condition": "reverse_condition",
        "answer_with_result": "answer_with_result",
        "answer_without_result": "answer_without_result",
    },
)


# 종료 edge
builder.add_edge("reverse_condition", END)
builder.add_edge("answer_with_result", END)
builder.add_edge("answer_without_result", END)

graph_instance = builder.compile()

############################################################
# global utilities
############################################################

def extract_messages(chats):
    """
    chats.models의 SingelChat list를 파싱하는 함수
    반환값을 state에 담아서 invoke 하면 됨

    input: list[SingleChat]
    output: list[HumanMessage|AIMessage]
    """
    messages = []
    for c in chats:
        mes = HumanMessage(content=c.content) if c.is_userchat else AIMessage(content=c.content)
        messages.append(mes)
    
    return messages

def clean_state(state:dict) -> dict:
    """
    messages invoke 간의 state 청소용 함수
    messages 이외의 모든 필드를 제거

    input: AgentState
    output: AgentState
    """
    for k in [l for l in state.keys() if l != "messages"]:
        state[k] = None

    return state

def invoke_graph(state:dict) -> dict:
    """
    graph build 없이 invoke하는 함수

    input: AgentState
    output: AgentState
    """
    global graph_instance

    result = graph_instance.invoke(state)

    return result