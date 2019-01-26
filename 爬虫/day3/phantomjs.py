from selenium import webdriver
browser = webdriver.PhantomJS(r'D:\phantomjs-2.1.1-windows\bin\phantomjs')
browser.get('https://www.baidu.com')
print(browser.current_url)