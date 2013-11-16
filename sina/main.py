#! /usr/bin/python
# coding=utf-8
import time
from sina.csv_encoder import UnicodeWriter, UnicodeReader

__author__ = "cysnake4713"
"""
引入Python SDK的包
"""

import weibo


'''
授权需要的三个信息，APP_KEY、APP_SECRET为创建应用时分配的，CALL_BACK在应用的设置网页中
设置的。【注意】这里授权时使用的CALL_BACK地址与应用中设置的CALL_BACK必须一致，否则会出
现redirect_uri_mismatch的错误。
'''

APP_KEY = '454121325'
APP_SECRET = '322ff921d12c1925c7e03dc4e1cfc4e3'
CALL_BACK = 'http://cysnake.com'

access_token = "2.00Dzy4zB0Vh8jU100fdb0406AEWCSB"
expires_in = "1541262699"
#access_token = ""
#expires_in = ""


def get_token():
    #weibo模块的APIClient是进行授权、API操作的类，先定义一个该类对象，传入参数为APP_KEY, APP_SECRET, CALL_BACK
    client = weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
    #获取该应用（APP_KEY是唯一的）提供给用户进行授权的url
    auth_url = client.get_authorize_url()
    #打印出用户进行授权的url，将该url拷贝到浏览器中，服务器将会返回一个url，该url中包含一个code字段（如图1所示）
    print "auth_url : " + auth_url
    #输入该code值（如图2所示）
    code = raw_input(u"请输入code: ")
    #通过该code获取access_token，r是返回的授权结果，具体参数参考官方文档：
    # http://open.weibo.com/wiki/Oauth2/access_token
    r = client.request_access_token(code)
    #将access_token和expire_in设置到client对象
    print("access_token : %s\n expires_in : %s" % (r.access_token, r.expires_in))
    return (r.access_token, r.expires_in)
    #以上步骤就是授权的过程，现在的client就可以随意调用接口进行微博操作了，下面的代码就是用用户输入的内容发一条新微博


def get_client(access_token, expires_in):
    #weibo模块的APIClient是进行授权、API操作的类，先定义一个该类对象，传入参数为APP_KEY, APP_SECRET, CALL_BACK
    client = weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
    client.set_access_token(access_token, expires_in)
    return client


def get_friends(client, uid=None, name=None, count=200):
    all_users = set()
    flag = True
    cursor = 0
    while flag:
        if uid is None:
            friends = client.friendships.friends.get(screen_name=name, count=count, cursor=cursor)
        else:
            friends = client.friendships.friends.get(uid=uid, count=count, cursor=cursor)
        cursor += count
        users = [(u['id'], u['name']) for u in friends['users']]
        all_users = all_users | set(users)
        if friends['next_cursor'] == 0:
            flag = False

    return all_users


def friends_list_to_file(client, file_name, path=""):
    file = open(path + file_name, 'w')
    file_no_dup = open(path + "no_dup" + file_name, 'w')

    users = []
    users = users + [(u[0], u[1], u"王富海规划") for u in get_friends(client, name=u"王富海规划")]
    users = users + [(u[0], u[1], u"中国城市规划设计研究院深圳分院") for u in get_friends(client, name=u"中国城市规划设计研究院深圳分院")]
    users = users + [(u[0], u[1], u"深圳市城市规划设计研究院") for u in get_friends(client, name=u"深圳市城市规划设计研究院")]

    users_set = set([(u[0], u[1]) for u in users])

    csv_file = UnicodeWriter(file)
    csv_no_dup_file = UnicodeWriter(file_no_dup)
    csv_file.writerows(users)
    csv_no_dup_file.writerows(users_set)
    file.close()


def from_point_get_vendor(client, users, out_file_name, count=150, cursor=0, path=""):
    #get vendor
    end = cursor + count if cursor + count < len(users) else len(users)
    friends_ids = [int(u[0]) for u in users]
    out_file = open(path + out_file_name, 'a')
    csv_file = UnicodeWriter(out_file)
    for i in range(cursor, end):
        user = users[i]
        print ("cursor: %s" % (i))
        try:
            relations = [[int(user[0]), u[0]] for u in get_friends(client, name=user[1]) if u[0] in friends_ids]
            csv_file.writerows(relations)
        except weibo.APIError, e:
            if e.error_code == 10023:
                print ("cursor: %d   out of limit!:%s" % (i, e.error))
                time.sleep(3600)
                relations = [[int(user[0]), u[0]] for u in get_friends(client, name=user[1]) if u[0] in friends_ids]
                csv_file.writerows(relations)
        except Exception, e:
            print("cursor: %d   error!:%s" % (i, e))

        out_file.flush()

    out_file.close()


def from_friend_get_relation(client, in_file_name, out_file_name, cursor_start, path="", count=150, timer=3600):
    file = open(path + in_file_name, 'r')
    in_file = UnicodeReader(file)
    users = []
    for user in in_file:
        users += [user]
    file.close()
    cursor = cursor_start
    while cursor < len(users):
        from_point_get_vendor(client, users, out_file_name=out_file_name, count=count, cursor=cursor)
        cursor += count


if __name__ == "__main__":
    point_file_name = 'no_duppoint.csv'
    edge_file_name = 'edgetttt.csv'
    user_relation = []
    if not (access_token or expires_in):
        #get token first time
        (access_token, expires_in) = get_token()
    else:
        client = get_client(access_token, expires_in)
        #get friends csv
        #friends_list_to_file(client, point_file_name)

        #get relationship list
        #from_friend_get_relation(client, in_file_name=point_file_name, out_file_name=edge_file_name, cursor_start=768,
        #                         count=1500,
        #                         timer=3660)

        get_friends(client,uid="2428951434")
