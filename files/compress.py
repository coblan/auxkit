import os, tarfile
import zipfile

#一次性打包整个根目录。空子目录会被打包。
#如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

#逐个添加文件打包，未打包空子目录。可过滤文件。
#如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz_one_by_one(output_filename, source_dir): 
    tar = tarfile.open(output_filename,"w:gz")
    for root,dir,files in os.walk(source_dir):
        for file in files:
            pathfile = os.path.join(root, file)
            tar.add(pathfile)
    tar.close()

def untar(fname, dirs):
    """
    解压tar.gz文件
    :param fname: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """
    try:
        t = tarfile.open(fname)
        t.extractall(path = dirs)
        return True
    except Exception as e:
        print(e)
        return False

def unzip(src,dst):
    zFile = zipfile.ZipFile(src, "r")
    for fileM in zFile.namelist(): 
        zFile.extract(fileM, dst)
    zFile.close()  

#def zipdir(src,dst):
    #"""
    #zipdir(r'd:\tmp\shark_backend', r'd:\tmp\shark_backend.zip')
    #"""
    #f = zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED)
    #for dirpath, dirnames, filenames in os.walk(src):
        #for filename in filenames:
            #f.write(os.path.join(dirpath,filename))
    #f.close()    

def zipdir(to_zip,save_zip_name):#save_zip_name是带目录的，也可以不带就是当前目录
#1.先判断输出save_zip_name的上级是否存在(判断绝对目录)，否则创建目录
    save_zip_dir=os.path.split(os.path.abspath(save_zip_name))[0]#save_zip_name的上级目录
    print(save_zip_dir)
    if not os.path.exists(save_zip_dir):
        os.makedirs(save_zip_dir)
        print('创建新目录%s'%save_zip_dir)
    f = zipfile.ZipFile(os.path.abspath(save_zip_name),'w',zipfile.ZIP_DEFLATED)
# 2.判断要被压缩的to_zip是否目录还是文件，是目录就遍历操作，是文件直接压缩
    if not os.path.isdir(os.path.abspath(to_zip)):#如果不是目录,那就是文件
        if os.path.exists(os.path.abspath(to_zip)):#判断文件是否存在
            f.write(to_zip)
            f.close()
            print('%s压缩为%s' % (to_zip, save_zip_name))
        else:
            print ('%s文件不存在'%os.path.abspath(to_zip))
    else:
        if os.path.exists(os.path.abspath(to_zip)):#判断目录是否存在，遍历目录
            zipList = []
            for dir,subdirs,files in os.walk(to_zip):#遍历目录，加入列表
                for fileItem in files:
                    zipList.append(os.path.join(dir,fileItem))
                    # print('a',zipList[-1])
                for dirItem in subdirs:
                    zipList.append(os.path.join(dir,dirItem))
                    # print('b',zipList[-1])
            #读取列表压缩目录和文件
            for i in zipList:
                f.write(i,i.replace(to_zip,''))#replace是减少压缩文件的一层目录，即压缩文件不包括to_zip这个目录
                # print('%s压缩到%s'%(i,save_zip_name))
            f.close()
            print('%s压缩为%s' % (to_zip, save_zip_name))
        else:
            print('%s文件夹不存在' % os.path.abspath(to_zip))
