import sys
from time import time

def collapse(f_in):
    f_in = open(f_in)
    f_out = open('%s.%f' % (f_in.name, time()), 'w')

    f_out.writelines( set(f_in.readlines()) )

    f_in.close()
    f_out.close()


if __name__ == '__main__':
    collapse(sys.argv[1])