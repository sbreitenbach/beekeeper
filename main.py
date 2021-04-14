import json
import logging

##Begin Config##
logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S%z",
                    level=logging.DEBUG)
##End Config##

def returns_true():
    return True

if __name__ == '__main__':
    with open('publicConfig.json') as json_file:
        data = json.load(json_file)
        my_setting_agent = data["settings"]["1"]


    print("Hello World!")
    print(returns_true())
    print(my_setting_agent)
    logging.info("Hello World!")