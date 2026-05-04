from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import time


# 제품 페이지 펼쳐서 전체 html 저장(txt)
def full_page(URL, kind):
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    wait = WebDriverWait(driver, 15)

    try:
        driver.get(URL)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='Product']")
            )
        )

        time.sleep(3)

        print("페이지 로딩 완료")

        click_count = 0

        while True:
            try:
                more_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(@class,'PlpPcButtonMore_more_btn')]"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    more_button
                )

                time.sleep(1)

                driver.execute_script("arguments[0].click();", more_button)

                click_count += 1
                print(f"{click_count}번째 클릭")

                time.sleep(3)

            except:
                print("끝까지 펼침 완료")
                break

        time.sleep(5)

        html = driver.page_source

        print("HTML 길이:", len(html))

        file_name = f"{kind}_full_page_html.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"HTML 저장 완료: {file_name}")

    finally:
        driver.quit()
        
    return html[:500]


# 개별 제품 링크 txt 저장
def product_links(kind):
    input_file = f"{kind}_full_page_html.txt"
    output_file = f"{kind}_product_links.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    links = set()

    product_cards = soup.find_all("li", attrs={"data-product": "plp-product-card"})

    for card in product_cards:
        a_tag = card.find("a", href=True)

        if a_tag:
            href = a_tag["href"]
            full_url = urljoin("https://www.lge.co.kr", href)
            links.add(full_url)

    with open(output_file, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")

    print(f"제품 카드 개수: {len(product_cards)}")
    print(f"추출된 링크 개수: {len(links)}")
    print(f"저장 완료: {output_file}")
    return list(links)[:5]
