"""
상품·찜 공통 조회 유틸.

- product_code 앞 3자(ACT/REF/TVT/VAC/WMT)로 제품군 모델 분기
- 챗봇 DB 검색(llm.db_search_node), 상세·마이페이지·API 찜에서 사용
"""

from django.db import models
from products import models as p_models
from accounts import models as a_models

def safe_get(mod:models.Model, dct):
    """DoesNotExist 시 None, 있으면 단일 ORM 인스턴스."""
    try:
        return mod.objects.get(**dct)
    except mod.DoesNotExist:
        return None

def get_model(product_code:str):
    """제품군 3자 코드(또는 product_code 접두)로 Product* 모델 클래스를 반환한다."""
    if not product_code or len(product_code) < 3:
        return None

    header = product_code[0:3].upper()

    match header:
        case "ACT":
            return p_models.ProductAC
        case "REF":
            return p_models.ProductFridge
        case "TVT":
            return p_models.ProductTV
        case "VAC":
            return p_models.ProductVAC
        case "WMT":
            return p_models.ProductWash
        case _:
            return None

def get_product(product_code:str):
    """
    전체 product_code로 DB 테이블명·상품 인스턴스를 조회한다.

    Returns:
        (db_table 또는 product_type 문자열, 모델 인스턴스|None)
    """
    header = product_code[0:3].upper()

    p_code = header + product_code[3:]

    match header:
        case "ACT":
            product_type = p_models.ProductAC._meta.db_table
            return product_type, safe_get(p_models.ProductAC, {"product_code": p_code})
        case "REF":
            product_type = p_models.ProductFridge._meta.db_table
            return product_type, safe_get(p_models.ProductFridge, {"product_code": p_code})
        case "TVT":
            product_type = p_models.ProductTV._meta.db_table
            return product_type, safe_get(p_models.ProductTV, {"product_code": p_code})
        case "VAC":
            product_type = p_models.ProductVAC._meta.db_table
            return product_type, safe_get(p_models.ProductVAC, {"product_code": p_code})
        case "WMT":
            product_type = p_models.ProductWash._meta.db_table
            return product_type, safe_get(p_models.ProductWash, {"product_code": p_code})
        case _:
            return None, None

def get_favorites(account_id:int):
    """계정의 찜 product_code 목록 — 챗봇 from_favorites 검색 범위 제한용."""
    return list(
        a_models.UserFavorite.objects
        .filter(account_id=account_id)
        .values_list("product_code", flat=True)
    )

def search_product(product_type, range, conditions):
    """
    제품군 모델의 search()로 조건 필터링된 상품 queryset/리스트 반환.

    Args:
        product_type: ACT/REF/TVT/VAC/WMT
        range: product_code_in 등 선필터(챗봇)
        conditions: intent·slots 병합 dict (__gte, __in 등)
    """
    model = get_model(product_type)
    if model is None:
        return []
    return model.search(range, **conditions)
