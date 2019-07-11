# -*- coding: utf-8 -*-
import scrapy
from zhihuusers.items import UserItem
import json


class ZhuhuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_user = 'zhang-jing-88-76'
    user_include = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    followers_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}'
    followees_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followees_url ='https://www.zhihu.com/api/v4/members/{user}/followees?include={include}'


    def start_requests(self):
        yield scrapy.Request(url=self.user_url.format(user = self.start_user,include = self.user_include),callback=self.parse_user)


    def parse_user(self, response):
        date = json.loads(response.text)
        item = UserItem()

        for field in item.fields:
            if field in date.keys():
                item[field] = date.get(field)
        yield item

        yield scrapy.Request(url=self.followers_url.format(user = date.get('url_token'),include = self.followers_include,offset=0,limit=20),callback=self.parse_followers)

        yield scrapy.Request(url=self.followees_url.format(user = date.get('url_token'),include = self.followees_include,offset=0,limit=20),callback=self.parse_followees)


    def parse_followers(self, response):
        date = json.loads(response.text)
        if 'data' in date.keys():
            for info in date.get('data'):
                yield scrapy.Request(url = self.user_url.format(user=info.get('url_token'),include=self.user_include),callback=self.parse_user)

        # 获取下一页
        if 'paging' in date.keys() and date.get('paging').get('is_end') == False:
            next_page = date.get('paging').get('next')
            print(next_page)
            yield scrapy.Request(next_page,callback=self.parse_followers)

    def parse_followees(self, response):
        date = json.loads(response.text)
        if 'data' in date.keys():
            for info in date.get('data'):
                yield scrapy.Request(url=self.user_url.format(user=info.get('url_token'), include=self.user_include),callback=self.parse_user)

        # 获取下一页
        if 'paging' in date.keys() and date.get('paging').get('is_end') == False:
            next_page = date.get('paging').get('next')
            yield scrapy.Request(next_page, callback=self.parse_followees)



