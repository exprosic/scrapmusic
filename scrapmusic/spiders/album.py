# vim: set noet ts=4 sw=4 fileencoding=utf-8:

import os
import re
from urllib.parse import urljoin
import scrapy
import sqlite3

conn = sqlite3.connect(os.path.expanduser('~/music.db'))
def execute(stmt, *args):
	curs = conn.cursor()
	curs.execute(stmt, args)
	conn.commit()
	return curs

def getAlbums():
	for line in open('album_url.txt'):
		if line.strip().startswith('#'): continue
		if not line.startswith('http'): continue
		url = re.sub('\?.*', '', line.split()[0])
		count = execute('SELECT COUNT(*) FROM album WHERE url=?', url).fetchone()[0]
		if count == 0:
			yield url

class AlbumSpider(scrapy.Spider):
	name = 'album'
	start_urls = getAlbums()

	def parse(self, response):
		albumTitle = response.xpath('//meta[@property="og:title"]/@content').extract()[0]
		albumImage = response.xpath('//meta[@property="og:image"]/@content').extract()[0]

		albumId = execute('INSERT INTO album(url,title,image) VALUES(?,?,?)',
				response.url, albumTitle, albumImage).lastrowid

		for link in response.xpath('//tr[td/div/a[@class="song_play"]]/td[@class="song_name"]/a'):
			songTitle = link.xpath('text()').extract()[0]
			songUrl = link.xpath('@href').extract()[0]
			songUrl = urljoin(response.url, songUrl)
			execute('INSERT INTO song(url,title,albumId) VALUES(?,?,?)',
					songUrl, songTitle, albumId)
