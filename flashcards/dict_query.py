from readmdict import MDX, MDD  # pip install readmdict
from pyquery import PyQuery as pq  # pip install pyquery

# 加载mdx文件
filename = "E:\\All Files\\GoldenDict\\content\\新建文件夹\\牛津高阶8简体spx\\牛津高阶8简体.mdx"
headwords = [*MDX(filename)]  # 单词名列表
items = [*MDX(filename).items()]  # 释义html源码列表
if len(headwords) == len(items):
    print(f'加载成功：共{len(headwords)}条')
else:
    print(f'【ERROR】加载失败{len(headwords)}，{len(items)}')

# 查词，返回单词和html文件
queryWord = 'apple1'
# print(headwords[120:123])
try:
    wordIndex = headwords.index(queryWord.encode())
    word, html = items[wordIndex]
    word, html = word.decode(), html.decode()
except ValueError:
    print('无单词')
