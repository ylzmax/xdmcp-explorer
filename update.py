import urllib
import re
import subprocess as sub
import sys 
VERSION='3.5'
FILEPATH='/home/liz/'
UPDATEURL='http://bfile1/sprdlogin/'
infodic={}
def getinfo():
	url=UPDATEURL+'updateinfo'
	try:
		updateinfo=urllib.urlopen(url)
	except:
		print 'urlopen error!'
	else:
		info=updateinfo.readlines()
		info=[e.split() for e in info]
		for l in info:
			U=l[0].split('=')
			infodic[U[0]]=U[1]
		if infodic['VERSION'] > VERSION:
			return infodic
		else:
			#print 'No update'
			#sys.exit()
			return False
		
def getupdatefile(dict):
	if dict:
		url=UPDATEURL+dict['FILE']
		filer=urllib.urlopen(url)
		filepath=FILEPATH+dict['FILE']
		file=open(filepath,'w')
		l=filer.read()
		file.write(l)
		file.flush()
		file.close()
		return filepath 
	else:
		print 'No dict info!'
		return False

def update(filepath):
	if file:
		tarcmd=['tar','zxvf',filepath,'-C',FILEPATH]
		tp=sub.Popen(tarcmd,stdout=sub.PIPE)
		tp.wait()
		runcmd=['bash',FILEPATH+'demo/'+infodic['CMD']]
		p=sub.Popen(runcmd)

if __name__=='__main__':
	if getinfo():
		update(getupdatefile(infodic))
	else:
		print 'No update!'



