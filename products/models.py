"""
제품군별 ORM 모델 및 공통 검색(search_model).

연결:
- common.utils.get_model / search_product → 각 Product*.search()
- products.views.searchpage: GET 쿼리 키(price__gte, color__in 등)
- common.llm.db_search_node: LLM 슬롯 키(price_gte, name_icontains 등) — _split_condition_key가 둘 다 해석

제품군 코드( product_code 접두 3자 ): ACT, TVT, REF, VAC, WMT
"""

from django.db import models
from django.core.exceptions import ValidationError


# Django ORM lookup + LLM 슬롯 접미사(gte / __gte 등) 통합
LOOKUPS = ("gte", "lte", "in", "icontains", "exact")
# icontains 기본 적용 대상(문자열 필드)
TEXT_FIELDS = (
    models.CharField,
    models.TextField,
    models.URLField,
    models.EmailField,
    models.SlugField,
)


def model_to_tuple_str(instance):
    """디버그·__str__용 — 모든 컬럼 값을 튜플 문자열로."""
    values = [str(getattr(instance, field.attname)) for field in instance._meta.fields]
    return f"({', '.join(values)})"


def _get_compare_field(field):
    """FK는 target_field 타입으로 비교·to_python."""
    if isinstance(field, models.ForeignKey):
        return field.target_field
    return field


def _is_text_field(field):
    """lookup 미지정 시 icontains vs exact 기본값 결정에 사용."""
    return isinstance(_get_compare_field(field), TEXT_FIELDS)


def _convert_value(field, value):
    """단일 조건값을 필드 타입에 맞게 변환, 실패·빈 값은 None."""
    compare_field = _get_compare_field(field)

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

    if value == "":
        return None

    try:
        return compare_field.to_python(value)
    except (TypeError, ValueError, ValidationError):
        return None


def _convert_filter_value(field, lookup, value):
    """in(콤마 분리)·icontains(리스트) 등 lookup별 값 정규화."""
    if lookup in ("in", "icontains"):
        if isinstance(value, str):
            values = [item.strip() for item in value.split(",")] if lookup == "in" else [value]
        else:
            values = value

        if not isinstance(values, (list, tuple, set)):
            values = [values]

        if lookup == "in":
            converted_values = [
                converted
                for item in values
                if (converted := _convert_value(field, item)) is not None
            ]
            return converted_values or None

        converted_values = []
        for item in values:
            if item is None:
                continue

            converted = str(item).strip()
            if converted:
                converted_values.append(converted)

        return converted_values or None

    return _convert_value(field, value)


def _split_condition_key(key, field_names):
    # Web GET uses Django keys (price__gte); LLM slots use price_gte, name_icontains, etc.
    for lookup in sorted(LOOKUPS, key=len, reverse=True):
        for sep in ("__", "_"):
            suffix = f"{sep}{lookup}"
            if not key.endswith(suffix):
                continue
            field_name = key[: -len(suffix)]
            if field_name in field_names:
                return field_name, lookup
            return None, None

    if key in field_names:
        return key, None

    return None, None


def search_model(model, range, conditions):
    """
    조건 dict → QuerySet.

    Args:
        range: product_code 목록(챗봇 product_code_in 선필터). 빈 리스트면 미적용.
        conditions: 필드명+lookup 키와 값. 무효 키·변환 실패는 스킵.

    icontains는 OR에 가깝게 필터를 체인으로 누적 적용한다.
    """
    ignores = []
    fields = {
        field.name: field
        for field in model._meta.fields
        if field.name not in ignores
    }
    filters = {}
    icontains_filters = []

    # 챗봇: 찜·이전 검색 결과 code만 대상으로 제한
    if range and "product_code" in {field.name for field in model._meta.fields}:
        filters["product_code__in"] = range

    for key, value in conditions.items():
        if value is None or value == "":
            continue

        field_name, lookup = _split_condition_key(key, fields)
        if not field_name:
            continue

        field = fields[field_name]
        if lookup is None:
            lookup = "icontains" if _is_text_field(field) else "exact"

        if lookup == "icontains" and not _is_text_field(field):
            lookup = "exact"

        converted_value = _convert_filter_value(field, lookup, value)
        if converted_value is None:
            continue

        if lookup == "icontains":
            icontains_filters.extend(
                (field_name, item)
                for item in converted_value
            )
            continue

        filters[f"{field_name}__{lookup}"] = converted_value

    queryset = model.objects.filter(**filters)
    for field_name, value in icontains_filters:
        queryset = queryset.filter(**{f"{field_name}__icontains": value})

    return queryset


# --- 제품군 테이블: cls.search(range, **conditions) → search_model 위임 ---

class ScreenResolution(models.Model):
    """TV 해상도 마스터 — ProductTV.resol_code FK."""
    resol_code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ScreenResolution'

    def __str__(self):
        return model_to_tuple_str(self)


class ProductAC(models.Model):
    """에어컨(ACT). db_table ProductAC."""
    product_code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    img_link = models.URLField(max_length=500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    proficiency_level = models.IntegerField(null=True, blank=True)
    power_consum = models.FloatField(null=True, blank=True)
    cool_cap = models.IntegerField(null=True, blank=True)
    voltage = models.IntegerField(null=True, blank=True)
    hertz = models.IntegerField(null=True, blank=True)
    in_width = models.IntegerField(null=True, blank=True)
    in_height = models.IntegerField(null=True, blank=True)
    in_depth = models.IntegerField(null=True, blank=True)
    out_width = models.IntegerField(null=True, blank=True)
    out_height = models.IntegerField(null=True, blank=True)
    out_depth = models.IntegerField(null=True, blank=True)
    coverage = models.FloatField(null=True, blank=True)
    wind_speed = models.IntegerField(null=True, blank=True)
    dehumid = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    manual_link = models.URLField(max_length=500, null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ProductAC'

    def __str__(self):
        return model_to_tuple_str(self)


class ProductTV(models.Model):
    """TV(TVT). db_table ProductTV."""
    product_code = models.CharField(max_length=50, primary_key=True)

    resol_code = models.ForeignKey(
        ScreenResolution,
        on_delete=models.PROTECT,
        db_column='resol_code',
        null=True
    )

    name = models.CharField(max_length=255, null=True, blank=True)
    img_link = models.URLField(max_length=500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    proficiency_level = models.IntegerField(null=True, blank=True)
    power_consum = models.FloatField(null=True, blank=True)
    screen_size = models.IntegerField(null=True, blank=True)
    display_type = models.CharField(max_length=100, null=True, blank=True)
    ref_rate = models.IntegerField(null=True, blank=True)
    os_type = models.CharField(max_length=100, null=True, blank=True)
    speaker_output = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    manual_link = models.URLField(max_length=500, null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ProductTV'

    def __str__(self):
        return model_to_tuple_str(self)


class ProductFridge(models.Model):
    """냉장고(REF). db_table ProductFridge."""
    product_code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    img_link = models.URLField(max_length=500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    proficiency_level = models.IntegerField(null=True, blank=True)
    power_consum = models.FloatField(null=True, blank=True)
    install_type = models.CharField(max_length=100, null=True, blank=True)
    door_cnt = models.IntegerField(null=True, blank=True)
    total_cap = models.IntegerField(null=True, blank=True)
    refrige_cap = models.IntegerField(null=True, blank=True)
    freeze_cap = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    door_type = models.CharField(max_length=100, null=True, blank=True)
    cool_type = models.CharField(max_length=100, null=True, blank=True)
    smart_diag = models.IntegerField(null=True, blank=True)
    ice_maker = models.IntegerField(null=True, blank=True)
    manual_link = models.URLField(max_length=500, null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ProductFridge'

    def __str__(self):
        return model_to_tuple_str(self)


class ProductVAC(models.Model):
    """청소기(VAC). db_table ProductVAC."""
    product_code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    img_link = models.URLField(max_length=500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    proficiency_level = models.IntegerField(null=True, blank=True)
    power_consum = models.IntegerField(null=True, blank=True)
    unit_width = models.IntegerField(null=True, blank=True)
    unit_height = models.IntegerField(null=True, blank=True)
    unit_depth = models.IntegerField(null=True, blank=True)
    tower_width = models.IntegerField(null=True, blank=True)
    tower_height = models.IntegerField(null=True, blank=True)
    tower_depth = models.IntegerField(null=True, blank=True)
    unit_weight = models.FloatField(null=True, blank=True)
    tower_weight = models.FloatField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    suction_power = models.IntegerField(null=True, blank=True)
    battery_cnt = models.IntegerField(null=True, blank=True)
    manual_link = models.URLField(max_length=500, null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ProductVAC'

    def __str__(self):
        return model_to_tuple_str(self)


class ProductWash(models.Model):
    """세탁기(WMT). db_table ProductWash."""
    product_code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    img_link = models.URLField(max_length=500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    proficiency_level = models.IntegerField(null=True, blank=True)
    power_consum = models.IntegerField(null=True, blank=True)
    washing_cap = models.IntegerField(null=True, blank=True)
    drying_cap = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    door_design = models.CharField(max_length=100, null=True, blank=True)
    control_type = models.CharField(max_length=100, null=True, blank=True)
    door_type = models.CharField(max_length=100, null=True, blank=True)
    water_temp = models.CharField(max_length=100, null=True, blank=True)
    spin_op = models.IntegerField(null=True, blank=True)
    manual_link = models.URLField(max_length=500, null=True, blank=True)

    @classmethod
    def search(cls, range:list=None, **conditions):
        return search_model(cls, range, conditions)

    class Meta:
        db_table = 'ProductWash'

    def __str__(self):
        return model_to_tuple_str(self)
