
import csv
import time
import random
import json
from kafka import KafkaProducer
from datetime import datetime

# parse the date string into a datetime object and remove time zone information as i dont need it
def parse_date(date_str):
    date_parts = date_str.split(' ')
    date_str_no_tz = ' '.join(date_parts[0:4] + date_parts[5:])
    return datetime.strptime(date_str_no_tz, '%a %b %d %H:%M:%S %Y')

# send a tweet to a Kafka topic
def send_tweet(tweet):
    producer.send('tweets-topic', value=tweet)
    producer.flush()
    print("After sending tweet")

#  KafkaProducer with broker information 
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Open and read the CSV file containing tweets
with open(r'C:\Users\I7\Desktop\py_scripts\tweets.csv', 'rt', encoding='utf-8') as f:
    csv_reader = csv.reader(f)
    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Check if the row contains at least 6 attributes (columns)
        if len(row) >= 6:
            # Parse the date attribute into a datetime object
            tweet_date = parse_date(row[2])
            # create document with extracted attributes
            tweet = {
                "id": row[1],
                "date": tweet_date.isoformat(),
                "user": row[4],
                "text": row[5],
                "retweets": int(random.random() * 10)  # Generate a random number of retweets
            }
            send_tweet(tweet)
            #  5 seconds delay to simulate real-time generation
            time.sleep(5)
