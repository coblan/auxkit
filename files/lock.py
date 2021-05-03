import os
import time
import errno
import threading
from pathlib import Path
import logging
general_log = logging.getLogger('general_log')

class FileLockException(Exception):
    pass

class FileLock(object):
    """ A file locking mechanism that has context-manager support so 
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """

    def __init__(self, file_name, timeout=10, delay=.5):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        if timeout is not None and delay is None:
            raise ValueError("If timeout is not None, then delay must not be None.")
        self.is_locked = False
        self.lockfile = os.path.join(os.getcwd(), "%s.lock" % file_name)
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay


    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws 
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                self.is_locked = True #moved to ensure tag only when locked
                self.t = threading.Thread(target=self.beatTouch,args=() )
                self.t.start()
                break;
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if self.timeout is None:
                    raise FileLockException("Could not acquire lock on {}".format(self.file_name))
                if self.timeout == -1:
                    pass
                elif (time.time() - start_time) >= self.timeout:
                    raise FileLockException("Timeout occured.")
                try:
                    self.checkTime()
                except Exception:
                    # 某时self.lockfile被另外进程删除，运行到这里刚好文件已经不存在了
                    pass
                time.sleep(self.delay)
#        self.is_locked = True
    
    def checkTime(self):
        tm = os.path.getmtime(self.lockfile)
        if time.time() - tm > 5:
            os.remove(self.lockfile)
            general_log.debug('remove Lockfile %s'%self.lockfile )
            
        
    def beatTouch(self):
        while self.is_locked:
            #os.utime(self.lockfile)
            Path(self.lockfile).touch()
            #general_log.debug('beat touch Lockfile %s'%self.lockfile )
            time.sleep(0.5)
    
        
    def release(self):
        """ Get rid of the lock by deleting the lockfile. 
            When working in a `with` statement, this gets automatically 
            called at the end.
        """
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False


    def __enter__(self):
        """ Activated when used in the with statement. 
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self


    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()


    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()
        
        
"""
#use as:
from filelock import FileLock
with FileLock("myfile.txt"):
    # work with the file as it is now locked
    print("Lock acquired.")
"""
