# 계정과 관심 제품

[기능 안내](README.md) · [스키마](../05-database/schema-and-erd.md)

## 경로

| 경로 | 처리 |
|---|---|
| `/accounts/` | 로그인 폼, 성공 시 메인으로 이동 |
| `/accounts/register/` | 가입 폼, 생성 후 로그인 화면으로 이동 |
| `/accounts/mypage/` | 로그인 사용자의 프로필과 찜 목록 |
| `/accounts/logout/` | POST 로그아웃 후 메인으로 이동 |

[accounts/views.py](../../accounts/views.py)는 Django 세션 인증을 사용합니다. 회원가입은 사용자명·비밀번호·닉네임·선택 사진을 받아 `create_user`로 저장합니다. 중복 사용자 등 예외를 통일된 폼 오류로 처리하는 구현은 없습니다.

## 마이페이지 액션

| POST action | 입력 | 결과 |
|---|---|---|
| `toggle_favorite` | `product_code` | JSON `{ok, favorited}` |
| `update_profile` | `nickname`, 선택 `profile_picture` | 저장 후 마이페이지 redirect |
| `logout` | 추가 필드 없음 | 메인 redirect |

찜은 `UserFavorite` 문자열 코드로 저장합니다. 빈 코드는 400이며 상품 존재 검증은 하지 않습니다. 마이페이지 표시 시 `get_product`에서 찾지 못한 코드는 목록에서 제외됩니다.

## 화면과 상담 연결

[wishlist-toggle.js](../../static/js/wishlist-toggle.js)가 상세와 마이페이지의 찜을 공통 처리합니다. 동일 상품 동시 클릭 가드, 버튼 busy, 실패 알림, 제거 후 개수 배지 갱신이 있습니다. 비로그인 상세 찜은 로그인 화면으로 이동합니다.

상담에서 `from_favorites`가 추출되면 [llm.py](../../common/llm.py)의 `intent_router`가 사용자의 찜 코드를 제품군별로 고릅니다. DB에는 사용자·상품 코드 unique 제약이 없으므로 클라이언트 가드만으로 중복 생성 방지를 보장하지 않습니다.

`/api/favorite/`와 `/api/check_favorite/`는 다른 응답 의미를 가진 대안 경로입니다. [API 명세](../06-api/api-reference.md)를 확인한 후 사용합니다.
