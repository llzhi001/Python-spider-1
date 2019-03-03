import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jieba
import os
from os import path
import re
from decimal import Decimal
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.style.use('ggplot')
fig = plt.figure(figsize=(8,5))
ax1 = fig.add_subplot(1,1,1)
colors = '#6D6D6D'
color_line = '#CC2824'
fontsize_title = 20
fontsize_text = 10


# 处理views列
def views_to_num(item):
    m = re.search('.*?(万)', item['views'])
    if m:
        ns = item['views'][:-1]
        nss = Decimal(ns)*10000
    else:
        nss = item['views']
    return int(nss)


# 收藏量前三
def topn(data):
    top = data.sort_values(by='loves',ascending=False)
    return top[:3]


# 清洗数据
def parse_pm():
    csv_data = pd.read_csv('data.csv',low_memory=False)   # 防止弹出警告
    data = pd.DataFrame(csv_data)
    #print(csv_df.shape)  # (6588, 10)
    #print(csv_df.info())
    #print(csv_df.head())

    # 修改date列时间，并转换为datetime格式
    data['date'] = pd.to_datetime(data['date'])
    # 将views字符串数字化，增加一列views_num
    data['views_num'] = data.apply(views_to_num,axis=1)
    #print(csv_df.info())

    # 判断是否有重复行
    #print(any(csv_df.duplicated()))    # False
    # 若返回True，则要进行以下处理
    # data_duplicated = data.duplicated().value_counts()
    # print(data_duplicated)
    # data = data.drop_duplicates(keep='first')
    # data = data.reset_index(drop=True)

    # 增加标题长度列和年份列
    data['title_length'] = data['title'].apply(len)
    data['year'] = data['date'].dt.year
    #print(data.info())
    #print(data.head())

    return data


# 数据分析
# 查看总体情况，文章季度发布情况
def analysis_01(data):
    pd.set_option('display.max_columns', 2)  # 显示的最大列数为2，如果超额就显示省略号
    # 数值型数据汇总统计
    # print(data.describe())
    # 非数值型数据汇总统计
    # print(data['author'].describe())
    # print(data['date'].describe())

    data.set_index(data['date'],inplace=True)
    data = data.resample('Q').count()['author']  # 以季度汇总
    data = data.to_period('Q')   # to_period()方法将时间点转换为包含该时间点的时间段

    x = np.arange(0,len(data),1)
    ax1.plot(x, data.values,
             color = color_line,
             marker = 'o', markersize = 4
             )
    ax1.set_xticks(x)
    ax1.set_xticklabels(data.index)
    plt.xticks(rotation=90)

    for x, y in zip(x, data.values):
        plt.text(x, y+10, '%.0f'%y, ha='center', color=colors, fontsize=fontsize_text)
        # '%.0f'%y 设置标签格式不带小数

    plt.title('人人都是产品经理产品经理栏目文章数量发布变化(2012-2019)',color=colors, fontsize=fontsize_title)
    plt.xlabel('时期')
    plt.ylabel('文章（篇）')
    plt.tight_layout()
    plt.savefig('人人都是产品经理产品经理栏目文章数量发布变化.png', dpi=200)
    plt.show()


# 文章收藏量、浏览量分析
def analysis_02(data):
    # 收藏量排名
    # top = data.sort_values(by='loves',ascending=False)
    # top.index = (range(1, len(top.index)+1))  # 重置index，从1开始编号
    # print(top[:10][['title','loves']])

    # 浏览量排名
    # top = data.sort_values(by='views_num',ascending=False)
    # top.index = (range(1, len(top.index)+1))
    # print(top[:10][['title','views_num']])

    data = data.groupby(by='year').apply(topn)
    #print(data[['title','loves']])

    # 增加每年top123列，列依次值为1、2、3
    data['add'] = 1
    data['top'] = data.groupby(by='year')['add'].cumsum()
    #print(data.head())

    data_reshape = data.pivot_table(index='year',columns='top',values='loves').reset_index()
    #print(data_reshape)

    data_reshape.plot(
        y=[1,2,3],
        kind='bar',
        width=0.3,
        color=['#1362A3', '#3297EA', '#8EC6F5']
    )

    years = data['year'].unique()
    plt.xticks(list(range(7)),years)
    plt.xlabel('Year')
    plt.ylabel('文章收藏数量')
    plt.title('历年 TOP3 文章收藏量比较',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('历年TOP3文章收藏量比较.png',dpi=200)
    plt.show()


# 发文最多的媒体top20
def analysis_03(data):
    data = data.groupby(by='author')['title'].count()
    data = data.sort_values(ascending=False)
    #print(data.head())

    data[:20].plot(kind='barh',color=color_line).invert_yaxis()

    for y,x in enumerate(list(data[:20].values)):
        plt.text(x+12,y+0.2,'%s'%round(x,1),ha='center',color=colors)

    plt.xlabel('文章数量')
    plt.ylabel('作者')
    plt.title('发文数量最多的TOP20作者',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('发文数量最多的TOP20作者.png',dpi=500)
    plt.show()

# 文章评论数top10
def analysis_04(data):
    top = data.sort_values(by='comment_num',ascending=False)
    top.index = (range(1,len(top.index)+1))
    print(top[:10][['title','comment_num','loves']])

#

# 发文超过至少5篇以上的作者的文章平均收藏数排名
def analysis_05(data):
    data = pd.pivot_table(data, values=['loves'],index='author',aggfunc=[np.sum,np.size])
    data['avg'] = data[('sum','loves')]/data[('size','loves')]
    #print(data.head())

    #平均收藏数取整
    data['avg'] = data['avg'].round(decimals=1)
    data['avg'] = data['avg'].astype('int')

    # flatten平铺列
    data.columns = data.columns.get_level_values(0)
    data.columns = ['total_loves','ariticls_num','avg_loves']
    #print(data.head())

    # 筛选出文章数至少5篇的
    data = data.query('ariticls_num>4')
    data = data.sort_values(by='avg_loves',ascending=False)

    #print(data[:5])  # 平均收藏率第一名,倒爷001
    #print(data[-5:])  # 平均收藏率倒数第一名,虫虫

    # 查看平均收藏率第一名的详情
    data = data.query('author=="倒爷001"')
    print(data[['total_loves','ariticls_num','avg_loves']])


# 散点图查看收藏数和评论数的关系
def analysis_06(data):
    plt.scatter(data['loves'],data['comment_num'],s=8,)
    plt.xlabel('文章收藏量')
    plt.ylabel('文章评论数')
    plt.title('文章评论数与收藏量关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('文章评论数与收藏量关系.png',dpi=200)
    plt.show()


# 查看标题长度与阅读量的关系
def analysis_07(data):
    plt.scatter(data['views_num'],data['title_length'],s=8)
    plt.xlabel('文章阅读量')
    plt.ylabel('文章标题长度')
    plt.title('文章阅读量和标题长度关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('文章阅读量和标题长度关系.png',dpi=200)
    plt.show()


# 词云
def analysis_08(data):
    jieba.load_userdict('互联网产品经理词库.txt')
    text = ''
    for i in data['art'].values:
        # 替换无用字符
        symbol_to_replace = '[!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
        i = re.sub(symbol_to_replace,'',i)
        text += ' '.join(jieba.cut(i,cut_all=False))

    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()

    background_Image = np.array(Image.open(path.join(d, 'woshipm.jpg')))
    font_path = 'C:\Windows\Fonts\STFANGSO.TTF'
    stopwords = set()
    stopwords.update(
        ['而且','之前','并且','等等','当然', '这种','只是','已经','最后','之后','甚至','应该','然后',
         '同时', '现在','一样', '一定','很多','开始','人人 产品经理','对于','以及','其实','时候','一些',
         '这些','比如','通过','自己','那么','需要','但是','因为','所以','他们','或者','如果','如何','怎么',
         '一个','什么','为什么','还是','我们','为何','可能','不是','没有','哪些','成为','可以','背后','到底',
         '就是','这么','不要','怎样','为了','能否','你们','还有','这样','这个','真的','那些'])

    wc = WordCloud(
        font_path=font_path,
        mask=background_Image,
        stopwords=stopwords,
        max_words=100,
        margin=3,
        max_font_size=100,
        random_state=42,
        scale=2
    )
    wc.generate_from_text(text)

    process_word = WordCloud.process_text(wc, text)
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    #print(sort[:50])

    img_colors = ImageColorGenerator(background_Image)
    wc.recolor(color_func=img_colors)

    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('pm词云图.png',dpi=200)
    plt.show()


if __name__ == '__main__':
    data = parse_pm()
    #analysis_01(data)
    #analysis_02(data)
    #analysis_03(data)
    #analysis_04(data)
    #analysis_05(data)
    #analysis_06(data)
    #analysis_07(data)
    analysis_08(data)