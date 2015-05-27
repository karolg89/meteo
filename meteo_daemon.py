from daemon import Daemon
import sys

from meteo_main import mainTask


PIDFILE = '/var/run/meteod.pid'
LOGFILE = '/var/log/meteod.log'

class MeteoDaemon(Daemon):
	def run(self):
		mainTask()


if __name__ == "__main__":
	daemon = MeteoDaemon(PIDFILE)
	if len(sys.argv) == 2:

		if 'start' == sys.argv[1]:
			try:
				daemon.start()
			except:
				pass

		elif 'stop' == sys.argv[1]:
			print "Stopping ..."
			daemon.stop()

		elif 'restart' == sys.argv[1]:
			print "Restaring ..."
			daemon.restart()

		elif 'status' == sys.argv[1]:
			try:
				pf = file(PIDFILE,'r')
				pid = int(pf.read().strip())
				pf.close()
			except IOError:
				pid = None
			except SystemExit:
				pid = None

			if pid:
				print 'MeteoDaemon is running as pid %s' % pid
			else:
				print 'MeteoDaemon is not running.'

		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)
