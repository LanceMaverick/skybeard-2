import os
import random
import logging
import datetime
import yaml
curr_path = os.path.dirname(__file__)
history_path = os.path.join(curr_path, 'gym_history.yaml')

def keySearch(lst,key,value):
    for item in lst:
        if item[key] == value:
            return item
    return None    

def check_gainz(message):
    #if there is no gym history, just post gainz photos anyway
    try:
        gainz_history = yaml.load(open(history_path,'rb'))
    except IOError:
        return True
    
    user_id = message.from_user.id
    entry = keySearch(gainz_history,'user_id',user_id)
    
    #check if it has been more than one week (168 hours, 10080 minutes) since last gym check-in
    if entry and not expiry(entry['time'],10080):
        return True
    else:
        return False

def update_gainz(message):
    user = message.from_user
    user_id = user.id
    name = user.first_name
    
    try:
        gainz_history = yaml.load(open(history_path, 'rb'))
    except IOError:
        logging.warning('no gainz_history.yaml found. Creating new file')
        gainz_history = []
    
    now = datetime.datetime.now()
    user_new ={'user_id': user_id, 'time': now, 'name': name }
    match = keySearch(gainz_history,'user_id',user_id)
    if match:
        for entry in gainz_history:
            if entry['user_id'] ==user_id:
                entry.update(user_new)
    else:
        gainz_history.append(user_new)
    yaml.dump(gainz_history,open(history_path, 'wb'))
    yaml.dump(gainz_history,sys.stdout)

def add_gym(bot, update):
    pass

def pics(bot, update):
    gain_photos= [
            'http://i.imgur.com/QrdcYCP.jpg',
            'http://i.imgur.com/zopXdvc.jpg',
            'http://i.imgur.com/jEi18ha.jpg'
            ]
    message = update.message 
    chat_id = message.chat_id 
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    random.seed()
    
    if (check_gainz(message)):
        i = random.randint(0, len(gain_photos)-1)
        bot.sendPhoto(chat_id=chat_id, photo=gain_photos[i])
    else:
        bot.sendPhoto(chat_id=chat_id, photo='http://i.imgur.com/Rra4uun.png') #send blobby gains
        message.reply_text('I have not seen you go to the gym this week {}. \
                You do not deserve to see proper gainz.'.format(user_name), quote= False)

def visit(bot, update):
    pass


    
