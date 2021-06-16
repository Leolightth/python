
try:
    table = input("Введите систему счисления...\n")
    num = int(input("Введите число...\n"))
except ValueError:
    print("Некорректный ввод аргументов, повторите попытку!")
    sys.exit()

def isoBase(nb, base):
    isoBase.t = table
    r = ''
    while nb:
        nb, y = divmod(nb, base)
        r = isoBase.t[y] + r
    return r

if __name__ == '__main__':
    print(isoBase(num, len(table)))
