#!/usr/bin/python3

import time
import requests
import urllib
from bs4 import BeautifulSoup
import json

COOKIE = None

# cookie名称
COOKIE_NAME = "sass_gym_shop_owner"

LOGIN_URL = "https://www.styd.cn/cm/c1680b71/user/bind"
HEAD = {"Content-Type": "application/x-www-form-urlencoded", "Connection": "keep-alive"}

def smsCode(mobile, img_captcha):
    public_key = "2868e6ba58d82517dd34b722f6be9b84"
    source = "wx"
    timestamp = int(time.time())
    data = urllib.parse.urlencode(
        {"public_key": public_key,
         "source": source,
         "timestamp": timestamp,
         "img_captcha": img_captcha,
         "mobile": mobile}
    ).encode(encoding='utf-8')
    res = requests.post("https://www.styd.cn/web/user/get_captcha", data=data, headers=HEAD)
    print("打印获取短信返回信息 %s" % (res.content.decode('unicode_escape')))

def login(mobile, captcha):
    data = urllib.parse.urlencode({"mobile": mobile, "captcha": captcha}).encode(encoding='utf-8')
    res = requests.post(LOGIN_URL, data=data, headers=HEAD)
    cookie = res.cookies[COOKIE_NAME]
    COOKIE = res.cookies
    print("打印登录返回信息 %s" % (res.content.decode('unicode_escape')))
    print("打印cookie信息 %s" % (cookie))

def search(storeId, date):
    result = requests.get(
        "https://www.styd.cn/cm/c1680b71/default/search?date=" + date + "&shop_id=" + storeId.__str__() + "&type=1",
        cookies=COOKIE, headers=HEAD)
    soup = BeautifulSoup(result.content, 'lxml')
    print("获取返回数据 %s" % (soup.get_text()))
    tags = soup.find_all("a")
    t = tags.pop()
    print("获取返回单节点所有属性值 %s" % (t.attrs))
    id = t['href'][34: -2]
    print("获取单车教练ID %s" % (id))
    return id


def submit(cardId, id, num):
    data = urllib.parse.urlencode({"class_type": 1, "class_id": id, "team_mc_id": cardId, "seat_number[]": num}).encode(
        encoding='utf-8')
    res = requests.post("https://www.styd.cn/cm/c1680b71/course/order_confirm", data=data, cookies=COOKIE, headers=HEAD)
    print("打印抢单车号返回信息 %s" % (res.content.decode('unicode_escape')))
    try:
        data = json.loads(res.content.decode('unicode_escape'))
        code = data['code']
        if(code != -1):
            return True
        return False
    except Exception:
        return False


# 菲特各店ID
FIT_STORE = {
    "洸河店": 178296502,
    "金菲特": 583983501,
    "万达店": 408459720,
    "新体店": 335795635,
    "济安桥店": 178548038,
    "龙行店": 178476921,
    "冠亚店": 178428313,
    "秀水店": 178400587,
    "古槐店": 178383949
}