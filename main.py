import twitter
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

config = json.load(open('/home/andrewda/boomboom/config.json'))

api = twitter.Api(consumer_key=config['consumer_key'],
                  consumer_secret=config['consumer_secret'],
                  access_token_key=config['access_token_key'],
                  access_token_secret=config['access_token_secret'])

update_tweet = """
Update @ {time}

Chicken Bites:
    {boom}w/ Boom Boom 💥
    {bbq}w/ BBQ 🤠
    {boom_bbq}w/ Boom Boom & BBQ 💥🤠
{breadsticks}Breadsticks 🥖
{cookies}Cookies 🍪
"""

open_tweet = """
Update @ {time}

Food2You is now open! 🎉
"""

closed_tweet = """
Update @ {time}

Food2You is now closed. Check https://food.oregonstate.edu for hours.
"""

positive_icon = '✅ '
negative_icon = '❌ '

def get_icon(value):
    return positive_icon if value else negative_icon

status_file = open('/home/andrewda/boomboom/status.json', 'r+')
prev_status = {}

try:
    prev_status = json.load(status_file)
except:
    pass

res = requests.get('https://my.uhds.oregonstate.edu/food2you', headers={'cookie': config['cookie']}, allow_redirects=False)

new_status = {
    'open': res.status_code == 200,
    'items': [],
}

if res.status_code == 200 and (not 'open' in prev_status or not prev_status['open']):
    tweet = open_tweet.format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print(tweet)
    api.PostUpdate(tweet)
elif res.status_code == 302 and (not 'open' in prev_status or prev_status['open']):
    tweet = closed_tweet.format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print(tweet)
    api.PostUpdate(tweet)

status_file.seek(0)
json.dump(new_status, status_file)
status_file.truncate()

if res.status_code == 302:
    print('[DEBUG {}] Food2You is closed'.format(datetime.now().strftime('%Y-%m-%d %H:%M')))
    exit(1)

soup = BeautifulSoup(res.content, 'html.parser')

items = [soup.find(class_=name) for name in ['ChickenBitesw/BoomBoomsauce', 'ChickenBitesw/BBQsauce', 'ChickenBitesw/BoomBoomandBBQsauce', '4Breadsticks', '3FreshBakedCookies']]
busy_items = list(map(lambda element: (element.find(class_='busy') or element.find(class_='out')) is None, items))

new_status['items'] = busy_items

status_file.seek(0)
json.dump(new_status, status_file)
status_file.truncate()

if prev_status['items'] != busy_items:
    tweet = update_tweet.format(
        time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        boom=get_icon(busy_items[0]),
        bbq=get_icon(busy_items[1]),
        boom_bbq=get_icon(busy_items[2]),
        breadsticks=get_icon(busy_items[3]),
        cookies=get_icon(busy_items[4]),
    )
    print(tweet)
    api.PostUpdate(tweet)
else:
    print('[DEBUG {}] No updates'.format(datetime.now().strftime('%Y-%m-%d %H:%M')))
