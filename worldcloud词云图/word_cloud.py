import os
from os import path
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
import random
import chardet
import jieba
import pandas as pd


def wc_english_basic():
    # 获取当前文件路径
    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    # 获取文本text
    text = open(path.join(d, 'legend1900.txt')).read()
    # 生成词云
    wc = WordCloud(
    scale=2,
    max_font_size=100,
    background_color='#383838',
    colormap='Blues'
    )
    wc.generate_from_text(text)
    # 显示图像
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    # 存储图像
    plt.savefig('1900_basic_01.png',dpi=200)
    plt.show()


def wc_english_improve_01():
    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    text = open(path.join(d, 'legend1900.txt')).read()
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d,'mask1900.jpg')))
    # or
    # background_Image = imread(path.join(d,'mask1900.jpg'))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)
    # 设置英文停止词，分割筛除文本中不需要的词汇，比如：a、an、the
    stopwords = set(STOPWORDS)
    wc = WordCloud(
        margin=2,
        mask=background_Image,
        scale=2,
        max_words=200,
        min_font_size=4,
        max_font_size=150,
        stopwords=stopwords,
        random_state=42,
        background_color='white'
    )
    # 生成词云
    wc.generate_from_text(text)
    # 根据图片色设置背景色
    wc.recolor(color_func=img_colors)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('1900_basic_02.png',dpi=200)
    plt.show()

# 去掉显眼的ONE
def wc_english_improve_02():
    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    text = open(path.join(d, 'legend1900.txt')).read()
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d,'mask1900.jpg')))
    # or
    # background_Image = imread(path.join(d,'mask1900.jpg'))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)
    # 设置英文停止词，分割筛除文本中不需要的词汇，比如：a、an、the
    stopwords = set(STOPWORDS)
    stopwords.add('one')

    wc = WordCloud(
        margin=2,
        mask=background_Image,
        scale=2,
        max_words=200,
        min_font_size=4,
        max_font_size=150,
        stopwords=stopwords,
        random_state=42,
        background_color='white'
    )
    # 生成词云
    wc.generate_from_text(text)

    # 获取文本词排序，调整stopwords
    process_word = WordCloud.process_text(wc, text)   # 返回的是dict，表示的是分词后的token以及对应出现的次数
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    #print(sort[:50]) # 获取文本词频最高的前50个词，one出现60次

    # 根据图片色设置背景色
    wc.recolor(color_func=img_colors)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('1900_basic_03.png',dpi=200)
    plt.show()

# 将词云颜色显示为黑白渐变色
def wc_english_improve_03():
    d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    text = open(path.join(d, 'legend1900.txt')).read()
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d,'mask1900.jpg')))
    # or
    # background_Image = imread(path.join(d,'mask1900.jpg'))
    # 提取背景图片颜色
    #img_colors = ImageColorGenerator(background_Image)
    # 设置英文停止词，分割筛除文本中不需要的词汇，比如：a、an、the
    stopwords = set(STOPWORDS)
    stopwords.add('one')

    wc = WordCloud(
        margin=2,
        mask=background_Image,
        scale=2,
        max_words=200,
        min_font_size=4,
        max_font_size=150,
        stopwords=stopwords,
        random_state=42,
        background_color='black'
    )
    # 生成词云
    wc.generate_from_text(text)

    # 获取文本词排序，调整stopwords
    process_word = WordCloud.process_text(wc, text)   # 返回的是dict，表示的是分词后的token以及对应出现的次数
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    #print(sort[:50]) # 获取文本词频最高的前50个词，one出现60次

    def grey_color_func(word, font_size, position,
                        orientation, random_state=None,**kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(50, 100)  # 随机设置hsl值，色相，饱和度，明度

    wc.recolor(color_func=grey_color_func)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('1900_basic_04.png',dpi=200)
    plt.show()


def wc_chinese():
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    # 确定文本编码格式
    text = open(path.join(d,'langchao.txt'),'rb').read()
    text_charInfo = chardet.detect(text)
    #print(text_charInfo)
    # 结果：{'encoding': 'UTF-8-SIG', 'confidence': 1.0, 'language': ''}

    text = open(path.join(d,r'langchao.txt'),encoding='UTF-8-SIG').read()
    text += ' '.join(jieba.cut(text,cut_all=False))  # cut_all=False 表示采用精确模式

    # 设置中文字体
    font_path = '‪C:\Windows\Fonts\STXIHEI.TTF'
    # 获取背景图片
    background_Image = np.array(Image.open(path.join(d,'circle.jpg')))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)
    # 设置中文停止词
    stopwords = set('')
    stopwords.update(['但是','一个','自己','因此','没有','很多','可以','这个','虽然','因为','这样','已经','现在','一些','比如','不是','当然','可能','如果','就是','同时','比如','这些','必须','由于','而且','并且','他们'])

    wc = WordCloud(
        font_path=font_path,
        margin=2,
        mask=background_Image,
        scale=2,
        max_words=200,
        min_font_size=4,
        max_font_size=100,
        stopwords=stopwords,
        random_state=42,
        background_color='white'
    )
    wc.generate_from_text(text)

    # 获取文本词排序，调整stopwords
    process_word = WordCloud.process_text(wc,text)
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    #print(sort[:50])  # 获取文本词频最高的前50个词

    # 根据图片色设置背景色
    wc.recolor(color_func=img_colors)
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('浪潮basic01.png',dpi=200)
    plt.show()


# Frenquency 词云图
def wc_frenquency():
    df = pd.read_csv('university.csv',encoding='utf-8')
    df = df.groupby(by='country').count()
    df = df['world rank'].sort_values(ascending=False)
    #print(df[:10])
    #or df = dict(df)

    wc = WordCloud(
        background_color='#F3F3F3',
        width=500,
        height=300,
        margin=2,
        max_font_size=200,
        random_state=42,
        scale=2,
        colormap='viridis'
    )
    wc.generate_from_frequencies(df)

    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('Frenquency词云图.png',dpi=200)
    plt.show()


if __name__ == '__main__':
    #wc_english_basic()
    #wc_english_improve_01()
    #wc_english_improve_02()
    #wc_english_improve_03()
    #wc_chinese()
    wc_frenquency()






