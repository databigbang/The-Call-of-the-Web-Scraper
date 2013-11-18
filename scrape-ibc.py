#!/usr/bin/python

import urllib2
import urlparse
import lxml.html
import os.path
from Queue import Queue
from threading import Thread
from downloader import Downloader
import time

NWORKERS = 25

search = 'http://ibc.lynxeds.com/locality/oriental/nepal'

print "Starting."

downloaded_calls = set()

Downloader = Downloader(NWORKERS, "ibc")
def get_sounds(url, data):
	failed = True

	while failed:
		failed = False
		try:
			page = urllib2.urlopen(url).read()
		except urllib2.URLError:
			failed = True
			print "FAILED at:", url
			time.sleep(3)

	root = lxml.html.fromstring(page)

	all_sounds = root.xpath("//div[@id='sound-list']/div/a[@class='media-total']")[0].attrib["href"]
	all_sounds_url = urlparse.urljoin(url,all_sounds)

	print all_sounds_url

	failed = True
	while failed:
		failed = False
		try:
			sounds_page = urllib2.urlopen(all_sounds_url).read()
		except urllib2.URLError:
			print "FAILED at", all_sounds_url
			failed = True
			time.sleep(3)

	root = lxml.html.fromstring(sounds_page)

	sound_nodes = root.xpath("//div[@id='sound-list']/div/div/ul/li")
	print "===>Sounds #", len(sound_nodes)
	for node in sound_nodes:
		flash_vars = node.xpath("./object/param[@name='FlashVars']")
		if len(flash_vars) != 0:
			qs = node.xpath("./object/param[@name='FlashVars']")[0].attrib["value"]
#		song_url = urllib2.unquote(encoded_song_url)
			song_url = urlparse.parse_qs(qs)['song_url'][0]
		else:
			song_url = node.xpath("./span[@class='audio']/a")[0].attrib["href"]

		print "***********",song_url,"*********"
		if song_url in downloaded_calls:
			continue

		downloaded_calls.add(song_url)

		location = node.xpath("./a[starts-with(@href, '/locality')]")

		location_str = ""

		f = True
		for l in location:
			if not f:
				location_str += "_"
			location_str += l.text_content()
			f = False

		print location_str

		description = node.xpath("./a[starts-with(@href,'/sound')]")[0].text_content()

		print description

		ranking = node.xpath("./span[@class='ranking']")[0].text_content()
		code = os.path.basename(urlparse.urlparse(song_url).path)
		node_data = data.copy()
		node_data["code"] = code
		node_data["rating"] = ranking
		node_data["downloadURL"] = song_url
		node_data["description"] = description
		node_data["location"] = location_str
		Downloader.put(node_data)
		print song_url, ranking

def main_loop():
	Downloader.start()

	total_species = 0
	total_species_with_sound = 0

	result = urllib2.urlopen(search).read()

	root = lxml.html.fromstring(result)

	nodes = root.xpath("//ul[@id='checklist-list']/li")
	#nodes = root.xpath("//div[@class='view view-sounds-in-species']/div/ul/li")
	#nodes = root.xpath("//div/div/ul/li")



	FF = True

	for node in nodes:

		# **************** Fast Forward to 7271

		# *****************
		total_species += 1
		sound_total = node.xpath("./span/span[@class='sound-total']")
		sound_total_value = 0
		if sound_total != None and len(sound_total) == 1:
			sound_total_value = int(sound_total[0].text_content())
			print sound_total_value

		if sound_total_value == 0:
			continue

		href = node.xpath("./a")[0].attrib["href"]
		url = urlparse.urljoin(search, href)
		print url
#		path = urlparse.urlparse(url).path
#		if FF == True and os.path.basename(path) != "3143":
#			print path
#			continue

#		if os.path.basename(path) == "3143":
#			FF = False

		common_name = node.xpath("./a/span[@class='english']")[0].text_content()
		scientific_name = node.xpath("./a/span[@class='scientific']")[0].text_content()
		print common_name, scientific_name
		data = {"scientificName":scientific_name, "commonName":common_name}

		get_sounds(url, data)

		total_species_with_sound += 1

#		break


	print "Total Species =", total_species
	print "Total Species with sounds =", total_species_with_sound

	Downloader.end()
	Downloader.wait_for_pending_workers()

main_loop()

