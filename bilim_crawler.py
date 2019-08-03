import scrapy
from w3lib.html import remove_tags, replace_tags
from datetime import datetime

class BilimOrgSpider(scrapy.Spider):
    name = 'bilim.org crawler'
    BASE_URL = 'https://www.bilim.org'
    start_urls = [BASE_URL]

    def parse(self, response):
        max_page_count = int(response.xpath('//*[@class="page-numbers"]/text()').getall()[-1])
        URLs = [f"{self.BASE_URL}/page/{i}/" for i in range(1, max_page_count+1)]
        print(len(URLs))
        for URL in URLs:
            request = scrapy.Request(URL, callback=self.parse_page)
            yield request

    def parse_page(self, response):
        docs_URLs = response.xpath('//article/header/div[@class="article__featured-image"]/a/@href').getall()

        for doc_URL in docs_URLs:
            request = scrapy.Request(doc_URL, callback=self.parse_doc)
            yield request

    def parse_doc(self, response):
        article_url = response.url
        article_title_image_data_lazy_src_url = response.xpath('//article/header/div[1]/img/@data-lazy-src').get()
        article_title = response.xpath('//article/header/h1/text()').get()
        article_author_name = response.xpath('//article/header/div[3]/div/div/span[@class="article__author-name"]/*[@class="vcard author"]/*[@class="url fn"]/text()').get()
        article_author_profile_url = response.xpath('//article/header/div[3]/div/div/span[@class="article__author-name"]/*[@class="vcard author"]/*[@class="url fn"]/@href').get()
        article_published_datetime = response.xpath('//article/header/div[3]/div/div/time/span/abbr/@title').get()
        article_comments_count = int(response.xpath('//article/header/div[3]/div/div/*[@class="article__comments-number"]/text()').get())
        article_comments_url = response.url+response.xpath('//article/header/div[3]/div/div/*[@class="article__comments-number"]/@href').get()
        article_links = [{'text':text, 'url':url} for text, url in zip(response.xpath('//article/section//a[contains(@href, "")]/text()').getall(), response.xpath('//article/section//a[contains(@href, "")]/@href').getall())]
        article_categories = [{'category':text, 'category_url':url} for text, url in zip(response.xpath('//article/footer/div[@class="meta--categories btn-list  meta-list"]/a[@class="btn  btn--small  btn--tertiary"]/text()').getall(), response.xpath('//article/footer/div[@class="meta--categories btn-list  meta-list"]/a[@class="btn  btn--small  btn--tertiary"]/@href').getall())]
        article_tags = [{'tag':text, 'tag_url':url} for text, url in zip(response.xpath('//article/footer/div[@class="meta--tags  btn-list  meta-list"]/a[@class="btn  btn--small  btn--tertiary"]/text()').getall(), response.xpath('//article/footer/div[@class="meta--tags  btn-list  meta-list"]/a[@class="btn  btn--small  btn--tertiary"]/@href').getall())]
        article_text = replace_tags(remove_tags(response.xpath('//article/section').get(), which_ones=('<a>')), token='\n').strip()
        
        article_comments = []
        for r in response.xpath('//article/div[@id="comments"]/ol[@class="commentlist"]/li'):
            comment_number = int(r.xpath('article[@id="comment-"]/span[@class="comment-number"]/text()').get())
            comment_avatar_media_img_data_lazy_src_url = r.xpath('article[@id="comment-"]/aside[@class="comment__avatar  media__img"]/img/@data-lazy-src').get()
            comment_author_name = r.xpath('article[@id="comment-"]/div[@class="media__body"]/header/span[@class="comment__author-name"]/text()').get()
            comment_datetime = r.xpath('article[@id="comment-"]/div[@class="media__body"]/header/time[@class="comment__time"]/@datetime').get()
            comment_url = response.url+r.xpath('article[@id="comment-"]/div[@class="media__body"]/header/div[@class="comment__links"]/a[@class="comment-reply-link"]/@href').get()
            comment_text = replace_tags(remove_tags(r.xpath('article[@id="comment-"]/div[@class="media__body"]/section[@class="comment__content comment"]').get(), which_ones=('<a>')), token='\n').strip()
            
            comment = {
                'comment_number' : comment_number, 
                'comment_avatar_media_img_data_lazy_src_url' : comment_avatar_media_img_data_lazy_src_url, 
                'comment_author_name' : comment_author_name, 
                'comment_datetime' : comment_datetime, 
                'comment_url' : comment_url, 
                'comment_text' : comment_text,
            }
            article_comments.append(comment)

        yield {
            'accessed_at' : datetime.now().isoformat(),
            'article_url' : article_url,
            'article_title_image_data_lazy_src_url' : article_title_image_data_lazy_src_url, 
            'article_title' : article_title,
            'article_author_name' : article_author_name,
            'article_author_profile_url' : article_author_profile_url,
            'article_published_datetime' : article_published_datetime,
            'article_comments_count' : article_comments_count,
            'article_comments_url' : article_comments_url,
            'article_comments' : article_comments,
            'article_links' : article_links,
            'article_categories' : article_categories,
            'article_tags' : article_tags,
            'article_text' : article_text,
        }
        # for article in response.xpath('//article').getall():
        #     print(article)
        #     print('\n\n\n')