import json
import logging
import requests
from bs4 import BeautifulSoup

##Begin Config##
logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S%z",
                    level=logging.DEBUG)
##End Config##


def in_stock(soup):
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

    result = requests.get("https://httpstat.us/418")

    c = result.content
    soup = BeautifulSoup(c)
    in_stock(soup)
