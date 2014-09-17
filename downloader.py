#!/usr/bin/python

import urllib2
import urlparse
import lxml.html
import os.path
import os
import time
from Queue import Queue
from threading import Thread

class Downloader:
	def __init__(self, nworkers, directory):
		self.workers = []
		self.queue = Queue()
		self.nworkers = nworkers
		self.directory = directory

	def start(self):
		for i in xrange(self.nworkers): # create workers
			self.workers.append(Worker(self.queue, self.directory))

		for w in self.workers: # run workers
			w.start()

	def end(self):
		for w in self.workers:
			self.queue.put(None)

	def wait_for_pending_workers(self):
		for w in self.workers:
			w.join()

	def put(self, item):
		self.queue.put(item)

	def get(self):
		return self.queue.get()


class Worker(Thread):
	def __init__(self, queue, directory):
		Thread.__init__(self)
		self.queue = queue
		self.directory = directory

	def run(self):
		while True:
			item = self.queue.get()
			if item == None:
				return

			try:
				filename = self.directory + "/" + item['commonName'] + '+' + item['scientificName'] + '+' + item['location'] + '+' + item['description'] + '+' + item['rating'] + '+' + item['code'] +  ".mp3"
	
				s = os.stat(filename)
				if s.st_size > 0:
					print filename, "Already Exists"
					continue

			except OSError:
				pass

			FAILED = True

			while FAILED:
				FAILED = False
				try:
					mp3 = urllib2.urlopen(item['downloadURL']).read()
				except urllib2.URLError:
					FAILED = True
					print "FAILED with mp3:", item['downloadURL']
					time.sleep(3)


			print "Writing", filename
			f = open(filename, "wb")
			f.write(mp3)
			f.close()
