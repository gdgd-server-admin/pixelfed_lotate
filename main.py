# -*- coding: utf8 -*-

#
# config.sample.iniをconfig.iniにリネームして中身を書いておく
# アカウント設定のページでアクセストークンを作っておく（Pixelfedの場合。他はわからない）
#
######################################

import configparser,requests,pprint,datetime,time
from dateutil import parser

print("削除を開始した")

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config["SETTING"]["TOKEN"]
URL = config["SETTING"]["URL"]
ID = config["SETTING"]["ID"]
DAYS = int(config["SETTING"]["DAYS"])

#
# config.iniの中身を読み込んだ
#
######################################

headers = {'Authorization': 'Bearer {}'.format(TOKEN)}

min_date = datetime.datetime.today().timestamp()
max_id = ""
first_id = ""

url_get_list = 'https://{}/api/v1/accounts/{}/statuses?limit=40&exclude_reblogs=true&exclude_replies=true'.format(URL,ID)

print("削除するかどうかの境界線になる日付を計算")

border_date = datetime.datetime.today().timestamp() - (86400 * DAYS)
while min_date > border_date:

    tmp_url = url_get_list
    if max_id != "":
        tmp_url = "{}&max_id={}".format(url_get_list,max_id)

    r_get = requests.get(tmp_url, headers=headers)

    r_json = r_get.json()

    for r in r_json:
        created_at = parser.parse(r["created_at"]).timestamp()
        if min_date > created_at:
            min_date = created_at
            max_id = r["id"]
    time.sleep(5)

dt = datetime.datetime.fromtimestamp(min_date)
print("{}よりも古い投稿を削除".format(dt))

#
# ここから一番古い投稿までを削除対象としてリストアップする 
#
###################################
lotate_target = []

while True:

    tmp_url = url_get_list
    if max_id != "":
        tmp_url = "{}&max_id={}".format(url_get_list,max_id)

    r_get = requests.get(tmp_url, headers=headers)

    r_json = r_get.json()

    for r in r_json:
        max_id = r["id"]
        lotate_target.append(r["id"])

    if len(r_json) < 40:
        break
    time.sleep(5)

print("削除対象の件数:{}".format(len(lotate_target)))

#
# ゆっくり消す
#
###################################

for did in lotate_target:

    url_delete = 'https://{}/api/v1/statuses/{}'.format(URL,did)
    res_d = requests.delete(url=url_delete, headers=headers)
    print("削除した投稿のID：{}".format(did))
    time.sleep(5)

print("削除が完了した")
