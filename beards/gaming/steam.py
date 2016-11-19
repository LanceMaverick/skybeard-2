import os
import requests
from . import config

api_key = config.steam_api_key
curr_path = os.path.dirname(__file__)

def keySearch(lst,key,value):
    for item in lst:
        if item[key] == value:
            return item
    return None

"""get latest steam news post using given payload parameters"""
def steam_news(payload):
    steam_url = 'http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/'
    response = requests.get(steam_url,params=payload)
    news = response.json()['appnews']
    return news['newsitems']

def get_new_patch(game_id, patch_id):

    yaml_path = os.path.join(curr_dir, 'yamls/'+game_id+'_patch_id.yaml')

    last_update = yaml.load(open(yaml_path),'rb')

    payload={
            'appid': game_id,
            'count':'20',
            'maxlength':'300'
            }
    news = steamNews(payload)
    if not news:
        return logging.error('No results or http code returned from steam news. Servers down?')
    patch = keySearch(news,'feedname','steam_updates')

    if patch:
        new_patch_id = patch['gid']
    else:
        return None
    if new_patch_id == last_update:
        return None
    else:
        logging.info('new patch data found:',patch)
        yaml.dump(patch_id,open(yaml_path,'wb'))
        return patch

def news_reply(header, news):
    title = '\n<b>'+news['title']+'</b>'
    contents = news['contents']
    url = news['url']
    texts = [
            header,
            title,
            contents,
            '\nSee the rest of this post here:',
            url]
    reply = '\n'.join(texts)
    return reply

def post_news(game_id):
    payload={
            'appid': game_id,  #dteam appid for dota2
            'count':'1',    #latest news post only
            'maxlength':'300' #maximum length of news summary for bot message
            }
    try:
        news = steam_news(payload)[0]
    except IndexError:
        return 'Request failed. Servers may be down'

    if not news:
        return 'No news items found in steam api request'

    header = '<b>Latest news post</b> ({})'.format(news['feedlabel'])
    return news_reply(header,news)
