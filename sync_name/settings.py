import os


# Twitter Keys
try:
    key = os.environ['TWITTER_API_KEY'].strip()
    key_sec = os.environ['TWITTER_API_SECRET'].strip()
    assert key
    assert key_sec
except Exception:
    raise ValueError('Please set the twitter api key!')
TWITTER_API_KEY = key
TWITTER_API_SECRET = key_sec

