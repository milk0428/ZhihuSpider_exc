# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent

class ZhihuspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class RandomUserAgentMiddlware(object):
    #随机更换user-agent
    def __init__(self,crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        # self.user_agent_list=crawler.settings.get("USER_AGENT_LIST",[])
        self.ua=UserAgent()
        #读取settings.py中配置的随机类型，默认值为random
        self.ua_type=crawler.settings.get("RANDOM_UA_TYPE","random")

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    #重写此方法是固定的
    def process_request(self,request,spider):
        #在函数中定义函数是动态语言的特点，非动态语言不能这样做
        #注意getattr()函数的用法。因为fake_useragent用法为ua.random
        def get_ua():
            return getattr(self.ua,self.ua_type)
        user_agent= "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36"
        #因知乎会校验user-agent版本，太旧的话会返回错误提示页面导致爬取失败，故此处还是采用固定的user-agent，若使用动态agent，只需将下列函数中的user_agent参数换成get_ua()
        request.headers.setdefault("User-Agent",user_agent)
