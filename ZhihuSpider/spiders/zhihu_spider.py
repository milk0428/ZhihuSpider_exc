# -*- coding: utf-8 -*-
import scrapy
import re
import json
from selenium import webdriver
import time
import pickle
import datetime

from scrapy.loader import ItemLoader
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
    orgin_answer_url="https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics&limit={1}&offset={2}"
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
                #如果提取到question相关的页面，则提取链接后交给parse_question()函数处理
                request_url=mathc_obj.group(1)
                # question_id=mathc_obj.group(2)    #这里获取的id没有通过meta元素传递出去，而是直接在下一个需要的位置运行正则表达式查找，所以此处先去掉
                yield scrapy.Request(request_url,headers=self.header,callback=self.parse_question)
            else:
                #如果当前url不是合适的链接，那么就进入该url查找看看这个url里有无合适的链接。（深度优先策略）callback可以不写，因为默认也是回调parse()
                yield scrapy.Request(url,headers=self.header,callback=self.parse)

    #处理question页面，从页面中提取具体的question item
    def parse_question(self, response):
        #知乎之前有新旧版本之分，有“QusetionHeader-title”的为新版本，无的为旧版本，故以此为判断依据
        if "QuestionHeader-title" in response.text:
            #注意使用itemloader方法先要import此类以及相关的item类
            mathc_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if mathc_obj:
                question_id = int(mathc_obj.group(2))

            #itemloader方式获取的数据为list对象，故需要在item类中再处理
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title",".QuestionHeader-title::text")
            item_loader.add_css("content",".QuestionHeader-detail")
            item_loader.add_value("url",response.url)
            item_loader.add_value("zhihu_id",question_id)
            item_loader.add_css("answer_num",".List-headerText span::text")#有其他数据，待调整
            item_loader.add_css("comments_num",".QuestionHeader-Comment button::text")#有其他数据，待调整
            item_loader.add_css("watch_user_num",".QuestionFollowStatus-counts .NumberBoard-itemValue::attr(title)")#包含了关注者及被浏览
            item_loader.add_css("click_num",".QuestionFollowStatus-counts .NumberBoard-itemValue::attr(title)")#包含了关注者及被浏览
            item_loader.add_css("topics",".QuestionHeader-topics .Popover div::text")#待完善
            question_item=item_loader.load_item()
            # yield scrapy.Request(self.orgin_answer_url.format(question_id,20,0),headers=self.header,callback=self.parse_answer)
            yield question_item

            #此处可再运行parse()中获取目标页面再请求Request(),为简化逻辑，这里不再运行。
        else:
            print("旧版本")

    #提取answer item
    def parse_answer(self,response):
        answers=json.loads(response.text)
        is_end=answers["paging"]["is_end"]
        next_url=answers["paging"]["next"]

        for answer in answers["data"]:
            answer_item=ZhihuAnswerItem()
            answer_item["zhihu_id"]=answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            #因可能会是匿名回复，故可能没有作者id，需判断
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None   #判断有可能无
            answer_item["content"] = answer["content"]
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] =datetime.datetime.time()
            # answer_item["crawl_update_time"] =time.time()   #暂时未获取
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url,headers=self.header,callback=self.parse_answer)

    def start_requests(self):
        #注意传入headers
        # return [scrapy.Request("https://www.zhihu.com/#signin",callback=self.login,headers=self.header)]
        browser=webdriver.Firefox(executable_path="D:/PycharmProjects/ZhihuSpider/geckodriver.exe")
        browser.get("https://www.zhihu.com/signin?next=%2F")

        browser.find_element_by_css_selector(".SignFlow-accountInput input").send_keys("13889931091")
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys("102733Cch")

        #暂停10秒以输入验证码
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
        browser.close()
        #注意dont_filter参数以及setting.py中设置ROBOTSTXT_OBEY = False
        # 没有写回调函数的话默认调用prase（）
        #注意要传入参数headers
        # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict,headers=self.header)]
        for url in self.start_urls:
            # 不写回调函数即提交至parse()
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict,headers=self.header)
