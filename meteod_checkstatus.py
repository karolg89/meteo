import subprocess
import sys, os

print 'sys.argv[0] =', sys.argv[0]             
pathname = os.path.dirname(sys.argv[0])        
print 'path =', pathname
print 'full path =', os.path.abspath(pathname)

fullpath = os.path.abspath(pathname)

p = subprocess.Popen(['python',fullpath+'/meteo_daemon.py','status'],stdout=subprocess.PIPE)

out,err = p.communicate()
print out
if "not running" in out:
	print "Restarting Meteo Daemon"
	p = subprocess.call(['python',fullpath+'/meteo_daemon.py','restart'])
else:
	print "Meteo Daemon is allread runing."