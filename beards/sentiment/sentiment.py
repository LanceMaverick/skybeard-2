import os
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from dateutil import parser
import dataset
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from . import config

#Plotting and sending. A bit rough. Would be better to use figures.
fpath = os.path.join(
        os.path.dirname(__file__),
        'sentiment{}.png')

def analyze(msg):
    #can take msg or string
    try:
        text = msg['text']
    except TypeError:
        text = msg
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score

async def save(msg, score):
    user_id = msg['from']['id']
    user_name = msg['from']['first_name']
    chat_id = msg['chat']['id']
    text = msg['text']
    date = msg['date']
    entry = dict(
            user_id = user_id,
            user_name = user_name,
            chat_id = chat_id,
            date = date,
            pos = score['pos'],
            neg = score['neg'],
            compound = score['compound']
            )
    with dataset.connect(config.db_path) as db:
        db['message_log'].insert(entry)
    
def get_results(msg, neut = True):
    
    with dataset.connect(config.db_path) as db:
        table = db['message_log']
    results = table.find(chat_id=msg['chat']['id'])
    
    #skip or include neutral messages based on neut value
    if neut: 
        results_list = [row for row in results]
    else:
        results_list = [
                row for row in results if row['compound'] != 0.0]

    u_name = [row['user_name'] for row in results_list]
    users = list(set(u_name))
    user_scores = {}
    for u in users:
        user_scores[u] = []
    
    pos = []
    neg = []
    compound = []
    date = []
    names = []
        
    for row in results_list:
        pos.append(row['pos'])
        neg.append(row['neg'])
        compound.append(row['compound'])
        date.append(row['date'])
        names.append(row['user_name'])
        user_name = row['user_name']
        user_scores[user_name].append(row['compound'])

    user_names = [k for k in user_scores.keys()]
    user_sums = [sum(v)/float(len(v)) for v in user_scores.values()]
    

    #data = np.column_stack((pos, neg, compound, date, names))
    #print(data)
    #df = pd.DataFrame(data, columns=["pos", "neg", "compound", "date", "names"])
    #df['names'] = df['names'].astype(str)
    #print(df)
    
    df = pd.DataFrame(
            {
                'pos': pos,
                'neg': neg,
                'compound': compound,
                'date': date,
                'names': names
                })
    
    sns.set(style="ticks")
    
    u_plot = sns.stripplot(
               x = 'names', 
               y = 'compound', 
               data=df, 
               jitter = True,
               order = user_names)

    for item in u_plot.get_xticklabels():
        item.set_rotation(45)
    sns.plt.title('Message scores for each user.')
    plt.savefig(fpath.format('2'), bbox_inches='tight')
    
    plt.clf()

    s_plot = sns.lmplot('pos', 'neg', 
               data=df, 
               fit_reg=False, 
               legend = False,
               hue="compound",  
               palette = 'RdBu',
               scatter_kws={"marker": "D", 
                            "s": 100})
    sns.plt.title('All message scores. Hue = compound score.')
    s_plot.savefig(fpath.format('1'), bbox_inches='tight')

    plt.clf()

    user_plot = sns.barplot(user_sums, user_names, orient = 'h')
    sns.plt.title('Average scores for each user.')
    user_plot.figure.savefig(fpath.format('3'), bbox_inches='tight')

    plt.clf()

    time_plot = sns.tsplot(data=df, value = 'compound', time='date')
    time_plot.figure.savefig(fpath.format('4'), bbox_inches='tight')

    plt.clf()

    plot1 = open(fpath.format('1'), 'rb')
    plot2 = open(fpath.format('2'), 'rb')
    plot3 = open(fpath.format('3'), 'rb')
    plot4 = open(fpath.format('4'), 'rb')

    return plot1, plot2, plot3, plot4

def get_user_results(msg, neut = True):
    user_id = msg['from']['id']
    user = msg['from']['first_name']

    with dataset.connect(config.db_path) as db:
        table = db['message_log']
    results = table.find(user_id = user_id)

    if neut:
        data = [r['compound'] for r in results]
    else:
        data = [r['compound'] for r in results if r['compound'] != 0.0]

    hist = sns.distplot(data, hist=False, rug=True)
    sns.plt.title('Kernel density estimated distribution for '+user)
    plt.savefig(fpath.format('user'), bbox_inches='tight')
    plot = open(fpath.format('user'), 'rb')
    plt.clf()

    return plot



    
