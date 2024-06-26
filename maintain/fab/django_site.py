from auxkit.maintain.fab.copy import big_remote_copy
import invoke
local = invoke.Context()
import shutil
import tarfile
from . mysql_db import MysqlProcess
from invoke import Responder
import os

class DjangoSite(object):
    def __init__(self,server,project_name,server_path=None,image='coblan/py38_sqlserver:v14'):  # 以前是v10版本
        self.server = server
        self.project_name=project_name
        self.server_path = server_path or f'/pypro/{project_name}'
        self.image = image
        #self.uwsgi= uwsgi
        #self.nginx=nginx
    
    def pullDocker(self):
        self.server.run(f'docker pull {self.image}')
    
    def createDocker(self, uwsgi):
        print(f'创建{self.project_name}的docker容器，并且执行')
        self.server.run(f'docker run -itd -v /pypro/{self.project_name}:/pypro/{self.project_name} --name {self.project_name} {self.image} /bin/bash'
                        ,pty=True)
        self.server.run(f'docker start {self.project_name}')
        self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    #def createSuperUser(self):
        #self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    #def makeNginx(self, nginx,path='/etc/nginx/sites-enabled', sudopassword=''):
        #"""
        #path='/etc/nginx/sites-enabled'  是ubuntu的默认的路径
        #path='/etc/nginx/conf.d'   是centos7的默认路径
        #"""
        #print(f'创建{self.project_name}的nginx配置')
        #with self.server.cd(path):
            ##self.server.run(f'ln -s /pypro/{self.project_name}/deploy/{nginx} {nginx}')
            #self.server.run(f'''sudo -S ln -s /pypro/{self.project_name}/deploy/{nginx} {nginx} <<EOF
          #{sudopassword}
          #<<EOF''',encoding='utf-8')  
            
    def makeNginx(self, nginx,path='/etc/nginx/sites-enabled', sudopassword=''):
        """
        path='/etc/nginx/sites-enabled'  是ubuntu的默认的路径
        path='/etc/nginx/conf.d'   是centos7的默认路径
        """
        print(f'创建{self.project_name}的nginx配置')

        sudopass = Responder(
             pattern=r'\[sudo\]',
             response=f'{sudopassword}\n')
    
        with self.server.cd(path):
            self.server.run(f'sudo -S ln -s /pypro/{self.project_name}/deploy/{nginx} {nginx}', pty=True, watchers=[sudopass],encoding='utf-8')     
     
            
    def initSiteDir(self):
        print(f'创建{self.project_name}的必要文件夹')
        self.server.run(f'mkdir /pypro/{self.project_name}')
        with self.server.cd(f'/pypro/{self.project_name}'):
            self.server.run(f'mkdir run')  
            self.server.run(f'mkdir log')
    
    def copyFile(self,src_server,src_password):
        big_remote_copy(src_server, f'/pypro/{self.project_name}', self.server, f'/pypro/{self.project_name}', src_password)
    
    def copyMedia(self,src_server,src_password,exclude=[]):
        """
        直接在远程服务器1上面，从src_server拷贝media文件
        为了防止permission问题
        把本地的 media文件夹，
        chmod -R 777 media/          权限全部打开
        chmod ubuntu -R media         归属为当前登录用户
        """
        print(f'创建{self.project_name}的media文件')
        big_remote_copy(src_server, f'/pypro/{self.project_name}/media', self.server, f'/pypro/{self.project_name}/media', src_password,exclude=exclude)
    
    def downLoadMediaToLocal(self,des_path=None):
        """
        下载media文件到本地。
        如果指定了des_path，则会解压到该路径(修改后未测试)
        """
        print(f'打包媒体文件')
        with self.server.cd(f'{self.server_path}/media'):
            self.server.run(f'tar -h -zcvf /tmp/media.tar.gz *',hide ='out')
        print(f'下载媒体文件到d:/tmp/{self.project_name}_media.tar.gz')
        self.server.get('/tmp/media.tar.gz',f'd:/tmp/{self.project_name}_media.tar.gz')
        if des_path:
            if os.path.exists('d:/tmp/media'):
                shutil.rmtree('d:/tmp/media')
                
            os.makedirs('d:/tmp/media')
            tf = tarfile.open('d:/tmp/media.tar.gz')
            tf.extractall('d:/tmp/media')
            shutil.rmtree(des_path)
            shutil.move(f'd:/tmp/media/{self.server_path}/media/',des_path)
    
    
    def localMediaToServer(self):
        self.server.put(f'd:/tmp/{self.project_name}_media.tar.gz','/tmp/media.tar.gz')
        untar = f'tar -zxvf /tmp/media.tar.gz -C /pypro/{self.project_name}/media/'
        self.server.run(untar)
    
    def reload(self):
        with self.server.cd(self.server_path):
            self.server.run(f'touch run/{self.project_name}.reload',encoding='utf-8')
            
    def migrate(self,sudo=True):
        self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/python /pypro/{self.project_name}/src/manage.py migrate') 
    
    def manageRun(self,cmd):
        """
        创建superuser
        site.manageRun('''shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'root@example.com', 'root123456789')"''')
    
        """
        self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/python /pypro/{self.project_name}/src/manage.py {cmd}') 
        
    
    def exportDb(self):
        cmd = f'docker exec mysql8 mysqldump --column-statistics=0 -u {user} -p{pswd} {mysqldb} >{mysqldb}.sql'
        self.server.run(cmd)
    
    
    def packageSrc(self,local_path, package:list, auxkit=False,):
        server_path = self.server_path
        print('git 打包当前分支')
        with local.cd(local_path):
            local.run(r'git archive -o d:\tmp\src.tar.gz HEAD')
        for pak in package:
            pak_name = pak.replace('/','_')
            with local.cd(fr'{local_path}\src\{pak}'):
                local.run(fr'git archive -o d:\tmp\{pak_name}.tar.gz HEAD')
        if auxkit:
            with local.cd(fr'{local_path}\script\auxkit'):
                local.run(r'git archive -o d:\tmp\auxkit.tar.gz HEAD')  
                
        print(fr'存放打包文件到D:\tmp\package')
        shutil.copy(fr'D:\tmp\src.tar.gz', fr'D:\tmp\package\src.tar.gz')
        #self.server.put(fr'D:\tmp\src.tar.gz','/tmp/src.tar.gz')
        for pak in package:
            pak_name = pak.replace('/','_')
            shutil.copy(fr'D:\tmp\{pak_name}.tar.gz', fr'D:\tmp\package\{pak_name}.tar.gz')
            #self.server.put(fr'D:\tmp\{pak_name}.tar.gz',f'/tmp/{pak_name}.tar.gz' ,)
        if auxkit:
            shutil.copy(fr'D:\tmp\auxkit.tar.gz', fr'D:\tmp\package\auxkit.tar.gz')
            #self.server.put(fr'D:\tmp\auxkit.tar.gz','/tmp/auxkit.tar.gz' ,)
         
        print('拷贝到/tmp文件夹,执行以下命令')
        print(f"tar  xvf /tmp/src.tar.gz -C {server_path}")
        #self.server.run(f"tar  xvf /tmp/src.tar.gz -C {server_path}")
        for pak in package:
            pak_name = pak.replace('/','_')
            print(f"tar  xvf /tmp/{pak_name}.tar.gz -C {server_path}/src/{pak}")
            #self.server.run(f"tar  xvf /tmp/{pak_name}.tar.gz -C {server_path}/src/{pak}")
        if auxkit:
            print(f"tar  xvf /tmp/auxkit.tar.gz -C {server_path}/script/auxkit")
            #self.server.run(f"tar  xvf /tmp/auxkit.tar.gz -C {server_path}/script/auxkit")
    
    def uploadFile(self,local_path, package:list, auxkit=False,):#logrotate=False
        
        """
        上传本地压缩包到服务器。需要制定package
        package=['src/helpers']
        """
        server_path = self.server_path
        print('git 打包当前分支')
        with local.cd(local_path):
            local.run(r'git archive -o d:\tmp\src.tar.gz HEAD')
        for pak in package:
            pak_name = pak.replace('/','_')
            with local.cd(fr'{local_path}\src\{pak}'):
                local.run(fr'git archive -o d:\tmp\{pak_name}.tar.gz HEAD')
        if auxkit:
            with local.cd(fr'{local_path}\script\auxkit'):
                local.run(r'git archive -o d:\tmp\auxkit.tar.gz HEAD')  
                
        print('上传打包文件')
        self.server.put(fr'D:\tmp\src.tar.gz','/tmp/src.tar.gz')
        for pak in package:
            pak_name = pak.replace('/','_')
            self.server.put(fr'D:\tmp\{pak_name}.tar.gz',f'/tmp/{pak_name}.tar.gz' ,)
        if auxkit:
            self.server.put(fr'D:\tmp\auxkit.tar.gz','/tmp/auxkit.tar.gz' ,)
         
        print('解压文件')
        self.server.run(f"tar  xvf /tmp/src.tar.gz -C {server_path}")
        for pak in package:
            pak_name = pak.replace('/','_')
            self.server.run(f"tar  xvf /tmp/{pak_name}.tar.gz -C {server_path}/src/{pak}")
        if auxkit:
            self.server.run(f"tar  xvf /tmp/auxkit.tar.gz -C {server_path}/script/auxkit")
        
        #if logrotate:
            #self.chmodLogrotateConfig()
    
    
    def createSettings(self, settings):
        self.server.run(f' echo "from . {settings} import *" >> {self.server_path}/src/settings/__init__.py')
    
    def hardReload(self,uwsgi,sudo=None):
        if sudo:
            self.server.run(f'sudo docker restart {self.project_name}')
            self.server.run(f'sudo docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')  
        else:
            self.server.run(f'docker restart {self.project_name}')
            self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    def stop(self,sudo=None):
        if sudo:
            self.server.run(f'sudo docker stop {self.project_name}')
        else:
            self.server.run(f'docker stop {self.project_name}')
            
    def start(self,uwsgi,sudo=None):
        if sudo:
            self.server.run(f'sudo docker start {self.project_name}')
            self.server.run(f'sudo docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
        else:
            self.server.run(f'docker start {self.project_name}')
            self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    def startCelery(self,autoscale='10,3',soft_time_limit=None,sudo=None,worker='worker',queue=None):#
        """
        多台运行时，需要制定Q
        """
        #cmd = f'docker exec -w /pypro/{self.project_name}/src {self.project_name}  /pypro/p3dj11/bin/celery -A settings worker -l info --autoscale={autoscale}  --detach --logfile=../log/celery.log' --pidfile=/var/run/celery/%n.pid
        cmd = f'docker exec -w /pypro/{self.project_name}/src {self.project_name}  /pypro/p3dj11/bin/celery multi start -A settings {worker} -l info  --autoscale={autoscale} --logfile=../log/celery.log --pidfile=/var/run/celery/%n.pid'
        if sudo:
            cmd = 'sudo '+cmd
        if soft_time_limit:
            cmd += f' --soft-time-limit={soft_time_limit}'
        if queue:
            cmd += f' -Q {queue}'
        print(cmd)
        self.server.run(cmd)
    
    def restartCelery(self,autoscale='10,3',soft_time_limit=None,sudo=None,worker="worker",queue=None):#
        """
        """
        cmd = f'docker exec -w /pypro/{self.project_name}/src {self.project_name}  /pypro/p3dj11/bin/celery multi restart  -A settings {worker} -l info  --autoscale={autoscale} --logfile=../log/celery.log --pidfile=/var/run/celery/%n.pid'
        
        if sudo:
            cmd = 'sudo '+cmd
        if soft_time_limit:
            cmd += f' --soft-time-limit={soft_time_limit}'
        if queue:
            cmd += f' -Q {queue}'
        self.server.run(cmd)
    
    def chmodLogrotateConfig(self):
        """
        修改logrotate的权限，否则无法运行。现在移到python manage.py jb_admin.logrotate里面去执行了。所以这个函数不用再调用了。
        """
        cmd = f'sudo docker exec -w /pypro/{self.project_name} {self.project_name}  chmod 600 deploy/logrotate.conf'
        self.server.run(cmd)
        cmd = f'sudo docker exec -w /pypro/{self.project_name} {self.project_name}  chown root deploy/logrotate.conf'
        self.server.run(cmd)
        
    
        