# 모델 노드 평가 기록

[문서 홈](../README.md) · [검증과 한계](verification-and-limitations.md)

기존 루트 README의 평가 결과를 옮긴 기록입니다. 원문에는 실행 날짜와 평가 당시 커밋이 없으며, 이 문서 정리 과정에서 외부 모델을 재호출하지 않았습니다. 아래 수치는 당시의 소규모 노드 평가 결과이며 전체 추천·RAG 답변 정확도나 현재 운영 성능을 나타내지 않습니다. 재현용 원본은 [llm_frame.ipynb](../../notebooks/evaluation/llm_frame.ipynb)입니다.

범위 밖 판정은 50건, 후속 질문 판정은 50건의 혼동행렬을 기록했습니다. 제품군 분류는 아래 20건의 예제입니다. 인사·모호한 질문의 정답 라벨에 대한 해석 차이도 원문에 포함되어 있습니다.

## 기존 평가 결과


### 10.1 평가 설정
- fall_case_node의 is_fall_case True, False 판정 확인
- subsequence_router_node의 is_subsequence True, False 판정 확인
- product_classification_node의 분류 정확도 확인



### 10.2 차수별 핵심 성능 비교

- fall_case_node Confusion Matrix

|                | Predicted Positive | Predicted Negative |
|----------------|-------------------|-------------------|
| Actual Positive | 24 | 1 |
| Actual Negative | 3 | 22 |

- fall_case_node Metrics

| Metric | Score |
|--------|--------|
| Accuracy | 0.9200 |
| Precision | 0.8889 |
| Recall | 0.9600 |
| F1 Score | 0.9231 |

- subsequence_router_node Confusion Matrix

|                | Predicted Positive | Predicted Negative |
|----------------|-------------------|-------------------|
| Actual Positive | 25 | 0 |
| Actual Negative | 0 | 25 |

- subsequence_router_node Metrics

| Metric | Score |
|--------|--------|
| Accuracy | 1.0000 |
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1 Score | 1.0000 |

- product_classification_node Prediction Results

| Index | 사용자의 질문 | 정답 라벨 | predict_label | is_correct |
|------|-----------------------------|-----------|---------------|------------|
| 0 | TV 화면이 너무 어두워 | TVT | TVT | True |
| 1 | 티비 리모컨 연결 방법 알려줘 | TVT | TVT | True |
| 2 | 에어컨 자동 청소 기능 어떻게 써? | ACT | ACT | True |
| 3 | 제습 잘 되는 에어컨 찾아줘 | ACT | ACT | True |
| 4 | 냉장고 필터 교체 방법 알려줘 | REF | REF | True |
| 5 | 김치냉장고 추천해줘 | REF | REF | True |
| 6 | 흡입력 좋은 청소기 찾아줘 | VAC | VAC | True |
| 7 | 로봇청소기 물걸레 기능 있어? | VAC | VAC | True |
| 8 | 세탁기 UE 에러가 뭐야? | WMT | WMT | True |
| 9 | 건조 기능 있는 세탁기 찾아줘 | WMT | WMT | True |
| 10 | 안녕 |  |  | True |
| 11 | 오늘 날씨 어때? |  |  | True |
| 12 | 전자레인지 추천해줘 |  |  | True |
| 13 | 노트북 찾아줘 |  |  | True |
| 14 | 공기청정기 필터 교체 방법 알려줘 |  |  | True |
| 15 | 그중에 제일 싼 거 |  |  | True |
| 16 | 두 번째 거 설명해줘 |  |  | True |
| 17 | 삼성 거 추천해줘 |  |  | True |
| 18 | LG 제품 찾아줘 |  |  | True |
| 19 | 건조기 추천해줘 |  |  | True |

- product_classification_node Accuracy
Accuracy: **100.00%**


### 10.3 질의 유형별 비교
3개의 분기 node모두 단순한 작업 단위로 나누어 llm요청을 보냈기 때문에
분기, 분류에 있어 높은 정확도를 확인할 수 있었다.


### 10.4 차수별 실패 패턴과 보완 포인트
- fall_case_node의 경우 아래의 test case가 예측이 실패했다

- 정답 라벨에서 fall_case가 False로 제시되어 있는 아래 질문들에 llm은 fall_case True를 판정했다.
비교해줘 > 어떤 전자제품을 비교해드릴까요? 제품명이나 종류를 알려주시면 도움을 드리겠습니다.
안녕 > 안녕하세요! 전자제품에 대한 질문이 있으시면 도와드릴게요.
질문해도 돼? > 전자제품에 대한 질문이 있으시면 말씀해 주세요!
>> 위의 질문들은 간단한 사교성/혹은 바로 답변할 수 있는 질문들로 fall_case True라고 할 수 있다.

- 정답 라벨에서 fall_case가 True로 제시되어 있는 아래 질문에 llm은 fall_case False를 판정했다.
이 TV 바로 구매해줘
>> 위의 질문은 TV의 구매라는 llm의 역할 범위 외의 질문이었지만 TV가 내용에 포함되어 있어 fall_case 판정에 실패했다.

### 10.5 무엇을 추가로 보완해야 하는가
- llm prompt의 허점을 확인하기 위해서 더 많은 테스트 케이스의 확인
- 더 많은 사용자 요청에 답변할 수 있게끔 langgraph node 구조의 고도화
- intent_router_node에 대해서도 추가로 슬롯 추출 정확도 테스트
- 확인한 제품 정보를 활용해서 더 다양한 답변을 생성할 수 있도록 프롬프트 최적화


### 10.6 재현 방법
llm 테스트는 아래의 파일의 코드를 통해 수행하였음
[notebooks/evaluation/llm_frame.ipynb](../../notebooks/evaluation/llm_frame.ipynb)


---
