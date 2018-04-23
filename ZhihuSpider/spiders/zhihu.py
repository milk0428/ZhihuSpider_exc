# -*- coding: utf-8 -*-
import scrapy
import re
import json

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    header={
        "HOST":"www.zhihu.com",
        "Referer":"https://www.zhihu.com",
        'User_Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.3.2000"
    }

    def parse(self, response):
        pass


    def start_requests(self):
        #注意传入headers
        return [scrapy.Request("https://www.zhihu.com/#signin",callback=self.login,headers=self.header)]


    def login(self,response):
        response_text=response.text
        #默认只匹配文本中第一行，除非加入参数re.DOTALL
        match_obj=re.match('.*name="_xsrf" value="(.*?)"',response_text,re.DOTALL)
        xsrf=""
        if match_obj:
            xsrf=(match_obj.group(1))

        if xsrf:
            post_url="https://www.zhihu.com/login/phone_num"
            post_data={
                "_xsrf":xsrf,
                "phone_num":"13889931091",
                "password":"123"
            }

        return [
            scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.header,
                callback=self.check_login
            )
        ]

        def check_login(self,response):
            text_json=json.loads(response.text)
            if "msg" in text_json and text_json["msg"]=="登陆成功":
                for url in self.start_urls:
                    #不写回调函数即提交至parse()
                    yield scrapy.Request(url,dont_filter=True,headers=self.header)