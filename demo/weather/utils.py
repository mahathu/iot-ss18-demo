from termcolor import colored
from datetime import datetime
from pytz import timezone

def log(msg='', color='yellow'):
	print( colored(msg, color) )

def getTime(tz):
	format = '%H:%M'
	time = datetime.now( timezone(tz) )
	return time.strftime(format)