import os
from os import path
import numpy as np
from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image
from matplotlib import pyplot as plt
import jieba

d = path.dirname(__file__) if '__file__' in locals() else os.getcwd()

# 对原文本分词
def cut_words():
    text = open(path.join(d,r'langchao.txt'),encoding='UTF-8-SIG').read()
    text = jieba.cut(text,cut_all=False)
    content = ''
    for i in text:
        content += i
        content += " "
    return content

# 加载stopwords
def load_stopwords():
    filepath = path.join(d,r'stopwords_cn.txt')
    stopwords = [line.strip() for line in open(filepath,encoding='utf-8').readlines()]
    #print(stopwords)
    return stopwords

# 去除原文stopwords，并生成新的文本
def move_stopwords(content,stopwords):
    content_after = ''
    for word in content:
        if word not in stopwords:
            if word != '\t' and '\n':
                content_after += word

    content_after = content_after.replace("   ", " ").replace("  "," ")
    #print(content_after)
    with open('langchao2.txt','w',encoding='UTF-8-SIG') as f:
        f.write(content_after)

def wc_chinese():
    text = open(path.join(d, 'langchao2.txt'), encoding='UTF-8-SIG').read()
    font_path = '‪C:\Windows\Fonts\STXIHEI.TTF'
    background_Image = np.array(Image.open(path.join(d, "circle.jpg")))
    img_colors = ImageColorGenerator(background_Image)

    stopwords = set('')

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
        background_color='white',
    )
    wc.generate_from_text(text)


    # 获取文本词排序，可调整 stopwords
    process_word = WordCloud.process_text(wc, text)
    sort = sorted(process_word.items(), key=lambda e: e[1], reverse=True)
    print(sort[:50])  # 获取文本词频最高的前50个词

    wc.recolor(color_func=img_colors)

    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('浪潮basic2.png',dpi=200)
    plt.show()


if __name__ == '__main__':
    content = cut_words()
    stopwords = load_stopwords()
    move_stopwords(content, stopwords)
    wc_chinese()

