import json
import tweepy
import time
import random



def delete_tweets(tweet_ids,api):
    # delete tweets
    for tweet_id in tweet_ids:
        print(f"Deleting tweet with ID: {tweet_id}")
        # Send the request to Twitter
        api.destroy_status(tweet_id)
        # Wait for a random number of seconds
        time.sleep(random.randint(1, 5))

if __name__ == "__main__":

        with open('secretConfig.json') as json_file:
                data = json.load(json_file)
                my_consumer_key = data["twitter"]["CONSUMER_KEY"]
                my_consumer_secret = data["twitter"]["CONSUMER_SECRET"]
                my_access_token = data["twitter"]["ACCESS_TOKEN"]
                my_access_toke_secret = data["twitter"]["ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(my_consumer_key, my_consumer_secret)
        auth.set_access_token(my_access_token, my_access_toke_secret)
        api = tweepy.API(auth)

        tweets = api.user_timeline(screen_name="beekeep86576354"
        , 
                                # 200 is the maximum allowed count
                                count=200,
                                include_rts = False,
                                # Necessary to keep full_text 
                                # otherwise only the first 140 words are extracted
                                tweet_mode = 'extended'
                                )

        tweets_to_delete = []
        for info in tweets:
                if info.id <= 1391326707618037763:
                        tweets_to_delete.append(info.id)
        
        delete_tweets(tweets_to_delete,api)