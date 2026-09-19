# 상품 상세

[기능 안내](README.md)

## 조회

GET `/products/<product_code>/` → [products.views.productpage](../../products/views.py) → [common.utils.get_product](../../common/utils.py) → [productpage.html](../../templates/productpage.html) 순서로 처리합니다. 코드 앞 3자로 제품군 모델을 선택하고 로그인한 사용자의 찜 여부를 함께 전달합니다.

없는 상품은 `product_data=None`으로 렌더링하며 명시적 404 처리가 아닙니다. NULL 가격·사양은 표시 대체값과 함께 확인해야 합니다.

## 컴포넌트

| 경로 | 내용 |
|---|---|
| [product_summary.html](../../templates/components/product/product_summary.html) | 이름·이미지·가격 |
| [product_detail_specs.html](../../templates/components/product/product_detail_specs.html) | 제품군별 상세 사양 |
| [product_tabs.html](../../templates/components/product/product_tabs.html) | 상세·스펙·리뷰·Q&A 탭 |
| [product_actions.html](../../templates/components/product/product_actions.html) | 찜·구매 버튼 |

리뷰·Q&A 본문은 템플릿에 입력된 예시이며 실제 구매 후기나 문의 데이터가 아닙니다. 구매 버튼은 로그인 확인만 수행하고 주문·결제 API를 호출하지 않습니다.

## 찜 연동

`product_actions`의 인증 상태·API URL·CSRF data 속성을 [wishlist-toggle.js](../../static/js/wishlist-toggle.js)가 읽습니다. `POST /accounts/mypage/`에 `action=toggle_favorite`를 전달하고 `{ok, favorited}`로 버튼을 갱신합니다. 비로그인은 로그인으로 이동하고 중복 클릭·실패 알림을 처리합니다.

[계정과 찜](accounts-and-favorites.md) · [API 명세](../06-api/api-reference.md)
