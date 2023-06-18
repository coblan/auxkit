from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import time
import requests
import hashlib
import os
import shutil

def switch_to_title(driver,title):
    findList=[]
    
    for item in driver.window_handles:
        driver.switch_to.window(item)
        if title in driver.title:
            findList.append(item)
    if len(findList)==1:
        driver.switch_to.window(findList[0])
    elif len(findList)>1:
        raise UserWarning('%s multiple window found'%title)
    else:
        raise UserWarning('%s window not found'%title)

def visible(driver,selector,timeout=10):
    #ls = driver.find_elements_by_css_selector(selector)
    #cout = 0
    #while not ls:
        #time.sleep(1)
        #cout += 1
        #ls = driver.find_elements_by_css_selector(selector)
        #if cout > timeout:
            #raise UserWarning('超时')

    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    ) 

def wait_click(driver,selector=None,element=None,timeout=10,):
    if element:
        try:
            element.click()
        except Exception  as e:
            if timeout < 0:
                raise UserWarning('等待超时')
            else:
                time.sleep(0.8)
                wait_click(driver,element=element,timeout = timeout-0.8)

def waite_clickable(driver,selector=None,timeout=10,):
    #if selector:
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    ) 
    #elif element:
        ##element = WebDriverWait(driver, timeout).until(
            ##EC.element_to_be_clickable((By.ID, element.id))
        ##)         
        #count = 0
        #if element.is_displayed() and element.is_enabled():
            #return True
        #else:
            #time.sleep(0.8)
            #count += 0.8
            #if count > timeout:
                #raise UserWarning('超时')
    
#def wn_inputable(driver,selector,timeout=10):
    #element = WebDriverWait(driver, timeout).until(
        #EC.el((By.CSS_SELECTOR, selector))
    #)   

def hide(driver,selector,timeout=60*5):
    element = WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
        
    )  

def inputText(driver,selector,text):
    inputele = driver.find_element(By.CSS_SELECTOR,selector)
    if not inputele.get_property('disabled'):
        #inputele.clear()
        clear_input(inputele)
        inputele.send_keys(str(text))
    else:
        print('selector =%s input has disabled when input "%s"'%(selector,text))

def inputTextById(driver,ID,text):
    inputele = driver.find_element_by_id(ID)
    if not inputele.get_property('disabled'):
        clear_input(inputele)
        inputele.send_keys(str(text) )
    else:
        print('ID=%s input has disabled when input "%s"'%(ID,text))

def click(driver,selector=None,eid=None):
    if eid:
        btn = driver.find_element_by_id(eid)
    else:
        btn = driver.find_element(By.CSS_SELECTOR,selector)
    btn.click()

def find_one_by_text(driver,selector,text):
    for ii in driver.find_elements(By.CSS_SELECTOR,selector):
        if text in ii.text:
            return ii

def clear_input(ele):
    ele.send_keys(Keys.CONTROL + "a")
    ele.send_keys(Keys.DELETE)

class MyDriver(object):
    def __init__(self,driver):
        self.driver = driver
        self.has_pre_ex = False
    
    def initJs(self):
        from .selenium_inject_js import js
        self.driver.execute_script(js)
        self.has_pre_ex = True
    
    def downLoadDomSnapshot(self,selector,filename):
        if not self.has_pre_ex:
            self.initJs()
            
        self.driver.execute_async_script(r''' const callback = arguments[arguments.length - 1];
            pre_ex.load_js("https://html2canvas.hertzen.com/dist/html2canvas.min.js").then(()=>{
                callback()
            })
        ''' )
        self.driver.execute_async_script( fr'''
        const callback = arguments[arguments.length - 1];
        html2canvas(document.querySelector("{selector}") ,{{
                                          allowTaint: true,
                                              useCORS: true                                          
                                          }}).then( canvas => {{
            pre_ex.downLoadCanvas(canvas,'{filename}')
            callback()
        }} )''' )    
    
    def findElements(self,selector):
        return self.driver.find_elements(By.CSS_SELECTOR,value=selector)
    

class MediaAdapter(object):
    def __init__(self,path) :
        self.path = path
        try:
            os.mkdir(self.path)
        except:
            pass
    
    def getFilePath(self,url,suffix):
        hl = hashlib.md5()
        hl.update(url.encode(encoding='utf-8'))
        return f'{hl.hexdigest()}.{suffix}'
    
    def saveImage(self,url):
        rt = requests.get(url,stream=True)
        if rt.status_code == 200:
            suffix = rt.headers.get('Content-Type').split('/')[1]
            path = os.path.join(self.path,self.getFilePath(url,suffix))            
            with open(path, 'wb') as f:
                rt.raw.decode_content = True
                shutil.copyfileobj(rt.raw, f) 
                print('Image Downloaded Successfully') 
                
    def adaptMediaPath(self,url):
        pass
        
    
    
        


