from . mysql_db import MysqlProcess

import invoke
local = invoke.Context()

class PostgreSqlProcess(MysqlProcess):
    def exportDb(self):
        """
        从服务器导出数据库
        """  
        cmd = f'docker exec mypostgre pg_dump {self.db_name} > {self.db_name}.sql'
        self.server.run(cmd,pty=True)  
    
    def importToLocal(self,local_db_name,local_container_name='mypostgre'):
        local.run(fr'docker cp d:/tmp/{self.db_name}.sql {local_container_name}:/home/{self.db_name}.sql')
        cmd = fr'docker exec {local_container_name} psql -d {local_db_name} -f /home/{self.db_name}.sql'
        local.run(cmd)
        
        
              