import requests
import re
import json
import pandas as pd
from pathlib import Path
import multiprocessing
import os


bearer_token = "AAAAAAAAAAAAAAAAAAAAAC7IlAEAAAAAfoaln2kKYoXI8xiBWLl203J6zoM%3DuRNUzaVpXBPJYFcQTliOP0GpjyroT40TNdhG56jKfDTVatOB8O"

def query_user_tweets(user_id : str, start_time : str):
    
    try: 
        request_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&start_time={start_time}"
        headers = {'Authorization': f'Bearer {bearer_token}' }
        response = requests.get(request_url, headers=headers)
        tweets = response.json().get('data')
    except:
        print(f"Couldn't reserve tweets for user {user_id}\nException: {response.json()}")
        raise Exception()
    if(not tweets):
        print(f"DANGEROUS Error on twitter user {user_id}")
        print(response.json())
        if(response.status_code == 429):
            raise Exception
        print(f"Add its username to accounts_to_skip")
        return None

    next_token = None # response.json()['meta'].get('next_token')
    page = 2
    while(next_token and page <= 5):
        try:
            response = requests.get(f"{request_url}&pagination_token={next_token}", headers=headers)
            tweets = tweets + response.json()['data']
            next_token = response.json()['meta'].get('next_token')
            page += 1
        except:
            print(f"Error paginating more tweets for user {user_id}.\n Restarting the process will resume correctly. Reponse:")
            print(response.json())
            print(f"Search : https://twitter.com/{user_id} . If \"This account doesn't exist\" add {user_id} to 'accounts_to_skip'")
            break
        
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

def process_users_dataframe(users):
    
    start_time = "2022-01-01T00:00:00Z"
    # accounts we're not processing! Note: some of this accounts may either have been deleted after the scraping process, or they just became private. 
    accounts_to_skip = [1400093333196791808, 1453041424136556555, 1005726141200715776,
                        1390410321131712518, 1232369725075861504, 1332382494914736128,
                        375282975, 1133103253573570561, 104120337, 1377330245850775556,
                        15699553, 92204371, 756556016649723904, 115313586, 2997889577,
                        1022908216815112192, 1325901630, 1118978367531962368, 22775616,
                        14744403, 65581806, 773799617003683840, 19652597, 1209084588393406464,
                        2270823308, 346285266, 28180275, 3796609599, 23823664, 747693332,
                        4817945427, 1417546088341544964, 1228370295746154496, 325868692,
                        1271494254490275846, 9817342, 4855009595, 20941392, 1523882642718011396,
                        2962960156, 2883291, 1351039079467642881, 1341848074860290050,
                        1333519596092076039, 913913679883718656, 1547838011261403136, 18463834,
                        1062773630264782849]
    
    for _, row in users.iterrows():
        twitter_id = row['twitter_id']
        twitter_user = row['twitter_username']
        
        
        if(Path(f"./tweets/{twitter_user}").is_dir() or twitter_id in accounts_to_skip):
            continue
        
        tweets = query_user_tweets(twitter_id, start_time)
        if(tweets == None):
            continue
        print(f"Saving {len(tweets)} tweets for user {twitter_user}")
        save_tweets_to_files(tweets, twitter_user)
            
   
'''           
def main(clean_users: bool):#, start_time: str, accounts_to_skip: list):
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
    
    # count amount of directories in tweets
    
    tot_users = len(users)
    #users_processed = len(next(os.walk('./tweets'))[1])
    #users_remaining = tot_users - users_processed
    #print(f"{users_remaining} users left to process")
    
    # now split dataframe in chunks to multiprocess
    num_processes = multiprocessing.cpu_count()
    chunk_size = int(tot_users/num_processes)
    chunks = [users.iloc[users.index[i:i + chunk_size]] for i in range(0, tot_users, chunk_size)]
    
    print(f"We have {len(chunks)} chunks")
    # create our pool with `num_processes` processes
    pool = multiprocessing.Pool(processes=num_processes)

    # apply our function to each chunk in the list
    pool.map(process_users_dataframe, chunks)

    
        
if __name__ == "__main__":
    
    # start_time = "2022-01-01T00:00:00Z"
    # accounts_to_skip = [2883291, 1351039079467642881, 1341848074860290050, 1333519596092076039, 913913679883718656, 1547838011261403136]
    main(clean_users=False)#, start_time = start_time, accounts_to_skip = accounts_to_skip)  
'''