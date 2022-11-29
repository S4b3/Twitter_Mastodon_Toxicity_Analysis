from bs4 import BeautifulSoup
import requests
import json
import os
import re
import glob, os
import csv
import subprocess
import time

bearer_token = "AAAAAAAAAAAAAAAAAAAAAHxzQAEAAAAAp%2FwFwzH8TnqjCihLYO%2Fzu2tmKBQ%3Db5IWOus5vbHL5EMO0oWmaRSF8cb2j1uvazwk6N0V6PYPzBpSyX"

def scrape_mastodon_tweets(bearer : str):
    # page counter
    page = 1

    # 1. let's start scraping for documents
    print(f"Processing Page # {page}")
    
    _url = "https://api.twitter.com/2/tweets/search/recent?query=(%23MastodonSocial OR %23MastodonMigration) has:links -has:media -is:retweet&expansions=author_id&max_results=100"
    
    # curl https://api.twitter.com/2/tweets/search/recent?query=cat%20has%3Amedia%20-grumpy&tweet.fields=created_at&max_results=100 -H "Authorization: Bearer $BEARER_TOKEN"
    request = requests.get(url=_url, headers={"Authorization" : f"Bearer {bearer}"})
    data = (request.json())['data']
    next_token = (request.json())['meta']['next_token']

    ten_perc = len(data) / 10

    for i, element in enumerate(data) : 
        # print completion percentage
        if(i % ten_perc == 0):
            print(f"Processed {10+(i*10)/ten_perc} % of files")
        id = element['id']
        element = json.dumps(element, indent=4)
        
        with open(f"./data/tweet_{id}.json", "w") as outfile:
            outfile.write(element)


    while(next_token):
        print(f"Fetching page {page}")
        request = requests.get(url=f"{_url}&next_token={next_token}", headers={"Authorization" : f"Bearer {bearer}"})
        data = (request.json())['data']
        
        next_token = (request.json())['meta'].get('next_token')
        ten_perc = len(data) / 10

        for j, element in enumerate(data) : 
            # print completion percentage
            if(j % ten_perc == 0):
                print(f"Processed {10+(j*10)/ten_perc} % of files")
            id = element['id']
            element = json.dumps(element, indent = 4)
            
            with open(f"./data/tweet_{id}.json", "w") as outfile:
                outfile.write(element)
        page += 1
    print(f"No more next tokens, we're finished!")

def extract_username_from_twitter_id(user_id: str, bearer:str):
    # twitter.com/anyuser/status/$id is the general link to find any tweet
    headers = {"Authorization": f"Bearer {bearer}"}
    # find username :
    username_response = requests.get(f"https://api.twitter.com/2/users/{user_id}", headers=headers)
    try:
        return username_response.json()['data']['username'], 200
    except:
        print(f"Couldn't resolve username for user_id {user_id}\nRequest returned code {username_response.status_code}.\nResponse Body: {username_response.json()}\n")
        if(username_response.status_code != 200):
            raise Exception()
        return None, 200

def extract_data_from_tweet_json(path: str):
    with open(path, "r") as file:
        tweet = json.load(file)
        return tweet['author_id'], tweet['id'], tweet['text']
    
def scrape_mastodon_profile(profile_url: str):
    try:
        mastodon_page = requests.get(profile_url, allow_redirects=True)
    except: 
        print(f"Exception returned processing url {profile_url}.")
        return False, None
    if(re.match(".*/@.*", mastodon_page.url)) :
        return True, mastodon_page.url
    return False, None


def main(start, checkpoint):    
    if(start):
        scrape_mastodon_tweets(bearer_token)
    counter_checkpoint = 0
    if(checkpoint):
        with open('checkpoint.txt', 'r') as checkpoint_file:
            counter_checkpoint = int(checkpoint_file.readline())
            print(f"Skipping files up to checkpoint {counter_checkpoint}")
    else:
        with open('./users.csv', "w+") as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['twitter_username', 'twitter_id', 'mastodon_username'])
        
    users = []
    counter = 0
    for path in sorted(glob.glob("./data/*.json")):
            
        if(counter % 50 == 0):
            print(f"Processed {counter} tweets")
            
        if(checkpoint and counter < counter_checkpoint):
            counter+=1
            continue

        user_id, tweet_id, content = extract_data_from_tweet_json(path)
        twitter_username = None
        try:
            twitter_username, code = extract_username_from_twitter_id(user_id, bearer_token)
            if(twitter_username == None and code == 200):
                counter+=1
                continue
        except:
            print(f"Most Likely Reached maximum api requests at {counter}")
            with open('./checkpoint.txt', "w+") as file:
                file.write(str(counter))
            break
        mastodon_url = re.search("(?P<url>https?://[^\s]+)", content).group("url")
        is_mastodon_profile, url = scrape_mastodon_profile(mastodon_url)
        if(is_mastodon_profile):
            mastodon_username = url#.split('@')[1].split('/')[0]
            users.append((twitter_username, user_id, mastodon_username))
            
        counter+= 1
    print(f"Finished processing Tweets! Extracted {len(users)} users.")
    with open('./users.csv', "a") as out:
        csv_out=csv.writer(out)
        csv_out.writerows(users)
     
    if(counter <= 1190):
        time.sleep(60*16)
        main(start = False,checkpoint = True)

if __name__ == "__main__":
    main(start = False, checkpoint = True)
        