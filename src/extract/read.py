# -*- coding: utf-8 -*- 



import re

#處理掉unicode 和 str 在ascii上的問題
import sys 
#import os
import psycopg2
#import datetime
#import calendar
#import csv
#import math
#from time import mktime as mktime
import cookielib, urllib2,urllib
from lxml import html,etree


reload(sys) 
sys.setdefaultencoding('utf8') 

class READSITE:
	address = None
	content = None
	cj = None
	opener = None

	database=""
	user=""
	password=""
	host=""
	port=""
	conn = None
	table = "cnyes"
	conn = None

	def __init__(self,website,filepath):
		self.address = website
		f = open(filepath,'r')
		self.database = f.readline()[:-1]
		self.user = f.readline()[:-1]
		self.password = f.readline()[:-1]
		self.host = f.readline()[:-1]
		self.port =f.readline()[:-1]
		f.close()

	def rebuildTable():
		print '執行重建Table'
		os.system('psql -d %s -f %s'%(self.database,sql))

	def listLink(self):
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		#self.opener.addheaders = [('Host', 'news.cnyes.com')]
		#self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')]
		r = self.opener.open(self.address)
		self.content = r.read()		
		r.close()

	def startDB(self):
		self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)

	def endDB(self):	
		self.conn.close()

	def parse(self):
		page = html.fromstring(self.content)
		i = 0
		cur = self.conn.cursor()	
		for link in page.xpath('//*[@id="container"]//*[@class="list_1 bd_dbottom"]//li/a'):			
			datatime = link.xpath('../span')[0].text
			typ = link.xpath('../strong/a')[0].text.translate({ord(i):None for i in '[]'})
			print "type: %s datatime: %s"%(typ,datatime)
			i=i+1
			address = link.get("href")
			print "%d Name: %s URL: %s"%(i,link.text,address)
			#補上某些網址不齊
			if address[0:4] != 'http':				
				address = 'http://news.cnyes.com/'+address
			l = urllib.quote(address.encode('utf-8'),safe=':/?=')		

			(author,datetime,title,info,fulltext) = self.read(l,typ)
			sql = "INSERT INTO "
			#break
		cur.close()


	def read(self,address,category):			
		try:
			print address
			r = self.opener.open(address)
			
			page = html.fromstring(r.read())		
			r.close()
			title = page.xpath('//*[@class="newsContent bg_newsPage_Lblue"]/h1')[0].text
			info = page.xpath('//*[@class="newsContent bg_newsPage_Lblue"]/span[@class="info"]')[0].text
			print info
			
			year,month,day,hour,mins = re.match(".*(\d{4})-(\d{2})-(\d{2})\W*(\d{2}):(\d{2})", info,re.U).group(1,2,3,4,5)
			datetime = "%s-%s-%s %s:%s"%(year,month,day,hour,mins)
			if re.match(u"鉅亨網新聞中心",info,re.U) is not None:
				author = "新聞中心"
			else:
				author = re.match(u".+記者(\w+)\W+.+",info,re.U).group(1)
			print author

			#print "%04d-%02d-%02d %02d:%02d"%(int(year),int(month),int(day),int(hour),int(mins))
			article = page.xpath('//*[@id="newsText"]/p')
			fulltext =''
			for a in article:
				if a.text is not None:
					fulltext = fulltext + "\n"+a.text
			print "title:%s\n gg:%s\n article:\n%s\n"%(title,info,fulltext)
			print "\n\n\n"
			return (author,datetime,title,info,fulltext)
		except Exception as e:
			print e
		

if __name__ == '__main__':
	worker = READSITE('http://news.cnyes.com/tw_bank/list.shtml','../../link.info')
	worker.rebuildTable('../../sql/cnYes.sql')
	worker.listLink()
	worker.parse()

