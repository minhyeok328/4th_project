from django.db import models
from django.core.exceptions import ValidationError


LOOKUPS = ("gte", "lte", "in", "icontains", "exact")
TEXT_FIELDS = (
    models.CharField,
    models.TextField,
    models.URLField,
    models.EmailField,
    models.SlugField,
)


def model_to_tuple_str(instance):
    values = [str(getattr(instance, field.attname)) for field in instance._meta.fields]
    return f"({', '.join(values)})"


def _get_compare_field(field):
    if isinstance(field, models.ForeignKey):
        return field.target_field
    return field


def _is_text_field(field):
    return isinstance(_get_compare_field(field), TEXT_FIELDS)


def _convert_value(field, value):
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
    if lookup == "in":
        if isinstance(value, str):
            values = [item.strip() for item in value.split(",")]
        else:
            values = value

        if not isinstance(values, (list, tuple, set)):
            values = [values]

        converted_values = [
            converted
            for item in values
            if (converted := _convert_value(field, item)) is not None
        ]
        return converted_values or None

    return _convert_value(field, value)


def _split_condition_key(key, field_names):
    for lookup in LOOKUPS:
        suffix = f"_{lookup}"
        if key.endswith(suffix):
            field_name = key[:-len(suffix)]
            if field_name in field_names:
                return field_name, lookup
            return None, None

    if key in field_names:
        return key, None

    return None, None


def search_model(model, range, conditions):
    ignores = ["product_code"]
    fields = {
        field.name: field
        for field in model._meta.fields
        if field.name not in ignores
    }
    filters = {}

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

        filters[f"{field_name}__{lookup}"] = converted_value

    return model.objects.filter(**filters)


class ScreenResolution(models.Model):
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
