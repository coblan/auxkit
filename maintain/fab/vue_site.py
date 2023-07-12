import invoke
local = invoke.Context()
from auxkit.files.compress import make_targz

class VueSite(object):
    def __init__(self,server,local_path,server_path):
        self.server = server
        #self.project_name=project_name
        self.server_path = server_path# or f'/pypro/{project_name}' 
        self.local_path=local_path
        
    def build(self):
        with local.cd(self.local_path):
            local.run('npm run build')
    
    def upload(self):
        make_targz(r'D:\tmp\web_dist.tar.gz', fr'{self.local_path}\dist\\')
        print('开始上传')
        self.server.put(r'D:\tmp\web_dist.tar.gz','/tmp/web_dist.tar.gz')
        print('上传成功')
        self.server.run(f"tar xvf /tmp/web_dist.tar.gz -C {self.server_path}")
        