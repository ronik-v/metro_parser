from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from json import dump
from bs4 import BeautifulSoup

import logging

# main "constants" site\user agent\file for received data from the site
METRO_URL: str = "https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca/syry"
USER_AGENT: str = UserAgent(browsers=['chrome', 'edge', 'internet explorer', 'firefox', 'safari', 'opera']).random
DATA_FILE: str = "metro.json"


# function to add data in json
# json format -> {"article": id, "title": title, "url": href,
# "price": old_price, "discout_price": new_price, "brand": brand}
def add_to_json(product_pool: list[dict[str, str]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        dump(product_pool, file, indent=4, ensure_ascii=False)


def metro_parser() -> None:
    op = Options()
    op.page_load_strategy = 'eager'
    op.add_argument(USER_AGENT)

    # pool for data
    product_pool: list[dict[str, str]] = []
    # product index in pool
    product_add_index = 0
    try:
        # driver with metro site url
        driver = webdriver.Chrome(options=op)
        driver.get(url=METRO_URL)

        # html document...
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # cycle with data collection from each page for the previously specified group of products
        for page_index in range(int(soup.find_all("a", "v-pagination__item catalog-paginate__item")[-1].text)):
            current_url = f"https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca/syry?page={page_index+1}"

            driver.get(url=current_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = soup.find_all("div", class_="product-card")

            # product card with details about it
            for card in cards:
                # details about the product are then added to json
                # according to the specified format in the comment before the "add_to_json" function
                product_add_index += 1
                id = card.get("data-sku")
                title = card.find("a").get("title")
                href = "https://online.metro-cc.ru" + card.find("a").get("href")
                prices = card.find_all("span", class_="product-price__sum-rubles")
                if len(prices) == 0:
                    continue
                elif len(prices) > 1:
                    old_price, new_price = prices[1].text, prices[0].text
                else:
                    old_price = prices[0].text
                    new_price = None

                driver.get(url=href)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                brand = soup.find("a", class_="product-attributes__list-item-link").text.strip()

                # adding data to the pull and logging the result of adding with time and percentage of completion
                product_pool.append({"article": int(id), "title": title, "url": href, "price": int(old_price), "discout_price": int(new_price), "brand": brand})
                logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
                logging.info(f'parsed data = {round(product_add_index / 680, 2) * 100}%\n{product_pool[-1]}')

    except Exception as exception:
        # exception logging
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.error(exception)
    finally:
        # writing to the file and closing the driver
        driver.close(); driver.quit(); add_to_json(product_pool)


if __name__ == '__main__':
    metro_parser()
