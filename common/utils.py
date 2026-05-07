from products import models as p_models

def get_product_type(product_code:str):
    header = product_code[0:3].upper()
    match header:
        case "ACT":
            return p_models.ProductAC._meta.db_table
        case "REF":
            return p_models.ProductFridge._meta.db_table
        case "TVT":
            return p_models.ProductTV._meta.db_table
        case "VAC":
            return p_models.ProductVAC._meta.db_table
        case "WMT":
            return p_models.ProductWash._meta.db_table
        case _:
            return None

def get_product(product_code:str):
    product_type = get_product_type(product_code)

    p_code = product_code[0:3].upper() + product_code[3:]

    match product_type:
        case p_models.ProductAC._meta.db_table:
            return product_type, p_models.ProductAC.objects.get(product_code=p_code)
        case p_models.ProductFridge._meta.db_table:
            return product_type, p_models.ProductFridge.objects.get(product_code=p_code)
        case p_models.ProductTV._meta.db_table:
            return product_type, p_models.ProductTV.objects.get(product_code=p_code)
        case p_models.ProductVAC._meta.db_table:
            return product_type, p_models.ProductVAC.objects.get(product_code=p_code)
        case p_models.ProductWash._meta.db_table:
            return product_type, p_models.ProductWash.objects.get(product_code=p_code)
        case _:
            return None, None
