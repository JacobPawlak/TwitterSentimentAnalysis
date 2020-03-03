#Jacob Pawlak
#twitter_sentiment_scraper.py
#go blue team!

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
        return data_list
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
    

    return


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
        cleaned_tweet['in_reply_to_status_id_str'] = "Top Tweet From Brand"
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

#################### MAIN () ####################

def main():

    print()

main()