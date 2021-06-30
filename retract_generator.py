#! python3

import os
import sys
import platform
import pathlib
import subprocess
import shutil
import getopt

import tools #tools.py

##################################################

curr_path = pathlib.Path(__file__).parent.absolute()

if platform.system() == "Linux":
	icesl_bin = "/Home/IceSL/bin/IceSL-slicer"
elif platform.system() == "Windows":	
	icesl_bin = "C:/Program Files/INRIA/IceSL/bin/IceSL-slicer.exe"
	#icesl_bin = "C:/Program Files/INRIA/IceSL/bin/IceSL-slicer-phasor.exe" # custom IceSL exec with phasor
	#icesl_bin = "C:/Program Files/INRIA/IceSL/bin/dev/bin/IceSL-slicer.exe" # custom IceSL exec with phasor

debug = False

retract_min = 2
retract_max = 6
retract_step = 1

speed_min = 15
speed_max = 50
speed_step = 5

total_steps = 0

##################################################

def get_total_steps():
	steps = 0
	for r in tools.in_range(retract_min,retract_max,retract_step):
		for s in tools.in_range(speed_min,speed_max,speed_step):			
			steps = steps + 1

	return steps
# get_total_steps()

##################################################

def prepare():
	if not os.path.exists("tmp"):
		os.mkdir("tmp")
	else:
		shutil.rmtree("tmp") # cleanup potential lua temp folder
		os.mkdir("tmp")

	if not os.path.exists("gcodes/"):
		pathlib.Path('gcodes/').mkdir(parents=True,exist_ok=True)
	else:
		shutil.rmtree("gcodes/") # cleanup previously generated gcodes
		pathlib.Path('gcodes/').mkdir(parents=True,exist_ok=True)

	global icesl_bin
	if not os.path.exists(icesl_bin): #check if path to IceSL is correct
		print("IceSL was not found on your computer, please select its executable:")
		fd = tools.fileDialog()
		if not fd:
			print('ERROR: No suitable IceSL executable was provided. This tool will now close.')
			clean(False)
			sys.exit()
		else:
			print("fd: " + fd)
			icesl_bin = fd
			print("The IceSL executable located in '" + icesl_bin + "' will be used.\n")

	# set the total number of steps
	global total_steps
	total_steps = get_total_steps()
# prepare()

##################################################

def clean(_gcode):
	if os.path.exists("tmp"):
		print("Cleaning temporary files...")
		shutil.rmtree("tmp")
	if _gcode:
		if os.path.exists("gcodes"):
			shutil.rmtree("gcodes")
			print("Gcodes were cleaned")
		else:
			print("Gcodes are already cleaned")
# clean()

##################################################

def gen_lua(_retract, _speed):
	fname = "R" + str(_retract) + "_F" + str(_speed)

	f = open("tmp/" + fname + ".lua", "w+")
	if debug:
		print("Generating tmp/" + fname + ".lua")

	f.write("dofile('" + tools.cleanPath(curr_path) + "/params.lua')\n")
	f.write("dofile('" + tools.cleanPath(curr_path) + "/part.lua')\n")

	f.write("set_setting_value('filament_priming_mm_0', " + str(_retract) + ")\n")
	f.write("set_setting_value('priming_mm_per_sec_0', " + str(_speed) + ")\n")	

	f.write("set_service('FilamentSlicer')\n")
	f.write("run_service('" + tools.cleanPath(curr_path) + "/gcodes/" + fname + ".gcode')\n")

	return fname
# gen_lua()

##################################################

def generator(_step, _retract, _speed):
	fname = gen_lua(_retract, _speed)

	if not debug:
		# ProgressBar update
		progress_prefix = 'Gcode ' + str(_step + 1) + ' out of ' + str(total_steps) + ' | Progress:'
		tools.printProgressBar(_step + 1, total_steps, prefix = progress_prefix, suffix = 'Complete', length = 50)
		# Note: icesl's output is hidden for convenicence
		subprocess.run([icesl_bin, tools.cleanPath(curr_path) + "/tmp/" + fname + ".lua", "--service"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
	else:
		subprocess.run([icesl_bin, tools.cleanPath(curr_path) + "/tmp/" + fname + ".lua", "--service"])
# generator()

##################################################

def run_generator():
	step = 0
	if not debug:
		# ProgressBar init
		progress_prefix = 'Gcode ' + str(step) + ' out of ' + str(total_steps) + ' | Progress:'
		tools.printProgressBar(step, total_steps, prefix = progress_prefix, suffix = 'Complete', length = 50)
	
	for r in tools.in_range(retract_min,retract_max,retract_step):
		for s in tools.in_range(speed_min,speed_max,speed_step):
			generator(step,r,s)
			step = step + 1
# run_generator()

##################################################

def display_settings():

	print("Retract Generator started with the following settings:")
	print("\t-Minimal length: " + str(retract_min))
	print("\t-Maximal length: " + str(retract_max))
	print("\t-Minimal speed: " + str(speed_min))
	print("\t-Maximal speed: " + str(speed_max))

	print(str(total_steps) + " Gcodes files will be produced.\n")
# display_settings()

##################################################

def display_help():
	tools.clear()
	print(" =====================")
	print(" | " + sys.argv[0] + " |")
	print(" =====================")
	print("\n")
	print("#Description:")
	print("\tA simple tool to generate retract test in bulk.")
	print("\n")
	print("#Syntax:")
	print("\t" + sys.argv[0] + " ")
	print("\n")
	print("#Arguments:")
	print("\t<none>\t\t\t Use hardcoded default values and launch the generator.")
	print("\t-h or -help\t\t Display this help section.")
	print("\t-e or -exec\t\t Specify an IceSL's executable (if you need a specific version).")
	print("\t-c or -clean\t\t Clean (delete) the Gcodes.")
	print("\t-d or -debug\t\t Launch the generator in debug-mode.\n")
	print("    For the following, if not specified, hardcoded default will be used.")
	print("\t-r or -retract_min [int]\t\t Minimal retract length to use for generation")
	print("\t-R or -retract_max [int]\t\t Maximal retract length to use for generation")
	print("\t-s or -speed_min [int]\t\t Minimal retract speed to use for generation")
	print("\t-S or -speed_max [int]\t\t Maximal retract speed to use for generation")

# display_help()

##################################################

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"cdehr:R:s:S:", ["retract_min=", "retract_max=", "speed_min=", "speed_max", "help", "debug", "clean", "exec"])
	except getopt.GetoptError:
		display_help()
		sys.exit(2)

	# get globals
	global debug
	global retract_min
	global retract_max
	global speed_min
	global speed_max

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			display_help()
			sys.exit()
		elif opt in ("-d", "--debug"):
			debug = True
		elif opt in ("-c", "--clean"):
			clean(True)
			sys.exit()
		elif opt in ("-e", "--exec"):
			print("Select your IceSL's executable:")
			icesl_bin = tools.fileDialog()
			print("The IceSL executable located in '" + icesl_bin + "' will be used.\n")
		elif opt in ("-r", "--retract_min"):
			retract_min = int(arg)
		elif opt in ("-R", "--retract_max"):
			retract_max = int(arg)
		elif opt in ("-s", "--speed_min"):
			speed_min = int(arg)
		elif opt in ("-S", "--speed_max"):
			speed_max = int(arg)

	prepare()
	display_settings()
	run_generator()
	if not debug:
		clean(False)
	print("Done generating the Gcodes !")
# main()

##################################################

if __name__ == "__main__":
	main(sys.argv[1:])
