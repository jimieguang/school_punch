import requests
import json
import time
from Crypto.Cipher import AES
import base64
# import datetime #获取系统时间
# import random

from get_cookie import get_cookie
#设置请求头，防止被发现
cookie = get_cookie()
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
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42'
    'user-agent':'Mozilla/5.0 (Linux; Android 11; Mi 10 Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4313 MMWEBSDK/20220805 Mobile Safari/537.36 MMWEBID/6691 MicroMessenger/8.0.27.2220(0x28001B59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
    'Cookie':cookie,

}
#设置请求网址
url_login = 'https://stuhealth.jnu.edu.cn/api/user/login'
url_get = 'https://stuhealth.jnu.edu.cn/api/user/stuinfo'
url_punch = 'https://stuhealth.jnu.edu.cn/api/write/main'

def encrypt(password) -> str:
        '''打卡密码加密'''
        # Init
        CRYPTOJSKEY = 'xAt9Ye&SouxCJziN'.encode('utf-8')
        BS = AES.block_size
        def _pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        # Hash
        cipher = AES.new(CRYPTOJSKEY, AES.MODE_CBC, CRYPTOJSKEY)
        enrypted = cipher.encrypt(_pad(password).encode('utf-8'))
        enrypted = base64.b64encode(enrypted).decode('utf-8')
        enrypted = enrypted.replace('/', '_').replace('+', '-').replace('=', '*', 1)
        return enrypted

def login(url_login,payload_login,header):
    '''检查是否已打卡'''
    payload_login = json.dumps(payload_login)
    #post传入的数据是json类型
    #增加了请求超时设定 timeout=2
    info_login = requests.post(url_login, data = payload_login, headers = header,timeout = 2)
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
    try: #捕获secendTable关键词异常以分析原因
        secondTable = {}
        for i in range(1,41):
            if dict_get['data']['secondTable']['other%d'%i] != '':
                secondTable['other%d'%i] = dict_get['data']['secondTable']['other%d'%i]
    except KeyError:
        return info_get
        # 愚蠢的三次虚假体温(暂时不用了)
        # temp_judge = 0
        # if temp_judge == 0:
        #     temp = 36.5
        #     date_now = datetime.datetime.now()
        #     date_yesterday = date_now - datetime.timedelta(days=1)
        #     secondTable['other29'] = temp + 0.1*random.randint(-5,5)
        #     secondTable['other30'] = str(date_now.date())
        #     secondTable['other31'] = temp + 0.1*random.randint(-5,5)
        #     secondTable['other32'] = str(date_yesterday.date())
        #     secondTable['other33'] = temp + 0.1*random.randint(-5,5)
        #     secondTable['other34'] = str(date_yesterday.date())
        #     temp_judge = 1

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


def main(validate_list,user_infos):
    '''主要的执行函数，需要传入验证码与用户信息（列表形式）'''
    # 获取本地时间（月日）
    date_now = str(time.localtime().tm_mon) + "月" + str(time.localtime().tm_mday) + "日"
    msg = date_now + "\n"
    #保存错误日志
    msg_error = ""
    try:
        for user_info in user_infos:
            account = user_info.split()[0]
            password = user_info.split()[1]
            name = user_info.split()[2]
            #设置最大重连次数与初始化（因为时效性，携带着验证码参数进行重连才可以）
            try_num = 0
            try_max_num = 3
            temp = ''
            while try_num < try_max_num and validate_list[0]!="error":
                # 等待selenium初始化
                while validate_list[0]=="waiting":
                    time.sleep(1)
                validate_try_num = 0
                while len(validate_list)<=1 and validate_try_num<10:
                    print("阻塞ing")
                    time.sleep(0.5)
                    validate_try_num += 1
                # 未获取成功验证码则跳至下一用户
                if len(validate_list)<=1:
                    temp = '%s 验证码获取超时！\n'%name
                    msg += temp
                    break
                validate = validate_list.pop()
                password = encrypt(password)
                try:
                    payload_login = {'username': "%s"%account, 'password': "%s"%password,'validate':'%s'%validate}
                    info_login = login(url_login,payload_login,header)
                    if '登录成功，今天未填写' in info_login:
                        info_get = get(url_get,info_login,header)
                        info_punch = punch(url_punch,info_get,header)
                        if '成功' in info_punch:
                            temp = '%s 自动打卡已完成！\n'%name
                            msg += temp
                        else:
                            temp = '%s 出现未知问题，请检查！\n'%name
                            msg += temp
                            msg_error += info_punch
                    elif 'error' in info_login:
                        temp = '%s 账号密码错误，请检查！\n'%name
                        msg += temp
                    elif '登录成功，今天已填写' in info_login:
                        temp = '%s 无需重复打卡！\n'%name
                        msg += temp
                    elif '行为验证码验证失败' in info_login:
                        temp = '%s 行为验证失败！\n'%name
                        msg += temp
                    # 临时处理措施，观察学校服务器后续响应
                    elif '"code":400' in info_login:
                        temp = '%s IP已被封禁！(code:400)\n'%name
                        msg += temp
                    else:
                        temp = "未知返回数据：%s\n"%info_login
                        msg += temp
                    break
                except(requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError) as e:
                    try_num += 1
                    msg_error += '%s 打卡请求超时%d次！\n'%(name, try_num)
                    msg_error += '错误信息为:%s\n'%e
                    if try_num == try_max_num:
                        temp = '%s 自动打卡失败\n'%name
                        msg += temp
            print(temp.rstrip())
    except IndexError:
        pass
    error_log(msg_error,date_now)
    return msg

def error_log(msg,date_now):
    '''将错误信息写入本地文件(追加模式）'''
    if msg !='':
        #添加时间戳
        msg = date_now + "\n" + msg
        # 保存错误日志
        with open("error_log.txt","a",encoding="utf-8") as f:
            f.write(msg) 
