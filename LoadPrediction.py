from tweepy import Stream
import time
import sys
import tweepy, json
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

import os
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
#import matplotlib.pyplot as plt

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory


#print(os.listdir("./input"))
#df = pd.read_csv("./input/train_AV3.csv") #Reading the dataset in a dataframe using Pandas
#print(df.head(10))
from urllib.request import urlretrieve, urlopen, Request
import requests
url = 'http://samplecsvs.s3.amazonaws.com/Sacramentorealestatetransactions.csv'
#urlretrieve(url, 'Sacramentorealestatetransactions.csv')

url = "https://www.wikipedia.org/"
request = Request(url)
response = urlopen(request)
html = response.read()
response.close()
#print(html)
r = requests.get(url)
text = r.text
#print(text)



#url = 'https://api.github.com/users/mralexgray/repos'
url = 'http://headers.jsontest.com/'
#url = 'http://www.omdbapi.com/?t=inception&y=&plot=short&r=json'
r = requests.get(url)

json_data = r.json()
#print(json_data)
#print(type(json_data))
for key, value in json_data.items():
	print(key + ':', value)

def process_or_store(tweet):
    print(json.dumps(tweet))

class MyListener(StreamListener):
    start_time = 0
    def __init__(self, time_limit=60):
        self.start_time = time.time()
        self.limit = time_limit
        self.saveFile = open('python.json', 'w')
        super(MyListener, self).__init__()
 
    def on_data(self, data):
        print(time.time() - self.start_time)
        if (time.time() - self.start_time) < self.limit:
            data = data.replace('\n','')
            self.saveFile.write(data)
            #self.saveFile.write('\n')
            return True
        else:
            self.saveFile.close()
            return False
 
    def on_error(self, status):
        print(status)
        return True


access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#for status in tweepy.Cursor(api.home_timeline).items(10):
    # Process a single status
    #print(status.text) 
#for tweet in tweepy.Cursor(api.user_timeline).items():
#    process_or_store(tweet._json)    

twitter_stream = Stream(auth, MyListener(time_limit=10))
twitter_stream.filter(track=['IPL'])

if os.path.getsize('python.json') == 0:
    quit()#sys.exit()

with open('python.json', 'r') as f:
    line = f.readline() # read only the first tweet/line
    #print("-->" + line + "<--")
    while True:
        tweet = json.loads(line) # load it as Python dict
        #print("--------" + tweet['extended_tweet']['full_text'])
        #print(tweet.keys())
        #break
        #if 'extended_tweet' in tweet:
        #    print('extended tweet FOUND')
        try :
             print(tweet['retweeted_status']['extended_tweet']['full_text'])
        except KeyError:
            print(tweet['text'])
        print("-------------------------------------")
        #break
        #else:
        #    print('extended tweet not found')
        #    print("--------" + tweet['text'])

        #with open('python.json.write.txt', 'a') as fw:
        #    fw.write(json.dumps(tweet, indent=4)) # pretty-print
        line = f.readline()
        if line == '':
            break
    

