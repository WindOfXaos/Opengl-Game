import sys

from objloader import * 

def objcenter(path):
    max_x = 0
    max_z = 0
    min_x = 0
    min_y = 0
    min_z = 0
    filename = os.path.join(scriptDIR, path)
    st = True
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = list(map(float, values[1:4]))
            if st == True:
                max_x = v[0]
                max_y = v[1]
                max_z = v[2]
                min_x = v[0]
                min_y = v[1]
                min_z = v[2]
                st = False
            else:
                if max_x < v[0] :
                    max_x = v[0]
                if max_y < v[1] :
                    max_y = v[1]
                if max_z < v[2] :
                    max_z = v[2]
                if min_x > v[0] :
                    min_x = v[0]
                if min_y > v[1] :
                    min_y = v[1]
                if min_z > v[2] :
                    min_z = v[2]

    mid_x = (max_x + min_x) / 2
    mid_y = (max_y + min_y) / 2
    mid_z = (max_z + min_z) / 2

    return mid_x,mid_y,mid_z