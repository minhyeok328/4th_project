import warnings
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings(
    "ignore",
    category=LangChainPendingDeprecationWarning
)

from typing_extensions import TypedDict
from typing import Literal
from django.urls import reverse
from urllib.parse import urlencode
from copy import deepcopy
from langgraph.graph import StateGraph, START, END

from .utils import search_product, get_favorites
import common.llm_agent as agents
import common.vector_search as vector_db

from chats.models import Chatroom

############################################################
# state definition
############################################################

result_boundary = 5

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
    # 사용자 id
    user_id: int
    root_url: str

    # 현재 대화 상태
    state: ConversationState
    # 다음 상태
    next_state: ConversationState

    # 채팅 기록 MessageList
    chats: list[str]

    # 제품군 / 슬롯
    product_type: str
    slots: dict
    intent: dict

    # 후속 질문 여부
    is_fall_case: bool
    is_subsequence: bool

    # DB 검색 결과
    result_count: int
    search_results: list

    # 사용설명서 검색 결과
    manual_results: list[dict]

    # 최종 답변
    response: str

    # 채팅 기록에는 안들어갈 추가 text
    response_tail: str


def _is_empty_condition(value):
    return value is None or value == "" or value == [] or value == () or value == set()


def _as_condition_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _get_condition_lookup(key):
    for lookup in ("gte", "lte", "in", "icontains"):
        if key.endswith(f"_{lookup}"):
            return lookup
    return None


def add_condition(base_condition: dict, new_condition: dict) -> dict:
    result = {
        key: deepcopy(value)
        for key, value in (base_condition or {}).items()
        if not _is_empty_condition(value)
    }

    for key, value in (new_condition or {}).items():
        if _is_empty_condition(value):
            continue

        lookup = _get_condition_lookup(key)
        current = result.get(key)

        if _is_empty_condition(current):
            result[key] = deepcopy(value)
            continue

        match lookup:
            case "gte":
                result[key] = max(current, value)
            case "lte":
                result[key] = min(current, value)
            case "in":
                value_list = _as_condition_list(value)
                result[key] = [
                    item
                    for item in _as_condition_list(current)
                    if item in value_list
                ]
            case "icontains":
                result[key] = _as_condition_list(current) + _as_condition_list(value)
            case _:
                result[key] = deepcopy(value)

    return result

def get_searchable_conditions(code_header: str) -> list[str]:
    match code_header:
        # TV
        case "TVT":
            return [
                "이름",
                "가격",
                "전력소비효율등급",
                "전력 소비량",
                "화면 크기",
                "디스플레이 종류",
                "주사율",
                "운영체제",
                "스피커 출력",
                "가로",
                "세로",
                "두께",
                "무게",
                "해상도",
            ]

        # 에어컨
        case "ACT":
            return [
                "이름",
                "가격",
                "전력소비효율등급",
                "전력 소비량",
                "냉방 능력",
                "전압",
                "주파수",
                "실내기 가로",
                "실내기 세로",
                "실내기 두께",
                "실외기 가로",
                "실외기 세로",
                "실외기 두께",
                "냉방 면적",
                "풍속",
                "제습 기능",
                "색상",
            ]

        # 냉장고
        case "REF":
            return [
                "이름",
                "가격",
                "전력소비효율등급",
                "전력 소비량",
                "설치 타입",
                "도어 개수",
                "전체 용량",
                "냉장 용량",
                "냉동 용량",
                "가로",
                "세로",
                "두께",
                "무게",
                "색상",
                "도어 타입",
                "냉각 방식",
                "스마트 진단",
                "제빙 기능",
            ]

        # 청소기
        case "VAC":
            return [
                "이름",
                "가격",
                "전력소비효율등급",
                "전력 소비량",
                "본체 가로",
                "본체 세로",
                "본체 두께",
                "타워 가로",
                "타워 세로",
                "타워 두께",
                "본체 무게",
                "타워 무게",
                "색상",
                "흡입력",
                "배터리 개수",
            ]

        # 세탁기
        case "WMT":
            return [
                "이름",
                "가격",
                "전력소비효율등급",
                "전력 소비량",
                "세탁 용량",
                "건조 용량",
                "가로",
                "세로",
                "두께",
                "무게",
                "색상",
                "도어 디자인",
                "제어 방식",
                "도어 타입",
                "수온",
                "탈수 성능",
            ]

        case _:
            return []

############################################################
# node definition
############################################################

def fall_case_node(state: GraphState) -> GraphState:
    """
    챗봇의 역량 밖의 답변을 처리하는 node
    적당한 수준의 사교성 대화나 이전 대화 목록을 참고하는 답변만 하고 이외의 답변은 무시
    """

    # llm implement part
    llm_result = agents.invoke_fall_case_node(state["chats"])

    is_fall_case = llm_result.is_fall_case
    response = llm_result.response

    # return value
    rstate = deepcopy(state)
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
    llm_result = agents.invoke_subsequence_router_node([state["chats"][-1]])
    is_subsequence = llm_result.is_subsequence

    rstate = deepcopy(state)
    rstate["is_subsequence"] = is_subsequence
    if not is_subsequence:
        rstate["state"] = "initial"
        rstate["product_type"] = ""
        rstate["slots"] = {}
        rstate["result_count"] = 0
        rstate["search_results"] = []
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
    llm_result = agents.invoke_product_classification_node([state["chats"][-1]])
    product_type = llm_result.product_type

    rstate = deepcopy(state)
    rstate["product_type"] = product_type
    if product_type:
        rstate["state"] = "context"
        rstate["slots"] = {}
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
    llm_result = agents.invoke_intent_router_node(state["product_type"], state["chats"])
    llm_result = llm_result.model_dump()

    cond_fav = {}
    if llm_result["from_favorites"]:
        cond_fav["product_code_in"] = [f for f in get_favorites(state["user_id"]) if f[:3] == state["product_type"]]
    
    manual_result = []
    cond_vec = {}
    if llm_result["vector_search"] != "":
        manual_result = vector_db.search_manual(state["product_type"], llm_result["vector_search"])
        cond_vec["product_code_in"] = [d["product_code"] for d in manual_result]

    buff = {k:v for k, v in llm_result.items() if k not in ["from_favorites", "vector_search"]}
    res = add_condition(cond_fav, cond_vec)
    res = add_condition(buff, res)

    rstate = deepcopy(state)
    rstate["intent"] = res
    rstate["manual_results"] = manual_result
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
    conditions = add_condition(state["slots"], state["intent"])

    if not ("product_code_in" in conditions and len(conditions["product_code_in"]) == 0):
        db_results = search_product(state["product_type"], conditions.get("product_code_in", []), conditions)
        result_count = len(db_results)

        if result_count <= result_boundary:
            search_result = db_results
        else:
            search_result = []
    else:
        result_count = 0
        search_result = []

    rstate = deepcopy(state)
    if result_count != 0:
        rstate["slots"] = conditions

    rstate["result_count"] = result_count
    rstate["search_results"] = search_result
    return rstate

def reverse_condition(state: GraphState) -> GraphState:
    """
    검색 결과가 0건일 경우

    가장 최신 조건을 삭제하고 답변 생성
    """

    response = "죄송합니다. 그 조건에 맞는 제품이 존재하지 않아 검색 조건을 되돌리겠습니다.\n다른 조건을 시도해주세요."

    rstate = deepcopy(state)
    rstate["next_state"] = rstate["state"]
    rstate["response"] = response
    rstate["response_tail"] = "가능한 조건: " + ", ".join(get_searchable_conditions(state["product_type"]))
    return rstate


def answer_with_result_node(state: GraphState) -> GraphState:
    """
    정보 충분 / 답변 생성기 노드

    검색 결과가 적절하게 나온 경우 답변 생성
    """

    # llm implement part
    llm_result = agents.invoke_answer_with_result_node(state, state["chats"])

    rstate = deepcopy(state)
    rstate["next_state"] = "subseq"
    rstate["response"] = llm_result.answer
    return rstate


def answer_without_result_node(state: GraphState) -> GraphState:
    """
    정보 불충분 / 답변 생성기 노드

    검색 결과가 너무 많거나 조건이 부족한 경우 추가 정보 요청
    """

    # 답변: 검색 결과가 너무 많아서 추가 조건이 필요해요
    # 제시할 수 있는 답변 목록
    response = f"해당 조건에 맞는 검색 결과는 총 {state['result_count']}건 입니다.\n다른 조건을 추가하거나 아래의 링크를 이용해 주세요."

    subq = deepcopy(state['slots'])
    subq["product_type"] = state["product_type"]

    base_url = reverse("products:searchpage")
    url = f"{state['root_url']}/{base_url}?{urlencode(subq, doseq=True)}"

    rstate = deepcopy(state)
    rstate["next_state"] = "context"
    rstate["response"] = response
    rstate["response_tail"] = "가능한 조건: " + ", ".join(get_searchable_conditions(state["product_type"])) + "\n" + url
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
    global result_boundary
    result_count = state.get("result_count", 0)

    if result_count == 0:
        return "reverse_condition"
    elif 0 < result_count <= result_boundary:
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
    "fall_case_node",
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

def add_chat(root_url:str, room:Chatroom, user_input:str) -> str:
    global graph_instance

    formal_state = room.agent_state

    if "user_id" not in formal_state:
        room.agent_state["user_id"] = room.account.id
        formal_state = room.agent_state

    state = deepcopy(formal_state)
    state["root_url"] = root_url

    room.add_chat(True, user_input)
    chats = []
    for c in room.view_chats():
        chats.append(c.content)
    state["chats"] = chats

    result = graph_instance.invoke(state)
    response_tail = result.get("response_tail", "")

    room.agent_state["state"] = result["next_state"]
    room.agent_state["product_type"] = result.get("product_type", "")
    room.agent_state["slots"] = result["slots"]
    room.agent_state["manual_results"] = result.get("manual_results", [])
    room.save()

    room.add_chat(False, result["response"])

    return result["response"], response_tail
