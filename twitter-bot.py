import tweepy
import openai
from langdetect import detect
from tweepy import OAuthHandler, API
import time

# twitter credentials
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# openAI GPT-3 credentials
openai_key = ''
openai.api_key = openai_key


# user ID whose tweets you're monitoring
user_ids = ['']
# cooldown period in seconds
cooldown = 60 * 10  # 10 minutes

# store the time of the last tweet
last_tweet_time = 0

# authenticate to Twitter
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

while True:
    for user_id in user_ids:
        try:
            tweets = tweepy.Cursor(api.user_timeline, id=user_id).items(20) # gets the 20 most recent tweets

            for tweet in tweets:
                if time.time() - last_tweet_time < cooldown:
                    continue

                if 'manchester city' in tweet.text.lower():
                    print(f"Received a tweet from {tweet.user.id_str}: {tweet.text}")

                    # check if the tweet is in English
                    if detect(tweet.text) != 'en':
                        # translate to English using GPT-3
                        translation_prompt = f"{tweet.text} English translation:"
                        tweet.text = openai.Completion.create(engine="text-davinci-002", prompt=translation_prompt, max_tokens=60).choices[0].text.strip()

                    # rephrase using GPT-3
                    rephrase_prompt = f"Please rephrase the following English text: {tweet.text}"
                    rephrase = openai.Completion.create(engine="text-davinci-002", prompt=rephrase_prompt, max_tokens=60).choices[0].text.strip()

                    # send new tweet
                    new_tweet = f"{rephrase} (source: {tweet.id_str})"
                    api.update_status(new_tweet)

                    last_tweet_time = time.time()
                    print("Tweeted successfully")

        except tweepy.TweepError as e:
            print(f"Encountered error with user {user_id}")
            print(e.reason)
            print(e.response.text)

    time.sleep(cooldown)