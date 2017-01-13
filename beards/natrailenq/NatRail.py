#!/usr/bin/env python

from lxml import html
import requests
import json
import re
import parser

class RailScraper:
      def __init__(self, url, station_codes_doc):
        self.coreurl = url
        self.codes = json.load(open(station_codes_doc, 'r'))     
        self.info = {}

      def planJourney(self, station, To, time='now'):
        

      def getDepartures(self, station, To=''):
        if To != '':
          To = self.codes[To]
          To = '/{}/To'.format(To)
        stc = self.codes[station.replace('/departures ','')]
        webpage = requests.get(self.coreurl+stc+To)
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
