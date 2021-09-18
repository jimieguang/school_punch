from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from io import BytesIO
import time, requests
import re
# from webdriver_manager.chrome import ChromeDriverManager

# 引入自定义函数用于判断滑动距离
from find import *

class CrackSlider():
    """
    通过浏览器截图，识别验证码中缺口位置，获取需要滑动距离，破解滑动验证码
    """
    def __init__(self):
        self.url = './code.html'
        # 声明一个谷歌配置对象
        self.opts = webdriver.ChromeOptions()    
        # 设置成无头
        self.opts.add_argument('--headless')
        self.opts.add_argument('--disable-gpu')
        # 设置开发者模式，防止被检测出来 ↓
        self.opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 隐藏日志信息
        self.opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        # self.driver = webdriver.Chrome(ChromeDriverManager().install(),options = self.opts)  #给用户安装webdriver
        self.driver = webdriver.Chrome(options = self.opts)
        self.wait = WebDriverWait(self.driver, 20)

    def open(self):
        self.driver.get(self.url)

    def get_pic(self):
        time.sleep(2)
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
        template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw')))
        target_link = target.get_attribute('src')
        template_link = template.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        target_img.save('target.jpg')
        template_img.save('template.png')



    def crack_slider(self,distance):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=distance+8, yoffset=0).perform()
        ActionChains(self.driver).release().perform()
        
        validate_element = self.driver.find_element_by_id('validate')
        time.sleep(0.5)
        validate = validate_element.get_attribute('outerHTML')
        self.driver.close()
        validate = re.findall(re.compile('>(.*?)</div'),validate)[0]
        return validate
            


def get_validate():
    validate = ''
    while validate == '':
        cs = CrackSlider()
        cs.open()
        cs.get_pic()

        # 比对五个已知图片，用于确定缺口图片为哪副
        for i in range(1,6):
            fileorder = find_pic(i)
            if fileorder != 0:
                break
        distance = find_distance(fileorder)
        validate = cs.crack_slider(distance)
        return validate

if __name__ == '__main__':
    validate = get_validate()
    print(validate)