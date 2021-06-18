# -*- coding: UTF-8 -*-

import sys
import re


def create_pattern(string_2: str='*'):
    '''
    Создание паттерна для поиска из заданной строки
    '''
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
        # получение параметров консоли
        # первая строка
        string_1 = sys.argv[1]
        # вторая строка
        string_2 = sys.argv[2]
        # создаем паттерн для сравнения из второй строки
        regex_string = create_pattern(string_2)
        # сравниваем первую строку с паттерном, созданным из второй
        match = regex_string.match(string_1)
        # в зависимости от наличия соответствия делаем пишем 'OK' или 'KO'
        if match:
            print('OK')
        else:
            print('KO')

    else:
        print("ошибка входных параметров")