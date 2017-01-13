#!/usr/bin/env python

from lxml import html
import requests
import json
import re
import parser
import datetime

def roundTo15(time):
    out = ''
    if int(time[2:]) > 0:
       out = time[:1]+'15'
    if int(time[2:]) > 15:
       out = time[:1]+'30'
    if int(time[2:]) > 30:
       out = time[:1]+'45'
    else:
       out = time[0] + str(int(time[1])+1) + '00'
    return out
class RailScraper:
      def __init__(self, url, station_codes_doc):
        self.coreurl = url
        self.codes = json.load(open(station_codes_doc, 'r'))     
        self.info = {}
        y = datetime.datetime.now().strftime('%Y')
        m = datetime.datetime.now().strftime('%m')
        d = datetime.datetime.now().strftime('%d')
        h = datetime.datetime.now().strftime('%H')
        m = datetime.datetime.now().strftime('%M')
        self.time = '{}{}'.format(h,m)
        self.date = '{}{}{}'.format(d,m,y)
      def planJourney(self, station, To, day='today',time='now'):
       org = self.codes[station]
       dest = self.codes[station] 
       if time.lower() == 'now':
          time = roundTo15(self.time)
       else:
          time = time.replace(':','')
       if date.lower() == 'today' or date.lower()=='now':
          date = self.date
       else:
          date = date.replace('/','')
       webpage = requests.get(self.coreurl+'/timesandfares/{}/{}/{}/{}/dep'.format(org,dest,date,time)) 
       print(webpage.content)
      def getDepartures(self, station, To=''):
        if To != '':
          To = self.codes[To]
          To = '/{}/To'.format(To)
        stc = self.codes[station.replace('/departures ','').replace('Road','Rd')]
        webpage = requests.get(self.coreurl+'ldbboard/dep/'+stc+To)
        i=1
        result = re.findall(r'(?:\s{29})([\w\s\&\.\)\(\']+)&\w+;(.*?)<\/td>', webpage.content.decode('utf-8'))	
        times = re.findall(r'(\d\d:\d\d|Cancelled|On time)', webpage.content.decode('utf-8'))
        if not result or not times:
          return
        due = times[0::3]
        expt = times[1::3]
        for element in result:
           dest, via = element
           self.info[i] = {}
           self.info[i]['destination'] = dest
           self.info[i]['via'] = via
           self.info[i]['due'] = due[i-1]
           self.info[i]['expected'] = expt[i-1]
           i+=1
      def makeDeptString(self, station, via=''):
           self.getDepartures(station, via)
           out_str = ''
           if bool(self.info):
            print("Passed")
            for key in self.info:
             out_str +='*{}*\t{}'.format(self.info[key]['due'], self.info[key]['destination'])
             if self.info[key]['via'] != '':
                out_str += '\tvia {}'.format(self.info[key]['via'])
             out_str += '\t_{}_\n'.format(self.info[key]['expected'])
             print(out_str)
            
           else:
              out_str = "No Services From This Station."
           return out_str
