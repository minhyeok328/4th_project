# Django 앱 상세

[백엔드](README.md)

## mainpage와 products

[mainpage/views.py](../../mainpage/views.py)는 메인 템플릿을 렌더링합니다. [products/views.py](../../products/views.py)의 `searchpage`는 `product_type`·`page` 누락 값을 추가해 redirect하고, 나머지 GET 키를 조건으로 전달합니다. 기존에 주어진 값은 유지합니다.

`_get_condition_values`는 일반 조건의 마지막 값을 사용하고 `_in`·`__in`은 쉼표와 반복 쿼리를 목록으로, `_icontains`·`__icontains`는 반복 값을 목록으로 만듭니다. 검색 결과는 `Paginator(..., 12)`로 처리합니다. `productpage`는 코드 조회와 사용자 찜 여부를 템플릿에 전달하며 미존재 상품에 명시적 404를 반환하지 않습니다.

## accounts

[Account](../../accounts/models.py)는 AbstractUser를 확장합니다. [views.py](../../accounts/views.py)는 로그인·회원가입·마이페이지·로그아웃을 구현합니다. 마이페이지 POST 액션은 `toggle_favorite`, `update_profile`, `logout`입니다. 비로그인은 로그인 페이지로 이동합니다.

프로필은 선택적으로 닉네임·사진을 갱신합니다. 찜은 DB FK 대신 상품 코드 문자열로 저장하고 화면 조회 때 `get_product`로 찾지 못한 항목은 제외합니다. 실제 상품 존재를 검증하지 않는 마이페이지 경로와 상품을 검사하는 레거시 API가 구분됩니다.

## chats

[chats/views.py](../../chats/views.py)는 사용자 소유 방 중 메시지가 있는 방만 최근 timestamp 순으로 표시합니다. `?chat_id=`로 선택한 방의 메시지를 읽고, POST `delete_id`는 소유 관계를 확인해 삭제합니다. 잘못된 ID는 선택·삭제를 하지 않고 화면을 계속 처리합니다.

[models.py](../../chats/models.py)의 메시지 index는 현재 메시지 수로 부여합니다. 방의 JSON 상태는 AI의 다음 요청에 사용됩니다.

## api와 common

[api/views.py](../../api/views.py)는 `send_chat`, `favorite`, `check_favorite`를 제공합니다. 요청·응답 차이는 [API 명세](../06-api/api-reference.md)에 있습니다.

[common/utils.py](../../common/utils.py)는 코드 접두로 모델을 선택하고 상품·찜을 조회합니다. [llm.py](../../common/llm.py)는 그래프와 대화 저장을 연결하고 [llm_agent.py](../../common/llm_agent.py)는 구조화된 LLM 출력을 정의합니다. `common`은 INSTALLED_APPS에 등록하는 앱이 아닙니다.

## 설정 의존성

[settings.py](../../config/settings.py)는 세션·인증·CSRF 미들웨어, SQLite, 커스텀 사용자, Tailwind 앱을 설정합니다. `.env` 로드와 외부 클라이언트 import가 실행 시작 단계에 연결되어 있습니다. 운영 구성은 [배포 조건](../09-deployment/deployment.md)을 참고합니다.
