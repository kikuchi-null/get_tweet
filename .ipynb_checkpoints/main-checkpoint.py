# main
import datetime
import time
from get_tweet import GetTweet
import json

with open("./settings.json", mode="r", encoding="utf-8") as f:
    tokens = json.load(f)
    
get_tweet = GetTweet(**tokens)

timelines = []
max_id = None
query = input("Query> ")

while True:
    start_date = input("Start data(Year/Month/Date)> ")

    if start_date == "q":
        break

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y/%m/%d")
        break
    except:
        raise ValueError

for i in range(7):
    date = (start_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d")

    since = f"{str(date)}_00:00:00_JST"
    until = f"{str(date)}_23:59:59_JST"

    while True:
        get_tweet.api_remain_and_sleep()

        timelines, max_id = get_tweet.search_timeline(query, since, until, max_id)
        get_tweet.write_tweet_to_file(timelines, date)

        time.sleep(5)

        if timelines == []:
            break

            print(max_id, len(timelines))

            if len(timelines) < SEARCH_LIMIT_COUNT:
                break