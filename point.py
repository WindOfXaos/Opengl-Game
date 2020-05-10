import sys

from objloader import *

def point(path):
    filename = os.path.join(scriptDIR, path)
    for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                x = v[0]
                y = v[1]
                z = v[2]

    return x,y,z