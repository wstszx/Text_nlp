# from googleapiclient.discovery import build
# import os

# # 设置 API 密钥和构建 YouTube API 客户端
# api_key = "AIzaSyA6vPa_C15NqqugLTva_66rDOayygeQx0A"
# youtube = build("youtube", "v3", developerKey=api_key)

# os.environ['http_proxy'] = 'http://127.0.0.1:7899'
# os.environ['https_proxy'] = 'http://127.0.0.1:7899'

# # 搜索正在直播的内容
# search_response = youtube.search().list(
#     q="",
#     type="video",
#     eventType="live",
#     part="id,snippet",
#     maxResults=50  # 最大结果数为 50
# ).execute()

# # 收集直播视频的链接
# live_video_links = []
# for item in search_response["items"]:
#     video_id = item["id"]["videoId"]
#     video_url = f"https://www.youtube.com/watch?v={video_id}"
#     live_video_links.append(video_url)

# for link in live_video_links:
#     print(link)






from googleapiclient.discovery import build
import os
import itertools
# 所有国家代码列表 (需要自行获取，例如从 pycountry 库获取)
import pycountry

# 设置 API 密钥和构建 YouTube API 客户端
api_key = "AIzaSyA6vPa_C15NqqugLTva_66rDOayygeQx0A"  # 请替换为你的 API 密钥
youtube = build("youtube", "v3", developerKey=api_key)

# 设置代理 (如果需要)
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

country_codes = [country.alpha_2 for country in list(pycountry.countries)]

# 将国家代码分成多个批次
batch_size = 10  # 每个批次包含 10 个国家代码
country_code_batches = list(itertools.zip_longest(*[iter(country_codes)] * batch_size))

# 存储直播视频链接的字典，以国家代码为键
live_video_links_by_country = {}

for batch in country_code_batches:
    for country_code in batch:
        if country_code is not None:
            try:
                # 使用 country_code 进行查询
                search_response = youtube.search().list(
                    q="",
                    type="video",
                    eventType="live",
                    part="id,snippet",
                    maxResults=50,
                    regionCode=country_code
                ).execute()

                # 收集直播视频的链接
                live_video_links = []
                for item in search_response["items"]:
                    video_id = item["id"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    live_video_links.append(video_url)

                live_video_links_by_country[country_code] = live_video_links

            except Exception as e:
                print(f"Error fetching data for country code {country_code}: {e}")

# 打印结果
for country_code, links in live_video_links_by_country.items():
    print(f"Country Code: {country_code}")
    for link in links:
        print(link)
    print("\n")
