#2.0更新日志：改为post登录，提高了打卡效率，降低了错误率
#2.1更新日志：增加了post请求超时，将超时的异常数据发送到qq中，方便检查
#2.2更新日志：增加了超时重试功能（暂定为三次），并增加了天气预报功能
#2.3更新日志：修复了打卡性别显示出错的问题
#2.4更新日志：修复了打卡登录出错却显示“已打卡”的问题
#2.5更新日志: 更改了群消息推送,并将报错信息单独推送给群主
#2.6更新日志：改动了部分post内容以模拟提交位置信息
#3.0更新日志：将用户信息迁移至服务器上，增强可移植性
#3.2更新日志：3.1版本废弃，未考虑jnuid是动态生成的，本版本使用selenium获取validate再进行打卡（大佬的帮忙~）
#3.3更新日志：改进了缺口匹配方式，牺牲速度以保证准确性，同时提高了效率
#3.4更新日志：优化了匹配算法，速度提升至0.3秒内处理完毕
#3.5更新日志：将打卡信息提交到服务器，便于机器人推送与查询，将天气预报模块独立，从主函数中删除
#3.6更新日志：增加了提交错误日志的功能，增加检测今日是否已打卡的功能（若已打卡则直接退出程序）
#3.7更新日志：增加了推送功能，自己搭建了qq机器人，使用该功能时向服务器发出请求，发送消息给指定人/群
#3.8更新日志：修正了定位出错的问题
#3.9更新日志：修改了获取验证码和进度输出的部分逻辑，留出空间后续实现“打卡补救”措施
#3.10更新日志：修复了新加用户不显示的问题，提高了获取验证码的成功率（增加伪装js）
#3.11更新日志：增加了三次虚假体温
#4.0更新日志：使用多线程，同时进行验证码的获取与打卡的进行，提高效率
import requests
import threading
import time


import get_validate
import qmsg
import punch

def get_weather(msg):
    '''获取天气信息'''
    params = 'key=c0a288bbaa1f4ab3a64dfd6213d24074&location=101280704'
    url = 'https://devapi.qweather.com/v7/weather/3d?%s'%params
    info = requests.get(url)
    #把双引号转化为单引号才可以变成字典型数据
    info = eval(info.text)
    info = dict(info)
    time = info['daily'][0]['fxDate']
    tempMin = info['daily'][0]['tempMin']
    tempMax = info['daily'][0]['tempMax']
    textDay = info['daily'][0]['textDay']
    textNight = info['daily'][0]['textNight']
    windDirDay = info['daily'][0]['windDirDay']
    windScaleDay = info['daily'][0]['windScaleDay']
    sunrise = info['daily'][0]['sunrise']
    sunset = info['daily'][0]['sunset']
    #对天气信息进行处理
    if textDay == textNight:
        weather_info = textDay
    else:
        weather_info =textDay + "转" + textNight
    msg += f"\n{time}天气预报\n温度:{tempMin}~{tempMax}℃\n天气:{weather_info}\n风向:{windDirDay+windScaleDay}级\n日出时间:{sunrise}\n日落时间:{sunset}"
    return msg

def detect():
    '''检测今日是否打卡（返回值是布尔型）'''
    url = 'https://www.hlamemastar.top/qqrobot/punch_info.txt'
    response = requests.get(url)
    res = response.content.decode('utf-8')
    if "今日暂未打卡，请耐心等待" in res: 
        return True
    else:
        return False

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

if __name__ == '__main__':
    # 如果今日已打卡，直接退出该程序
    if not detect():
        print('今日已打卡')
        exit()
    #调用打卡主程序
    validate_list = []
    #多线程获取验证码
    thread1 = myThread("1", get_validate.get_validate, validate_list)
    thread1.start()
    try:
        msg = punch.main(validate_list)
    except Exception as e:
        print(e)
    #附加功能，如显示打卡时间
