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

def analyze(msg):
    text = msg['text']
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
    
def get_results(msg):
    
    with dataset.connect(config.db_path) as db:
        table = db['message_log']
    results = table.find(chat_id=msg['chat']['id'])

    results_list = [row for row in results]
    u_name = [row['user_name'] for row in results_list]
    users = list(set(u_name))
    user_scores = {}
    for u in users:
        user_scores[u] = []
    
    pos = []
    neg = []
    compound = []
    date = []
        
    for row in results_list:
        pos.append(row['pos'])
        neg.append(row['neg'])
        compound.append(row['compound'])
        date.append(row['date'])
        user_name = row['user_name']
        user_scores[user_name].append(row['compound'])

    user_names = [k for k in user_scores.keys()]
    user_sums = [sum(v)/float(len(v)) for v in user_scores.values()]

    data = np.column_stack((pos, neg, compound, date))
    df = pd.DataFrame(data, columns=["pos", "neg", "compound", "date"])
    
    #Plotting and sending. A bit rough. Would be better to use figures.
    fpath = os.path.join(
            os.path.dirname(__file__),
            'sentiment{}.png')
    
    sns.set(style="ticks")
    
    matrix_plot = sns.pairplot(df, hue = "compound");
    matrix_plot.savefig(fpath.format('1'))
    plt.clf()

    s_plot = sns.lmplot('pos', 'neg', 
               data=df, 
               fit_reg=False, 
               hue="compound",  
               scatter_kws={"marker": "D", 
                            "s": 100})
    s_plot.savefig(fpath.format('2'))
    plt.clf()
    user_plot = sns.barplot(user_sums, user_names, orient = 'h')
    user_plot.figure.savefig(fpath.format('3'))
    plt.clf()
    time_plot = sns.pointplot(data=df, x='date', y = 'compound')
    time_plot.figure.savefig(fpath.format('4'))
    plt.clf()

    plot1 = open(fpath.format('1'), 'rb')
    plot2 = open(fpath.format('2'), 'rb')
    plot3 = open(fpath.format('3'), 'rb')
    plot4 = open(fpath.format('4'), 'rb')
    return plot1, plot2, plot3, plot4

