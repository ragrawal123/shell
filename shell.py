import os
import subprocess
import glob
import sys
import tty
import termios
import signal
from shlex import split

jobsdict = {}
foreground = []
background = []

def main():

	global pid
	x = 0
	while True:
		cleanjobs()
		#signal.signal(signal.SIGINT, sig_handler)
		command = input('$ ')
		temp = parsecmd_wrapper(command)
		command_parsed = temp[0]
		parsechecks = temp[1]
		first_in = temp[2]
		last_out = temp[3]
		background =  temp[4]

		print(command_parsed)
		executec(command_parsed, parsechecks, first_in, last_out, background)
		#os.wait()
			
def parsecmd_wrapper(command_line):
	first_in, last_out = None, None
	pipecheck = '|' in command_line
	globcheck = '*' in command_line or '?' in command_line
	subcmdcheck = '$' in command_line
	parsechecks = [pipecheck, globcheck, subcmdcheck]
	background = "&" in command_line
	if "<" in command_line:
		filename = command_line[command_line.index("<") + 1:]
		command_line = command_line[:command_line.index("<")]
		try:
			first_in = open(os.path.abspath(filename.strip()), 'r')
		except Exception:
			print(filename + ": no such file or directory")

	if ">>" in command_line:
		filename = command_line[command_line.index(">") + 1:]
		command_line = command_line[:command_line.index(">")]
		try:
			last_out = open(os.path.abspath(filename.strip()), 'a')
		except Exception:
			print(filename + ": no such file or directory")
	elif ">" in command_line: 
		filename = command_line[command_line.index(">") + 1:]
		command_line = command_line[:command_line.index(">")]
		try:
			last_out = open(os.path.abspath(filename.strip()), 'w')
		except Exception:
			print(filename + ": no such file or directory")
	return parsecmd(command_line), parsechecks, first_in, last_out, background


def parsecmd(command_line):
	pipecheck = '|' in command_line
	globcheck = '*' in command_line or '?' in command_line
	subcmdcheck = '$' in command_line
	parsechecks = [pipecheck, globcheck, subcmdcheck]
	if '&' in command_line:
		command_line = command_line[:command_line.index('&')] + command_line[command_line.index('&'): +1]
	
	if pipecheck:
		'''command_line = command_line.split()
		temp = ''
		newcmd = []
		for cmd in command_line:
			if "|" in cmd:	
				temp = temp + cmd[:cmd.index('|')]
				newcmd.append(parsecmd(temp))
				temp = cmd[cmd.index('|') + 1:]
			else:
				temp = temp + cmd
		if temp:
			newcmd.append(parsecmd(temp))
		command_line = newcmd'''
		command_line = list(map(lambda x: x.strip().split(), command_line.split('|')))

	if subcmdcheck:
		newcmd = []
		cmdcopy = command_line
		t = ''
		while cmdcopy:
			ch = cmdcopy[0]
			if '$' in ch:
				if t.strip():
					newcmd.append(t.strip().split())
				t = ''
				temp = cmdcopy[1:]
				if temp.find("$") < temp.find(")"):
					endch = temp.find('$')
					cmdcopy = cmdcopy[endch:]
				else:
					endch = temp.find(')') 
				newcmd.append(temp[1:endch].strip().strip('(').strip(')').split())
				
			else:
				t = t + ch
				cmdcopy = cmdcopy[1:]
			#print(cmdcopy)

		return newcmd

					


	'''if globcheck:
		newcmd = []
		for cmd in command_line:
			if '*' in cmd or '?' in cmd:
				newcmd.append(glob.glob(cmd))
			else :
				newcmd.append(cmd)

	command_line = newcmd'''
	if sum(parsechecks) == 1 or  sum(parsechecks) == 0:
		command_line = command_line.split()
	return command_line

def sig_handler(sig, frame):
	if os.fork() == 0:
		os._exit(0)
	

def getChar():
	fd = sys.stdin.fileno()
	oldSettings = termios.tcgetattr(fd)

	try:
		tty.setcbreak(fd)
		answer = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
	return answer

def psh_cd(inp):
	try:
		os.chdir(os.path.abspath(inp[1]))
	except Exception:
		print("no directory found")

		
def executec(command, parsechecks, first_in=None, last_out=None, background = False):
	global jobsdict
	if parsechecks[0]:
		#print(command)
		c = command.pop(0)
		#print(c)
		#print(last_out)
		f = subprocess.Popen(c, stdin = first_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		jobsdict[f.pid()] = ' '.join(c)
		while len(command) > 1:
			c = command.pop(0)
			f = subprocess.Popen(c, stdin=f.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			jobsdict[f.pid()] = ' '.join(c)

		c = command.pop(0)
		#print(f)
		if background:
			f = subprocess.Popen(c, stdin=f.stdout, stdout=last_out, stderr=subprocess.PIPE)
		else:
			f = subprocess.Popen(c, stdin=f.stdout, stdout=last_out, stderr=subprocess.PIPE).wait()
		jobsdict[f.pid()] = ' '.join(c)



	elif parsechecks[1]:
		stdout = ''
		print(command)
		for i in range(0, len(command)):
			t = command[i]
			if '*' in t or '?' in t:
				for stuff in glob.glob(t):
					newc = command
					newc[i] = stuff
					c = subprocess.Popen(command, stdout=subprocess.PIPE)
					jobsdict[c.pid()] = ' '.join(newc)
					c.wait()
					stdout = stdout + c.communicate()[0].decode()
		print(stdout)
		

	elif parsechecks[2]:
		#print(command)
		c = command.pop(0)
		#print(c)
		#print(last_out)
		f = subprocess.Popen(c, stdin = first_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		jobsdict[f.pid()] = ' '.join(c)
		while len(command) > 1:
			c = command.pop(0)
			f = subprocess.Popen(c, stdin=f.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			jobsdict[f.pid()] = ' '.join(c)

		c = command.pop(0)
		#print(f)
		if background:
			f = subprocess.Popen(c, stdin=f.stdout, stdout=last_out, stderr=subprocess.PIPE)
		else:
			f = subprocess.Popen(c, stdin=f.stdout, stdout=last_out, stderr=subprocess.PIPE).wait()
		jobsdict[f.pid()] = ' '.join(c)

	elif 'cd' in command:
		#print('cd')
		psh_cd(command)
	elif 'pwd' in command:
		#print('pwd')
		print(os.getcwd())
	elif 'exit' in command:
		print("done")
		sys.exit()
	elif 'jobs' in command:
		cleanjobs()
		for job in job.keys():
			print("PID: " + job + " " + jobsdict[job])
	elif 'fg' in command:
		cleanjobs()
		pid = int(command[3:].strip())
		foreground.append(pid)
		background.remove(pid)
		os.kill(pid, signal.SIGCONT)

	elif 'bg' in command:
		cleanjobs()
		pid = int(command[3:].strip())
		foreground.remove(pid)
		background.append(pid)
		os.kill(pid, signal.SIGCONT)
	else:
		if background:
			f = subprocess.Popen(command, stdout=last_out)

		else:	
			f = subprocess.Popen(command, stdout=last_out)
			
			f.wait()
		#print(f)
		addbgfg(f.pid, background)
		

def cleanjobs():
	global jobsdict
	#print (jobsdict)
	for job in list(jobsdict):
		try:
			os.kill(job, 0)
		except OSError:
			del jobsdict[job]
	#print (jobsdict)


def addbgfg(pid, back):
	global foreground
	global background
	if back:
		background.append(pid)
	else:
		foreground.append(pid)

if __name__ == "__main__":
	main()





