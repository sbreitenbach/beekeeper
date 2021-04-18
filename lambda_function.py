import boto3
import json
import logging
import requests
import random
import time
from boto3.dynamodb.conditions import Key
from bs4 import BeautifulSoup
from requests import RequestException

##Begin Config##
logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S%z",
                    level=logging.INFO)
##End Config##


def was_instock(site, table):

    data = table.query(
        KeyConditionExpression=Key('site').eq(site)
    )

    stock_status = data['Items'][0]['instock']

    return stock_status


def update_stock_status(site, stock_status, table):

    if(stock_status):
        table.update_item(Key={'site': site},
                          UpdateExpression="SET instock = :true",
                          ExpressionAttributeValues={':true': 'true'})
    else:
        table.update_item(Key={'site': site},
                          UpdateExpression="SET instock = :false",
                          ExpressionAttributeValues={':false': 'false'})


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
            proxies=proxies, headers=headers
        )

        c = result.content

        soup = BeautifulSoup(c)
    except requests.exceptions.RequestException as e:
        logging.warn(f"Could not reach {site} due to {e}")
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
            return False
        elif "Add to cart" in button_string:
            return True
        else:
            logging.warn("Not sure if in stock.")
            return False
    else:
        logging.warn("No buttons found")


def main():

    with open('secretConfig.json') as json_file:
        data = json.load(json_file)
        my_proxies = data["proxies"]
        my_user_agents = data["user_agents"]
        my_sites = data["sites"]
        my_region = data["region"]
        my_table = data["table"]
        my_min_sleep = data["min_sleep"]
        my_max_sleep = data["max_sleep"]

        dynamodb = boto3.resource('dynamodb', region_name=my_region)

        table = dynamodb.Table(my_table)

        for site in my_sites:
            soup = get_data(site, my_proxies, my_user_agents)
            is_product_instock = in_stock(soup)
            logging.debug(f"{site} status is {is_product_instock}")
            was_product_instock = was_instock(site, table)
            logging.debug(f"{site} status was {was_product_instock}")
            if((is_product_instock and not was_product_instock) or (not is_product_instock and was_product_instock)):
                logging.info(
                    f"Changing status of {site} to {is_product_instock}")
                update_stock_status(site, is_product_instock, table)
            time.sleep(random.randint(my_min_sleep, my_max_sleep))


def lambda_handler(event, context):
    main()