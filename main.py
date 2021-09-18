#2.0更新日志：改为post登录，提高了打卡效率，降低了错误率
#2.1更新日志：增加了post请求超时，将超时的异常数据发送到qq中，方便检查
#2.2更新日志：增加了超时重试功能（暂定为三次），并增加了天气预报功能
#2.3更新日志：修复了打卡性别显示出错的问题
#2.4更新日志：修复了打卡登录出错却显示“已打卡”的问题
#2.5更新日志: 更改了群消息推送,并将报错信息单独推送给群主
#2.6更新日志：改动了部分post内容以模拟提交位置信息
#3.0更新日志：将打卡信息迁移至服务器上，增强可移植性
#3.1更新日志：由于滑块验证码的存在，改进程序以绕过，破解留待日后进行
import requests
import json
import datetime #获取系统时间

#设置请求头，防止被发现
header={
    'authority': 'stuhealth.jnu.edu.cn',
    'method': 'POST',
    'path': '/api/user/login',
    'scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-length': '63',
    'content-type': 'application/json',
    'origin': 'https://stuhealth.jnu.edu.cn',
    'pragma': 'no-cache',
    'referer': 'https://stuhealth.jnu.edu.cn/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42'
}
#设置请求网址
url_login = 'https://stuhealth.jnu.edu.cn/api/user/login'
url_get = 'https://stuhealth.jnu.edu.cn/api/user/stuinfo'
url_punch = 'https://stuhealth.jnu.edu.cn/api/write/main'

def get_userinfos():
    '''以列表形式返回用户信息'''
    #此处改动以暂时性打卡
    url = 'https://www.hlamemastar.top/punch/temp.txt'
    response = requests.get(url)
    infos = response.content
    infos = infos.decode('utf-8')
    infos = infos.split("\r\n")
    return infos


def get(url_get,jnuid,header):
    '''如果今天未打卡，则提取打卡信息'''
    payload_get = {"jnuid":"%s"%jnuid,"idType":"1"}
    # payload_get = json.dumps(payload_get)
    info_get = requests.post(url_get,data = payload_get,headers=header, timeout = 2)
    #关闭请求，释放内存
    info_get.close()
    return info_get.text

def punch(url_punch,info_get,header,jnuid):
    '''进行打卡操作'''
    dict_get = json.loads(info_get)
    #将获取数据中非空字符串提取出来
    secondTable = {}
    for i in range(1,41):
        if dict_get['data']['secondTable']['other%d'%i] != '':
            secondTable['other%d'%i] = dict_get['data']['secondTable']['other%d'%i]
    payload_punch = {
	"mainTable": {
        "passAreaC2":"中国",
        "passAreaC3":"%s"%secondTable['other4'],
        "passAreaC4":"%s"%secondTable['other6'],
        "leaveTransportationOther":"html5",
        "other":"113.269632,23.126325",
		"way2Start": "",
		"language": "cn",
		"declareTime": "%s"%dict_get['data']['declare_time'],
		"personNo": "%s"%dict_get['data']['jnuId'],
		"personName": "%s"%dict_get['data']['xm'],
		"sex": "%s"%dict_get['data']['xbm'],
		"professionName": "%s"%dict_get['data']['zy'],
		"collegeName": "%s"%dict_get['data']['yxsmc'],
		"phoneArea": "%s"%dict_get['data']['mainTable']['phoneArea'],
		"phone": "%s"%dict_get['data']['mainTable']['phone'],
		"assistantName": "%s"%dict_get['data']['mainTable']['assistantName'],
		"assistantNo": "%s"%dict_get['data']['mainTable']['assistantNo'],
		"className": "%s"%dict_get['data']['mainTable']['className'],
		"linkman": "%s"%dict_get['data']['mainTable']['linkman'],
		"linkmanPhoneArea": "%s"%dict_get['data']['mainTable']['linkmanPhoneArea'],
		"linkmanPhone": "%s"%dict_get['data']['mainTable']['linkmanPhone'],
		"personHealth": "%s"%dict_get['data']['mainTable']['personHealth'],
		"temperature": "%s"%dict_get['data']['mainTable']['temperature'],
		"personHealth2": "%s"%dict_get['data']['mainTable']['personHealth2'],
		"schoolC1": "%s"%dict_get['data']['mainTable']['schoolC1'],
		"currentArea": "%s"%dict_get['data']['mainTable']['currentArea'],
		"personC4": "%s"%dict_get['data']['mainTable']['personC4'],
		"otherC4": "%s"%dict_get['data']['mainTable']['otherC4'],
		"isPass14C1": "%s"%dict_get['data']['mainTable']['isPass14C1'],
		"isPass14C2": "%s"%dict_get['data']['mainTable']['isPass14C2'],
		"isPass14C3": "%s"%dict_get['data']['mainTable']['isPass14C3']
	},
	"secondTable": secondTable,
	"jnuid": "%s"%jnuid
    }
    payload_punch = json.dumps(payload_punch)
    info_punch = requests.post(url_punch,data = payload_punch,headers = header, timeout = 2)
    #关闭请求，释放内存
    info_punch.close()
    return info_punch.text


def main():
    '''主要的执行函数'''
    msg = ""
    #保存错误日志
    msg_error = ""
    infos = get_userinfos()
    try:
        for info in infos:
            name = info.split()[0]
            jnuid = info.split()[1]
            #设置最大重连次数与初始化
            try_num = 0
            try_max_num = 3
            while try_num < try_max_num:
                try:
                    info_punch = punch(url_punch,jnuid,header)
                    if '成功' in info_punch:
                        msg += '%s自动打卡已完成！\n'%name
                    else:
                        msg += '%s出现未知问题:%s\n'%(name,info_punch)
                        break
                except(requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout) as e:
                    try_num += 1
                    msg_error += '%s打卡请求超时%d次！\n'%(name, try_num)
                    msg_error += '错误信息为%s\n'%e
                    if try_num == try_max_num:
                        msg += '%s自动打卡失败\n'%name
    except IndexError:
        pass
    msg += get_weather(msg)
    mail_group(msg)
    mail(msg_error)
    return msg


def mail_group(msg):
    '''将消息发送到QQ群'''
    if msg !='':
        qq = '281700803'
        qqtalk = 'https://qmsg.zendee.cn/group/6c34b0bac7951dc116ef0c64730db7fe?msg=%s&qq=%s'%(msg,qq)
        requests.post(qqtalk)

def mail(msg):
    '''将消息发送到群主QQ'''
    if msg !='':
        qq ='1137040634'
        qqtalk = 'https://qmsg.zendee.cn/send/6c34b0bac7951dc116ef0c64730db7fe?msg=%s&qq=%s'%(msg,qq)
        requests.post(qqtalk)

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
    msg = "\n%s天气预报\n温度:%s~%s℃\n天气:%s转%s\n风向:%s%s级\n日出时间:%s\n日落时间:%s"%(time,tempMin,tempMax,textDay,textNight,windDirDay,windScaleDay,sunrise,sunset)
    return msg

def main_handler(event, context):
    '''调用云函数'''
    return main()

if __name__ == '__main__':
    #调用打卡主程序
    msg = main()
    #附加功能，如显示打卡时间
    print(msg)
    print('\n')
    #打包成exe时需取消注释
    input('按enter键退出程序')