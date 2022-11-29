import requests
import re
import json
import pandas as pd
from pathlib import Path



bearer_token = "AAAAAAAAAAAAAAAAAAAAAHxzQAEAAAAAp%2FwFwzH8TnqjCihLYO%2Fzu2tmKBQ%3Db5IWOus5vbHL5EMO0oWmaRSF8cb2j1uvazwk6N0V6PYPzBpSyX"

def query_user_tweets(user_id : str, start_time : str):
    
    try: 
        request_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&start_time={start_time}"
        headers = {'Authorization': f'Bearer {bearer_token}' }
        response = requests.get(request_url, headers=headers)
        tweets = response.json().get('data')
    except:
        print(f"USERNAME {user_id}\n\n")
        print(f"REPONSE {response.url}")
        print(f"Couldn't reserve tweets for user {user_id}\nException: {response.json()}")
        raise Exception()
    if(not tweets):
        print(f"DANGEROUS Error on twitter user {user_id}")
        print(response.json())

    next_token = response.json()['meta'].get('next_token')

    while(next_token):
        try:
            response = requests.get(f"{request_url}&pagination_token={next_token}", headers=headers)
            tweets = tweets + response.json()['data']
            next_token = response.json()['meta'].get('next_token')
        except:
            print(f"Error paginating more tweets for user {user_id}.\n Restarting the process will resume correctly. Reponse:")
            print(response.json())
            print(f"Search : https://twitter.com/{user_id} . If \"This account doesn't exist\" add {user_id} to 'accounts_to_skip' and resume")
            raise Exception
    
    return tweets
    

def save_tweets_to_files(tweets: list, username: str):
    Path(f"./tweets/{username}").mkdir(parents=True, exist_ok=True)
    tot_tweets = len(tweets)
    for idx, tweet in enumerate(tweets):
        with open(f"./tweets/{username}/tweet_{str(tweet['id'])}.json", "w+") as tweet_json:
            tweet_json.write(json.dumps(tweet, indent=4))
        if(idx != 0 and (idx / tot_tweets)*10 == 0):
            print(f"Processed {(idx / tot_tweets)*10}% of user {username}'s tweets")
        

def process_mastodon_profile_urls(url: str):
    match = re.match('(.*)(\/[0-9]{1,})', url)
    if(match):
        return True, match[0]
    elif(re.match('medium', url)): 
        return False, None
    return True, url

def main(clean_users: bool, start_time: str, accounts_to_skip: list):
    users = pd.read_csv('./users.csv', delimiter=',', index_col=None)
    
    if(clean_users):
        cleaned_users = []
        for idx, row in users.iterrows():
            is_mastodon, mast_url = process_mastodon_profile_urls(row['mastodon_username'])
            if(is_mastodon):
                cleaned_users.append([row['twitter_username'],row['twitter_id'],mast_url])
        
        cleaned_users = pd.DataFrame(data=cleaned_users, columns=['twitter_username','twitter_id','mastodon_username'])
        users = cleaned_users.drop_duplicates()
        users.to_csv('users.csv', index=False)
    
    tot_users = len(users)
    for idx, row in users.iterrows():
        twitter_id = row['twitter_id']
        twitter_user = row['twitter_username']
        
        
        if(Path(f"./tweets/{twitter_user}").is_dir() or twitter_id in accounts_to_skip):
            continue
        
        tweets = query_user_tweets(twitter_id, start_time)
        print(f"Saving {len(tweets)} tweets for user {twitter_user}")
        save_tweets_to_files(tweets, twitter_user)
        
        if(idx != 0 and (idx / tot_users)*10 == 0):
            print(f"Processed {(idx / tot_users)*10}% of users")
        
if __name__ == "__main__":
    
    start_time = "2022-01-01T00:00:00Z"
    accounts_to_skip = [2883291, 1351039079467642881]
    main(clean_users=False, start_time = start_time, accounts_to_skip = accounts_to_skip)