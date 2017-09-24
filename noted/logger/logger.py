import logging
from gi.repository import GLib

class Logger(object):

	def __init__(self):
		self.logger = logging.getLogger('Main')
		self.logger.setLevel(logging.DEBUG)
		logging_path = "{}/Noted/Main".format(GLib.get_user_data_dir())
		self.handler = logging.FileHandler(logging_path)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
		self.handler.setFormatter(formatter)
		self.logger.addHandler(self.handler)


def logging_decorator(logger):
	def decorator(function):
		def wrapper(*args,**kwargs):
			try:
				result = function(*args,**kwargs)
				logger.logger.debug('Succesfully completed {}'.format(function.__name__))
				return result
			except Exception as e:
				logger.logger.debug('There was a problem running the function {} ; ERROR MESSAGE > {}'.format(function.__name__,e))
				#NOTE figure out how to close on exception
				raise e
		return wrapper
	return decorator