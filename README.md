# Twitter and Mastodon Social Toxicity Analysis

Welcome to our repository!  
We'd like to thank Professor [Walter Quattrociocchi](https://walterquattrociocchi.site.uniroma1.it/research) for the inspiration. 

## A brief introduction
This work takes its idea based on the many articles online refering to Mastodon as the new "less-toxic Twitter".  
The core tool used in this work is [Perspective API](https://perspectiveapi.com/) produced by [JigSaw](https://jigsaw.google.com/) and Google to regulate toxicity among the web.  
The study aims at either confirming or negating the theory of Mastodon being less toxic than twitter, by exploring users that are usually very, or non, toxic.  
For the results achieved in the work we leave you to the [report](https://github.com/S4b3/Twitter_Mastodon_Toxicity_Analysis/blob/main/paper/Twitter%20and%20Mastodon%20Social%20Toxicity%20Analysis.pdf)


## Work Flow
In order to work with this project please **create** a **./apikey.txt file** containing your **Google Perspective API KEY** and a **data** folder, containing a **./scraped_data folder** and a **./checkpoint.txt file** to save checkpoints for twitter users processing.  
The flow of execution should be:

1. **./scraping.py** with start = True and checkpoint = False to scrape tweets citing mastodon accounts
2. **./process_twitter_users.py** with clean = True to process users in csv and clean their data
3. **./scrape_mastodon_profiles.py** to scrape mastodon profiles associated with tweets and save posts
4. **./data_extraction.ipynb** where we perform the extraction of the data
5. **./Code_Analysis.ipynb** where we analyze the data to explore relationships and perform the analysis
6. **./explore_users.py** can be used to extract informations about the amount of users and posts you have once data extraction has been run.

Please Note if you run this work that some folders may require to be created by hand as some cells are commented or their creation is not automatized.  
The code contains our Bearer Token for Twitter V2 API calls, but note that this token will be expired for when this code is released. 

## Team
Valentino Sacco - [GitHub](https://github.com/s4b3) - [LinkedIn](https://www.linkedin.com/in/valentino-sacco-61b84113b/)  
Camilla Savarese - [GitHub](https://github.com/Camillasavarese) - [LinkedIn](https://www.linkedin.com/in/camilla-savarese-78aa67220/)  
