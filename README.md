# Twitter_Mastodon_Toxicity_Analysis

In order to work with this project please **create** a **./data folder**, **./apikey.txt file** containing your **Google Perspective API KEY** and **./checkpoint.txt file** to save checkpoints for twitter users processing.  
The flow of execution should be:

1. ./scraping.py with start = True and checkpoint = False to scrape tweets citing mastodon accounts
2. ./process_twitter_users.py with clean = True to process users in csv and clean their data
3. ./scrape_mastodon_profiles.py to scrape mastodon profiles associated with tweets and save posts
4. ./main.ipynb where we perform the actual analysis