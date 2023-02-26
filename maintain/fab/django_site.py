from auxkit.maintain.fab.copy import big_remote_copy
import invoke
local = invoke.Context()

class MysqlProcess(object):
    def __init__(self,server,user,password,db_name):
        self.server = server
        self.user = user
        self.password = password
        self.db_name = db_name
    
    def exportDb(self):
        cmd = f'docker exec mysql8 mysqldump --column-statistics=0 -u {self.user} -p{self.password} {self.db_name} >{self.db_name}.sql'
        self.server.run(cmd) 
    
    def copyToLocal(self):
        self.server.get(f'{self.db_name}.sql',fr'd:/tmp/{self.db_name}.sql')
    
    def importToLocal(self,local_db_name,local_container_name='mysql8_1'):
        local.run(fr'docker cp d:/tmp/{self.db_name}.sql {local_container_name}:/home/{self.db_name}.sql')
        cmd = fr'docker exec {local_container_name} /bin/bash -c "mysql --host=localhost --port=3306 -u root -proot53356 {local_db_name}</home/{self.db_name}.sql'
        local.run(cmd)

class DjangoSite(object):
    def __init__(self,server,project_name,server_path=None):
        self.server = server
        self.project_name=project_name
        self.server_path = server_path or f'/pypro/{project_name}'
        #self.uwsgi= uwsgi
        #self.nginx=nginx
    
    def createDocker(self, uwsgi):
        print(f'创建{self.project_name}的docker容器，并且执行')
        self.server.run(f'docker run -itd -v /pypro/{self.project_name}:/pypro/{self.project_name} --name {self.project_name} coblan/py38_sqlserver:v10 /bin/bash'
                        ,pty=True)
        self.server.run(f'docker start {self.project_name}')
        self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    #def createSuperUser(self):
        #self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    def makeNginx(self, nginx,path='/etc/nginx/sites-enabled', sudopassword=''):
        """
        path='/etc/nginx/sites-enabled'  是ubuntu的默认的路径
        path='/etc/nginx/conf.d'   是centos7的默认路径
        """
        print(f'创建{self.project_name}的nginx配置')
        with self.server.cd(path):
            #self.server.run(f'ln -s /pypro/{self.project_name}/deploy/{nginx} {nginx}')
            self.server.run(f'''sudo -S ln -s /pypro/{self.project_name}/deploy/{nginx} {nginx} <<EOF
          {sudopassword}
          <<EOF''')        
                   
            
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
    
    def reload(self):
        with self.server.cd(self.server_path):
            self.server.run(f'touch run/{self.project_name}.reload')
            
    def migrate(self):
        self.server.run(f'sudo docker exec {self.project_name} /pypro/p3dj11/bin/python /pypro/{self.project_name}/src/manage.py migrate') 
        
    def importDb(self):
        pass
    
    def exportDb(self):
        cmd = f'docker exec mysql8 mysqldump --column-statistics=0 -u {user} -p{pswd} {mysqldb} >{mysqldb}.sql'
        self.server.run(cmd)
    
    def createMysql(self):
        pass
    
    def uploadFile(self,local_path, package, auxkit=False):
        """
        package=['src/helpers']
        """
        server_path = self.server_path
        print('git 打包当前分支')
        with local.cd(local_path):
            local.run(r'git archive -o d:\tmp\src.tar.gz HEAD')
        for pak in package:
            with local.cd(fr'{local_path}\src\{pak}'):
                local.run(fr'git archive -o d:\tmp\{pak}.tar.gz HEAD')
        if auxkit:
            with local.cd(fr'{local_path}\script\auxkit'):
                local.run(r'git archive -o d:\tmp\auxkit.tar.gz HEAD')  
                
        print('上传打包文件')
        self.server.put(fr'D:\tmp\src.tar.gz','/tmp/src.tar.gz')
        for pak in package:
            self.server.put(fr'D:\tmp\{pak}.tar.gz',f'/tmp/{pak}.tar.gz' ,)
        if auxkit:
            self.server.put(fr'D:\tmp\auxkit.tar.gz','/tmp/auxkit.tar.gz' ,)
         
        print('解压文件')
        self.server.run(f"tar  xvf /tmp/src.tar.gz -C {server_path}")
        for pak in package:
            self.server.run(f"tar  xvf /tmp/{pak}.tar.gz -C {server_path}/src/{pak}")
        if auxkit:
            self.server.run(f"tar  xvf /tmp/auxkit.tar.gz -C {server_path}/script/auxkit")
    
    
    def createSettings(self, settings):
        self.server.run(f' echo "from . {settings} import *" >> {self.server_path}/src/settings/__init__.py')
    
    def hardReload(self,uwsgi,sudo=None):
        if sudo:
            self.server.run(f'sudo docker restart {self.project_name}')
            self.server.run(f'sudo docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')  
        else:
            self.server.run(f'docker restart {self.project_name}')
            self.server.run(f'docker exec {self.project_name} /pypro/p3dj11/bin/uwsgi /pypro/{self.project_name}/deploy/{uwsgi}')
    
    def startCelery(self,autoscale='10,3',soft_time_limit=None,sudo=None,queue=None):
        """
        """
        cmd = f'docker exec -w /pypro/{self.project_name}/src {self.project_name}  /pypro/p3dj11/bin/celery -A settings worker -l info --autoscale={autoscale}  --detach --logfile=../log/celery.log'
        if sudo:
            cmd = 'sudo '+cmd
        if soft_time_limit:
            cmd += f' --soft-time-limit {soft_time_limit}'
        if queue:
            cmd += f' -Q {queue}'
        self.server.run(cmd)

    
        