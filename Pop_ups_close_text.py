import uiautomator2 as u2
import os
import time


base_dir = os.path.dirname(__file__)
apk_path = os.path.join(base_dir, "D:\\download\\apk\\bilibili.apk")


d = u2.connect_usb(serial='AVYYUT1708002110')


# 从安装到登录成功后，可能会出现的弹窗，在这里进行注册，这个是华为手机出现的弹窗类型
d.watcher.when('继续安装').click()
d.watcher.when('完成').click()
d.watcher.when('同意并继续').click()
d.watcher.when("我知道了").click()
d.watcher.start()


d.app_install(apk_path)


d.app_start('tv.danmaku.bili')


# d(text='我的').click()
# time.sleep(3)
# if d(resourceId="tv.danmaku.bili:id/btn_change_account").exists:
#     d(resourceId="tv.danmaku.bili:id/btn_change_account").click()
# else:
#     d(resourceId="tv.danmaku.bili:id/tv_login").click()
# time.sleep(3)
# d(resourceId="tv.danmaku.bili:id/username").set_text('xxxxxxxxx')


# d(resourceId="tv.danmaku.bili:id/userpwd").set_text('xxxxxxxx')


# d(resourceId="tv.danmaku.bili:id/log_reg_checkbox").click()


# time.sleep(2)
# d(resourceId="tv.danmaku.bili:id/btn_login").click()
# d(text='首页')