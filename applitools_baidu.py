from selenium import webdriver
from applitools.selenium import Eyes, Target
from selenium.webdriver.common.by import By

# 创建一个Eyes对象，并设置API key
eyes = Eyes()
eyes.api_key = 't5QgBlVl1053G3yqZtK19nTqKENFKx1dHmX5x54LIjkpA110'

try:
    # 打开一个Chrome浏览器
    driver = webdriver.Chrome()

    # 在Eyes对象中打开一个测试会话，指定应用程序的名称和测试的名称
    eyes.open(driver, "Baidu", "Baidu Search Test", {'width': 800, 'height': 600})

    # 访问百度首页
    driver.get('https://www.baidu.com')

    # 添加一个检查点，截取首页的整个窗口，并给它一个描述性的名称
    eyes.check("Baidu Homepage", Target.window())

    # 在搜索框中输入"applitools"并点击搜索按钮
    driver.find_element(By.ID, 'kw').send_keys('applitools')
    driver.find_element(By.ID, 'su').click()

    # 添加一个检查点，截取搜索结果页面的整个窗口，并给它一个描述性的名称
    eyes.check("Baidu Search Result", Target.window())

    # 结束测试会话，并获取测试结果
    results = eyes.close(False)
    print(results)
finally:
    # 释放Eyes对象和驱动对象的资源
    driver.quit()
    eyes.abort()
