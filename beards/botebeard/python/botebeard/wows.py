import os
from datetime import datetime
import yaml
import wargaming
from .config import app_id, region, language

ships_path = os.path.join(
        os.path.dirname(__file__),
        'ships.yml')

def get_player_stats(captain_id):
    wows = wargaming.WoWS(
            application_id = app_id, 
            region = region, 
            language = language)
    
    data = wows.account.info(account_id = captain_id).data[captain_id]
    name = data['nickname']
    last_played = datetime.fromtimestamp(
            int(data['last_battle_time']),
            ).strftime('%d.%m.%Y')
    pvp = data['statistics']['pvp']
    battles = pvp['battles']
    winrate = round(float(pvp['wins'])/float(battles)*100, 2)
    av_xp = round(float(pvp['xp'])/float(battles), 2)

    return dict(
            name = name,
            last_played = last_played,
            battles = battles,
            winrate = winrate,
            xp = av_xp
            )

def find_ship(search):
    ship_names = yaml.load(open(ships_path, 'r'))
    for ship in ship_names:
        if search.lower() in ship['name'].decode('utf8').lower():
            return ship
    return None

def get_player_ship_stats(captain_id, ship_id):
    wows = wargaming.WoWS(
            application_id = app_id, 
            region = region, 
            language = language)
    request = wows.ships.stats(
            ship_id = ship_id, 
            account_id = captain_id
            )
    
    try:
        data=request.data[captain_id][0]['pvp']
    except TypeError:
        battles = None 
        av_damage = None
        winrate = None
        av_xp = None
        av_kills = None
    else:
        battles = data['battles']
        damage = data['damage_dealt']
        frags = data['frags']
        wins = data['wins']
        xp = data['xp']
        av_damage = round(float(damage)/float(battles), 2)
        winrate = round(float(wins)/float(battles)*100, 2)
        av_xp = round(float(xp)/float(battles), 2)
        av_kills = round(float(frags)/float(battles), 2)

    ship = wows.encyclopedia.ships(ship_id=ship_id).data[ship_id]
    image_url = ship['images']['small']
    ship_name = ship['name']
        
    stats = dict(
            name = ship_name,
            battles = battles,
            av_damage = av_damage,
            xp = av_xp,
            winrate = winrate,
            kills = av_kills)

    return dict(
            image = image_url,
            stats = stats)
