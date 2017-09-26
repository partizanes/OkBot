import os, sys, subprocess

corePath = os.path.join(os.getcwd(), "core.py")
subprocess.Popen([sys.executable, corePath])
