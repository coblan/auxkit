import re
from functools import partial
from . share import decode_utf8,strip_word,strip_span,save_message,recover_message
import re
import datetime
import os
import requests
import sqlite3
import urllib

if os.environ.get('geo_db'):
    import geoip2.database
    reader = geoip2.database.Reader(os.environ.get('geo_db') )
    #reader = geoip2.database.Reader(r'D:\wok_file\program\GeoLite2-City.mmdb')

def get_ip(lines):
    pattern = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    for line in lines:
        messge = line['message']
        messge = messge.lstrip()
        mt = re.search(pattern,messge)
        if mt :
            line['ip'] = mt.group()
            line['message'] = messge[len(line['ip']):]
    return lines

def nginx_datetime(lines):
    "[13/Mar/2020:07:25:00 +0800] GET ...."
    pattern = r'\[(\d{2}\/[A-Za-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2}) (\+|\-)\d{4}\]'
    beijin = datetime.timezone(datetime.timedelta(hours=8))
    for line in lines:
        messge = line['message']
        mt = re.search(pattern,messge)
        if mt :
            timestamp_str = mt.group(1)
            line['@timestamp'] = datetime.datetime.strptime(timestamp_str,'%d/%b/%Y:%H:%M:%S').replace(tzinfo = beijin)
            line['message'] = messge[:mt.start(0)] + messge[mt.end(0): ]
    return lines
    
def nginx_path(lines):
    pattern = r'[^\s]+'
    for line in lines:
        messge = line['message']
        mt = re.search(pattern,messge)
        if mt :
            url = mt.group()
            rt = urllib.parse.urlparse(url)
            line['url'] = rt.path
            line['message'] = messge[:mt.start(0)] + messge[mt.end(0): ]
    return lines

def nginx_agent(lines):
    pattern = r'"([^"]*)"$'
    for line in lines:
        messge = line['message']
        mt = re.search(pattern,messge)
        if mt :
            line['agent'] = mt.group(1)
    return lines

def location_router(lines):
    baidu_ak = os.environ.get('baidu_ak')
    ip_db = os.environ.get('ip_db')
    if ip_db:
        return ip_baidu_location(lines)
    elif os.environ.get('geo_db'):
        return ip_location(lines)
    else:
        return lines

def ip_location(lines):
    if not os.environ.get('geo_db'):
        return lines
    for line in lines:
        ip = line['ip']
        response = reader.city(ip)
        line['location'] = {
            'lat':response.location.latitude,
            'lon':response.location.longitude,
        }
        line['city'] = response.city.name
    return lines


def create_db():
    db = os.environ.get('ip_db')
    conn = sqlite3.connect(db)
    c = conn.cursor()
    create_table_sql= '''CREATE TABLE IF NOT EXISTS iptable
             (ip text, city text, lat real, lon real)'''
    c.execute(create_table_sql)
    conn.commit()
    conn.close()
    
if os.environ.get('ip_db'):
    create_db()  
    
def ip_web_location(lines):
    "无缓存，则切换为web请求"
    db = os.environ.get('ip_db')
    if not db:
        return lines
    conn = sqlite3.connect(db)
    c = conn.cursor()
    #url = 'http://ip-api.com/json/%s'
    url = os.environ.get('web_ip')
    for line in lines:
        ip = line['ip']
        dc = {}
        find = False
        for item in c.execute('select * from iptable where ip="%s"'%ip):
            dc = {
                'ip':item[0],
                'city':item[1],
                'lat':item[2],
                'lon':item[3]
            }
            break
        if not dc:
            rt = requests.get(url%{'ip':ip})
            dc = rt.json().get('data')
            c.execute('insert into iptable VALUES ("%s","%s",%s,%s)'%(ip,dc.get('city'),dc.get('lat'),dc.get('lon')))
            conn.commit()
        line['location'] = {
            'lat':dc.get('lat'),
            'lon':dc.get('lon'),
        }
        line['city'] = dc.get('city')
    return lines
    
def ip_baidu_location(lines):
    db = os.environ.get('ip_db')
    baidu_ak = os.environ.get('baidu_ak')
    
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for line in lines:
        ip = line['ip']
        response = reader.city(ip)
        if response.country.name != 'China':
            line['location'] = {
            'lat':response.location.latitude,
            'lon':response.location.longitude,
            }
            line['city'] = response.city.name
        else:
            dc = {}
            find = False
            for item in c.execute('select * from iptable where ip="%s"'%ip):
                dc = {
                    'ip':item[0],
                    'city':item[1],
                    'lat':item[2],
                    'lon':item[3]
                }
                break
            if not dc:
                """ {'address': 'CN|北京|北京|None|CDSNET|0|0', 
                    'content': {'address': '北京市', 
                        'address_detail': {'city': '北京市', 'city_code': 131, 'district': '', 'province': '北京市', 'street': '', 'street_number': ''}, 
                        'point': {'x': '116.40387397', 'y': '39.91488908'}}, 
                    'status': 0} """
                url = 'http://api.map.baidu.com/location/ip?ak=%s&ip=%s&coor=bd09ll'%(baidu_ak,ip) #
                rt = requests.get(url)
                dc = rt.json()
                c.execute('insert into iptable VALUES ("%s","%s",%s,%s)'%(ip,dc['content']['address_detail']['city'],
                                                                          float( dc['content']['point']['y']),
                                                                          float( dc['content']['point']['x'] )  ))
                conn.commit()
            line['location'] = {
                'lat':dc.get('lat'),
                'lon':dc.get('lon'),
            }
            line['city'] = dc.get('city')
    return lines
    
    

nginx_log_parser = [
    #decode_utf8,
    ##get_ip,
    ##partial(strip_span,'_no_use',5),
    #nginx_datetime
    
    decode_utf8,
    nginx_datetime,
    save_message,
    get_ip,
    
    #location_router,
    #ip_location,
    ip_web_location,
    partial(strip_span,'_no_use',4),
    partial(strip_span,'_no_use',1),
    partial(strip_word,'method'),
    nginx_path,
    nginx_agent, 
    recover_message,
    
]

nginx_log_full_parser = [
    decode_utf8,
    get_ip,
    partial(strip_span,'_no_use',4),
    nginx_datetime,
    partial(strip_span,'_no_use',1),
    partial(strip_word,'method'),
    nginx_path,

]