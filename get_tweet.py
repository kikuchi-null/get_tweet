import json
import datetime
import time
import math
from requests_oauthlib import OAuth1Session
from pytz import timezone
from dateutil import parser

# src
# URL
SEARCH_TWEETS_URL = 'https://api.twitter.com/1.1/search/tweets.json'
RATE_LIMIT_STATUS_URL = "https://api.twitter.com/1.1/application/rate_limit_status.json"
SEARCH_LIMIT_COUNT = 100

class GetTweet:

    def __init__(self, CK, CS, AT, ATS):
        self._CK, self._CS, self._AT, self._ATS = CK, CS, AT, ATS

    def get_session(self):
        oauth = OAuth1Session(self._CK, self._CS, self._AT, self._ATS)
        return oauth

    def search_timeline(self, query, since=None, until=None, max_id=None):
        self.query = query
        timelines = []
        id = ""
        session = self.get_session()

        # Set Paramerters
        params = {"q": query, 'count': SEARCH_LIMIT_COUNT, 'result_type': "mixed"}

        if max_id is not None:
            params["max_id"] = max_id
        if since is not None:
            params["since"] = since
        if until is not None:
            params["until"] = until

        for k, v in params.items():
            print(f"{k}: {v}")

        # Request

        request = session.get(SEARCH_TWEETS_URL, params=params)

        if request.status_code == 200:
            search_timeline = json.loads(request.text)

            for tweet in search_timeline["statuses"]:
                # 結果表示
                """
                print("-" * 30)
                id = tweet['id']
                print(f"ID: {id}")
                created_at = parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo'))
                print(f"Created at {created_at}")
                """

                # 次の100件を取得したときにmax_idとイコールのものはすでに取得済みなので捨てる
                if max_id == tweet["id"]:
                    print("continue")
                    continue

                timeline = {"id": tweet["id"], 
                            "created_at": str(parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo'))), 
                            "text": tweet["text"], 
                            "use_id": tweet["user"]["id"], 
                            "user_created_at": str(parser.parse(tweet['user']['created_at']).astimezone(timezone('Asia/Tokyo'))), 
                            "user_name": tweet["user"]["name"], 
                            }

                # Get URL
                if "media" in tweet["entities"]:
                    medias = tweet["entities"]["media"]
                    for media in medias:
                        timeline["url"] = media["url"]
                        break
                elif "urls" in tweet["entities"]:
                    urls = tweet['entities']['urls']
                    for url in urls:
                        timeline['url'] = url['url']
                        break
                else:
                    timeline["url"] = None

                timelines.append(timeline)

        else:
            print("ERROR: %d" % request.status_code)

        print("-" * 30)
        session.close()

        return timelines, id
        
    def get_rate_limit_status(self):
        session = self.get_session()
        limit = 1
        remaining = 1
        reset_minute = 0

        request = session.get(RATE_LIMIT_STATUS_URL)
        if request.status_code == 200:
            limit_api = json.loads(request.text)

            limit = limit_api['resources']['search']['/search/tweets']['limit']
            remaining = limit_api['resources']['search']['/search/tweets']['remaining']
            reset = limit_api['resources']['search']['/search/tweets']['reset']
            reset_minute = math.ceil((reset - time.mktime(datetime.datetime.now().timetuple())) / 60)

        session.close()

        return limit, remaining, reset_minute

    def api_remain_and_sleep(self):
        limit, remaining, reset_minute = self.get_rate_limit_status()
        print("-" * 30)
        print(f"limit: {limit}\n remaining: {remaining}\n reset: {reset_minute}\n")

        if remaining == 0:
            time.sleep(60 * (int(reset_minute) + 1))

    def write_tweet_to_file(self, timelines, date, name=None):
        if name is None:
            name = self.query
            
        with open(f"./tweet/{name}_{date}.json", "a") as f:
            json.dump(timelines, f, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            f.write("\n")

if __name__ == "__main__":
    pass