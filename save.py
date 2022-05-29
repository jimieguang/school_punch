import requests
import json
import datetime #获取系统时间


import get_validate
import qmsg

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
    url = 'https://www.hlamemastar.top/punch/punch.txt'
    response = requests.get(url)
    infos = response.content
    infos = infos.decode('utf-8')
    infos = infos.split("\r\n")
    return infos

def login(url_login,payload_login,header):
    '''检查是否已打卡'''
    payload_login = json.dumps(payload_login)
    #post传入的数据是json类型
    #增加了请求超时设定 timeout=2
    info_login = requests.post(url_login, data = payload_login, headers = header,timeout = 5)
    #关闭请求，释放内存
    info_login.close()
    return info_login.text

def get(url_get,info_login,header):
    '''如果今天未打卡，则提取打卡信息'''
    dict_login = json.loads(info_login)
    global jnuid
    jnuid = dict_login['data']['jnuid']
    idtype = dict_login['data']['idtype']
    payload_get = {"jnuid":"%s"%jnuid,"idType":"%s"%idtype}
    payload_get = json.dumps(payload_get)
    info_get = requests.post(url_get,data = payload_get,headers=header, timeout = 2)
    #关闭请求，释放内存
    info_get.close()
    return info_get.text

def punch(url_punch,info_get,header):
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
        "other":"%s"%dict_get['data']['mainTable']['other'],
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


def main(infos,validate=''):
    '''主要的执行函数'''
    msg = ""
    #保存错误日志
    msg_error = ""
    try:
        for info in infos:
            account = info.split()[0]
            password = info.split()[1]
            name = info.split()[2]
            #设置最大重连次数与初始化（因为时效性，携带着验证码参数进行重连才可以）
            try_num = 0
            try_max_num = 3
            while try_num < try_max_num:
                try:
                    #获取验证码参数
                    if validate=="":
                        validate = get_validate.get_validate()
                    payload_login = {'username': "%s"%account, 'password': "%s"%password,'validate':'%s'%validate}
                    info_login = login(url_login,payload_login,header)
                    if '登录成功，今天未填写' in info_login:
                        info_get = get(url_get,info_login,header)
                        info_punch = punch(url_punch,info_get,header)
                        if '成功' in info_punch:
                            msg += '%s自动打卡已完成！\n'%name
                        else:
                            msg += '%s出现未知问题，请检查！\n'%name
                    elif 'error' in info_login:
                        msg += '%s账号密码错误，请检查！\n'%name
                    elif '登录成功，今天已填写' in info_login:
                        msg += '%s无需重复打卡！\n'%name
                    else:
                        msg += "未知返回数据：%s\n"%info_login
                    break
                except(requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout) as e:
                    try_num += 1
                    msg_error += '%s打卡请求超时%d次！\n'%(name, try_num)
                    msg_error += '错误信息为%s\n'%e
                    if try_num == try_max_num:
                        msg += '%s自动打卡失败\n'%name
            print('请查看%s的打卡信息'%name)
    except IndexError:
        pass
    mail_web(msg)
    mail(msg_error)
    return msg


def mail_web(msg):
    '''将信息推送到群里'''
    if msg !='':
        # 推送到群里
        robot = qmsg.Robot()
        robot.mail_group(281700803,msg)

def mail(msg):
    '''将消息发送到群主QQ(使用qmsg),并将错误信息写入服务器'''
    if msg !='':
        # 发送qq
        robot = qmsg.Robot()
        robot.mail_private(1137040634,msg)
        # 写入服务器
        url = 'https://www.hlamemastar.top/qqrobot/punch_error.php'
        payload = {'action':'write','infos':msg}
        requests.post(url,data=payload)

if __name__ == '__main__':
    # 补救名单
    infos = get_userinfos()

    save_list = ["林饱饱","耶","cn","JNU气人","LLLLLLL","飞飞鱼","我是熊猫"]
    #调用打卡主程序
    punch_infos = []
    for info in infos:
        if info == "":
            continue
        if info.split("  ")[2] in save_list:
            punch_infos.append(info)
    try:
        msg = main(punch_infos)
    except Exception as e:
        print(e)
    #附加功能，如显示打卡时间
    print(msg)
    print('\n')
    #打包成exe时需取消注释
    input('按enter键退出程序')