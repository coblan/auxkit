import requests
import hashlib
import os
import shutil
import urllib

class MediaAdapter(object):
    def __init__(self,path,media_path=None) :
        """
        @path: 保存文件的根目录，如 D:\work\part3\long\merchant_fish\media\popv
        @media_path: /media/popv/   相对media的路径，注意最后有一个斜线。 如果不需要获取mediaPath，可以不用设置这个路径。
        """
        self.path = path
        self.media_path = media_path
        self.filename = ''
        try:
            os.makedirs(self.path)
        except Exception as e:
            print(e)

    def getFilePath(self,url,suffix):
        hl = hashlib.md5()
        hl.update(url.encode(encoding='utf-8'))
        return f'{hl.hexdigest()}.{suffix}'

    def saveImage(self,url):
        rt = requests.get(url,stream=True)
        if rt.status_code == 200:
            suffix = rt.headers.get('Content-Type').split('/')[1]
            self.filename = self.getFilePath(url,suffix)
            path = os.path.join(self.path,self.filename)            
            with open(path, 'wb') as f:
                rt.raw.decode_content = True
                shutil.copyfileobj(rt.raw, f) 

    def getMediaPath(self):
        return urllib.parse.urljoin(self.media_path,self.filename)