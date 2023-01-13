import requests
import pandas as pd
import xml.etree.ElementTree as ET
import json
import html
import multiprocessing
from bs4 import BeautifulSoup
from pathlib import Path


def process_mastodon_profile(mastodon_url, save_path = None):
    
    # 2. split information in "server" /@ "username" / rest...
    _mast_info = mastodon_url.split('/@')
    # 3. save both server and username, we will need them to query the api.
    mastodon_server = _mast_info[0]
    mastodon_username = _mast_info[1].split('/')[0]
    if(mastodon_username == 'dsotm'):
        return False
    # every user on mastodon has an associated rss. This can be requested to scrape a user's ID
    request_url = f"{mastodon_server}/@{mastodon_username}.rss"
    try:
        mastodon_rss_reponse = requests.get(request_url)
        # use an xml parser to extract the tag that contains our id
        id_pre = ET.fromstring(mastodon_rss_reponse.text).find('./channel/image/url')#.text.split('/')[-1]
        id = ''.join(id_pre.text.split('avatars/')[-1].split('/original')[0].split('/'))
    except:
        print(f"Got an error processing current user: {mastodon_url}. \nRequest url: {request_url}.\nIts id was {id}. Going next")
        return False
    if(id == "originalmissing.png"):
        return False
    
    # we can now use this id to query mastodon's timeline public api !
    # example request -> https://mstdn.social/api/v1/accounts/109394907532170837/statuses
    api_request_url = f"{mastodon_server}/api/v1/accounts/{id}/statuses"
    # interrogate the api, response will contain a list of posts parsed in json 
    try:
        api_response = requests.get(api_request_url)
    except:
        print(f"CAUTION Exception raised when querying the api at {api_request_url}.\nUSER INFO:\nmastodon url : {mastodon_url}\nid_pre : {id_pre}\nid : {id}")
        return False
    # load the posts
    if(Path(f"./mastodon_posts/{mastodon_server.split('/')[-1]}_{mastodon_username}").is_dir()):
        already_processed += 1
        return False
    
    Path(f"./mastodon_posts/{mastodon_server.split('/')[-1]}_{mastodon_username}").mkdir(parents=True, exist_ok=True)
    
    
    user_posts = json.loads(api_response.text)
    
    for post_json in user_posts:
        if(post_json['reblog'] or post_json['content'] == ""):
            continue
        _mast_info = post_json['uri'].split('/users/')
        mastodon_server = _mast_info[0].split('/')[-1]
        mastodon_username = _mast_info[1].split('/statuses')[0]
        try:
            content = BeautifulSoup(post_json['content'], "html.parser").find('p').text
        except:
            print(post_json['uri'])
            print(post_json['content'])
            continue
        
        dir_path = save_path or f"./mastodon_posts/{mastodon_server}_{mastodon_username}"
        
        with open(f"{dir_path}/{post_json['id']}.json", 'w+') as json_file:
            json_file.write(json.dumps(
                {
                    'id' : post_json['id'],
                    'created_at': post_json['created_at'],
                    'language': post_json['language'],
                    'uri': post_json['uri'],
                    'content': content,
                    'account': post_json['account']
                } 
            ))
    return True
    
def parse_mastodon_post_to_txt(chunk):
    '''
    for each post we have a structure like this:
    'id'
    'created_at'
    'in_reply_to_id'
    'in_reply_to_account_id'
    'sensitive'
    'spoiler_text'
    'visibility'
    'language'
    'uri'
    'url'
    'replies_count'
    'reblogs_count'
    'favourites_count'
    'edited_at'
    'content'
    'reblog'
    'application'
    'account'
    'media_attachments'
    'mentions'
    'tags'
    'emojis'
    'card'
    'poll'
    from which we only need to extract the "content" part. this will be what we are saving to a file, which is in html form.
    '''
    skipped_users = 0
    processed_now = 0
    
    chunk_id = chunk[0]
    users = chunk[1]
    
    print(f"Init chunk {chunk_id}")
    
    for idx, user in users.iterrows():
        check = process_mastodon_profile(mastodon_url = user['mastodon_username'])
        if(check):
            processed_now +=1
        else : skipped_users += 1

    print(f"Finished Chunk {chunk_id+1} with :\nProcessed: {processed_now}\nDiscarded Users: {discarded_users}\nOriginal Missing PNG as ID : {original_missing}\nAlready Processed: {already_processed}")
    
def scrape(multithreading):
    users = pd.read_csv('./users.csv')
    # first let's process our user's username and id
    # 1. extract known url
    print(f"Going to scrape {len(users)} users")
    
    if(multithreading):
        num_processes = multiprocessing.cpu_count()
        
        chunk_size = int(len(users)/num_processes)
        chunks = [users.iloc[users.index[i:i + chunk_size]] for i in range(0, len(users), chunk_size)]
        
        for idx, chunk in enumerate(chunks):
            print(f"Chunk {idx + 1} has size {len(chunk)}")
            chunks[idx] = [idx, chunk]
        
        print(f"We have {len(chunks)} chunks")
        # create our pool with `num_processes` processes
        pool = multiprocessing.Pool(processes=num_processes)

        # apply our function to each chunk in the list
        pool.map(parse_mastodon_post_to_txt, chunks)
    else:
        parse_mastodon_post_to_txt([0, users])

def query_perspective(api_client):
    
    with open('./mastodon_posts/c.im_3RingCircus/109395051045403099.json', 'r+') as post_file:
        post = json.load(post_file)
    
    
    analyze_request = {
        'comment': { 'text': post['content'] },
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = api_client.comments().analyze(body=analyze_request).execute()
    print(json.dumps(response, indent=2))

  
'''
def main(multithreading=True):
    scrape(multithreading)
    
  
if __name__ == "__main__":
    main()
'''