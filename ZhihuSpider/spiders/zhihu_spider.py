# -*- coding: utf-8 -*-
import scrapy
import re
import json
from selenium import webdriver
import time
import pickle

from  scrapy.loader import ItemLoader
from ZhihuSpider.items import ZhihuQuestionItem,ZhihuAnswerItem

try:
    # python2写法
    import urlprase as prase
except:
    # python3写法
    from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    header={
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36"
    }

    def parse(self, response):
        """
        采用深度优先策略
        提取出html页面中的所有url，并跟踪这些url进行一步爬取
        如果提取的url中格式为/question/XXX 就下载之后直接进入解析函数
        """
        all_urls=response.css("a::attr(href)").extract()

        #采用列表生成式拼接url
        all_urls=[parse.urljoin(response.url,url) for url in all_urls]

        #采用filter函数过滤没有用的url（注意filter及lambda的用法）
        all_urls=filter(lambda x:True if x.startswith("https") else False,all_urls)

        #提取出question id及相应的网址，注意正则表达式的用法
        for url in all_urls:
            mathc_obj=re.match("(.*zhihu.com/question/(\d+))(/|$).*",url)
            if mathc_obj:
                request_url=mathc_obj.group(1)
                question_id=mathc_obj.group(2)
                yield scrapy.Request(request_url,headers=self.header,callback=self.parse_question)

    #处理question页面，从页面中提取具体的question item
    def parse_question(self, response):
        item_loader=ItemLoader(item=ZhihuQuestionItem(),response=response)


    def start_requests(self):
        #注意传入headers
        # return [scrapy.Request("https://www.zhihu.com/#signin",callback=self.login,headers=self.header)]
        browser=webdriver.Firefox(executable_path="D:/PycharmProjects/ZhihuSpider/geckodriver.exe")
        browser.get("https://www.zhihu.com/signin?next=%2F")

        #知乎账号密码
        #测试版本
        #测试同步功能
        browser.find_element_by_css_selector(".SignFlow-accountInput input").send_keys("13889931091")
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys("102733Cch")

        time.sleep(10)

        browser.find_element_by_css_selector(".SignFlow .SignFlow-submitButton").click()
        #等待5秒以使得页面读取完毕
        time.sleep(5)
        cookies=browser.get_cookies()
        # print(cookies)
        cookie_dict={}
        for cookie in cookies:
            f = open('D:/PycharmProjects/ZhihuSpider/cookies/zhihu/' + cookie['name'] + '.zhihu', 'wb')
            pickle.dump(cookie, f)
            f.close()
            #只获取cookie的name/value字段的值并装进字典，将该字典赋值给scrapy的cookies以维持登陆状态。注意该原来的字典中有很多字段。
            cookie_dict[cookie['name']] = cookie['value']
        # browser.close()
        #注意dont_filter参数以及setting.py中设置ROBOTSTXT_OBEY = False
        # 没有写回调函数的话默认调用prase（）
        #注意要传入参数headers
        # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict,headers=self.header)]
        for url in self.start_urls:
            # 不写回调函数即提交至parse()
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict,headers=self.header)
