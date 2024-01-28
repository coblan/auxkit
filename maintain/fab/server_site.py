from datetime import datetime

class Site(object):
    def __init__(self,server):
        self.server= server
        
    def backupToServer(self,source,target,exclude=[]):
        print(f'打包{src_path}')
        self.server.run(f'tar -h -zcvf /tmp/transfer/remote_dir.tar.gz {src_path}',hide ='out')
        print(f'下载{item.get("name")}')
    
    def returnToServer(self,source,target):
        pass
    
    