import os
import subprocess

def main():
	while True:
		print(" ")
		command = input('$ ')
		if command == "exit":
			print("done")
			break
		else:
			executec(command)

def executec(command):
	print(command.split())
	try: 
		subprocess.run(command.split())
	except Exception:
		print("not working")

if __name__ == "__main__":
	main()





