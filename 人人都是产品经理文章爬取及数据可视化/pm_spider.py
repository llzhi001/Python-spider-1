import requests
from bs4 import BeautifulSoup
import csv

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "Hm_lvt_b85cbcc76e92e3fd79be8f2fed0f504f=1548430869; Hm_lpvt_b85cbcc76e92e3fd79be8f2fed0f504f=1548520859",
    "Host": "www.woshipm.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}

with open('data.csv','w',encoding='utf-8', newline='') as csvfile:
    fieldnames = ['title', 'author', 'author_des', 'date', 'views', 'loves', 'zans', 'comment_num', 'art', 'url']
    writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
    writer.writeheader()

    for page_number in range(1,551):
        page_url = "http://www.woshipm.com/category/pmd/page/{}".format(page_number)
        print("正在抓取第" + str(page_number)+"页>>>")
        response = requests.get(url=page_url,headers=headers)
        if response.status_code == 200:
            page_data = response.text
            if page_data:
                soup = BeautifulSoup(page_data,'lxml')
                article_urls = soup.find_all('h2',class_='post-title')
                for item in article_urls:
                    url = item.find('a').get('href')
                    response = requests.get(url=url, headers=headers)
                    print("正在抓取：" + url)
                    # print(response.status_code)
                    if response.status_code == 200:
                        article = response.text
                        if article:
                            try:
                                soup = BeautifulSoup(article,'lxml')
                                # 文章标题
                                title = soup.find(class_='article-title').get_text().strip()
                                # 作者
                                author = soup.find(class_='post-meta-items').find_previous_siblings()[1].find('a').get_text().strip()
                                # 作者简介
                                author_des = soup.find(class_='post-meta-items').find_previous_siblings()[0].get_text().strip()
                                # 日期
                                date = soup.find(class_='post-meta-items').find_all(class_='post-meta-item')[0].get_text().strip()
                                # 浏览量
                                views = soup.find(class_='post-meta-items').find_all(class_='post-meta-item')[1].get_text().strip()
                                # 收藏量
                                loves = soup.find(class_='post-meta-items').find_all(class_='post-meta-item')[2].get_text().strip()
                                # 点赞量
                                zans = soup.find(class_='post-meta-items').find_all(class_='post-meta-item')[3].get_text().strip()
                                # 评论量
                                comment = soup.find('ol',class_='comment-list').find_all('li')
                                comment_num = len(comment)
                                # 正文
                                art = soup.find(class_='grap').get_text().strip()

                                writer.writerow({'title':title,'author':author,'author_des':author_des,
                                                 'date':date,'views':views,'loves':int(loves),
                                                 'zans':int(zans),'comment_num':int(comment_num),
                                                 'art':art,'url':url})

                                print({'title':title,'author':author,'author_des':author_des,
                                                 'date':date,'views':views,'loves':int(loves),
                                                 'zans':int(zans),'comment_num':int(comment_num)})
                            except:
                                print('抓取失败')

    print('抓取完毕！')










