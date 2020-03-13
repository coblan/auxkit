import subprocess
import datetime
import re
from functools import partial
import _thread
import time
from .line_parser.django import join_line
from .line_parser.django import django_log_parsers
from .line_parser.nginx import nginx_log_parser

from .output.elastic import elastice_search

class DFileBeat(object):
    def __init__(self, harvest, parsers,outputs,beat_span=5):
        self.harvest=harvest
        self.parsers = parsers
        self.outputs = outputs
        self.beat_span = beat_span
    
    def run(self):
        self.cache_list = []
        self.harvest(self)
        self.beat()

               
    def beat(self):
        while True:
            print('心跳')
            out_list = self.cache_list
            self.cache_list =[]
            if not out_list:
                time.sleep(self.beat_span)
                continue
            for parser in self.parsers:
                out_list = parser(out_list)
            for output in self.outputs:
                output(self,out_list)
            time.sleep(self.beat_span)


def multi_tail_file(path_list,self):
    self.running_thread =[]
    for path in path_list:
        self.running_thread.append(
             _thread.start_new_thread(tail_file,(path, self))
        )
       

def tail_file(path,self):
    print('watching path:%s'%path)
    p = subprocess.Popen('tail -f %s'%path,stdout= subprocess.PIPE,shell=True)
    start_now = datetime.datetime.now()
    record = False
    while p.poll() is None:
        line = p.stdout.readline()
        line_temp = line.strip()
        if not record:
            now = datetime.datetime.now()
            if now- start_now > datetime.timedelta(seconds =2):
                record = True
                print('start recording')
        if line_temp and record:
            self.cache_list.append( {'path':path,'message':line}  )


if __name__ =='__main__':
    pp = DFileBeat(harvest= partial(multi_tail_file,
                                    [
                                        r'D:\coblan\py3\fastdog\maintain\filebeat\test_ok.log',
                                        r'D:\coblan\py3\fastdog\maintain\filebeat\test_ok2.log'
                                    ]),
                   parsers =[
                       decode_utf8,
                       join_line,
                       partial(strip_word,'level'),
                       partial(strip_span,'@timestamp',23), datetime_timestamp,
                       
                    ],
                   outputs = [
                       partial(elastice_search,'z.enjoyst.com:9200','elastic','he27375089','beat-test')
                   ] )
    pp.run()
    
