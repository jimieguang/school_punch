from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from io import BytesIO
import time, requests
import re


import os

# 引入自定义函数用于判断滑动距离
from find import *

class CrackSlider():
    """
    通过浏览器截图，识别验证码中缺口位置，获取需要滑动距离，破解滑动验证码
    """
    def __init__(self):
        self.url = os.getcwd()+'\\code.html'
        # 声明一个火狐配置对象
        # self.opts = webdriver.ChromeOptions()    
        self.opts = webdriver.FirefoxOptions()
        # 设置成无头
        # self.opts.set_headless()

        self.driver = webdriver.Firefox(options = self.opts)
        self.wait = WebDriverWait(self.driver, 20)
        # 伪造浏览器指纹，防止被检测出(参考资料：https://jishuin.proginn.com/p/763bfbd33b73)
        # with open('./stealth.min.js') as f:
        #     js = f.read()
        # self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        # "source": js
        # })

    def open(self):
        self.driver.get(self.url)

    def get_pic(self):
        # 注释掉了无意义的图片获取（即template）
        # 加入了对获取空url（None）的处理
        time.sleep(0.5)
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
        target_link = target.get_attribute('src')
        while target_link==None:
            time.sleep(0.5)
            target_link = target.get_attribute('src')
        # print(target_link)
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        target_img.save('./temp/target.jpg')

    def crack_slider(self,distance):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        # time.sleep(2)
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=distance+8, yoffset=0).perform()
        ActionChains(self.driver).release().perform()
        
        validate_element = self.driver.find_element_by_id('validate')
        time.sleep(0.5)
        validate = validate_element.get_attribute('outerHTML')
        self.driver.close()
        validate = re.findall(re.compile('>(.*?)</div'),validate)[0]
        return validate

def get_validate(max_num):
    validate = ''
    num = 0
    while validate == '' and num <= max_num:
        num += 1
        cs = CrackSlider()
        cs.open()
        try:
            cs.get_pic()
            # 比对五个已知图片，用于确定缺口图片为哪副
            for i in range(1,6):
                fileorder = find_pic(i)
                if fileorder != 0:
                    break
            distance = find_distance(fileorder)
            if distance != 0:
                validate = cs.crack_slider(distance)
        except Exception as e:
            print("获取校验码错误，已重试：%s"%e)
            continue
            
    return validate

if __name__ == '__main__':
    start = time.time()
    validate = get_validate(3)
    print(validate)
    end = time.time()
    print("time: %f"%(end-start))
