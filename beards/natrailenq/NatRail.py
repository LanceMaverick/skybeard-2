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
       out = time[:2]+'15'
    if int(time[2:]) > 15:
       out = time[:2]+'30'
    if int(time[2:]) > 30:
       out = time[:2]+'45'
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
        M = datetime.datetime.now().strftime('%M')
        
        self.time = '{}{}'.format(h,M)
        self.date = '{}{}{}'.format(d,m,y)

      def searchStations(self, search):
         out_str = '' 
         out_list = []
         for key in self.codes:
           if search in key:
              out_str += '{}\n'.format(key)
              out_list.append(key)
         return (out_str, out_list)         

      def planJourney(self, station, To, date='today',time='now'):
       org = self.codes[station]
       dest = self.codes[To] 
       if time.lower() == 'now':
          time = roundTo15(self.time)
       else:
          time = time.replace(':','')
       if date.lower() == 'today' or date.lower()=='now':
          date = self.date
       else:
          date = date.replace('/','')
       webpage = requests.get(self.coreurl+'/timesandfares/{}/{}/{}/{}/dep'.format(org,dest,date,time)) 
       
       print(self.coreurl+'timesandfares/{}/{}/{}/{}/dep'.format(org,dest,date,time))

       dep_time = re.findall(r'(.*?)<td\sclass\=\"dep\"\>(\d\d:\d\d)', webpage.content.decode('utf-8'))
       print(dep_time)
       arr_time = re.findall(r'(.*?)<td\sclass\=\"arr\"\>(\d\d:\d\d)', webpage.content.decode('utf-8'))
       print(arr_time)
       print(webpage.content.decode('utf-8'))
       duration = (re.findall(r'(.*?)<td\sclass\=\"dur\"\>\d+', webpage.content.decode('utf-8')), re.findall(r'\d\d<abbr', webpage.content.decode('utf-8')))
       changes = re.findall(r'changestip\-link\"\>\d+', webpage.content.decode('utf-8'))
       ticket_info =re.findall(r'\<input\stype\=\"hidden" value\=\"([\w\s]+)\|\d+\|\w+\|([\w\-\s]+)\|(?:\w+|)\|(\d+.\d+)\|(?:\w+|)\|\w+\|\w+\|(?:\w+|)\|\w+\|([\w\d\s]+)\|\d+\|\d+\|([\w\s\d]+)', webpage.content.decode('utf-8'))
       out_str = '' 
       for i, j, k, l, m in zip(dep_time, arr_time, duration, changes, ticket_info):
          (fare_type, fare_desc, price, toc, desc) = m
          out_str += '*{}* {} to {}*{}* {} {}\n'.format(i, station, To, j, '£'+price, fare_desc)
          out_str += 'A {} service. {}\n'.format(toc, desc)
       return out_str

      def getDepartures(self, station, To=''):
        if To != '':
          if To.replace('/departures ','').replace('Road','Rd') in self.codes:
            stc = self.codes[To.replace('/departures ','').replace('Road','Rd')]
          else:
            return 'nTo'
          To = self.codes[To]
          To = '/{}/To'.format(To)
        if station.replace('/departures ','').replace('Road','Rd') in self.codes:
          stc = self.codes[station.replace('/departures ','').replace('Road','Rd')]
        else:
          return 'nOrigin'
        webpage = requests.get(self.coreurl+'ldbboard/dep/'+stc+To)
        i=1
        result = re.findall(r'(?:\s{29})([\w\s\&\.\)\(\']+)&\w+;(.*?)<\/td>', webpage.content.decode('utf-8'))	
        times = re.findall(r'(\d\d:\d\d|Cancelled|On time)', webpage.content.decode('utf-8'))
        plat = re.findall(r'<td>(\d+|)<\/td>', webpage.content.decode('utf-8'))
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
           self.info[i]['plat'] = plat[i-1]
           i+=1
        return "Success"
      def makeDeptString(self, station, via=''):
           success = self.getDepartures(station, via)
           out_str = ''
           if bool(self.info):
            print("Passed")
            for key in self.info:
             out_str +='*{}* {}'.format(self.info[key]['due'], self.info[key]['destination'])
             if self.info[key]['via'] != '':
                out_str += ' {}'.format(self.info[key]['via'])
             out_str += ' _{}_'.format(self.info[key]['expected'])
             if self.info[key]['plat'] == '':
                self.info[key]['plat'] = '-'
             out_str+=' Plat {}\n'.format(self.info[key]['plat'])
           
           elif success == "nOrigin":
              x,y = self.searchStations(station)
              out_str = ''
              if x != '':
                 for i in y:
                   out_str += "Departs from {}\n".format(i)
                   out_str += self.makeDeptString(i,via)
           elif success == "nTo":
              x,y = self.searchStations(via)
              out_str = ''
              if x != '':
                 for i in y:
                   out_str += "Departs from {}\n".format(station)
                   out_str += self.makeDeptString(station,i)
           else:
              out_str = "No Services From This Station."
           return out_str
