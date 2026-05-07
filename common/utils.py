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
    return product_type, test_product(product_type)

def test_product(product_type:str):
    match product_type:
        case p_models.ProductAC._meta.db_table:
            return p_models.ProductAC(
                product_code="ACT000",
                name="Test Air Conditioner",
                img_link="https://www.lge.co.kr/kr/images/air-conditioners/md10302855/gallery/medium-interior01.jpg",
                price=1500000,
                proficiency_level=1,
                power_consum=1800,
                cool_cap=6500,
                voltage=220,
                hertz=60,
                in_width=998,
                in_height=345,
                in_depth=210,
                out_width=870,
                out_height=650,
                out_depth=330,
                coverage=62,
                wind_speed=5,
                dehumid=2,
                color="White",
                manual_link="https://gscs-b2c.lge.com/open/downloadFile?fileId=CSr78KtELvOMwqG5DMlLw",
            )
        case p_models.ProductFridge._meta.db_table:
            return p_models.ProductFridge(
                product_code="REF000",
                name="Test Refrigerator",
                img_link="https://www.lge.co.kr/kr/images/wash-tower/md10694827/gallery/medium01.jpg",
                price=2300000,
                proficiency_level=1,
                power_consum=37.5,
                install_type="Freestanding",
                door_cnt=4,
                total_cap=870,
                refrige_cap=520,
                freeze_cap=350,
                width=914,
                height=1787,
                depth=918,
                weight=140,
                color="Silver",
                door_type="French Door",
                cool_type="Indirect Cooling",
                smart_diag=1,
                ice_maker=1,
                manual_link="https://gscs-b2c.lge.com/open/downloadFile?fileId=aYgXp4bXIhCWq82n4TlDPw",
            )
        case p_models.ProductTV._meta.db_table:
            resolution = p_models.ScreenResolution(
                resol_code="RESOL_TEST_001",
                name="4K UHD",
                width=3840,
                height=2160,
            )

            return p_models.ProductTV(
                product_code="TVT000",
                resol_code=resolution,
                name="Test TV",
                img_link="https://www.lge.co.kr/kr/images/tvs/md10794841/gallery/medium-interior01.jpg",
                price=1200000,
                proficiency_level=1,
                screen_size=65,
                display_type="OLED",
                ref_rate=120,
                os_type="webOS",
                speaker_output=40,
                width=1449,
                height=830,
                depth=46,
                weight=24.0,
                manual_link="https://gscs-b2c.lge.com/open/downloadFile?fileId=7g7LHiPnQ0ArCiR4LHqw",
            )
        case p_models.ProductVAC._meta.db_table:
            return p_models.ProductVAC(
                product_code="VAC000",
                name="Test Vacuum Cleaner",
                img_link="https://www.lge.co.kr/kr/images/vacuum-cleaners/md10572836/gallery/medium-interior01.jpg",
                price=900000,
                proficiency_level=2,
                power_consum=590,
                unit_width=260,
                unit_height=1120,
                unit_depth=270,
                tower_width=300,
                tower_height=1000,
                tower_depth=300,
                unit_weight=2.7,
                tower_weight=10.5,
                color="Black",
                suction_power=250,
                battery_cnt=2,
                manual_link="https://gscs-b2c.lge.com/open/downloadFile?fileId=R7gAjp2pyJlWCe61RZANwA",
            )
        case p_models.ProductWash._meta.db_table:
            return p_models.ProductWash(
                product_code="WMT000",
                name="Test Washing Machine",
                img_link="https://www.lge.co.kr/kr/images/washing-machines/md09853827/gallery/medium-interior01.jpg",
                price=1800000,
                proficiency_level=1,
                power_consum=2100,
                washing_cap=25,
                drying_cap=15,
                width=700,
                height=990,
                depth=830,
                weight=95,
                color="White",
                door_design = "Open Window",
                door_type="Front Load",
                water_temp="Cold/Warm/Hot",
                spin_op=5,
                manual_link="https://gscs-b2c.lge.com/open/downloadFile?fileId=IEswLl1yVo2eq6NubIuoog",
            )
        case _:
            return None
