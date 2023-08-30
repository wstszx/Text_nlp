from snownlp import SnowNLP
# from snownlp import sentiment
texts = ['崔恩泽', 'suratman', '学生温州医科大学浙江开放的姐姐点我，正经人勿扰流行麻辣烫麻辣香锅靠谱跑步金庸三亚周杰伦千与千寻宅日韩成都古典北京烤鸭乒乓球火锅烤串泰坦尼克号黑客帝国火影忍者海贼王七龙珠',
         '想扣篮一男的', '你真不要脸', '发神经，这样抹黑人，你觉得好吗？自己风骚勾引来人，又到处黑人，这种行为准时令人作呕。[/挖鼻孔][/挖鼻孔][/挖鼻孔]',
         '幸福永远']
s_list = [SnowNLP(doc) for doc in texts]
for s in s_list:
    print(s.words)
    print(s.sentiments)