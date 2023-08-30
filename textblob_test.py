from textblob import TextBlob

# 做情感分析的文本
text = "i feel a little happy"

# 进行情感分析
blob = TextBlob(text)
sentiment = blob.sentiment.polarity

# 打印结果
print("Text: ", text)
print("Sentiment: ", sentiment)