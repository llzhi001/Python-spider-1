import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import jieba
import os
from PIL import Image
from os import path

plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False

plt.style.use('ggplot')
fig= plt.figure(figsize=(8,5))
ax1 = fig.add_subplot(1,1,1)
colors = '#6D6D6D'
color_line = '#CC2824'
fontsize_title = 20
fontsize_text = 10



# 清洗数据
def parse_huxiu():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['Huxiu']
    collection = db['huxiu_news']

    # 将数据库数据转为dataframe
    data = pd.DataFrame(list(collection.find()))

    # 删除无用的_id列
    data.drop(['_id'],axis=1,inplace=True)
    # 删除特殊符号©
    data['name'].replace('©','',inplace=True,regex=True)

    # 判断整行是否有重复值
    # print(any(data.duplicated()))
    # 显示yes，表明有重复值，进一步提取出重复值数量
    data_duplicated = data.duplicated().value_counts()
    # print(data_duplicated)
    # 删除重复值
    data = data.drop_duplicates(keep='first')

    # # 判断整行是否有缺失值
    # print(any(data.isnull()))
    # # 查看每列缺失值个数
    # data_colnull = data.shape[0] - data.count()
    # print(data_colnull)

    # # 查看每行缺失值个数,数量太多,不用
    # data_rownull = data.shape[1] - data.count(axis=1)
    # print(data_rownull)

    # 将是数值列的改为数值列
    data = data.apply(pd.to_numeric,errors='ignore')

    # 修改时间,并转换为 datetime 格式
    data['write_time'] = data['write_time'].replace('.*前','2019-02-25',regex=True)
    data['write_time'] = pd.to_datetime(data['write_time'])

    # 删除部分行后，index中断，需重新设置index
    data = data.reset_index(drop=True)

    # 增加标题长度列
    data['title_length'] = data['title'].apply(len)
    # 年份列
    data['year'] = data['write_time'].dt.year

    # print(data.shape)
    # print(data.info())

    return data


# 查看总体概括、文章发布变化
def analysis_01(data):
    # # 汇总统计
    # print(data.describe())
    # print(data['name'].describe())
    # print(data['write_time'].describe())

    data.set_index(data['write_time'],inplace=True)
    data = data.resample('Q').count()['name'] #以季度汇总
    data = data.to_period('Q')

    # 创建x,y轴标签
    x = np.arange(0,len(data),1)
    ax1.plot(x,data.values, #x、y坐标
        color = color_line , #折线图颜色为红色
        marker = 'o',markersize = 4 #标记形状、大小设置
        )
    ax1.set_xticks(x) # 设置x轴标签为自然数序列
    ax1.set_xticklabels(data.index) # 更改x轴标签值为年份
    plt.xticks(rotation=90) # 旋转90度，不至太拥挤

    for x,y in zip(x,data.values):
        plt.text(x,y + 10,'%.0f' %y,ha = 'center',color = colors,fontsize=fontsize_text )
        # '%.0f' %y 设置标签格式不带小数
    # 设置标题及横纵坐标轴标题
    plt.title('虎嗅网文章数量发布变化(2012-2019)',color = colors,fontsize=fontsize_title)
    plt.xlabel('时期')
    plt.ylabel('文章(篇)')
    plt.tight_layout()  # 自动控制空白边缘
    plt.savefig('虎嗅网文章数量发布变化.png',dpi=200)
    plt.show()


# 文章收藏量 TOP 10
def analysis_02(data):
    #     # 总收藏排名
    #     top = data.sort_values(by='favorites', ascending = False)
    #     # 收藏前100
    #     top.index = (range(1,len(top.index)+1))  # 重置index,并从1开始编号
    #     print(top[:100][['title','favorites','comment']])

    #     # 评论前100
    #     top = data.sort_values(['comment'],ascending = False)
    #     top.index = (range(1, len(data.index)+1))
    #     print(data[:100][['title','favorites','comment']])

    # 按年份排名
    def topn(data):
        top = data.sort_values(by='favorites', ascending=False)
        return top[:3]

    data = data.groupby('year').apply(topn)
    # print(data[['title','favorites']])

    # 增加每年top123列，列依次值为1,2,3
    data['add'] = 1
    data['top'] = data.groupby('year')['add'].cumsum()

    data_reshape = data.pivot_table(index='year', columns='top',
                                    values='favorites').reset_index()

    # print(data_reshape)

    data_reshape.plot(y=[1, 2, 3],
                      kind='bar',
                      width=0.3,
                      color=['#1362A3', '#3297EA', '#8EC6F5'])
    # 添加x轴标签
    years = data['year'].unique()
    plt.xticks(list(range(8)), years)
    plt.xlabel('Year')
    plt.ylabel('文章收藏数量')
    plt.title('历年TOP3文章收藏量比较', color=colors, fontsize=fontsize_title)
    plt.tight_layout()  # 自动控制空白边缘
    plt.savefig('历年TOP3文章收藏量比较.png', dpi=200)
    plt.show()


# 发文最多的媒体 top20
def analysis_03(data):
    data = data.groupby(by='name')['title'].count()
    data = data.sort_values(ascending=False)
    # print(data.head())
    # print(data.shape)

    # 1 pandas 直接绘制,.invert_yaxis()颠倒顺序
    data[1:21].plot(kind='barh',color=color_line).invert_yaxis()

    for y,x in enumerate(list(data[1:21].values)):
        plt.text(x+12,y+0.2,'%s'%round(x,1),ha='center',color=colors)
    plt.xlabel('文章数量')
    plt.ylabel('作者')
    plt.title('发文数量最多的 TOP20 作者',color = colors,fontsize=fontsize_title)
    #plt.tight_layout()
    plt.savefig('发文数量最多的TOP20作者.png',dpi=200)
    plt.show()


# 发文超过至少5篇以上的作者的文章平均收藏数排名
def analysis_04(data):
    data = pd.pivot_table(data, values='favorites',
                          index='name',aggfunc=[np.sum, np.size])
    data['avg'] = data[('sum','favorites')]/data[('size','favorites')]

    # 平均收藏数取整
    data['avg'] = data['avg'].astype('int')

    # flatten平铺列
    data.columns = data.columns.get_level_values(0)
    data.columns = ['total_favorites', 'articles_num', 'avg_favorites']

    # 筛选出文章数至少5篇的
    data = data.query('articles_num > 4')
    data = data.sort_values(by='avg_favorites',ascending=False)

    print(data[:10])
    # 查看平均收藏率第一名详情
    print(data.query('name == "L先生说"'))

    print(data[-10:])
    # 查看平均收藏率倒数第一名详情
    print(data.query('name == "Yang Yemeng"'))


# 收藏和评论的分布直方图
def analysis_05(data):
    # 用matplot做
    # plt.hist(data['favorites'],bins=50)
    # plt.hist(data['comment'],bins=50)

    # 用pandas做
    # data['favorites'].plot(kind='hist', bins=50, edgecolor='grey',
    #                        density=True,label='所有文章收藏分布图')
    # data['favorites'].plot(kind='kde')

    # 用seaborn做
    sns.distplot(data['favorites'])
    plt.tight_layout()  # 自动控制空白边缘，以全部显示X轴名称
    plt.savefig('收藏数分布直方图.png',dpi=200)
    plt.show()


# 散点图查看收藏和评论数的关系，发现个别异常
def analysis_06(data):
    plt.scatter(data['favorites'],data['comment'],s=8,color='#1362A3')
    plt.xlabel('文章收藏量')
    plt.ylabel('文章评论数')
    plt.title('文章评论数与收藏量关系',color=colors,fontsize=fontsize_title)
    plt.tight_layout()   # 自动控制空白边缘，以全部显示X轴名称
    plt.savefig('文章评论数与收藏量关系.png', dpi=200)
    plt.show()


# 查看标题长度与收藏量的关系
def analysis_07(data):
    plt.scatter(data['favorites'],data['title_length'],s=8)
    plt.xlabel('文章收藏量')
    plt.ylabel('文章标题长度')
    plt.title('文章收藏量和标题长度关系',color=colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('文章收藏量和标题长度关系.png', dpi=200)
    plt.show()


# 查看标题长度与收藏量和评论数之间的关系
def analysis_08(data):
    plt.scatter(data['favorites'], data['comment'], s=data['title_length']/2)
    plt.xlabel('文章收藏量')
    plt.ylabel('文章评论数')
    plt.title('文章标题长度与收藏量和评论数之间的关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('标题长度与收藏量和评论数之间的关系.png', dpi=200)
    plt.show()


# 词云
def analysis_09(data):
    jieba.load_userdict('userdict.txt')
    jieba.add_word('区块链')

    text=''
    for i in data['title'].values:
        # 替换无用字符
        symbol_to_replace = '[!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
        i = re.sub(symbol_to_replace,'',i)
        text += ' '.join(jieba.cut(i, cut_all=False))

    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()

    background_Image = np.array(Image.open(path.join(d, "tiger.png")))

    font_path = 'C:\Windows\Fonts\STFANGSO.TTF'
    # 添加stopwords
    stopwords = set()
    # 先运行对text进行词频统计再排序，再选择要增加的停用词
    stopwords.update(
        ['如何', '怎么', '一个', '什么', '为什么', '还是', '我们', '为何', '可能', '不是', '没有', '哪些', '成为', '可以', '背后', '到底', '就是', '这么',
         '不要', '怎样', '为了', '能否', '你们', '还有', '这样', '这个', '真的', '那些'])

    wc = WordCloud(
        background_color='black',
        font_path=font_path,
        mask=background_Image,
        stopwords=stopwords,
        max_words=200,
        margin=2,
        max_font_size=100,
        random_state=42,
        scale=2
    )
    wc.generate_from_text(text)

    process_word = WordCloud.process_text(wc,text)
    # 字典排序
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    print(sort[:50])
    img_colors = ImageColorGenerator(background_Image)
    wc.recolor(color_func=img_colors)  # 颜色跟随图片颜色

    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('词云图.png', dpi=200)
    plt.show()


# 绘制标题形式饼图
def analysis_10(data):
    data1 = data[data['title'].str.contains("(.*\?.*)|(.*\？.*)")]
    data2 = data[data['title'].str.contains("(.*\!.*)|(.*\！.*)")]

    # 带有问号的标题数量
    quantity1 = data1.shape[0]
    # 带有叹号的标题数量
    quantity2 = data2.shape[0]
    # 剩余数量
    quantity = data.shape[0] - quantity1 - quantity2

    sizes = [quantity2,quantity1,quantity]
    labels = ['叹号标题','问号标题','陈述性标题']
    colors_pie = ['#1362A3','#3297EA','#8EC6F5']  # 定义每块颜色
    explode = [0,0.05,0]
    plt.pie(sizes,
            autopct='%.1f%%',
            labels=labels,
            colors=colors_pie,
            shadow=False,
            explode=explode,
            textprops={'fontsize':12, 'color':'w'}
            )
    plt.title('三分之一文章的标题喜欢用问号',color=colors,fontsize=fontsize_title)
    plt.axis('equal')
    plt.axis('off')
    plt.legend(loc = 'upper right')
    plt.tight_layout()
    plt.savefig('title问号.png', dpi=200)
    plt.show()


if __name__ == '__main__':
    data = parse_huxiu()
    #analysis_01(data)
    #analysis_02(data)
    #analysis_03(data)
    #analysis_04(data)
    #analysis_05(data)
    #analysis_06(data)
    #analysis_07(data)
    #analysis_08(data)
    analysis_09(data)
    #analysis_10(data)




