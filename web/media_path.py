import requests
import hashlib
import os
import shutil

class MediaAdapter(object):
    def __init__(self,path) :
        self.path = path
        try:
            os.mkdir(self.path)
        except:
            pass

    def getFilePath(self,url,suffix):
        hl = hashlib.md5()
        hl.update(url.encode(encoding='utf-8'))
        return f'{hl.hexdigest()}.{suffix}'

    def saveImage(self,url):
        rt = requests.get(url,stream=True)
        if rt.status_code == 200:
            suffix = rt.headers.get('Content-Type').split('/')[1]
            path = os.path.join(self.path,self.getFilePath(url,suffix))            
            with open(path, 'wb') as f:
                rt.raw.decode_content = True
                shutil.copyfileobj(rt.raw, f) 

    def getMediaPath(self,url):
        pass