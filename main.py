# -*- coding: utf-8 -*-


__author__ = 'shaw'

import random
import time

import requests


x_relation_tag_url = 'https://api.bilibili.com/x/relation/tag'
x_relation_tags_url = 'https://api.bilibili.com/x/relation/tags'
x_relation_tags_addUsers_url = 'https://api.bilibili.com/x/relation/tags/addUsers'
x_space_wbi_arc_search_url = 'https://api.bilibili.com/x/space/wbi/arc/search'
my_uid = 13589200
cookie_str = r""
headers = {
    'referer': 'https://space.bilibili.com/13589200/fans/follow?tagid=-2',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}


def cookie_str_2_jar(cookie_str):
    """
    cookie字符串转cookiejar
    """
    cookie_dict = {}
    for item in cookie_str.split(';'):
        item_kv = item.split('=')
        key = item_kv[0].strip()
        if len(item_kv) == 1:
            cookie_dict[key] = ''
        else:
            cookie_dict[key] = item_kv[1].strip()
    return requests.utils.cookiejar_from_dict(cookie_dict)


def get_my_follow_groups():
    """
    获取我的关注分组
    :return:
    """
    cookies = cookie_str_2_jar(cookie_str)

    resp = requests.get(x_relation_tags_url, headers=headers, cookies=cookies)
    json = resp.json()

    if json['code'] != 0:
        print('获取我的关注分组失败: %s' % json['message'])
        return None

    return json['data']


def get_my_follows_by_tag(tagid, pn):
    """
    获取我关注的指定分组的用户
    :return:
    """
    params = {
        'mid': my_uid,
        'tagid': tagid,
        'pn': pn,
        'ps': 20
    }
    cookies = cookie_str_2_jar(cookie_str)

    time.sleep(random.randint(0, 2))

    resp = requests.get(x_relation_tag_url, params=params, headers=headers, cookies=cookies)
    json = resp.json()

    if json['code'] != 0:
        print('获取我的未分组的关注用户失败: %s' % json['message'])
        return None
    return json['data']


def get_user_max_count_tag(mid):
    """
    获取指定用户视频投稿数量最多分区
    :param mid:
    :return:
    """
    params = {'mid': mid}
    cookies = cookie_str_2_jar(cookie_str)

    time.sleep(random.randint(0, 2))

    resp = requests.get(x_space_wbi_arc_search_url, params=params, headers=headers, cookies=cookies)
    json = resp.json()

    if json['code'] != 0:
        print('获取指定用户视频投稿数量最多分区失败: %s' % json['message'])
        return None

    tlist = json['data']['list']['tlist']
    if tlist is None or len(tlist) == 0:
        print('用户没有视频投稿')
        return None

    max_count_tag = {'count': 0}
    for tag_tid in tlist:
        tag = tlist[tag_tid]
        tag_count = tag['count']
        if tag_count > max_count_tag['count']:
            max_count_tag = tlist[tag_tid]

    return max_count_tag


def set_user_in_my_follow_group(mid, tagid):
    """
    设置用户到我的关注分组
    :param mid:
    :param tagid:
    :return:
    """
    params = {'cross_domain': 'true'}
    data = {
        'fids': mid,
        'tagids': tagid,
        'csrf': 'd049e0b89124b570194bda4c3cf5177c'
    }
    cookies = cookie_str_2_jar(cookie_str)

    time.sleep(random.randint(0, 2))

    resp = requests.post(x_relation_tags_addUsers_url, data=data, params=params, headers=headers, cookies=cookies)
    json = resp.json()

    if json['code'] != 0:
        print('设置用户到我的关注分组失败: %s' % json['message'])
        return
    print('设置用户到我的关注分组成功')


def handle(my_follow_groups, tagid, pn, tags_not_in_my_follow):
    # 获取我关注的指定分组的用户
    follows = get_my_follows_by_tag(tagid, pn)

    for follow in follows:
        print('--------------------------------')

        uname = follow['uname']
        mid = follow['mid']
        print('用户: uname=%s, mid=%s' % (uname, mid))

        tag = get_user_max_count_tag(mid)
        if tag is None:
            continue

        tid = tag['tid']
        tag_name = tag['name']
        tag_count = tag['count']
        print('视频投稿数量最多分区: name=%s, tid=%s, count=%s' % (tag_name, tid, tag_count))

        # 匹配该用户视频投稿数量最多分区名称与我的关注分组名称
        tagid = 0
        for group in my_follow_groups:
            if tag_name == group['name']:
                tagid = group['tagid']
                break
        print('对应我的关注分组id: %s' % tagid)

        if tagid == 0:
            print('我的关注分组中没有: %s' % tag_name)
            tags_not_in_my_follow.add(tag_name)
            continue

        # 设置用户到我的关注分组
        set_user_in_my_follow_group(mid, tagid)


if __name__ == '__main__':
    tags_not_in_my_follow = set()

    tagid = 0

    # 获取我的关注分组
    my_follow_groups = get_my_follow_groups()
    for i in range(1):
        handle(my_follow_groups, tagid, i + 1, tags_not_in_my_follow)

    print('我的关注分组中缺少的: %s' % tags_not_in_my_follow)
