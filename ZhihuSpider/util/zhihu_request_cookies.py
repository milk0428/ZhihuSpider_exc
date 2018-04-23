# _*_ coding: utf-8 _*_

#注意requests需要先pip install
import requests

#注意python3中的包叫cookielib，python2中叫http.cookiejar，这里用异常处理的方式使得python2和3兼容
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

#引入session以保存登录状态
session = requests.session()
#用这个包之后才能使用session.cookies.save()函数保存cookies文件到本地，保存路径在此设置
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")

#读取已经保存在本地的cookies，如果有则读取，如果无则显示“cookie未能加载”
try:
    #ignore_discard的意思是即使cookies将被丢弃也将它读取下来，
    # ignore_expires的意思是如果cookies已经过期也将它保存并且文件已存在时将覆盖
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

#header的内容可从浏览器的每个请求头里复制
agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36"
header = {
    "HOST":"www.zhihu.com",
    "Referer": "https://www.zhizhu.com",
    'User-Agent': agent
}

def is_login():
    #通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/question/56250357/answer/148534773"
    #注意这里的allow_redirects参数，因为如果没有登录而访问这个网址的话会自动重定向到登录页面，
    # 重定向到登录到登录页面后会显示状态码200以表示读取成功。这里就是要获取重定向成功前的状态码（302重定向）
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True

def get_xsrf():
    #获取xsrf code
    #注意要传入header，很多报500错误的都是没有传入header
    response = session.get("https://www.zhihu.com", headers=header)
    response_text = response.text
    #注意非贪婪模式符号“？”
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
    xsrf = ''
    if match_obj:
        xsrf = (match_obj.group(1))
        return xsrf


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        #注意这里要由unicode编码成utf-8，因为python3要使用utf-8编码
        f.write(response.text.encode("utf-8"))
    print("ok")

def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    t = session.get(captcha_url, headers=header)
    with open("captcha.jpg","wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    captcha = input("输入验证码\n>")
    return captcha

def zhihu_login(account, password):
    #知乎登录
    if re.match("^1\d{10}",account):
        print ("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            "captcha":get_captcha()
        }
    else:
        if "@" in account:
            #判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

# get_index()
# is_login()
# get_captcha()
zhihu_login("18487255487", "ty158917")