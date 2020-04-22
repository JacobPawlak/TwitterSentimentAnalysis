#Jacob Pawlak
#twitter_sentiment_scraper.py
#go blue team!

#################### API REF ####################
'''
https://developer.twitter.com/en/docs/tweets/search/overview/premium
https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search
https://developer.twitter.com/en/docs/tweets/search/guides/premium-operators
https://developer.twitter.com/en/docs/basics/rate-limiting
'''
#################### IMPORTS ####################

#i am going to be using the twitter api to pull down full archive queries
from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterPager
#bringing this in for the sleep() method
import time
#json lib for json.dump()
import json
#going to convert my dicts to dataframes for csv output
import pandas
#bringing in the natural language tool kit - one of our favorites, this is a huge environment requirement
import nltk
#VADER is the sentiment analizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#going to use the tokenize method to chunk up our tweet data
from nltk import tokenize
#since we cant do sentiment over emojis with vader (i dont think?) i need this to remove emojis
import emoji
#regex library for cleaning strings and matching tweets
import re
#using these two libs for the datafile i am going to pass in (simulating some env variables)
import os
import sys
#i need a few libs for webscraping twitter since it is a dynamic site that has some weird modal stuff idk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#importing tweepy so i can grab the tweets scraped from the webscraper
import tweepy
#importing the streamlit library for some fun graphing and dataviz
import streamlit


#################### HELPERS ####################

def open_file(file_path):
    #since i will probably reuse this helper i am going to make sure it can accept multiple file types
    #for pulling in csv into pandas dataframe
    if(file_path.split('.')[-1].lower() == 'csv'):
        dataframe = pandas.read_csv(file_path)
        print('returning a pandas dataframe')
        return dataframe
    #for pulling json files into [{}] structures
    elif(file_path.split('.')[-1].lower() == 'json'):
        data_file = open(file_path, 'r')
        data_list = []
        for line in data_file:
            data_list = eval(line)
        print('returning a list of dictionaries')
        return data_list[0]
    #basically same thing as the json file, just saved as a text file
    elif(file_path.split('.')[-1].lower() == 'txt'):
        data_file = open(file_path, 'r')
        data_list = []
        for line in data_file:
            data_list = eval(line)
        print('returning a list of dictionaries')
        return data_list
    #if the filetype doesnt match on of our cases, just return
    else:
        print("You passed in an unrecognized file type, please use a csv, json, or txt file")
        return None


def connect_api(c_key, c_secret, a_token, a_secret):
    #using an OAuth api connection to twitter with my personal twitter account.
    # i will be passing in these keys and tokens from a datafile passed in via command line
    api = TwitterAPI(c_key, c_secret, a_token, a_secret)
    #return the api object to the main
    return api


def add_senti_analysis(tweet_object):

    #bringing in the cleaned tweet so i can add the vader sentiment scores to them
    senti_tweet = tweet_object
    senti_tweet['senti_score_pos'] = 0
    senti_tweet['senti_score_neu'] = 0
    senti_tweet['senti_score_neg'] = 0
    senti_tweet['senti_score_com'] = 0

    tweet_text = senti_tweet['text']
    #now i want to take out all of the emoji or emoji like things in the text since VADER (again, i dont think) cannot run
    # over emojis
    tweet_text = emoji.demojize(tweet_text)
    #i also dont want hashtags in there so I am going to pull that out too with the regex match
    # this regex looks for the hashtag symbol followed by a word, then replaces it with an empty string
    tweet_text = re.sub(r'#\w*', "", tweet_text)
    #this next one is to pull out usernames, same idea with regex match
    tweet_text = re.sub(r'@\w*', "", tweet_text)
    #now i need to remove all of the urls that get left in the tweet (either a gif link or the extended tweet link)
    tweet_text = re.sub(r'(\w*\.)?\w*\.\w*', "", tweet_text)
    #the line above should get any www.xyz.com formats, the one below should get any http(s)://(www.)blah.com
    tweet_text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', "", tweet_text)
    #now that the tweet text is pretty cleaned, I need to use the nltk tokenizer to split up the text (will result in a list of strings)
    tweet_sents = tokenize.sent_tokenize(tweet_text)
    #sometimes the tweet was composed of only things that got cleaned out, so i need to set a limit/count of sentences
    num_sents = len(tweet_sents)
    #setting up the scores that will be edited when I bring in VADER
    score_pos = 0
    score_neu = 0
    score_neg = 0
    score_com = 0
    #here I will correct the case that num_sents is 0 (all emojis or something, no text)
    if(num_sents < 1):
        #gotta do this to avoid dividing by zero (from experience)
        num_sents = 1
    #time to bring in the big guy. the darth. the master.
    vader = SentimentIntensityAnalyzer()
    #now I will run vader over each sentence. vader is really nice because it picks up on so much more than just POS and token scores, it takes the whole sentence into account
    # and produces a score that incorporates syntax and expression
    for sent in tweet_sents:
        #calling vader over the string will return a dictionary of scores
        scores = vader.polarity_scores(sent)
        score_pos += scores['pos']
        score_neu += scores['neu']
        score_neg += scores['neg']
        score_com += scores['compound']

    #okay it's time to add the scores back into the tweet dictionary.
    senti_tweet['senti_score_pos'] = score_pos/num_sents
    senti_tweet['senti_score_neu'] = score_neu/num_sents
    senti_tweet['senti_score_neg'] = score_neg/num_sents
    senti_tweet['senti_score_com'] = score_com/num_sents

    return senti_tweet


def clean_tweet(tweet_object):

    #staring a new dictionary to add all of the cleaned data to
    cleaned_tweet = {}

    #here i will be pulling out some of the data from the raw tweet object
    cleaned_tweet['id_str'] = tweet_object['id_str']
    #grab the screen name (handle) of the tweet owner
    cleaned_tweet['screen_name'] = tweet_object['user']['screen_name']
    #also grab the user name (different from the handle)
    cleaned_tweet['user_name'] = tweet_object['user']['name']

    #pull out the date and time from the timestamp of when the tweet was created, we are going to split up the date and time
    #here is an example of the "created_at": "Tue Oct 08 18:42:30 +0000 2019"
    created_date = tweet_object['created_at']
    #splitting by whitespace to get a list, and since i know all of the indecies i can build the date and time strings
    created_date = created_date.split()
    #you can follow along with the example above 
    year = created_date[-1]
    #made a small list of month abrev. to index for a quick str month -> int month
    months = ['Jan', 'Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month = created_date[1]
    #0 index start
    month_digit = 1 + months.index(month)
    day = created_date[2]
    time = created_date[3]
    new_date = str(str(year) + '-' + str(month_digit) + '-' + str(day))
    cleaned_tweet['date'] = new_date
    cleaned_tweet['time'] = str(time)

    #for some steps later it will be important to know if it a top level tweet from the brand or from a comment
    if(tweet_object['in_reply_to_status_id_str'] == None):
        cleaned_tweet['in_reply_to_status_id_str'] = "Brand Tweet"
    else:
        cleaned_tweet['in_reply_to_status_id_str'] = tweet_object['in_reply_to_status_id_str']

    #so now that twitter allows 280 chars in a tweet, we have to account for the 'full_text' flag
    if('extended_tweet' in tweet_object.keys()):
        cleaned_tweet['text'] = tweet_object['extended_tweet']['full_text']
    else:
        cleaned_tweet['text'] = tweet_object['text']

    #the tweets also have a retweet and favorite count that i can pull
    cleaned_tweet['retweet_count'] = tweet_object['retweet_count']
    cleaned_tweet['favorite_count'] = tweet_object['favorite_count']

    #I can also build the url (like you would see if you browsed on a desktop)
    cleaned_tweet['url'] = "https://twitter.com/{}/status/{}".format(cleaned_tweet['screen_name'], cleaned_tweet['id_str'])

    return cleaned_tweet


def scrape_comments(datafile_, brand_tweets_list):

    #bringing in the datafile and the brand list
    datafile = datafile_
    brand_tweets = brand_tweets_list

    #going to make another save file too while im here in the preamble
    savefile = open('comments_for_' + str(datafile['output_file_name']) + '.txt', 'w')

    #here is where i am setting up the tweepy connection. I am using tweepy because it is an easy and free connection
    #  to twitter (outside of the official twitterapi library) and it has this cool get_status() method ill use later
    auth = tweepy.OAuthHandler(str(datafile['c_key']), str(datafile['c_secret']))
    auth.set_access_token(str(datafile['a_token']), str(datafile['a_secret']))
    api = tweepy.API(auth)

    #gotta bring in our reliable CHROMEDRIVER baby
    driver = webdriver.Chrome('./Chrome/' + str(datafile['chrome_version']) + '/chromedriver')

    #setting up an empty list to put comment tweet obj in there
    comment_tweets = []

    #quick little counter for the tweets
    tweet_count = 0

    #it's time to start pulling tweets from the twitter website, i can loop over the brand tweets list and point the webscraper at the url
    for brand_tweet in brand_tweets:
        
        tweet_count += 1
        print("Scraping brand tweet #{}: {}".format(tweet_count, brand_tweet['text']))

        #going to call the chrome browser
        driver.get(brand_tweet['url'])
        time.sleep(4)

        '''
        here is where i need to add the part where it hits page down a whole bunch because if i dont do it here or manually it will only pull like 5 comments per tweet
        '''

        #this is the combination of selenium and bs4 that i have been able to get to work for twitter
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        #after experience i know that i can grab all of the links (each tweet in the thread is like a link to the individual page, and i can pull the id out of the link)
        comment_links = soup.find_all('a', attrs={'href': re.compile(r'/*/status/[0-9]+$')})
        comment_tweet_ids = [comment['href'].split('/')[-1] for comment in comment_links]

        for comment_tweet_id in comment_tweet_ids:

            #here is where i start to bring in the tweepy method for getting a status
            try:
                new_comment = add_senti_analysis(clean_tweet(api.get_status(comment_tweet_id)._json))
                if(new_comment['in_reply_to_status_id_str'] == "Brand Tweet"):
                    new_comment['in_reply_to_status_id_str'] = brand_tweet['id_str']
                print(new_comment['text'])
                #add it to the list of comment tweets
                comment_tweets.append(new_comment)
                savefile.write(str(new_comment) + '\n')
                
                #reset our rate_limit_hit error counter
                rate_limit_errs = 0

            #since this is a try clase we need to look for exceptions. the ones i know of are the tweepy rate limit error or a chromedriver error (cant do a whole lot about)
            except tweepy.RateLimitError as err:
                print("Oh no, we seem to have run into the rate limiter from tweepy: {}. Sleeping for 3 minutes to hold".format(err))
                time.sleep(180)
            
            #a more general exception
            except Exception as err:
                print("Oh no, we seem to have run into a strange error: {}. Please check to see if this will impare performance. Sleeping for 10 seconds to hold".format(err))
                time.sleep(10)
                rate_limit_errs += 1
                
                #if there are like more than 5 errors that werent rate limit errors then we need to break
                if(rate_limit_errs > 4):
                    driver.quit()
                    #time to dump our data out to the directory
                    with open('comments_for_' + str(datafile['output_file_name']) + '.json', 'w') as comments_json:
                        json.dump(comment_tweets, comments_json)
                    comment_tweets_df = pandas.DataFrame(comment_tweets)
                    comment_tweets_df.to_csv('comments_for_' + str(datafile['output_file_name']) + '.csv', encoding='utf-8')
                    break

                continue

        #i know that the selenium browser will get slow after opening so many pages (it is chrome after all)
        # so every 25 brand tweets we are going to close the browser and reopen it
        if(tweet_count % 25 == 0):
            driver.quit()
            time.sleep(2)
            driver = webdriver.Chrome('./Chrome/' + str(datafile['chrome_version']) + '/chromedriver')

    #closing the save file to free that mem back up        
    savefile.close()
    
    #after it's done pulling comments per tweet, lets report the successes and return the comments list
    try:
        print("Total number of comments pulled: {} with an average of {} tweets per comment".format(len(comment_tweets), (len(comment_tweets)/len(brand_tweets))))
    except ZeroDivisionError as err:
        print("There seems to be no tweets to scrape comments from! See log above for more details.")
        driver.quit()
        
    return comment_tweets


#################### MAIN () ####################

def main():

    #since i am passing in some arguements through a json file to replicate env vars, i need to check that it was included in the terminal call
    #if it wasnt, i can just let the user know how to run the program and then return out (nothing will be run past this point)
    if(len(sys.argv) != 2):
        print("\nPlease use the program like so:\n>> python3 twitter_sentiment_scraper.py unique_datafile.json\nWhere the unique_datafile.json is a json created by make_json_datafile.py")
        return

    try:
        datafile = open_file(sys.argv[1])
    except Exception as err:
        print("Oh no, there was an error ({}) trying to open the datafile {}, perhaps it was formatted incorrectly? Please try again".format(err, sys.argv[1]))
        return
    
    #these two lists are going to hold all of the tweets as they get cleaned and sorted into Brand tweets or response tweets
    TWEET_LIST = []
    BRAND_LIST = []

    #now i am going to setup the api connection with the helper function i wrote in the HELPERS section
    #since this is not a garunteed connection, i am going to wrap it in a try/except clause
    try:
        api = connect_api(str(datafile['c_key']), str(datafile['c_secret']), str(datafile['a_token']), str(datafile['a_secret']))
    except Exception as err:
        print("Oh no, there was an error ({}) trying to connect to the Twitter API, perhaps the consumer/access keys are incorrect? Please try again.".format(err))
        return

    #I am going to make a file to save the data in incase there is an error and the program crashes, i wont have lost everything (cant get requests back)
    savefile = open(str(datafile['output_file_name']) + '.txt', 'w')

    #so before i make the api request there are a few things to check, one of those being the max_results. if it is less than 10 the request will fail
    if(int(datafile['max_results']) < 10):
        datafile['max_results'] = "10"
    #also going to check if the number is over 100 since I can only pull 100 tweets per request, and it might err out if i try more. tbh i think it sets it to max anyways, but might as well do it myself
    elif(int(datafile['max_results']) > 100):
        datafile['max_results'] = "100"

    #heeeeeere it goes! time to make the api call! I will continue to make calls in a loop underneath this call.
    request = api.request("tweets/search/fullarchive/:{}".format(str(datafile['dev_environment'])), {"query": "from:{} lang:en".format(str(datafile['target_user_id'])), "toDate": str(datafile['toDate']), "fromDate": str(datafile['fromDate']), "maxResults": int(datafile['max_results'])})

    #in the case that the number of tweets queried is greater than 100, we will require a 'next token' to grab the rest (or next 100) tweets from the api
    # we are going to initiate it here
    next_token = ''
    #also going to set up a counter for the rate limiter (doing this after experience where it sat for ~3 hours on rate limit. it would have gone for a few weeks before the limit was refreshed)
    rate_limit_hit = 0
    #now it is time to loop!
    while(True):

        #time to check if the request went through and returned our tweets or returned an error
        #from the docs i know that the request comes back with a status code 
        if(request.status_code is not 200):
            #well if we got here we know there was an error, so lets let someone know about it
            print("Oh no, there was an error recieved from the request ({})...".format(request.status_code))
            #okay so the only errors we need to address are the rate limit error, bad requests (hopefully only once), or internal server errors
            #here is the bad request. all i need to do is let the user know that the request failed (there is no use trying again is the request is bad.)
            if(request.status_code is 400):
                print("Oh no, the error was a 400 - bad request. Please reformat your datafile and try again.")
                return
            #okay so now if we make it here and it is a rate limit error code, i can just let the program run for a couple loops 
            if(request.status_code is 429):
                #now to increment the rate limit count
                rate_limit_hit += 1
                #just so the program doesnt run forever, lets set a sentinal value
                if(rate_limit_hit > 5):
                    print("Oh no, it seems like the request limit has been hit, it's time to stop the program. Please check the https://developer.twitter.com/en/dashboard to make sure.")
                    #so instead of returning out of the program i am going to break so that I can save the tweets already collected
                    break
                #if the sentinal wasnt reached yet then the program can just sit for a few mins
                print("Sleeping for 3 minutes to wait out the rate limit")
                time.sleep(180)
                continue
            #so these 50X error codes that we dont have really any control over so its best to just hang out like with the rate limit 
            if( (request.status_code is 500) or (request.status_code is 503) or (request.status_code is 504) ):
                rate_limit_hit += 1
                if(rate_limit_hit > 5):
                    print("Oh no, there seems to be an internal server error from Twitter, time to break")
                    break
                print("Sleeping for 3 minutes to wait out the rate limit")
                time.sleep(180)
                continue
            else:
                #there must be some error that we dont know how to deal with just yet so its time to break
                break
        #wowzers so the request made it here, which means that we didnt hit the error code list and the request came through
        #lets reset the rate limit count
        else:
            rate_limit_hit = 0

        #time to extract the tweets from the request package.
        for tweet in request:
            if('text' in tweet):
                #so this is kinda fun, we get to call the clean_tweet function inside the add_senti_analysis function
                clean_senti_tweet = add_senti_analysis(clean_tweet(tweet))
                
                #now that the tweet is cleaned and has the senti scores added, it's time to add it to the list
                TWEET_LIST.append(clean_senti_tweet)

                #this is a section where we determine if the tweet was a top level tweet from the brand or a response to someone, etc. 
                if(clean_senti_tweet['in_reply_to_status_id_str'] == "Brand Tweet"):
                    #if the tweet has the @ symbol in the first few chars then it's either a retweet or a response (most likely, it could be the case that it is a response with preamble...)
                    if('@' not in clean_senti_tweet['text'][0:4]):
                        BRAND_LIST.append(clean_senti_tweet)
                
                #just for safekeeping its time to write out to the save file
                savefile.write(str(clean_senti_tweet) + '\n')
                #just so we arent left with a blank screen or just errors
                print(clean_senti_tweet['text'])
        
        #this is the method we are going to use to check for that next token we set earlier
        #this is to extract the _json payload that comes with the request
        request_json = request.json()
        if('next' not in request_json):
            #if we are inside this if statement then there isnt a next token in the request, so in theory we have reached the end of the selection of tweets
            break
        #if we made it past that break statement than we know that the next token is there so lets grab it
        next_token = request_json['next']
        #okay now that we made it here its time to complete the loop and call the Twitter api again. all that is required is to add the next token in the params dictionary like so:
        request = api.request("tweets/search/fullarchive/:{}".format(str(datafile['dev_environment'])), {"query": "from:{} lang:en".format(str(datafile['target_user_id'])), "toDate": str(datafile['toDate']), "fromDate": str(datafile['fromDate']), "maxResults": int(datafile['max_results']), "next": str(next_token)})

    #Time to write out some files now that the tweet pull down is done!
    #it would be easy enough to write out a json file and a csv file for the tweet list and brand_tweets list
    with(open(str(datafile['output_file_name']) + '.json', 'w')) as json_tweets:
        json.dump(TWEET_LIST, json_tweets)
    tweet_list_df = pandas.DataFrame(TWEET_LIST)
    tweet_list_df.to_csv(str(datafile['output_file_name']) + '.csv', encoding='utf-8')

    with(open('brand_' + str(datafile['output_file_name']) + '.json', 'w')) as json_brand:
        json.dump(BRAND_LIST, json_brand)
    brand_list_df = pandas.DataFrame(BRAND_LIST)
    brand_list_df.to_csv('brand_' + str(datafile['output_file_name']) + '.csv', encoding='utf-8')

    #also need to close the save file so it doesnt take up any memory while we are working on the webscraper
    savefile.close()

    #after running this a few times and getting a div by zero error, going to throw a try/catch block here
    try:
        print("Total number of tweets pulled: {}. Of those, {}% were from the brand ({} tweets)".format(len(TWEET_LIST), (100 * len(BRAND_LIST)/len(TWEET_LIST)), len(BRAND_LIST)))
    except ZeroDivisionError as err:
        print("Okay so we have one of two cases: There are no brand tweets to scrape comments from, or we have run out of requests and were unable to find any tweets (see above for an error code 429).")

    #I am going to start the webscraping portion of the program here.
    print("Starting webscraper in", end=" ")
    for i in range(0,3):
        print(3 - i)
        #lmao this might trip someone up, probably not tho and this is just for entertainment
        time.sleep(.9)

    #i wrote a helper function to do all of the webscraping, which you can see above in the HELPERS section, but this will pull all of the comments for the brand tweets
    comment_tweets = scrape_comments(datafile, BRAND_LIST)
    #now i can just dump them out to the local directory the same way as before, in json and in csv
    with open("{}.json".format(str(datafile["output_file_name"])), 'w') as comments_json:
        json.dump(comment_tweets, comments_json)
    comment_tweets_df = pandas.DataFrame(comment_tweets)
    comment_tweets_df.to_csv("{}.csv".format(str(datafile["output_file_name"])), encoding="utf-8")


    '''
    here is where i want to do all of the streamlit stuff. Maybe. I should probably just do it in Power BI...
    '''


main()