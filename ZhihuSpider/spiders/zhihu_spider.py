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
        #知乎之前有新旧版本之分，有“QusetionHeader-title”的为新版本，无的为旧版本，故以此为判断依据
        if "QuestionHeader-title" in response.text:
            #注意使用itemloader方法先要import此类以及相关的item类
            mathc_obj = re.match ( "(.*zhihu.com/question/(\d+))(/|$).*" , response.url )
            if mathc_obj:
                question_id =int(mathc_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title",".QuestionHeader-title::text")
            item_loader.add_css("content",".QuestionHeader-detail")
            item_loader.add_value("url",response.url)
            item_loader.add_value("zhihu_id",question_id)
            item_loader.add_css("answer_num",".QuestionMainAction::text")#有其他数据，待调整----------
            item_loader.add_css("comments_num",".QuestionHeader-Comment button::text")#有其他数据，待调整
            item_loader.add_css("watch_user_num",".QuestionFollowStatus-counts .NumberBoard-itemValue::attr(title)")#包含了关注者及被浏览
            item_loader.add_css("click_num",".QuestionFollowStatus-counts .NumberBoard-itemValue::attr(title)")#包含了关注者及被浏览
            item_loader.add_css("topics",".QuestionHeader-topics .Popover::text")#待完善---------------

            question_item=item_loader.load_item()
            # # zhihu的问题item
            # zhihu_id = scrapy.Field ()--------------
            # topics = scrapy.Field ()--------------
            # url = scrapy.Field ()------------
            # title = scrapy.Field ()------------
            # content = scrapy.Field ()---------
            # # 下边两个通过question页面直接获取不到，所以这里不要
            # # create_time=scrapy.Field()
            # # update_time=scrapy.Field()
            # answer_num = scrapy.Field ()---------
            # comments_num = scrapy.Field ()--------------
            # watch_user_num = scrapy.Field ()--------------
            # click_num = scrapy.Field ()----------
            # crawl_time = scrapy.Field ()
            # crawl_update_time = scrapy.Field ()

            # text1=response.css(".QuestionHeader-title::text").extract_first()
            # print(text1)
            pass
        else:
            print("旧版本")



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
