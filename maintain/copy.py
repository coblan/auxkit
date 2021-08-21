import os
import zipfile
import invoke
import shutil
import filecmp

local = invoke.Context()
base_dir = os.path.dirname(__file__)

def git_copy(src,dst,temp_dir=base_dir):
    tmp_fl_path = os.path.join(base_dir,'git_copy_tmp.zip')
    with local.cd(src):
        local.run(r'git archive -o %(tmp_fl_path)s HEAD'%locals())
    
    with zipfile.ZipFile(tmp_fl_path, 'r') as zip_ref:
        zip_ref.extractall(dst)


def copy(src_root,target_root,filters=[],overwrite="always"):
    """
    @overwrite:"always","check_updatetime","no_overwrite"
    """
    #src_root = r'D:\work\H5\dist'
    #target_root = r'D:\work\Release\Live-Binary\H5\dist'

    for root, dirs, files in os.walk(src_root):
        rel_path = os.path.relpath(root, src_root)
        for fl in files:
            check_passed = True
            for item in filters:
                if not item.check_file(root,fl):
                    check_passed= False
                    break
            if check_passed:
                fl_path = os.path.join(root, fl)
                try:
                    os.makedirs(os.path.join(target_root, rel_path))
                except Exception:
                    pass
                target_path = os.path.join(target_root, rel_path, fl)
                if overwrite =='always':
                    shutil.copy2(fl_path, target_path)
                    print(target_path)
                elif not os.path.exists(target_path):
                    shutil.copy2(fl_path, target_path)
                    print(target_path) 
                elif overwrite =='no_overwrite':
                    pass
                elif overwrite =='check_updatetime':
                    if os.path.getmtime(fl_path) > os.path.getmtime(target_path):
                        shutil.copy2(fl_path, target_path)
                        print(target_path)                         
        
        # 去掉不要的dir
        left_dirs = []
        for d_item in dirs:
            check_passed = True
            for item in filters:
                if not item.check_dir(root,d_item):
                    check_passed= False
                    break
            if check_passed:
                left_dirs.append(d_item)
        dirs[:] = left_dirs #[d for d in dirs if left_dirs(d)]
        for d in dirs:
            target_dir_path = os.path.join(target_root, rel_path, d)
            if not os.path.exists(target_dir_path):
                # 文件夹也可以 shutil.copy2 拷贝，但是考虑到文件夹对文件没影响，所以暂时不管这里。
                os.makedirs(target_dir_path)
                print(target_dir_path)

class CopyDiff(object):
    def __init__(self, src_dir,cache_dir,dst_dir,filters=[]):
        self.src_dir=src_dir
        self.cache_dir = cache_dir
        self.dst_dir = dst_dir
        self.filters= filters
    
    def check_dif(self,relative_path):
        src_fl = os.path.join(self.src_dir,relative_path)
        cache_fl = os.path.join(self.cache_dir,relative_path)
        if not os.path.exists(cache_fl):
            return True
        if not filecmp.cmp(src_fl,cache_fl):
            return True
    
    def update_cache(self):
        copy(self.dst_dir, self.cache_dir)
    
    def clear_cache(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
    
    def copy(self):
        if os.path.exists(self.dst_dir):
            shutil.rmtree(self.dst_dir,ignore_errors=True)
        try:
            os.makedirs(self.dst_dir)
            os.makedirs(self.cache_dir)
        except :
            pass
        
        for root, dirs, files in os.walk(self.src_dir):
            rel_path = os.path.relpath(root, self.src_dir)
            for fl in files:
                check_passed = True
                for item in self.filters:
                    if not item.check_file(root,fl):
                        check_passed= False
                        break
                fl_path = os.path.join(root, fl)
                relative_path = os.path.relpath(fl_path,self.src_dir)
                if check_passed and self.check_dif(relative_path):
                    try:
                        os.makedirs(os.path.join(self.dst_dir, os.path.dirname(relative_path) ))
                    except Exception:
                        pass
                    target_path = os.path.join(self.dst_dir,relative_path)
                    shutil.copy(fl_path, target_path)
                    print(target_path)
        
            # 去掉不要的dir
            # 空文件夹无法比较新旧，所以去掉
            #left_dirs = []
            #for d_item in dirs:
                #check_passed = True
                #for item in self.filters:
                    #if not item.check_dir(root,d_item):
                        #check_passed= False
                        #break
                #if check_passed:
                    #left_dirs.append(d_item)
            #dirs[:] = left_dirs #[d for d in dirs if left_dirs(d)]
            #for d in dirs:
                #target_dir_path = os.path.join(self.dst_dir, rel_path, d)
                #if not os.path.exists(target_dir_path):
                    #os.makedirs(target_dir_path)
                    #print(target_dir_path)
        
        self.update_cache()
                

class PythonFilter(object):
    def check_file(self,path,name):
        if name.endswith('.pyc'):
            return False
        if name.startswith('.'):
            return False
        else:
            return True
    
    def check_dir(self,path,name):
        if name == '__pycache__':
            return False
        return True

class JsFilter(object):
    def check_file(self,path,name):
        return True
    
    def check_dir(self,path,name):
        if name.startswith('.'):
            return False
        elif name in ['node_modules']:
            return False
        else:
            return True