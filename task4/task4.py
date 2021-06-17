# -*- coding: UTF-8 -*-

import sys
import re


def create_pattern(string_2: str='*'):
    pattern = ''
    for symbol in string_2:
        if symbol == '*':
            pattern += '.*'
        else:
            pattern += symbol
    regex_string = re.compile(pattern)
    return regex_string


if __name__ == '__main__':
    if len(sys.argv) == 3:
        #sys.argv[0] - имя программы

        string_1 = sys.argv[1]
        string_2 = sys.argv[2]
        regex_string = create_pattern(string_2)
        match = regex_string.match(string_1)
        if match:
            print('OK')
        else:
            print('KO')

    else:
        print("ошибка входных параметров")