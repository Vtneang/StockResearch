import threading
import time

exitFlag = 0

class myThread (threading.Thread):

   cur_threads = 0

   def __init__(self, threadID, name, counter, marker, storage):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.marker = marker
      self.storage = storage
      myThread.cur_threads += 1

   def run(self, store):
      print("Starting " + self.name + " # of Threads = " + str(self.cur_threads))
      print_time(self.name, 5, self.counter, self.marker, self.storage)
      print("Exiting " + self.name)
      print(str(maker.total))

def print_time(threadName, counter, delay, marker, storage):
   while counter:
      if exitFlag:
         threadName.exit()
      time.sleep(delay)
      print("%s: %s" % (threadName, time.ctime(time.time())))
      storage[marker] = ("%s: %s" % (threadName, time.ctime(time.time())))
      counter -= 1
      marker += marker


class maker:
	total = {}
	def __init__(self):
		self.thread1 = myThread(1, "Thread-1", 1, "A", self.total)
		self.thread2 = myThread(2, "Thread-2", 2, "B", self.total)
		self.thread3 = myThread(3, "Thread-3", 0, "C", self.total)

	def start(self):
		# Start new Threads
		self.thread1.start()
		self.thread2.start()
		self.thread3.start()


hi = maker()
hi.start()
print(myThread.cur_threads)

print("Exiting Main Thread")