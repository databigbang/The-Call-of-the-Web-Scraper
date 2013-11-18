#!/usr/bin/python

import urllib2
import urlparse
import lxml.html
from Queue import Queue
from threading import Thread
from downloader import Downloader

NWORKERS = 25

search = 'http://www.xeno-canto.org/browse.php?query=+cnt%3A"Nepal"&view=0&pg='

print "Starting."

downloaded_calls = set()
Downloader = Downloader(NWORKERS, "xeno-canto")

def get_sounds(url):
	print url
	result = urllib2.urlopen(url).read()
	root = lxml.html.fromstring(result)
	nodes = root.xpath("//table[@class='results']/tr")

	for node in nodes:
		download_url = node.xpath(".//a[contains(@href, 'download')]")[0].attrib["href"]
#		download_url = node.xpath(".//a[contains(@href, 'download')]")

		full_download_url = urlparse.urljoin(url, download_url)

		if full_download_url in downloaded_calls:
			continue

		downloaded_calls.add(full_download_url)

		p = urlparse.urlparse(full_download_url)
		qa = urlparse.parse_qs(p.query)
		code = qa['XC'][0]

		selected_rating = node.xpath(".//li[@class='selected']/span")
		rating = ""
		if selected_rating != None and len(selected_rating) != 0:
			rating = selected_rating[0].text_content()

		common_name = node.xpath(".//span[@class='common-name']")[0].text_content()
#		common_name = node.xpath(".//span[@class='common-name']")

		scientific_name = node.xpath(".//span[@class='scientific-name']")[0].text_content()
#		scientific_name = node.xpath(".//span[@class='scientific-name']")

#		location = node.xpath(".//a[starts-with(@href,'/location')]")[0].text_content()
		location2 = node.xpath("td[7]")[0].text_content().strip()
		location1 = node.xpath("td[8]")[0].text_content().strip()
		location = location1 + "_" + location2
		print location1
		print location2

		description = node.xpath("td[10]")[0].text_content()

		description = description.strip().lower()

		Downloader.put({'commonName':common_name, 'scientificName':scientific_name, 'downloadURL':full_download_url, 'rating':rating, 'code':code, 'location':location, 'description':description})

#		print common_name, scientific_name, download_url, code, rating
	

def main_loop():
	Downloader.start()

	page = 1
	while True:
		print "page:", page
		result = urllib2.urlopen(search + str(page)).read()

		root = lxml.html.fromstring(result)

		nodes = root.xpath("//span[@class='common-name']")

		if len(nodes) == 0:
			break

		for node in nodes:
			anchor = node.xpath("./a")[0]
			text = anchor.text_content()
			href = anchor.attrib["href"]
			url = urlparse.urljoin(search, href)
			get_sounds(url)
#			print "*****************"
#			break

		page += 1
#		break

	Downloader.end()
	Downloader.wait_for_pending_workers()

main_loop()

print "Finished."
