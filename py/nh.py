from lxml import etree
import requests
from time import time
from multiprocessing.pool import ThreadPool
import os

def get_binary(url):
	r = requests.get(url)
	if r.status_code == 200:
		return r
	else:
		return get_binary(url)

def download(entry):
	path, uri = entry
	if not os.path.exists(path):
		r = requests.get(uri, stream=True)
		if r.status_code == 200:
			with open(path, ‘wb’) as f:
				for chunk in r:
					f.write(chunk)
				return ‘已下载’
		return download(entry)
	return ‘图片已存在！’

def get_html(entry):
	xpath, uri, i = entry
	r = requests.get(uri)
	if r.status_code == 200:
		h = r.content
		sel = etree.HTML(h)
		return [sel.xpath(xpath), i]
	return get_html(entry)

while True:
	book_id = input(‘请输入BOOK_ID（输入”end”退出）：’)
	if book_id == ‘end’:
		break

	url = ‘https://nhent.ai/g/‘ + book_id

	code = 0
	while code != 200:
		response = requests.get(url)
		code = response.status_code
	html = response.content
	selector = etree.HTML(html)
	rez = selector.xpath(“//body/div[2]/div/div[2]/div/div[1]/text()”)
	name = selector.xpath(“//body/div[2]/div/div[2]/div/h2/text()”)

	yn = input(‘您是否要下载\n’+name[0]+’\n(y/n)：’)
	if yn == ‘n’:
		continue

	print(‘共’+(rez[0])[:-6]+’页’)

	urls = []
	for i in range(1, int((rez[0])[:-6])+1):
		urls.append(tuple([“//body/div[2]/div/section[2]/a/img/attribute::src”, ‘https://nhent.ai/g/‘ + book_id + ‘/‘ + str(i), i]))
	
	results = ThreadPool(8).imap_unordered(get_html, urls)

	if not os.path.exists(str(book_id)):
		os.mkdir(str(book_id))

	print(‘开始获取图片信息’)
	fin_urls = []
	for res in results:
		ext = ‘.png’ if ‘.png’ in url else ‘.jpg’
		fin_urls.append(tuple([book_id+”/“+str(res[1])+ext, (res[0])[0]]))

	results = ThreadPool(8).imap_unordered(download, fin_urls)

	print(‘开始下载’)
	start = time()
	i = 1
	for path in results:
		print(path+str(i))
		i += 1
	print(f”下载总耗时： {time() - start} 秒”)