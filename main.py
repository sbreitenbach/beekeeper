import json
import logging
import requests
import random
import time
from bs4 import BeautifulSoup
from requests import RequestException

##Begin Config##
logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S%z",
                    level=logging.INFO)
##End Config##


def get_data(site, proxies, user_agents):
    user_agent = random.choice(user_agents)
    headers = {
        'authority': 'kobeesco.com',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://kobeesco.com/',
        'accept-language': 'en-US,en;q=0.9'
    }
    try:
        result = requests.get(
            site,
            proxies=proxies
        )

        c = result.content

        soup = BeautifulSoup(c)
    except requests.exceptions.RequestException as e:
        logging.warn(f"Could not reach {site}")
        return None

    return soup


def in_stock(soup):
    if soup is None:
        return False

    buttons = soup.find_all(
        'button', class_='btn product-form__cart-submit btn--secondary-accent')
    if(buttons):
        first_button = buttons[0]
        button_string = str(first_button)
        if "Sold out" in button_string:
            print("out of stock")
            return False
        elif "Add to cart" in button_string:
            print("in stock")
            return True
        else:
            print("Not sure if in stock.")
            logging.warn("Not sure if in stock.")
            return False
    else:
        print("No buttons found")


if __name__ == '__main__':

    with open('secretConfig.json') as json_file:
        data = json.load(json_file)
        my_proxies = data["proxies"]
        my_user_agents = data["user_agents"]
        my_sites = data["sites"]

        for site in my_sites:
            soup = get_data(site, my_proxies, my_user_agents)
            in_stock(soup)
            time.sleep(random.randint(5, 37))
