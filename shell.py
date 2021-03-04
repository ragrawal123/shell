import os
import subprocess

def main():
	while True:
		print(" ")
		command = input('$ ')
		if command == "exit":
			print("done")
			break
		elif command[:3] == 'cd ':
			psh_cd(command[3:])
		else:
			executec(command)

def psh_cd(inp):
	try:
		os.chdir(os.path.abspath(inp))
	except Exception:
		print("no directory found")
def executec(command):
	print(command.split())
	try: 
		subprocess.run(command.split())
	except Exception:
		print("not working")

if __name__ == "__main__":
	main()





