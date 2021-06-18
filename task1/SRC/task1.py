import sys

def isoBase(nb, base):
    isoBase.t = table
    r = ''
    while nb:
        nb, y = divmod(nb, base)
        r = isoBase.t[y] + r
    return r


if __name__ == '__main__':
    if len(sys.argv) == 3:
        table = sys.argv[1]
        num = int(sys.argv[2])
        print(isoBase(num, len(table)))
    else:
        print("ошибка входных параметров")