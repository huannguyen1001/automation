import os, sys
cd='/../'
libpath=os.path.abspath(__file__)
while not os.path.exists(libpath + '/Environment'):
    libpath=os.path.abspath(libpath + cd)
sys.path.append(libpath)
