# TwitterSentimentAnalysis
Using the twitter api to pull historical tweets from a user and then runing a sentiment analysis over them, with a dashboard powered by Power BI (coming soonish, need to let request count replenish)


## instructions for use

### step 1: dependencies
Please install the following python dependencies while i figure out how to bundle all of this together for super easy use. Use pip3 to install these libraries for python3

* TwitterAPI (https://pypi.org/project/TwitterAPI/)
* pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-from-pypi)
* nltk (download all of the tokenize and sentiment submodules, see https://www.nltk.org/data.html for an easy explanation)
* emoji (https://pypi.org/project/emojis/)
* bs4 (https://pypi.org/project/beautifulsoup4/)
* selenium (https://pypi.org/project/selenium/)
* tweepy (https://pypi.org/project/tweepy/)



### step 2: setting up the template for make_json_datafile
You will need a twitter dev account before using this program because you will need to set up an app and dev environment. After you sign up your twitter account, head to https://developer.twitter.com/en/apps to create an app. Answer all of the questions and create the app, then "Set up dev environment" in the Search Tweets: Full Archive section. It will ask you for a _Dev environment label_ (you will need this later) and the app assigned to the environment. Select the app that you just made, then click the Complete setup button. 


Now you will need to go to the apps page again (https://developer.twitter.com/en/apps) find your app and click the "details" button. Click over to the Keys and tokens tab, here you will find the API key and secret key. You will also need to generate the access token and secret token (You will need to either copy these to a clip board, or just generate these codes when you are ready to copy them into the make_json_datafile template.)


Open the Templates/make_json_datafile_template.py file in an editor and place the following snippets in the following places:

* line 32 -> enter _your_ 'API key' and 'API secret key' in as the arguments
* line 34 -> enter _your_ 'Access token' and 'Access secret token' in as the arguments
* line 76 -> enter _your_ keys and tokens so that the line contains "c_key": "API key", "c_secret": "API Secret key", "a_token": "Access token", "a_secret": "Access secret token"
* line 76 -> enter _your_ dev environment label so that the line contains "dev_environment": "Dev environment label"


### step 3: running the make_json_datafile_template.py
you can rename the file if you want, or move it out of Templates/ if you want. there are a few command line args you need to pass with the file name, they are the account name (string) a from and a to date (date: YYYYMMDDhhmm), the output file name for the tweet data (string), and the version of chrome you have installed on your machine (int) - find your version (https://www.whatismybrowser.com/detect/what-version-of-chrome-do-i-have)
To run the file you will need to do it like so:

python3 make_json_datafile_template.py 'account_name' 'From Date (first)' 'To Date (today)' 'output file name' 'ChromeVersion' 

an example would be like: python3 make_json_datafile_template.py 'Tesla' '201801010000' 'today' 'tesla_tweets' '80'

running this python script will output a file called 'account name'.json - this will be used in the next step.


### step 4: running the twitter_sentiment_scraper.py

once you have the json datafile, for ease of use move it to the same directory you have the twitter_sentiment_scraper.py file, this directory will be the output dir for the python script so make sure it is cleanish. 

to run the file you will need to do it like so:

python3 twitter_sentiment_scraper.py datafile.json

continuing from the example above: python3 twitter_sentiment_scraper.py tesla.json

running this script will output several files and open up a few browsers if it finds tweets to scrape comments from. If you have just the sandbox account, you can pull ~5000 tweets per month from the account you are scraping, and then the web scraper will grab the comments from all of the account's original tweets.


## Notes

### Twitter accounts I have pulled from already
* Tesla (TSLA)
* Scotts Miracle-Gro (SMG)

#### april 22nd, 2020
I realised i was somehow using an old work user account, but all of this code was written on my personal machine and I have changed the username and email accordingly

#### april 23rd/24th, 2020
I added some python Jupyter Notebooks to the repo, i think that will make it easier for people to run this
