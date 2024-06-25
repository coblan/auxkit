
import invoke
local = invoke.Context()


class MysqlProcess(object):
    def __init__(self,server,user,password,db_name):
        self.server = server
        self.user = user
        self.password = password
        self.db_name = db_name
        
    
    def rawExportDb(self):
        """
        从服务器导出数据库
        """
        cmd = f'mysqldump --column-statistics=0 -u {self.user} -p{self.password} {self.db_name} >{self.db_name}.sql'
        self.server.run(cmd) 
    
    def exportDb(self):
        """
        从服务器导出数据库
        """
        cmd = f'docker exec mysql8 mysqldump --column-statistics=0 -u {self.user} -p{self.password} {self.db_name} >{self.db_name}.sql'
        self.server.run(cmd) 
    
    def localExport(self,db_name,user='root',password='root53356',local_container_name='mysql8_1'):
        """从本地导出数据库"""
        cmd = f'docker exec {local_container_name} /bin/bash -c "mysqldump --column-statistics=0 -u {user} -p{password} {db_name} >/tmp/{db_name}.sql"'
        local.run(cmd) 
        local.run(fr'docker cp {local_container_name}:/tmp/{db_name}.sql d:/tmp/{db_name}.sql ')
    
    def copyToLocal(self):
        print(fr'拷贝文件到d:/tmp/{self.db_name}.sql')
        self.server.get(f'{self.db_name}.sql',fr'd:/tmp/{self.db_name}.sql')
    
    def importToLocal(self,local_db_name,local_container_name='mysql8_1'):
        local.run(fr'docker cp d:/tmp/{self.db_name}.sql {local_container_name}:/home/{self.db_name}.sql')
        cmd = fr'docker exec {local_container_name} /bin/bash -c "mysql --host=localhost --port=3306 -u root -proot53356 {local_db_name}</home/{self.db_name}.sql"'
        local.run(cmd)
        
    def importToServer(self,container='mysql8',local_path=None):
        if local_path:
            self.server.put(local_path,fr'/tmp/{self.db_name}.sql')
        else:
            self.server.put(fr'd:/tmp/{self.db_name}.sql',fr'/tmp/{self.db_name}.sql')
        self.server.run(fr'docker cp /tmp/{self.db_name}.sql {container}:/tmp/{self.db_name}.sql')
        cmd = fr'docker exec {container} /bin/bash -c "mysql --host=localhost --port=3306 -u root -proot53356 {self.db_name}</tmp/{self.db_name}.sql"'
        self.server.run(cmd)  
    
    def runSql(self,sql_cmd,container='mysql8'):
        """
        db.runSql('select now()')
        db.runSql('DROP DATABASE usa_user')
        db.runSql('CREATE DATABASE usa_user  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci;')
        """
        cmd = fr'docker exec {container} /bin/bash -c "mysql --host=localhost --port=3306 -u root -proot53356 -e \"{sql_cmd}\" "'
        self.server.run(cmd) 
        
    def localRunSql(self,sql_cmd,local_container_name='mysql8_1'):
        """
        db.localRunSql('select now()')
        db.localRunSql('DROP DATABASE usa_user')
        db.localRunSql('CREATE DATABASE usa_user  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci;')
        """
        cmd = fr'docker exec {local_container_name} /bin/bash -c "mysql --host=localhost --port=3306 -u root -proot53356 -e \"{sql_cmd}\" "'
        local.run(cmd)        