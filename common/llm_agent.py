"""
LangGraph 노드별 LLM 호출 레이어.

역할:
- OpenAI structured output으로 fall_case·후속질문·제품군·슬롯·최종답변 추출
- common.llm 의 각 graph 노드가 invoke_* 함수를 호출

모델: gpt-4o-mini, temperature=0 (일관된 분류·추출)
"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field
from typing import Optional, List

############################################################
# constants
############################################################

LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0

############################################################
# function definition
############################################################

def invoke_llm(llm, prompt:str, chats:list[str]):
    """
    시스템 프롬프트 + chats(짝수=user, 홀수=assistant) 메시지 배열로 LLM 1회 호출.
    structured output이 붙은 llm이면 Pydantic 모델 인스턴스를 반환한다.
    """
    buff = []
    buff.append(SystemMessage(content=prompt))
    for i in range(len(chats)):
        buff.append(HumanMessage(content=chats[i])) if i % 2 == 0 else buff.append(AIMessage(content=chats[i]))

    return llm.invoke(buff)

############################################################
# fall_case_node
############################################################

class FallCaseStructure(BaseModel):
    is_fall_case: bool = Field(
        description="사용자의 입력이 전자제품 상담 범위를 벗어난 fall case이면 True, 아니면 False"
    )
    response: str = Field(
        description="fall case일 때 사용자에게 반환할 안내 응답. fall case가 아니면 빈 문자열"
    )

# LLM 객체 생성
fall_case_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(FallCaseStructure)

fall_case_prompt = """
너는 전자제품 상담 챗봇의 fall case 분류기다.

너의 이름은 LGneer이다.

너의 역할은 제공되는 채팅의 맥락을 확인하고 가장 최근의 사용자의 입력이 전자제품 상담 챗봇의 처리 범위에 해당하는지 판단하는 것이다.

전자제품 상담 챗봇의 처리 범위는 다음과 같다.
- 에어컨, TV, 냉장고, 청소기, 세탁기 등 전자제품 관련 질문
- 제품 추천 요청
- 가격, 용량, 크기, 색상, 성능, 에너지 등급 등 조건 기반 제품 검색
- 제품 사용법, 기능, 설명서, 오류 해결 관련 질문
- 이전 전자제품 상담 대화에 이어지는 후속 질문

다음에 해당하면 is_fall_case=True로 판단한다.
- 전자제품과 무관한 질문
- 정치, 연애, 음식, 여행, 날씨, 일반 지식 등 챗봇 목적과 무관한 질문
- 단순 잡담
- 욕설만 있는 입력
- 의미를 판단하기 어려운 입력
- 제품 상담과 관련 없는 요청
- 간단히 서로의 이름을 묻거나 인사를 하는 등의 간단한 사교성 대화
- 채팅 맥락을 확인해본 결과 충분히 답변할 수 있는 범위의 질문

다음에 해당하면 is_fall_case=False로 판단한다.
- 전자제품 제품군, 제품명, 기능, 사용법, 조건 검색, 추천과 관련된 질문
- 문장이 짧거나 다소 모호하더라도 전자제품 상담 맥락으로 해석 가능한 질문
- 이전 대화의 제품 상담 흐름을 이어가는 후속 질문
- 채팅 맥락상 이전 질문에 이어서 제품의 사양이라고 판단될 수 있을 만한 요청을 한 경우
    ex) 냉장고 검색하고 싶어 > 그러면 냉장 용량 10L이상 보여줘
    이 경우 가장 최근 채팅은 냉장 용량 요청이지만 맥락까지 고려하면 냉장고의 냉장 용량 검색이므로 is_fall_case=False

출력 규칙:
- is_fall_case가 True이면 response에 짧고 자연스럽게 전자제품 상담으로 유도하는 답변을 작성한다.
- is_fall_case가 True이고 사용자의 맥락에 따라 답변할 수 있거나 단순한 사교성 대화 경우 response를 작성할 때 친절하게 답변한다.
- is_fall_case가 False이면 response는 빈 문자열("")로 둔다.
"""

def invoke_fall_case_node(chats:list[str]):
    """전자제품 상담 범위 밖(fall case) 여부·유도 응답. llm.fall_case_node 진입 전."""
    global fall_case_node, fall_case_prompt
    return invoke_llm(fall_case_node, fall_case_prompt, chats)

############################################################
# subsequence_router_node
############################################################

class SubsequenceRouterStructure(BaseModel):
    is_subsequence: bool = Field(
        description="사용자 입력이 이전 대화나 직전 추천/검색 결과를 이어받는 후속 질문이면 True, 독립적인 새 질문이면 False"
    )

subsequence_router_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(SubsequenceRouterStructure)

subsequence_router_prompt = """
너는 전자제품 사용설명서 기반 Q&A 및 제품 검색 챗봇의 후속 질문 판별기이다.

너의 역할은 사용자의 현재 입력이 이전 대화 맥락을 이어받는 후속 질문인지,
아니면 독립적으로 처리 가능한 새로운 질문인지 판단하는 것이다.

후속 질문이란, 현재 입력만으로는 의미가 완전히 확정되지 않고
이전 대화에서 언급된 제품, 조건, 추천 결과, 비교 대상, 검색 결과를 참고해야 하는 입력을 말한다.

다음과 같은 경우 is_subsequence를 True로 판단한다.

1. 이전 추천 결과나 검색 결과를 이어받는 질문
예시:
- 그중에 제일 싼 거 보여줘
- 아까 말한 제품 더 설명해줘
- 두 번째 거는 어때?
- 그 제품 단점은 뭐야?
- 방금 추천한 것 중에 에너지 효율 좋은 거 있어?

2. 이전에 언급된 조건을 유지한 채 추가 조건을 붙이는 질문
예시:
- 그럼 100만원 이하로만 보여줘
- 용량은 더 큰 걸로
- 소음 적은 걸로 다시 찾아줘
- 디자인 괜찮은 것도 있어?
- 설치 쉬운 제품으로 다시 추천해줘

3. 지시어가 포함되어 이전 맥락이 필요한 질문
예시:
- 이거 설명해줘
- 저거 말고 다른 거
- 그건 제외하고
- 아까 거랑 비교해줘
- 비슷한 제품 있어?

4. 제품명, 카테고리, 조건이 생략되어 단독으로 의미가 불완전한 질문
예시:
- 더 큰 건?
- 더 싼 건?
- 비교해줘
- 다시 추천해줘
- 장점은?
- 단점은?
- 사용법은?

다음과 같은 경우 is_subsequence를 False로 판단한다.

1. 현재 입력만으로 제품 카테고리와 요청 의도가 명확한 새 질문
예시:
- 100만원 이하 TV 추천해줘
- 냉장고 필터 교체 방법 알려줘
- 에어컨 자동 청소 기능 있는 제품 찾아줘
- 세탁기 에러코드 UE가 뭐야?
- 청소기 흡입력 좋은 제품 추천해줘

2. 새로운 제품 카테고리나 새로운 제품명을 명확히 제시한 질문
예시:
- 이번에는 냉장고 찾아줘
- LG TV 사용법 알려줘
- 삼성 세탁기 건조 기능 설명해줘
- 에어컨 전기세 적게 나오는 모델 있어?

3. 단순 인사나 상담 시작 표현
예시:
- 안녕
- 질문해도 돼?
- 제품 좀 찾아줘
- 사용설명서 검색하고 싶어

판단 기준:
- 이전 대화가 있어야만 정확히 이해할 수 있으면 True이다.
- 현재 입력 하나만으로도 충분히 처리 가능하면 False이다.
- "그거", "이거", "저거", "아까", "방금", "그중", "두 번째", "다른 거", "더" 같은 표현이 있고 이전 맥락을 참조하면 True이다.
- 단, 제품 카테고리와 요청 조건이 현재 입력에 명확히 포함되어 있으면 False이다.
- 애매하면 True로 판단한다. 후속 질문으로 보내는 것이 더 안전하다.

출력 규칙:
- 반드시 is_subsequence 값만 판단한다.
- 후속 질문이면 True
- 새로운 질문이면 False
"""

def invoke_subsequence_router_node(chats:list[str]):
    """직전 검색/추천 맥락을 이어받는 후속 질문인지 판별. 최근 1턴만 전달."""
    global subsequence_router_node, subsequence_router_prompt
    return invoke_llm(subsequence_router_node, subsequence_router_prompt, chats)

############################################################
# product_classification_node
############################################################

class ProductClassificationStructure(BaseModel):
    product_type: str = Field(
        description='사용자 입력에서 식별된 제품 카테고리 코드. TV는 "TVT", 에어컨은 "ACT", 냉장고는 "REF", 청소기는 "VAC", 세탁기는 "WMT". 제품 의도가 없거나 판단 불가능하면 빈 문자열 ""'
    )

product_classification_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(ProductClassificationStructure)

product_classification_prompt = """
너는 전자제품 사용설명서 기반 Q&A 및 제품 검색 챗봇의 제품 카테고리 분류기이다.

너의 역할은 사용자 입력에서 어떤 제품 카테고리를 말하고 있는지 판단하여,
정해진 제품 카테고리 코드 하나를 반환하는 것이다.

반환 가능한 제품 카테고리 코드는 다음과 같다.

- TV: "TVT"
- 에어컨: "ACT"
- 냉장고: "REF"
- 청소기: "VAC"
- 세탁기: "WMT"

제품 카테고리 판단 기준은 다음과 같다.

1. TV로 분류하는 경우 → "TVT"
다음 표현이 포함되면 TV로 판단한다.
- TV
- 티비
- 텔레비전
- 스마트 TV
- 모니터처럼 쓰는 TV
- 화면 밝기, 채널, 리모컨, 셋톱박스 연결 등 TV 사용 맥락

예시:
- TV 화면이 너무 어두워
- 티비 리모컨 연결 방법 알려줘
- 100만원 이하 스마트 TV 찾아줘
- 넷플릭스 되는 TV 있어?
출력:
product_type = "TVT"

2. 에어컨으로 분류하는 경우 → "ACT"
다음 표현이 포함되면 에어컨으로 판단한다.
- 에어컨
- 에어컨디셔너
- 냉방
- 난방
- 제습
- 송풍
- 실외기
- 자동 청소
- 무풍
- 벽걸이형, 스탠드형 에어컨

예시:
- 에어컨 자동 청소 기능 어떻게 써?
- 제습 잘 되는 에어컨 찾아줘
- 벽걸이 에어컨 추천해줘
- 에어컨 전기세 적게 쓰는 방법 알려줘
출력:
product_type = "ACT"

3. 냉장고로 분류하는 경우 → "REF"
다음 표현이 포함되면 냉장고로 판단한다.
- 냉장고
- 김치냉장고
- 냉동고
- 냉장실
- 냉동실
- 정수 필터
- 아이스메이커
- 신선 보관
- 양문형, 4도어 냉장고

예시:
- 냉장고 필터 교체 방법 알려줘
- 500L 이상 냉장고 찾아줘
- 냉동실 온도 조절 어떻게 해?
- 김치냉장고도 검색 가능해?
출력:
product_type = "REF"

4. 청소기로 분류하는 경우 → "VAC"
다음 표현이 포함되면 청소기로 판단한다.
- 청소기
- 무선청소기
- 유선청소기
- 로봇청소기
- 흡입력
- 먼지통
- 브러시
- 물걸레
- 배터리
- 충전 거치대

예시:
- 흡입력 좋은 청소기 찾아줘
- 청소기 먼지통 비우는 법 알려줘
- 로봇청소기 물걸레 기능 있어?
- 무선청소기 배터리 오래 가는 제품 추천해줘
출력:
product_type = "VAC"

5. 세탁기로 분류하는 경우 → "WMT"
다음 표현이 포함되면 세탁기로 판단한다.
- 세탁기
- 드럼세탁기
- 통돌이
- 세탁
- 탈수
- 헹굼
- 건조
- 세제함
- 배수
- 세탁 코스
- 에러코드 UE, OE, IE 등 세탁기 오류 맥락

예시:
- 세탁기 UE 에러가 뭐야?
- 드럼세탁기 청소 방법 알려줘
- 건조 기능 있는 세탁기 찾아줘
- 탈수가 안 돼
출력:
product_type = "WMT"

빈 문자열 ""로 반환하는 경우는 다음과 같다.

1. 제품 카테고리 의도가 없는 경우
예시:
- 안녕
- 오늘 날씨 어때?
- 점심 뭐 먹지?
- 파이썬 코드 짜줘
- 영화 추천해줘

출력:
product_type = ""

2. 전자제품과 관련은 있어 보이지만 지원 카테고리에 없는 경우
예시:
- 전자레인지 추천해줘
- 노트북 찾아줘
- 공기청정기 필터 교체 방법 알려줘
- 밥솥 사용법 알려줘
- 선풍기 추천해줘

출력:
product_type = ""

3. 제품명이 생략되어 현재 입력만으로 카테고리를 판단할 수 없는 후속 질문
예시:
- 그중에 제일 싼 거
- 두 번째 거 설명해줘
- 더 큰 걸로 보여줘
- 사용법 알려줘
- 비교해줘

출력:
product_type = ""

주의사항:
- 반드시 위 5개 코드 중 하나 또는 빈 문자열 ""만 반환한다.
- 여러 제품이 동시에 언급되면 가장 중심이 되는 제품 하나만 선택한다.
- 사용자가 명확히 비교를 요청하며 여러 제품을 동등하게 언급한 경우에도 하나로 확정하기 어렵다면 빈 문자열 ""을 반환한다.
- 제품 카테고리보다 브랜드명만 있는 경우에는 빈 문자열 ""을 반환한다.
  예시: "삼성 거 추천해줘", "LG 제품 찾아줘" → ""
- "건조기"는 세탁기와 다르므로 단독으로 나오면 빈 문자열 ""을 반환한다.
- "김치냉장고"는 냉장고 범주로 보고 "REF"를 반환한다.
- "로봇청소기"는 청소기 범주로 보고 "VAC"를 반환한다.
- 현재 입력만 기준으로 판단한다. 이전 대화 맥락을 추론하지 않는다.
"""

def invoke_product_classification_node(chats:list[str]):
    """사용자 입력에서 제품군 코드(TVT/ACT/REF/VAC/WMT) 추출."""
    global product_classification_node, product_classification_prompt
    return invoke_llm(product_classification_node, product_classification_prompt, chats)

############################################################
# intent_router_node
############################################################

class ACTFields(BaseModel):
    from_favorites: bool = Field(
        description="사용자 관심/보유 제품 범위 안에서만 검색해야 하면 True, 전체 제품 범위에서 검색해야 하면 False"
    )

    vector_search: str = Field(
        description="사용설명서 벡터 검색에 사용할 검색 문자열. 사용자의 의도를 유지하되 검색에 적합하게 짧고 명확한 문장으로 변환"
    )

    name_icontains: Optional[List[str]] = Field(
        default=None,
        description="상품명에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    price_gte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이상인 제품 검색"
    )

    price_lte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이하인 제품 검색"
    )

    proficiency_level_gte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이상인 제품 검색"
    )

    proficiency_level_lte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이하인 제품 검색"
    )

    proficiency_level_in: Optional[List[int]] = Field(
        default=None,
        description="에너지 소비 효율 등급 목록 중 하나와 일치하는 제품 검색"
    )

    voltage_gte: Optional[int] = Field(
        default=None,
        description="전압이 지정 값 이상인 제품 검색"
    )

    voltage_lte: Optional[int] = Field(
        default=None,
        description="전압이 지정 값 이하인 제품 검색"
    )

    voltage_in: Optional[List[int]] = Field(
        default=None,
        description="전압 목록 중 하나와 일치하는 제품 검색"
    )

    hertz_gte: Optional[int] = Field(
        default=None,
        description="주파수가 지정 값 이상인 제품 검색"
    )

    hertz_lte: Optional[int] = Field(
        default=None,
        description="주파수가 지정 값 이하인 제품 검색"
    )

    hertz_in: Optional[List[int]] = Field(
        default=None,
        description="주파수 목록 중 하나와 일치하는 제품 검색"
    )

    cool_cap_gte: Optional[int] = Field(
        default=None,
        description="냉방 능력이 지정 값 이상인 제품 검색"
    )

    cool_cap_lte: Optional[int] = Field(
        default=None,
        description="냉방 능력이 지정 값 이하인 제품 검색"
    )

    coverage_gte: Optional[float] = Field(
        default=None,
        description="냉방 면적이 지정 값 이상인 제품 검색"
    )

    coverage_lte: Optional[float] = Field(
        default=None,
        description="냉방 면적이 지정 값 이하인 제품 검색"
    )

    color_icontains: Optional[List[str]] = Field(
        default=None,
        description="색상에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )


class TVTFields(BaseModel):
    from_favorites: bool = Field(
        description="사용자 관심/보유 제품 범위 안에서만 검색해야 하면 True, 전체 제품 범위에서 검색해야 하면 False"
    )

    vector_search: str = Field(
        description="사용설명서 벡터 검색에 사용할 검색 문자열. 사용자의 의도를 유지하되 검색에 적합하게 짧고 명확한 문장으로 변환"
    )

    name_icontains: Optional[List[str]] = Field(
        default=None,
        description="상품명에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    resol_code_in: Optional[List[str]] = Field(
        default=None,
        description="해상도 코드 목록 중 하나와 일치하는 제품 검색"
    )

    price_gte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이상인 제품 검색"
    )

    price_lte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이하인 제품 검색"
    )

    proficiency_level_gte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이상인 제품 검색"
    )

    proficiency_level_lte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이하인 제품 검색"
    )

    proficiency_level_in: Optional[List[int]] = Field(
        default=None,
        description="에너지 소비 효율 등급 목록 중 하나와 일치하는 제품 검색"
    )

    screen_size_gte: Optional[int] = Field(
        default=None,
        description="화면 크기가 지정 값 이상인 제품 검색"
    )

    screen_size_lte: Optional[int] = Field(
        default=None,
        description="화면 크기가 지정 값 이하인 제품 검색"
    )

    display_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="디스플레이 타입에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    ref_rate_gte: Optional[int] = Field(
        default=None,
        description="주사율이 지정 값 이상인 제품 검색"
    )

    ref_rate_lte: Optional[int] = Field(
        default=None,
        description="주사율이 지정 값 이하인 제품 검색"
    )

    ref_rate_in: Optional[List[int]] = Field(
        default=None,
        description="주사율 목록 중 하나와 일치하는 제품 검색"
    )

    os_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="운영체제 이름에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )


class REFFields(BaseModel):
    from_favorites: bool = Field(
        description="사용자 관심/보유 제품 범위 안에서만 검색해야 하면 True, 전체 제품 범위에서 검색해야 하면 False"
    )

    vector_search: str = Field(
        description="사용설명서 벡터 검색에 사용할 검색 문자열. 사용자의 의도를 유지하되 검색에 적합하게 짧고 명확한 문장으로 변환"
    )

    name_icontains: Optional[List[str]] = Field(
        default=None,
        description="상품명에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    price_gte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이상인 제품 검색"
    )

    price_lte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이하인 제품 검색"
    )

    proficiency_level_gte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이상인 제품 검색"
    )

    proficiency_level_lte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이하인 제품 검색"
    )

    proficiency_level_in: Optional[List[int]] = Field(
        default=None,
        description="에너지 소비 효율 등급 목록 중 하나와 일치하는 제품 검색"
    )

    install_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="설치 타입에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    door_cnt_gte: Optional[int] = Field(
        default=None,
        description="도어 개수가 지정 값 이상인 제품 검색"
    )

    door_cnt_lte: Optional[int] = Field(
        default=None,
        description="도어 개수가 지정 값 이하인 제품 검색"
    )

    door_cnt_in: Optional[List[int]] = Field(
        default=None,
        description="도어 개수 목록 중 하나와 일치하는 제품 검색"
    )

    total_cap_gte: Optional[int] = Field(
        default=None,
        description="전체 용량이 지정 값 이상인 제품 검색"
    )

    total_cap_lte: Optional[int] = Field(
        default=None,
        description="전체 용량이 지정 값 이하인 제품 검색"
    )

    color_icontains: Optional[List[str]] = Field(
        default=None,
        description="색상에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    door_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="도어 타입에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    cool_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="냉각 방식에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    smart_diag_in: Optional[List[int]] = Field(
        default=None,
        description="스마트 진단 지원 여부 값 목록 중 하나와 일치하는 제품 검색"
    )

    ice_maker_in: Optional[List[int]] = Field(
        default=None,
        description="아이스 메이커 지원 여부 값 목록 중 하나와 일치하는 제품 검색"
    )


class VACFields(BaseModel):
    from_favorites: bool = Field(
        description="사용자 관심/보유 제품 범위 안에서만 검색해야 하면 True, 전체 제품 범위에서 검색해야 하면 False"
    )

    vector_search: str = Field(
        description="사용설명서 벡터 검색에 사용할 검색 문자열. 사용자의 의도를 유지하되 검색에 적합하게 짧고 명확한 문장으로 변환"
    )

    name_icontains: Optional[List[str]] = Field(
        default=None,
        description="상품명에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    price_gte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이상인 제품 검색"
    )

    price_lte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이하인 제품 검색"
    )

    proficiency_level_gte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이상인 제품 검색"
    )

    proficiency_level_lte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이하인 제품 검색"
    )

    proficiency_level_in: Optional[List[int]] = Field(
        default=None,
        description="에너지 소비 효율 등급 목록 중 하나와 일치하는 제품 검색"
    )

    suction_power_gte: Optional[int] = Field(
        default=None,
        description="흡입력이 지정 값 이상인 제품 검색"
    )

    suction_power_lte: Optional[int] = Field(
        default=None,
        description="흡입력이 지정 값 이하인 제품 검색"
    )

    battery_cnt_gte: Optional[int] = Field(
        default=None,
        description="배터리 개수가 지정 값 이상인 제품 검색"
    )

    battery_cnt_lte: Optional[int] = Field(
        default=None,
        description="배터리 개수가 지정 값 이하인 제품 검색"
    )

    battery_cnt_in: Optional[List[int]] = Field(
        default=None,
        description="배터리 개수 목록 중 하나와 일치하는 제품 검색"
    )

    color_icontains: Optional[List[str]] = Field(
        default=None,
        description="색상에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )


class WMTFields(BaseModel):
    from_favorites: bool = Field(
        description="사용자 관심/보유 제품 범위 안에서만 검색해야 하면 True, 전체 제품 범위에서 검색해야 하면 False"
    )

    vector_search: str = Field(
        description="사용설명서 벡터 검색에 사용할 검색 문자열. 사용자의 의도를 유지하되 검색에 적합하게 짧고 명확한 문장으로 변환"
    )

    name_icontains: Optional[List[str]] = Field(
        default=None,
        description="상품명에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    price_gte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이상인 제품 검색"
    )

    price_lte: Optional[int] = Field(
        default=None,
        description="가격이 지정 값 이하인 제품 검색"
    )

    proficiency_level_gte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이상인 제품 검색"
    )

    proficiency_level_lte: Optional[int] = Field(
        default=None,
        description="에너지 소비 효율 등급이 지정 값 이하인 제품 검색"
    )

    proficiency_level_in: Optional[List[int]] = Field(
        default=None,
        description="에너지 소비 효율 등급 목록 중 하나와 일치하는 제품 검색"
    )

    washing_cap_gte: Optional[int] = Field(
        default=None,
        description="세탁 용량이 지정 값 이상인 제품 검색"
    )

    washing_cap_lte: Optional[int] = Field(
        default=None,
        description="세탁 용량이 지정 값 이하인 제품 검색"
    )

    drying_cap_gte: Optional[int] = Field(
        default=None,
        description="건조 용량이 지정 값 이상인 제품 검색"
    )

    drying_cap_lte: Optional[int] = Field(
        default=None,
        description="건조 용량이 지정 값 이하인 제품 검색"
    )

    color_icontains: Optional[List[str]] = Field(
        default=None,
        description="색상에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    door_design_icontains: Optional[List[str]] = Field(
        default=None,
        description="도어 디자인에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    control_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="조작 방식에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    door_type_icontains: Optional[List[str]] = Field(
        default=None,
        description="도어 타입에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

    water_temp_icontains: Optional[List[str]] = Field(
        default=None,
        description="지원 물온도 옵션에 포함되어야 하는 문자열 목록. 목록의 모든 문자열을 포함하는 제품 검색. 대소문자 구분 없음"
    )

ACT_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(ACTFields)

TVT_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(TVTFields)

REF_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(REFFields)

VAC_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(VACFields)

WMT_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(WMTFields)

intent_router_prompt = """
너는 전자제품 검색 조건 추출기다.

너의 역할은 사용자의 자연어 입력에서 현재 structured output schema에 존재하는 필드 값만 추출하는 것이다.
현재 어떤 제품군 schema가 사용되는지는 런타임에 결정된다.
schema에 없는 필드는 절대 만들지 말아라.

사용자가 전자제품의 기능을 언급한 경우에만 사용설명서 벡터 검색을 실시해라.
ex) "에어컨 자동 청소 기능 어떻게 써?" → vector_search="에어컨 자동 청소 방법"
ex) "세탁기 에러코드 UE가 뭐야?" → vector_search="세탁기 에러코드 UE 해결 방법"
ex) "가정용 청소기 검색해줘" → 기능 언급 없음 → vector_search=""

사용자 요청의 자연어 입력 맥락을 고려해서 적당한 조건을 찾아 추가해라.
ex) 가정용 세탁기 찾아줘 > 세탁기에는 washing_cap_lte, drying_cap_lte 같은 용량 조건이 있으니 가정용이라는 표현을 고려해서 20정도로 낮은 값의 washing_cap_lte=20 조건을 추출해서 넣어본다. 인원수가 명시되어 있을 경우 인당 5kg 정도로 계산해서 3인의 경우 용량을 washing_cap_gte=12, washing_cap_lte=20으로 한다.
ex) 원룸용 냉장고 찾아줘 > 냉장고에는 total_cap_lte 같은 용량 조건이 있으니 원룸용이라는 표현을 고려해서 낮은 값의 total_cap_lte=450 정도의 조건을 추출해서 넣어준다.
ex) 가성비 좋은 TV 추천해줘 > TV는 900만원정도가 비싸고 450만원 정도가 중간이니 가격이 저렴한 제품을 선호하는 것으로 보고 price_lte=4500000 조건을 넣어본다.
ex) 거실용 에어컨 용량 추천해줘 > 에어컨에는 coverage 같은 냉방 능력 조건이 있으니 거실용이라는 표현을 고려해서 40정도의 coverage_lte=40 조건을 추출해서 넣어본다.

채팅의 맥락도 같이 제공되지만 가장 최근의 사용자 메시지에 요구 조건을 추출 하는 것을 최우선으로 하고 이전 맥락은 참고하는데만 사용한다.
다만 이전의 조건을 활용해서 해석할 필요 없이 단순히 같은 조건으로 더 검색하는 경우는 이전 맥락을 참조하지 않는다.
ex) 그럼 그 중에서 색상에 베이지가 들어간 제품 찾아줘, 그러면 베이지 색상 제품 찾아줘 > 이전 조건을 활용해서 새 조건을 정할 필요가 없으니 단순히 color_icontains=["베이지"]만 채움
ex) 그럼 조금 더 비싸게 검색해봐 > 이전 조건을 활용해서 새 조건을 세울 필요가 있음, 가장 최근 채팅이 "100000원 이상 제품 찾아줘"임을 확인하고 price_gte 200000을 반환

공통 규칙:
- bool 필드는 명확한 근거가 있을 때만 True/False를 판단한다.
- 숫자 필드는 int 또는 float로 변환한다.
- 가격은 원 단위 정수로 변환한다.
  예: "100만원 이하" → price_lte=1000000
  예: "50만 원 이상" → price_gte=500000
- "이상", "부터", "넘는", "큰" 조건은 *_gte에 넣는다.
- "이하", "까지", "안으로", "미만", "작은" 조건은 *_lte에 넣는다.
- "정확히", "중 하나", "또는", "나"처럼 여러 후보가 있으면 *_in 필드를 사용한다.
- *_icontains 필드는 사용자가 말한 핵심 문자열 목록을 넣는다.
- *_icontains 필드의 목록에 들어간 문자열은 모두 포함되어야 하는 AND 조건으로 사용된다.
- 하나의 *_icontains 조건만 있어도 반드시 ["문자열"] 형태의 리스트로 넣는다.
- 같은 필드에 대해 사용자가 여러 핵심 문자열을 말하면 각각 분리해서 리스트에 넣는다.
- 사용자가 제품명, 브랜드명, 모델명을 말하면 name_icontains에 리스트로 넣는다.
- 색상 표현은 color_icontains에 리스트로 넣는다.
- 사용자가 모호하게 말한 조건을 임의로 수치화하지 않는다.
- 단위는 제거하고 값만 넣는다.
- schema에 존재하지 않는 필드와 관련된 정보는 무시한다.

에너지 소비 효율 등급 규칙:
- "1등급" → proficiency_level_in=[1]
- "1등급이나 2등급" → proficiency_level_in=[1, 2]
- "2등급 이상"처럼 등급 표현은 일반 숫자 크기와 반대로 해석하지 말고, 사용자의 문장을 그대로 조건화한다.
  단, 애매하면 proficiency_level_in을 우선 사용한다.

from_favorites 규칙:
- "내 관심 제품", "찜한 제품", "보유 제품", "내가 가진 제품", "즐겨찾기에서"처럼 사용자의 개인 제품 범위가 언급되면 True
- "전체 제품", "모든 제품", "새로 찾아줘"처럼 전체 검색이면 False
- 해당 필드가 schema에 있고 별도 언급이 없으면 False

vector_search 규칙:
- 해당 필드가 schema에 있으면 항상 채운다.
- 사용자의 의도를 유지하되, 사용설명서 검색에 적합한 짧고 명확한 한국어 문장으로 만든다.
- 상품 필터 조건보다 사용자의 실제 질문 의도에 집중한다.
- 예: "에어컨 필터 청소 어떻게 해?" → "에어컨 필터 청소 방법"
- 단순 제품 검색 요청이면 핵심 검색 의도를 짧게 요약한다.
- 만약 사용설명서 내용을 참고할 필요가 없거나 사양에 대한 의사만 밝혔을 경우 빈 문자열 ""로 채운다.

제품군별 의미 참고:
- ACTFields: 에어컨. 전압, 주파수, 냉방 능력, 냉방 면적, 색상 등을 추출한다.
- TVTFields: TV. 해상도, 화면 크기, 디스플레이 타입, 주사율, OS 타입 등을 추출한다.
- REFFields: 냉장고. 설치 타입, 도어 개수, 전체 용량, 색상, 도어 타입, 냉각 방식, 스마트 진단, 아이스 메이커 여부 등을 추출한다.
- VACFields: 청소기. 흡입력, 배터리 개수, 색상 등을 추출한다.
- WMTFields: 세탁기/건조기. 세탁 용량, 건조 용량, 색상, 도어 디자인, 조작 방식, 도어 타입, 물온도 옵션 등을 추출한다.

지원 여부 값 규칙:
- smart_diag_in, ice_maker_in 같은 지원 여부 필드는 지원/있음/가능이면 [1], 미지원/없음/불가능이면 [0]으로 추출한다.

반드시 현재 structured output schema에 맞는 객체만 반환하라.
설명 문장, markdown, JSON 코드블록은 출력하지 마라.
"""

def invoke_intent_router_node(product_type:str, chats:list[str]):
    """
    제품군별 Pydantic 스키마로 검색 슬롯·벡터 검색어·from_favorites 등 intent 추출.
    product_type에 맞는 structured output 모델을 선택한다.
    """
    global ACT_node, TVT_node, REF_node, VAC_node, WMT_node
    global intent_router_prompt

    match product_type:
        case "ACT":
            target_model = ACT_node
        case "TVT":
            target_model = TVT_node
        case "REF":
            target_model = REF_node
        case "VAC":
            target_model = VAC_node
        case "WMT":
            target_model = WMT_node
        case _:
            target_model = REF_node

    return invoke_llm(target_model, intent_router_prompt, chats)

############################################################
# answer_with_result_node
############################################################

class AnswerWithResultStructure(BaseModel):
    answer: str = Field(
        description="검색 결과를 바탕으로 사용자에게 제공할 최종 답변"
    )

answer_with_result_node = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
).with_structured_output(AnswerWithResultStructure)

answer_with_result_prompt = """
너는 전자제품 사용설명서 기반 Q&A 및 제품 검색 챗봇의 최종 답변 생성기이다.

너의 역할은 이전 단계에서 검색된 결과를 바탕으로 사용자에게 자연스럽고 정확한 최종 답변을 제공하는 것이다.

채팅의 맥락도 같이 제공되지만 가장 최근의 사용자 메시지에 답변을 하는 것을 최우선으로 하고 이전 맥락은 참고하는데만 사용한다.

입력으로는 다음 정보가 제공될 수 있다.

1. 사용자 질문
- 사용자가 실제로 입력한 질문이다.

2. 제품 카테고리
- TVT: TV
- ACT: 에어컨
- REF: 냉장고
- VAC: 청소기
- WMT: 세탁기

3. DB 검색 결과
- 가격, 용량, 크기, 색상, 에너지 등급, 성능 조건 등을 기준으로 검색된 제품 목록이다.

4. 사용설명서 검색 결과
- 제품 사용법, 기능 설명, 오류 해결 방법 등 매뉴얼 기반 검색 결과이다.

답변 원칙:

1. 검색 결과 기반 답변
- 반드시 제공된 검색 결과를 우선 근거로 답변한다.
- 검색 결과에 없는 제품명, 기능, 가격, 수치, 설명을 임의로 만들어내지 않는다.
- 검색 결과가 여러 개일 경우 사용자의 조건에 가장 잘 맞는 결과를 우선적으로 정리한다.

2. 제품 추천/검색 답변
- 사용자가 제품 추천이나 조건 검색을 요청했다면, 적합한 제품을 1~3개 정도로 정리한다.
- 각 제품에 대해 사용자가 요청한 조건과 관련된 핵심 정보만 간결하게 설명한다.
- 가격, 용량, 크기, 색상, 에너지 등급, 성능 정보가 있으면 함께 제시한다.
- 검색 결과가 없으면 조건을 완화하거나 다른 조건으로 다시 검색해볼 수 있다고 안내한다.

3. 사용설명서 Q&A 답변
- 사용자가 사용법, 기능, 오류 해결 방법을 물었다면 사용설명서 검색 결과를 바탕으로 설명한다.
- 단계가 필요한 경우 번호를 사용해 순서대로 설명한다.
- 에러코드나 기능 설명은 사용자가 바로 이해할 수 있게 풀어서 설명한다.
- 매뉴얼 검색 결과가 부족하면 확인 가능한 정보가 부족하다고 말하고, 제품명이나 모델명을 추가로 요청한다.
- 매뉴얼 정보는 실제 검색된 제품 범위보다 넓게 제시되므로 DB 검색 결과를 우선해서 관련된 제품 코드가 존재하는 매뉴얼만을 참조해서 답변한다.
- 매뉴얼 정보에 대해서는 page_number를 활용해서 출처를 명시한다

4. 관심/보유 제품 범위 답변
- from_favorites가 True인 경우 사용자의 관심/보유 제품 범위 안에서 확인한 결과임을 자연스럽게 언급한다.
- from_favorites가 False인 경우 전체 제품 범위에서 검색한 결과로 답변한다.
- 단, 이 정보가 입력으로 제공되지 않으면 따로 언급하지 않는다.

5. 응답 스타일
- 과도하게 장황하게 말하지 않는다.
- 사용자의 질문에 직접 답한다.
- 불확실한 내용은 단정하지 않는다.
- 검색 결과가 부족하면 임의로 보완하지 말고 부족하다고 말한다.
- 마지막에는 필요하면 추가 조건을 제안한다.

출력 규칙:
- answer 필드에만 최종 답변을 작성한다.
"""

def invoke_answer_with_result_node(graph_state, chats:list[str]):
    """
    DB·매뉴얼 검색 결과를 컨텍스트에 넣어 최종 자연어 답변 생성.
    graph_state: search_results, manual_results 등 llm.GraphState 필드.
    """
    global answer_with_result_node, answer_with_result_prompt

    recent_user_chat = chats[-1]
    data_loader_chat = f"""
사용자 입력:
{recent_user_chat}

사용자 입력 기반 DB 검색 결과:
{graph_state["search_results"]}

제품 설명서 검색 결과:
{graph_state["manual_results"]}
"""
    
    cop = [l for l in chats]
    cop[-1] = data_loader_chat

    return invoke_llm(answer_with_result_node, answer_with_result_prompt, cop)
