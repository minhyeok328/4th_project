from django.db import models
from products import models as p_models

def safe_get(mod:models.Model, dct):
    try:
        return mod.objects.get(**dct)
    except mod.DoesNotExist:
        return None

def get_model(product_code:str):
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

def search_product(product_type, range, conditions):
    model = get_model(product_type)
    return model.search(range, **conditions)
