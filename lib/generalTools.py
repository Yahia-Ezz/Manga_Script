import sys

class ProgressBar:
	def __init__(self, iterableCount=None, useErrStream=False):
		try:
			import tqdm
			self.pbar = tqdm.tqdm(total=iterableCount,
								  file=(sys.__stderr__ if useErrStream else sys.__stdout__),ascii=True)
			self.tqdmSupport=True
		except ImportError:
			self.tqdmSupport=False
			print('Warning: Module "tqdm" is not installed.')

	def update(self, ammount=1):
		if(self.tqdmSupport):
			self.pbar.update(ammount)

	def close(self):
		if(self.tqdmSupport):
			self.pbar.close()