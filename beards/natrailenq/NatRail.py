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

      def getStationFromCode(self, stat):
          for key in self.codes:
             if self.codes[key] == stat:
                 return key
          return stat

      def searchStations(self, search):
         out_str = '' 
         out_list = []
         for key in self.codes:
           if search in key:
              out_str += '{}\n'.format(key)
              out_list.append(key)
         return (out_str, out_list)         
    
      def getStatus(self):
       webpage = requests.get('http://www.nationalrail.co.uk/service_disruptions/indicator.aspx')
       toc = re.findall(r'class\=\"first\">([\w\s\(\d\)\'\,]+)', webpage.content.decode('utf-8'))[1:]
       status = re.findall(r'(Major[\w\s]+|Good[\w\s]+|Minor[\w\s]+)+', webpage.content.decode('utf-8'))[1:]
       out_str = ''
       for i,j in zip(toc, status): 
         out_str += '*{}* {}\n'.format(i, j)
       return out_str        

      def getDepartures(self, station, To=''):
        if To != '':
          if To.replace('/departures ','').replace('Road','Rd') in self.codes:
            to = self.codes[To.replace('/departures ','').replace('Road','Rd')]
          elif To.replace('/departures ', '') in self.codes.values():
               to = To
          else:
            return 'nTo'
          to = '/{}/To'.format(to)
        if station.replace('/departures ','').replace('Road','Rd') in self.codes:
          stc = self.codes[station.replace('/departures ','').replace('Road','Rd')]
        elif station.replace('/departures ','') in self.codes.values():
          stc = station
        else:
          return 'nOrigin'
        webpage = requests.get(self.coreurl+'ldbboard/dep/'+stc+to)
        i=1
        result = re.findall(r'(?:\s{29})([\w\s\&\.\)\(\']+)&\w+;(.*?)<\/td>', webpage.content.decode('utf-8'))	
        times = re.findall(r'(\d\d:\d\d|Cancelled|On time)', webpage.content.decode('utf-8'))
        plat = re.findall(r'<td>([\d\w]+|)<\/td>', webpage.content.decode('utf-8'))
        if not result or not times:
          return
        due = times[0::3]
        expt = times[1::3]
        print(plat) 
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
           station = self.getStationFromCode(station)
           via = self.getStationFromCode(via)
           out_str = ''
           if bool(self.info):
            out_str += "Departures from {}\n".format(station)
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
                   out_str += "Departures from {}\n".format(i)
                   out_str += self.makeDeptString(i,via)
           elif success == "nTo":
              x,y = self.searchStations(via)
              out_str = ''
              if x != '':
                 for i in y:
                   out_str += "Departure from {}\n".format(station)
                   out_str += self.makeDeptString(station,i)
           else:
              out_str = "No Services From This Station."
           return out_str

      def getNews(self, search=''):
          webpage = requests.get('http://www.nationalrail.co.uk/service_disruptions/today.aspx')
          news = re.findall(r'colspan\=\"2\">([\w\d\s\:\'\)\(\-\,\.&amp;\/]+)', webpage.content.decode('utf-8'))
          start = '*Service Disruptions Today*\n\n'
          out_str = start
          print(search)
          for item in news:
             if search != '':
               if search in item:
                 out_str += '- {}\n\n'.format(item)
             else:
                 out_str += '- {}\n\n'.format(item)
          if out_str == start:
             if search != '':
               out_str = 'There are currently no reported disruptions on {} services.'.format(search)
             else:
               out_str = 'There are currently no disruptions on the National Rail network.'
          return out_str
