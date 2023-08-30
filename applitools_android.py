from appium import webdriver
from applitools.selenium import Eyes, Target, MatchLevel, BatchInfo, StitchMode
import os

# 设置环境变量，指定Clash代理地址
os.environ['HTTP_PROXY'] = 'http://localhost:7890'
os.environ['HTTPS_PROXY'] = 'http://localhost:7890'

class HelloWorld:
    # Initialize the eyes SDK and set your private API key.
    eyes = Eyes()
    eyes.api_key = 't5QgBlVl1053G3yqZtK19nTqKENFKx1dHmX5x54LIjkpA110'

    # Create a batch info object to group the tests
    batch = BatchInfo("Applitools App Test")

    # Desired capabilities.
    desired_caps = dict(
        platformName = 'Android',
        deviceName = 'AVYYUT1708002110',
        platformVersion= '12.0',
        automationName= 'UiAutomator2',
        app='https://applitools.jfrog.io/artifactory/Examples/eyes-hello-world.apk')

    # Open the app.
    wd = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
    wd.implicitly_wait(10)

    try:
        # Start the test.
        eyes.open(driver=wd, app_name='applitools app', test_name='手机applitools测试')

        # Set the match level to Layout2
        eyes.match_level = MatchLevel.STRICT

        # Visual UI testing.
        eyes.check(Target.window().fully().with_name('Contact list!'))

        # End the test.
        eyes.close()
    finally:
        # Close the app.
        wd.quit()

        # If the test was aborted before eyes.close was called, ends the test as aborted.
        eyes.abort()
