# from selenium import webdriver
# from scrapy.selector import Selector
#
# #下载的驱动路径，注意改成反斜杠
# browser = webdriver.Firefox(executable_path="D:/PycharmProjects/ZhihuSpider/geckodriver.exe")
#
# browser.get("https://www.zhihu.com/signin?next=%2F")
#
# # print(browser.page_source)
#
# #selenium提供了多种find_element函数，类似于scrapy的selecter，但非必要的话还是推荐使用scrapy的selecter。因为selenium的find_element是用python写的，scrapy的selecter是用C语言写的，C语言写的速度比较快。
# #除非要使用selenium的点击网页按钮功能。
# # t_selector=Selector(text=browser.page_source)
# # print(t_selector.css(".tm-promo-price .tm-price::text").extract())
#
# #使用selenium实现模拟手工登陆
# browser.find_element_by_css_selector(".SignFlow-accountInput input").send_keys("13889931091")
# browser.find_element_by_css_selector(".SignFlow-password input").send_keys("102733Cch")
# browser.find_element_by_css_selector(".SignFlow .SignFlow-submitButton").click()
#
#
#
# # browser.quit()