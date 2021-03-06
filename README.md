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

----------
#分词

使用结巴分词，并将结果可视化

    import jieba
    from wordcloud import WordCloud 
    
    f = open(u'天龙八部.txt','r').read()
    s = {}
    f = jieba.cut(f)
    for w in f:
    	if len(w) > 1:
    		previous_count = s.get(w,0)
    		s[w] = previous_count+1
    
    word = sorted(s.items(),key=lambda (word,count):count, reverse = True)
    word = word[1:100]
    #print word[:100]
    wordcloud = WordCloud(font_path = 'MSYH.TTF').fit_words(word)
    import matplotlib.pyplot as plt
    plt.imshow(wordcloud) 
    plt.axis("off")
    plt.show()

----------
# 机器学习读取数据集

    IMAGE_SIZE = 32
    
    
    def load_images():
    	"""
    	Returns a tuple made of an array of 18 (types) datasets of the shape 
    	(len(type_image), IMAGE_SIZE, IMAGE_SIZE, 3), another array that has 
    	the labels (Pokemon type), and an array made of the name of the Pokemon
    	"""
    	labels = []
    	pokemon_name = []
    	image_index = 0
    	# 714 because the Flying Pokemon were removed
    	dataset = np.ndarray(shape=(714, IMAGE_SIZE, IMAGE_SIZE, 3),
    	dtype=np.float32)
    	# Loop through all the types directories
    	for type in os.listdir('./Images/data'):
    		type_images = os.listdir('./Images/data/' + type + '/')
	    	# Loop through all the images of a type directory
	    	for image in type_images:
			    image_file = os.path.join(os.getcwd(), 'Images/data', type, image)
			    pokemon_name.append(image)
			    # reading the images as they are; no normalization, no color editing
			    image_data = (ndimage.imread(image_file, mode='RGB'))
			    if image_data.shape != (IMAGE_SIZE, IMAGE_SIZE, 3):
			    	raise Exception('Unexpected image shape: %s %s' % (str(image_data.shape), image_file))
			    dataset[image_index, :, :] = image_data
			    image_index += 1
			    labels.append(type)
    
    	return (dataset, labels, pokemon_name)



# Python中的多线程与多进程

----------
## 一直在搞Python的爬虫编程，在起初的时候，爬虫很小，也就看不到多进程的意义。随着爬虫的进阶，需要爬的东西越来越多，也就需要了多线程的支持。我们一步一步地来看爬虫多线程。

### 爬虫初体验

    import requests
    import os
    from urllib.request import urlretrieve
    def download(url):
    	filename = os.path.basename(url)
    	urlretrieve(url,filename)
    	print('finished download {filename}'.format(filename=filename))
    if __name__ == '__main__':
    	urls=["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]*3
    	for url in urls:
    			download(url)

上面就是一个再简单不过的一个小爬虫，我选取的就是美国的一些文件，至于后面为什么要*3，我想大家都懂得。
在我的机器上，运行时间是16.6s。

### 第一步，看一下多线程爬虫

    import requests
    from multiprocessing import Pool
    import os
    from urllib.request import urlretrieve
    from time import sleep
    def download(url):
    	filename = os.path.basename(url)
    	urlretrieve(url,filename)
    	print('finished download {filename}'.format(filename=filename))
    if __name__ == '__main__':
    	urls=["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
    		"http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]*3
    	pool = Pool(processes=6)
    	pool.map(download,urls)

这是一个简单的多线程爬虫，运行时间是6.2s，缩减时间为一半还多。线程中的6是我自己随便写的，一半为电脑核的个数加1即可。

### 下载带有打印进度条的功能:

    import sys
    import os
    import urllib.request
    def _print_download_progress(count, block_size, total_size):
	    pct_complete = float(count * block_size) / total_size
	    msg = "\r- Download progress: {0:.1%}".format(pct_complete)
	    sys.stdout.write(msg)
	    sys.stdout.flush()
    def maybe_download(url, download_dir):
	    filename = url.split('/')[-1]
	    file_path = os.path.join(download_dir, filename)
	    if not os.path.exists(file_path):
	    	if not os.path.exists(download_dir):
	    		os.makedirs(download_dir)
	    	file_path, _ = urllib.request.urlretrieve(url=url,
	      												filename=file_path,
	      												reporthook=_print_download_progress)
	    
	    print()
	    print("Download finished.")
    if __name__ == '__main__': 
	    data_url = "https://s3.amazonaws.com/cadl/models/vgg16.tfmodel"
	    data_dir = "vgg/"
	    maybe_download(url=data_url, download_dir=data_dir)
	    
### 获取图像的额外信息
在Python中，PIL库封装了大量的信息，其中包括exif信息，通过exif信息我们可以知道各种各样的信息，比如拍摄时间，拍摄系统，拍摄地点，以及其他。

	def geoPic(file):
	    img = Image.open(file)
	    exif_date = img._getexif()
	    ###信息参数 http://www.exiv2.org/tags.html
	    # for k in sorted(exif_date):
	    #     print(str(k)+'  >   '+str(exif_date[k]))
	
	    DataTime_ = exif_date[306]
	    """2015:05:31 11:31:21"""
	    data_, time_ = DataTime_.split(' ')
	    data_ = '{}年{}月{}日'.format(*data_.split(':'))
	    time_ = '{}时{}分{}秒'.format(*time_.split(':'))
	    GPSInfo = exif_date[34853]
		###这段代码是将照片中的经纬度分数形式转换成小数形式。
	    def dms2de(dms):
	        de = dms[0][0] / dms[0][1] \
	             + dms[1][0] / dms[1][1] \
	             + dms[2][0] / dms[2][1]
	        if GPSInfo[1] in ('W', 'S'):
	            de *= -1
	        return de
	
	    try:
	        lat, lng = dms2de(GPSInfo[2]), dms2de(GPSInfo[4])
	        return data_, time_, lat, lng
	    except:
	        return None
		
### 函数时间计算装饰器
    
	    def timeit(method):
	    def timed(*args, **kw):
		ts = time.time()
		result = method(*args, **kw)
		te = time.time()
		print(te - ts)
		return result

	    return timed
