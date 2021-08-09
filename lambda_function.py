import boto3
import json
import logging
import requests
import random
import time
import tweepy
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

HAPPY_EMOJIS = ['😀', '😃', '😄', '😄', '🤩', '🤗', '👉', '🙌']
SAD_EMOJIS = ['😒', '😔', '😢', '😦', '😢', '😭']


def was_instock(site, table):

    data = table.query(
        KeyConditionExpression=Key('site').eq(site)
    )

    stock_status = data['Items'][0]['instock']

    if(stock_status == "true"):
        return True
    else:
        return False


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
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9'
    }
    try:
        result = requests.get(
            site,
            proxies=proxies, headers=headers
        )

        c = result.content

        soup = BeautifulSoup(c, features="html.parser")

    except requests.exceptions.RequestException as e:
        logging.warn(f"Could not reach {site} due to {e}")
        return None

    return soup


def in_stock(soup, button_class, button_text_instock, button_text_outofstock):
    if soup is None:
        return False

    buttons = soup.find_all(
        'button', class_=button_class)
    if(buttons):
        first_button = buttons[0]
        button_string = str(first_button)
        if button_text_outofstock in button_string:
            return False
        elif button_text_instock in button_string:
            return True
        else:
            logging.warn("Not sure if in stock.")
            return False
    else:
        logging.warn("No buttons found")
        return False


def tweet_stock_change(is_product_instock, site, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    if is_product_instock:
        emoji = random.choice(HAPPY_EMOJIS)
        update = f"This product is back in stock! {emoji} {site}"
    else:
        emoji = random.choice(SAD_EMOJIS)
        update = f"This product is now out of stock! {emoji} {site}"
    api.update_status(update)

def stock_changed(is_product_instock, was_product_instock):
    if is_product_instock and not was_product_instock:
        return True
    elif not is_product_instock and was_product_instock:
        return True
    else:
        return False

def main():

    with open('secretConfig.json') as json_file:
        data = json.load(json_file)
        my_proxies = data["proxies"]
        my_user_agents = data["user_agents"]
        my_products = data["products"]
        my_region = data["region"]
        my_table = data["table"]
        my_min_sleep = data["min_sleep"]
        my_max_sleep = data["max_sleep"]
        my_consumer_key = data["twitter"]["CONSUMER_KEY"]
        my_consumer_secret = data["twitter"]["CONSUMER_SECRET"]
        my_access_token = data["twitter"]["ACCESS_TOKEN"]
        my_access_toke_secret = data["twitter"]["ACCESS_TOKEN_SECRET"]

        dynamodb = boto3.resource('dynamodb', region_name=my_region)

        table = dynamodb.Table(my_table)

        for product in my_products:
            url = data['products'][product]["url"]
            button_class = data['products'][product]["button_class"]
            button_text_instock = data['products'][product]["button_text_instock"]
            button_text_outofstock = data['products'][product]["button_text_outofstock"]
            soup = get_data(url, my_proxies, my_user_agents)
            is_product_instock = in_stock(soup, button_class, button_text_instock, button_text_outofstock)
            #print(f"{product} status is {is_product_instock}")
            #"""
            logging.debug(f"{product} status is {is_product_instock}")
            was_product_instock = was_instock(url, table)
            logging.debug(f"{product} status was {was_product_instock}")
            if(stock_changed(is_product_instock, was_product_instock)):
                logging.info(
                    f"Changing status of {product} to {is_product_instock}")
                update_stock_status(url, is_product_instock, table)
                tweet_stock_change(is_product_instock, url, my_consumer_key,
                                   my_consumer_secret, my_access_token, my_access_toke_secret)
            #"""
            time.sleep(random.randint(my_min_sleep, my_max_sleep))


def lambda_handler(event, context):
    main()

#main()