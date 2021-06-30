import os
import sys
import platform

import tkinter as tk
from tkinter import filedialog

##################################################

if platform.system() == "Linux":
	clear = lambda: os.system('clear') or None
	cleanPath = lambda path: path
elif platform.system() == "Windows":	
	clear = lambda: os.system('cls') or None
	cleanPath = lambda path: str(path).replace("\\", "/")


##################################################

def fileDialog():
	root = tk.Tk()
	root.withdraw()
	filePath = filedialog.askopenfilename()
	return filePath
# fielDialog()

##################################################

# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	"""
	Call in a loop to create terminal progress bar
	@params:
	    iteration   - Required  : current iteration (Int)
	    total       - Required  : total iterations (Int)
	    prefix      - Optional  : prefix string (Str)
	    suffix      - Optional  : suffix string (Str)
	    decimals    - Optional  : positive number of decimals in percent complete (Int)
	    length      - Optional  : character length of bar (Int)
	    fill        - Optional  : bar fill character (Str)
	    printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
	# Print New Line on Complete
	if iteration == total:
		print()
# printProgressBar()

##################################################

#range() on specific interval to include _end value
def in_range(_start, _end, _step):
	return range(_start, _end + _step, _step)
# get_steps()

##################################################
