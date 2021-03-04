#!/usr/bin/python3

import requests
import urllib
from bs4 import BeautifulSoup
import json

# cookie名称
COOKIE_NAME = "sass_gym_shop_owner"

LOGIN_URL = "https://www.styd.cn/cm/c1680b71/user/bind"
HEAD = {"Content-Type": "application/x-www-form-urlencoded", "Connection": "keep-alive"}


def smsCode(cookie ,mobile, img_captcha):
    result = requests.get("https://www.styd.cn/cm/c1680b71/user/bind")
    soup = BeautifulSoup(result.content, 'lxml')
    public_key = soup.find_all('input', attrs={'name': 'public_key'})
    timestamp = soup.find_all('input', attrs={'name': 'timestamp'})
    public_key = public_key.pop(0)['value']
    source = 'wx'
    timestamp = timestamp.pop(0)['value']
    data = urllib.parse.urlencode(
        {"mobile": mobile,
         "timestamp": timestamp,
         "public_key": public_key,
         "source": source,
         "img_captcha": img_captcha,
         }
    ).encode(encoding='utf-8')
    header = {"Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "origin": "https://www.styd.cn",
            "referer": "https://www.styd.cn/cm/c1680b71/user/bind",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Mobile Safari/537.36 FS"}
    res = requests.post("https://www.styd.cn/web/user/get_captcha", data=data, cookies=cookie, headers=header)
    print("打印获取短信返回信息 %s" % (res.content.decode('unicode_escape')))


def login(mobile, captcha):
    data = urllib.parse.urlencode({"mobile": mobile, "captcha": captcha}).encode(encoding='utf-8')
    res = requests.post(LOGIN_URL, data=data, headers=HEAD)
    cookie = res.cookies[COOKIE_NAME]
    print("打印登录返回信息 %s" % (res.content.decode('unicode_escape')))
    print("打印cookie信息 %s" % (cookie))
    return res.cookies


def search(cookie, storeId, date):
    result = requests.get(
        "https://www.styd.cn/cm/c1680b71/default/search?date=" + date + "&shop_id=" + storeId.__str__() + "&type=1",
        cookies=cookie, headers=HEAD)
    soup = BeautifulSoup(result.content, 'lxml')
    print("获取返回数据 %s" % (soup.get_text()))
    tags = soup.find_all("a")
    t = tags.pop()
    print("获取返回单节点所有属性值 %s" % (t.attrs))
    id = t['href'][34: -2]
    print("获取单车教练ID %s" % (id))
    return id


def submit(cookie, cardId, id, num):

    header = {"Content-Type": "application/x-www-form-urlencoded",
     "Connection": "keep-alive",
     "origin": "https://www.styd.cn",
     "referer": "https://www.styd.cn/cm/c1680b71/course/seat?id=" + id + "&fee_type=0",
     "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Mobile Safari/537.36 FS"}

    data = urllib.parse.urlencode({"class_type": 1, "class_id": id, "team_mc_id": cardId, "seat_number[]": num}).encode(
        encoding='utf-8')
    res = requests.post("https://www.styd.cn/cm/c1680b71/course/order_confirm", data=data, cookies=cookie, headers=header)
    print("打印抢单车号返回信息 %s" % (res.content.decode('unicode_escape')))
    try:
        data = json.loads(res.content.decode('unicode_escape'))
        code = data.get("code")
        if code == 200 or code == '200':
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
