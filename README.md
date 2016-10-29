# Python-simple-code
#Python小代码片

##这里收集了平时编程的一些小代码片，由于Python知识零碎且多，于是就想将平时打的一些小代码收集到这里，以防忘记

包括**数据库**，**爬虫**，**文本处理**，**多线程**等等，只要是容易忘记的代码片都收集到这里

----------
##爬虫部分
    # coding=utf-8
    import sys
    import requests
    import json
    from collections import OrderedDict
    import csv
    import codecs
    reload(sys)
    sys.setdefaultencoding('utf-8')
    url = """http://japi.juhe.cn/joke/content/list.from?key=\
    d68998b6d9b1a184edd33160a6e30f82"""
    
    num = 20
    page = 100
    payload = {'page': 1, 'sort': 'asc', 'time': '1418745237', 'pagesize': num}
    res = requests.get(url, params=payload)
    jsObj = json.loads(res.text, object_pairs_hook=OrderedDict)
    xiaohua = []
    for i in range(num):
    	xiaohua.append(jsObj['result']['data'][i]['content'])
    with open('xiaohua.csv', 'w') as f:
    	f.write(codecs.BOM_UTF8) 
    	f_csv = csv.writer(f)
    	f_csv.writerow([f+'\n' for f in xiaohua])

这里有一个非常有用的技巧，就是处理中文的部分，引入下面5行代码：

    import codecs
	import sys
	reload(sys)
    sys.setdefaultencoding('utf-8')
    csvfile.write(codecs.BOM_UTF8)


----------
将来补充的
----------


#数据库部分
##使用MySQL数据库
    import MySQLdb
    import _mysql
    conn = MySQLdb.connect('localhost', 'root', 'sa', db='my_oa')
    cur = conn.cursor()
    cur.execute('select * from user_sys')
    c = cur.fetchall()

##使用SQLite3数据库
   将上面的数据存到sqlite3数据库中去

	xh = [(f,) for f in xiaohua]  #非常重要的一步
	
	类似这种格式：
	stocks = [
		('GOOG', 100, 490.1),
		('AAPL', 50, 545.75),
		('FB', 150, 7.45),
		('HPQ', 75, 33.2),
	]

	conn = sqlite3.connect('xiaohua.db')
	cur = conn.cursor()
	cur.execute("create table xiaohua(ID INTEGER PRIMARY KEY AUTOINCREMENT, 	xiaohua text)")
	conn.commit()
	cur.executemany("insert into xiaohua (xiaohua) values(?)", xh)
	conn.commit()
	row in cur.execute('select * from xiaohua'):
    	print row[1]

##使用MongoDB数据库

	for row in cur.execute('select * from xiaohua'):
    try:
        xiaohua.append({'id': row[0], 'text': row[1]}) #mongodb中必须要字典
    except Exception as e:
        continue
	client = MongoClient()
	db = client.test
	xh = db.xiaohua
	for res in xh.find():
    try:
        print res['id'], res['text']
    except Exception as e:
        continue

##使用Redis数据库
