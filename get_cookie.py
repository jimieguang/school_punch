import requests
import re

def get_cookie():
    '''获取狗学校的验证cookie'''
    url_1 = "https://stuhealth.jnu.edu.cn/"
    header={
        'authority':'stuhealth.jnu.edu.cn',
        'method':'GET',
        'path':'/jnu_authentication/public/redirect',
        'scheme':'https',
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'sec-ch-ua':'"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'none',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
    }
    response = requests.get(url_1,headers=header,allow_redirects=False)
    url_2 = response.headers['Location']
    response = requests.get(url_2,headers=header,allow_redirects=False)
    find_verifyID = re.compile(r'verifyID%3D(.*?)&')
    verifyID = re.findall(find_verifyID,response.text)[0]
    url_3 = f"https://open.weixin.qq.com/connect/qrconnect?appid=wxd029a39585c4f410&redirect_uri=https%3A%2F%2Fauth7.jnu.edu.cn%2Fwechat_auth%2Fwechat%2FwechatScanAsync%3FverifyID%3D{verifyID}&response_type=code&scope=snsapi_login"
    response = requests.get(url_3,headers=header,allow_redirects=False)
    url_4 = f"https://auth7.jnu.edu.cn/wechat_auth/wechat/wechatScanAsync?verifyID={verifyID}&code=071GSR100Zi3GO1Zn2300fcQD40GSR1p&state="
    response = requests.get(url_4,headers=header,allow_redirects=False)
    url_5 = response.headers['Location']
    response = requests.get(url_5,headers=header,allow_redirects=False)
    cookie = response.headers['Set-Cookie']
    return cookie

if __name__ == '__main__':
    get_cookie()