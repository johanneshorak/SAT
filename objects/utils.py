import sys as sys
import os.path

def mwrite(string):
	sys.stdout.write(string)
	sys.stdout.flush()

def file_exists(fname):
	return(os.path.isfile(fname))
