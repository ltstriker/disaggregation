import sys
sys.path.insert(0, '../..')
import numpy

import parse_ns2_trace as parse
import ideal as ideal


def main(load):
    print "calculating on", load, "load"
    f = open("./Dataset/flow_"+str(load)+"Load.tr").readlines()
    #Flow info is array: [size fct oracle_fct norm_fct]
    ideal_fct = ideal.get_ideal_fcts(f, 2.5)
    out = open("./Dataset/ideal_"+str(load)+"Result_large.txt", "w")
    for fct in ideal_fct:
        out.write(str(fct)+'\n')
    print "finish", load



if __name__ == '__main__':
    [main(i) for i in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]