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
#4.0更新日志：使用多线程，并行获取验证码与打卡，提高效率
#4.1更新日志：增加了验证码获取超时的异常处理，将信息的记录与获取改至本地
#4.2更新日志：优化了日志记录逻辑，调整了代码结构
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

def get_userinfos():
    '''以列表形式返回用户信息'''
    url = 'https://www.hlamemastar.top/punch/punch.txt'
    response = requests.get(url)
    infos = response.content
    infos = infos.decode('utf-8')
    infos = infos.split("\r\n")
    return infos

def get_saverinfos(savers):
    '''匹配打卡出错的用户，以列表形式返回其相关信息'''
    res = []
    users = get_userinfos()
    for user in users:
        if user.split("  ")[2] in savers:
            res.append(user)
    return res

def detect():
    '''打卡信息检测（尚未打卡：0，打卡成功：1，存在异常：list）'''
    # 获取本地时间（月日）
    date_now = str(time.localtime().tm_mon) + "月" + str(time.localtime().tm_mday) + "日"
    # 以列表形式读取打卡信息
    with open("info_log.txt","r",encoding="utf-8") as f:
        info_logs = f.readlines()
    if info_logs[0] != date_now:
        return 0              #今日尚未打卡
    success_keywords = ["自动打卡已完成","无需重复打卡"]
    res = []                              # 异常日志
    for info_log in info_logs[1:]:        # 第一行固定储存打卡日期
        infos = info_log.split(" ", 2)    # 将信息拆分为昵称与状态
        if infos[1] not in success_keywords:
            res.append(infos[0])
    if len(res)==0:
        return 1              #打卡成功
    else:
        return res            #存在异常

def info_log(msg,mode):
    '''将消息保存至本地待查询,并将信息推送到群里,mode为文件打开模式'''
    if msg !='':
        # 保存至服务器
        with open("info_log.txt",mode,encoding="utf-8") as f:
            f.write(msg)
        # 推送到群里
        robot = qmsg.Robot()
        robot.mail_group(281700803,msg)

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
    # 对打卡状态进行检测，根据结果进行相应操作
    status = detect()
    if status == 1:
        print("今日已打卡！")
        exit()
    elif status == 0:
        print("今日暂未打卡！")
        user_infos = get_userinfos()
    else:
        print("部分打卡异常，实施补救！")
        user_infos = get_saverinfos(status)
    #调用打卡主程序
    validate_list = ["running"]
    #多线程获取验证码
    thread1 = myThread("1", get_validate.get_validate, validate_list)
    thread1.start()
    try:
        msg = punch.main(validate_list,user_infos)
        if status == 0:
            info_log(msg,"w")
        else:
            info_log(msg,"r")
    except Exception as e:
        print(e)
    # 停止子进程
    validate_list[0] = "end"
    
    #附加功能，如显示打卡时间
