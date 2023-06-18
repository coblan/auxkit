
from invoke import Responder


def exist(server,path):
    output = server.run(f'ls {path}' ,warn=True)
    if 'No such file' in output.stderr:
        return False
    else:
        return True

def remote_copy(src_server,  src_path, target_server,target_path,src_password):
    """在服务器上面用命令直接拷贝"""
    sudopass = Responder(
         pattern=r'password:',
         response=f'{src_password}\n')
    
    print(f'打包{src_path}')
    src_server.run(f'tar -h -zcvf /tmp/transfer/remote_dir.tar.gz {src_path}',hide ='out')
    print(f'下载{item.get("name")}')
    scp_cmd = f'scp {src_server.user}@{src_server.host}:/tmp/transfer/remote_dir.tar.gz /tmp/remote_dir.tar.gz'
    target_server.run(scp_cmd,pty=True, watchers=[sudopass])
    untar = f'tar -zxvf /tmp/remote_dir.tar.gz -C {target_path}'
    target_server.run(untar)
  
def big_remote_copy(src_server,  src_path, target_server,target_path,src_password,exclude=[]):
    """直接在两个远程服务器上面用命令直接拷贝。会对下一级目录分文件夹进行拷贝。适合比较大的文件夹
    exclude：用来排除那些已经拷贝过的目录"""
    with src_server.cd(src_path):
        output= src_server.run('ls -al',hide ='out')
        outls = output.stdout.split('\n')
        outdir =[]
        last_exclude =list(exclude)
        sudopass = Responder(
             pattern=r'password:',
             response=f'{src_password}\n')
        fingerprint = Responder(
            pattern=r'fingerprint',
            response='yes\n'
        )
        
        for item in outls[1:]:
            ls = item.split(' ')
            if ls[-1] not in ['.','..']:
                if ls[-1] in exclude:
                    continue
                if ls[0].startswith('d'):
                    outdir.append({'is_dir':True,'name':ls[-1]})
                elif ls[0].startswith('-'):
                    outdir.append({'is_dir':False,'name':ls[-1]})
        if exist(src_server,'/tmp/transfer'):
            src_server.run('rm -R /tmp/transfer')
        src_server.run('mkdir /tmp/transfer')
        if not exist(target_server,'/tmp/recieve'):
            target_server.run('mkdir /tmp/recieve')
        if not exist(target_server,target_path):
            target_server.run(f'mkdir {target_path}')
        for item in outdir:         
            if(item.get('is_dir')):
                print(f'打包目录{item.get("name")}')
                src_server.run(f'tar -h -zcvf /tmp/transfer/{item.get("name")}.tar.gz {item.get("name")}',hide ='out')
                print(f'下载{item.get("name")}')
                scp_cmd = f'scp {src_server.user}@{src_server.host}:/tmp/transfer/{item.get("name")}.tar.gz /tmp/recieve/{item.get("name")}.tar.gz'
                target_server.run(scp_cmd,pty=True, watchers=[sudopass,fingerprint])
                untar = f'tar -zxvf /tmp/recieve/{item.get("name")}.tar.gz -C {target_path}'
                target_server.run(untar)
            else:
                print(f'下载{item.get("name")}')
                scp_cmd= f'scp {src_server.user}@{src_server.host}:{src_path}/{item.get("name")}  {target_path}/{item.get("name")}'
                target_server.run(scp_cmd,pty=True, watchers=[sudopass,fingerprint])

            last_exclude.append(item.get("name"))
            print(f'已经下载: \n{last_exclude}')

