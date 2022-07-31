from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import time

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
    


