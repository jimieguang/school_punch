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

# 引入第三方算法判断拼图交换位置
import gaps_demo

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
        self.opts.set_headless()

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

    def refresh(self):
        # 刷新当前界面
        self.driver.refresh()

    def stop(self):
        # 关闭浏览器，停止程序
        self.driver.close()

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

    def repuzzle(self,res):
        '''还原拼图'''
        element_source = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, f'yidun_inference--{res[0]}')))
        while "src=" not in element_source.get_attribute('innerHTML'):
            time.sleep(0.5)
        source = element_source.find_element_by_class_name('yidun_inference__border')
        element_target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, f'yidun_inference--{res[1]}')))
        target = element_target.find_element_by_class_name('yidun_inference__border')
        ActionChains(self.driver).drag_and_drop(source, target).perform()
        validate_element = self.driver.find_element_by_id('validate')
        time.sleep(0.5)
        validate = validate_element.get_attribute('outerHTML')
        validate = re.findall(re.compile('>(.*?)</div'),validate)[0]
        return validate

def get_validate(validate_list):
    cs = CrackSlider()
    cs.open()
    print("waiting")
    # 等待第一张图片出现
    cs.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
    print("初始化完毕")
    validate_list[0]="running"
    num = 0
    max_num = 100
    while num<max_num and validate_list[0]!="end":
        num += 1
        try:
            cs.get_pic()
            # 获取需要交换的拼图位置
            path = os.getcwd() + "/temp/target.jpg"
            res = gaps_demo.main(path)
            if len(res) != 0:
                validate = cs.repuzzle(res)
            if validate!="":
                validate_list.append(validate)
                print(f"validate_list_length:{len(validate_list)}")
                cs.refresh()
            else:
                print("wrong")
        except Exception as e:
            print("存在错误，已重试：%s"%e)
            cs.refresh()
            continue
    cs.stop()

if __name__ == '__main__':
    import threading
    class myThread (threading.Thread):   #继承父类threading.Thread
        """多线程类"""
        def __init__(self, threadID, function_name,list):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.func = function_name
            self.list = list
        def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
            print("Starting " + self.threadID)
            self.func(self.list)
    validate_list = ["running"]
    thread1 = myThread("1", get_validate, validate_list)
    thread1.start()
    input("停止请键入enter:")
    validate_list[0] = "end"
