import sys
from time import time

if __name__ == '__main__':
    f_in = open(sys.argv[1])
    f_out = open('%s.%f' % (sys.argv[1], time()), 'w')

    f_out.writelines(set(f_in.readlines()))

    f_in.close()
    f_out.close()