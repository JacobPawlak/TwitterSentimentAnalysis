#Jacob Pawlak
#make_json_datafile.py
#go blue team!

########################## IMPORTS ##########################
#bringing in the tweepy library since we dont need to pull in the entire TwitterAPI lib, just want to access some of the get_user etc methods
import tweepy
#need json to write out the json files
import json
#using sys to pull in the command line arg 'flags'
import sys
#making it easy for me to prop up dates
import datetime

########################## MAIN () ##########################

'''
Hello! You are going to need to fill in a few places with your access tokens and keys, please check line 32, 34, and 76. You will also need to fill in your development environment on line 76
You can find your keys in the twitter dev portal under https://developer.twitter.com/en/apps/<Your app number> "Keys and Tokens" tab.
'''

def main():

    #if we do not see the correct number of command line args, gotta break
    if(len(sys.argv) != 6):
        #need to get the target account name, the start and end dates, and the desired output file name
        print("Please use the program as follows:\n~$ python3 make_json_datafile.py <account_name> <From Date (first)> <To Date (today)> <output file name> <ChromeVersion>\n\twhere date formats should be YYYYMMDDhhmm or 'first', 'today'")
        return

    #set up your auth stuff here. You will need to grab the 4 codes from your twitter dev App page under "Keys and Tokens"
    #keys go here, (api key, secret key)
    auth = tweepy.OAuthHandler('','')
    #tokens go here (access token, access secret token)
    auth.set_access_token('', '')
    #once we set the API keys and Acess tokens, we need to push the auth to the Tweepy auth handler, and hopefully we get a api connect returned to us
    api = tweepy.API(auth)

    #now we need to grab the target user name from the command line
    target_user = sys.argv[1]
    #grabbing the from and to dates as well
    from_date = sys.argv[2]
    to_date = sys.argv[3]
    #and the output file name down here - 
    # **** this is not name of the json file that is created by this file, the output_file_name is passed as a param for the datafile 
    output_file_name = sys.argv[4]
    #need the chrome version too
    chrome_version = sys.argv[5]

    #calling the tweepy API get_user method (and then the _json object attached to the return json). from here we can find the id_str for the twitter account
    target_user_id = api.get_user(target_user)._json['id_str']

    #a tiny check of the start date against the string 'first'. if it is, we give it the first day of twitter
    if(from_date.lower() == "first"):
        from_date = "200603210000"

    #now if we want to get the most up-to-date tweets, we can pass the commandline flag 'today' 
    if(to_date.lower() == "today"):
        #passing 'today' will let us call the datetime methods and set the to_date param to the current time
        #below is just some cheeky datetime manip, its cool and works so we leave it at that. the dates have to be in a certain format so we make it work
        now = datetime.datetime.now()
        month = str(now.month)
        day = str(now.day)
        hour = str(now.hour)
        minute = str(now.minute)
        if(len(month) == 1):
            month = '0' + month
        if(len(day) == 1):
            day = '0' + day
        if(len(hour) == 1):
            hour = '0' + hour
        if(len(minute) == 1):
            minute = '0' + minute
        to_date = str(now.year) + month + day + hour + minute

    #here is the json file that is being written out to the given filename. it includes all of the datapoints we need to give the 
    datafile = [{"target_user_id": str(target_user_id), "target_user_screen_name": str(target_user), "c_key": "", "c_secret": "", "a_token": "", "a_secret": "", "output_file_name": str(output_file_name), "dev_environment": "", "max_results": "100", "toDate": str(to_date), "fromDate": str(from_date), "chrome_version": str(chrome_version)}]

    #lets name the datafile the name of the brand or account we are looking for. that makes sense to me when you are searching through these, since the account's id is included.
    file_name = "{}.json".format(target_user.lower())

    with open(file_name, 'w') as o_f:
        json.dump(datafile, o_f)

main()