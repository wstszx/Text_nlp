import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 启动优酷app
d.app_start("com.youku.phone") # 这里指定了要启动的activity

# 等待app启动
d.implicitly_wait(10)

# 找到视频播放的进度条元素
# 注意：这需要你知道进度条的元素ID，你可以通过app的UI测试工具来获取
progress_bar = d(resourceId="com.youku.phone:id/svf_play_position_progress")

# 计算进度条的开始、结束和中间位置
start_x = progress_bar.info['bounds']['left']
end_x = progress_bar.info['bounds']['right']
mid_x = (start_x + end_x) / 2 # 这是中间位置
y = progress_bar.info['bounds']['top']

# 使用swipe方法来模拟拖动操作
# 这里我们模拟从开始到中间的拖动，你可以根据需要调整
d.swipe(start_x, y, mid_x, y)
