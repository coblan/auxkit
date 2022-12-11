from auxkit.maintain.fab.copy import big_remote_copy

class DjangoSite(object):
    def __init__(self,server,project_name,uwsgi,nginx):
        self.server = server
        self.project_name=project_name
        self.uwsgi= uwsgi
        self.nginx=nginx
    
    def createDocker(self):
        print(f'创建{self.project_name}的docker容器，并且执行')
        self.server.run(f'docker run -itd -v /pypro/{self.project_name}:/pypro/{self.project_name} --name {self.project_name} coblan/py38_sqlserver:v10 /bin/bash'
                        ,pty=True)
        self.server.run(f'docker start {self.project_name}')
        self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{self.uwsgi}') 
    
    def makeNginx(self):
        print(f'创建{self.project_name}的nginx配置')
        with self.server.cd('/etc/nginx/sites-enabled'):
            self.server.run(f'ln -s /pypro/{self.project_name}/deploy/{self.nginx} {self.nginx}')
    def initSiteDir(self):
        print(f'创建{self.project_name}的必要文件夹')
        self.server.run(f'mkdir /pypro/{self.project_name}')
        with self.server.cd(f'/pypro/{self.project_name}'):
            self.server.run(f'mkdir run')  
            self.server.run(f'mkdir log')
    
    def copyFile(self,src_server,src_password):
        big_remote_copy(src_server, f'/pypro/{self.project_name}', self.server, f'/pypro/{self.project_name}', src_password)
    
    def copyMedia(self,src_server,src_password):
        print(f'创建{self.project_name}的media文件')
        big_remote_copy(src_server, f'/pypro/{self.project_name}/media', self.server, f'/pypro/{self.project_name}/media', src_password)
        
    def importDb(self):
        pass
    
        