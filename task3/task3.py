import pandas as pd
import sys
from datetime import datetime
from datetime import timedelta
import csv

from random import *


def random_date(start, end):
    """
    Функция, возвращающая случайную дату между двумя заданными
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def read_log_file(filename):
    """
    Функция, читающая .log файл.
    Возвращает полученный из лога датафрейм и обьем в бочке на начальный момент времени
    """
    with open(filename, 'r', encoding='utf-8') as f:

        # формируем словарь для последующего создания датафрейма
        d = {'time_stamp': [], 'username': [], 'direction': [], 'value': [], 'success': []}

        # читаем лог и получаем список строк в нем
        data = f.read().splitlines()

        # получаем стартовый и максимальный обьем бочки
        barrel_max = float(data[1].split()[0])
        barrel_start = float(data[2].split()[0])

        # удаляем первые 3 строки
        data = data[3:]

        # парсим каждую строку и обновляем словарь
        for line in data:
            # формат строки: "2020-01-01Т12:51:34.769Z – [username2] - wanna scoop 50l (фейл)"
            # или
            # формат строки: "2020-01-01Т12:51:32.124Z – [username1] - wanna top up 10l (успех)"
            #сплит по дэшу перед username
            splitted_line = line.split('–')

            # получаем время попытки и преобразуем в datetime обьект
            time_stamp = splitted_line[0].replace('Z', '').strip()
            time_stamp = datetime.fromisoformat(time_stamp)

            # получаем username
            username = splitted_line[1].split('-')[0].strip()

            # получем все что правее последнего дэша
            action = splitted_line[1].split('-')[1].strip()
            action_list = action.split()

            # если в строке есть "top" - это попытка налить- обозначаем ее символом "+"
            if 'top' in action_list:
                direction = '+'
            else:
                direction = '-'

            value = 0
            # элемент с "l" - это обьем, который пытаются налить/вылить
            # элемент с "(" - это индикатор успеха или фейла
            for item in action_list:
                if 'l' in item:
                    value = float(item.replace('l', ''))
                if '(' in item:
                    success = item

            # обновляем словарь
            d['time_stamp'].append(time_stamp)
            d['username'].append(username)
            d['direction'].append(direction)
            d['value'].append(value)
            d['success'].append(success)

        # создаем датафрейм из словаря
        df = pd.DataFrame(data=d)

    return df, barrel_start


def write_log(filename=''):
    """
    Функция, для генерации лог файла- в программе далее не используется
    """

    # диапазон дат для генерации рандомной даты внутри диапазона
    d1 = datetime.fromisoformat('2019-01-01Т12:51:33.124')
    d2 = datetime.fromisoformat('2022-01-02Т12:51:32.124')

    # максимальный и стартовый размер бочки
    barrel_max = 200
    barrel_start = 32

    # списки для рандомной генерации данных в лог
    dates_list = []
    direction_list = []
    value_list = []
    username_list = []
    success_list = []

    # количество записей в логфайле- так лог равен ровно 1Мб
    max_iter = 12975

    # формируем max_iter записей
    for i in range(max_iter):
        # генерируем случайную дату в заданном диапазоне
        dates_list.append(random_date(d1, d2))
        # генерируем попытку - наливаем или выливаем
        direction_list.append(choice(['+', '-']))
        # генерируем обьем попытки - сколько литров наливаем или выливаем
        value_list.append(round(uniform(0, barrel_max), 2))
        # генерируем username из списка заданных
        username_list.append(choice(['username1', 'username2', 'username3','username4', 'username5']))

    # сортируем даты, чтобы легче было определять успех/неуспех попытки
    dates_list = sorted(dates_list)

    # открываем файл лога для записи
    with open(filename, 'w', encoding='utf-8') as f:
        # записываем первые три строки метаданных
        f.write('META DATA:\n')
        f.write('{} (объем бочки)\n'.format(barrel_max))
        f.write('{} (текущий объем воды в бочке)\n'.format(barrel_start))

        # для каждой попытки - определяем успешна ли она и записываем в лог
        current_value = barrel_start
        for i in range(max_iter):
            # при этой попытке мы наливаем или выливаем?
            direction = direction_list[i]
            # какой обьем?
            value = value_list[i]

            # если наливаем, нельзя перелить
            if direction == '+':
                direction_string = 'wanna top up'
                if current_value+value <= barrel_max:
                    current_value = current_value+value
                    success_list.append('(успех)')
                else:
                    success_list.append('(фейл)')

            # если выливаем, нельзя вычерпнуть больше, чем есть в бочке на данный момент
            else:
                direction_string = 'wanna scoop'
                if current_value-value >= 0:
                    current_value = current_value-value
                    success_list.append('(успех)')
                else:
                    success_list.append('(фейл)')
                pass

            # формируем строку по формату лога
            row = "{}Z – [{}] - {} {}l {}\n".format(dates_list[i].isoformat(), username_list[i], direction_string,  value, success_list[i])
            # пишем строку в файл
            f.write(row)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        # получение параметров консоли
        filename = sys.argv[1]
        period_start = sys.argv[2]
        period_end = sys.argv[3]

        # проверка первой даты
        try:
            date_start = datetime.fromisoformat(period_start)
        except ValueError:
            print("Первый аргумент не является датой, повторите попытку!")
            sys.exit()
            pass

        # проверка второй даты
        try:
            date_end = datetime.fromisoformat(period_end)
        except ValueError:
            print("Второй аргумент не является датой, повторите попытку!")
            sys.exit()
            pass

        # проверка перевернуты ли даты
        if date_start > date_end:
            print("Даты перевернуты, повторите попытку!")
            sys.exit()

        # чтение лога - на выходе начальный обьем бочки и сформированный из лога pandas-dataframe
        df, barrel_start = read_log_file(filename=filename)

        # получаем датафрейм данных, которые находятся между заданными периодами
        df_filtered = df[df['time_stamp'].between(date_start, date_end)]

        # всего всех попыток
        try_number = df_filtered.shape[0]

        # всего попыток налить
        plus_try_number = df_filtered[df_filtered['direction'] == '+'].shape[0]
        # количество фейлов при наливании
        plus_try_number_failed = df_filtered[(df_filtered['direction'] == '+') & (df_filtered['success'] == '(фейл)')].shape[0]

        # всего попыток вылить
        minus_try_number = df_filtered[df_filtered['direction'] == '-'].shape[0]
        # количество фейлов при выливании
        minus_try_number_failed = df_filtered[(df_filtered['direction'] == '-') & (df_filtered['success'] == '(фейл)')].shape[0]

        # если были попытки налить то считаем процент фейлов, если их не было то ставим 0
        if plus_try_number:
            plus_error_ratio = plus_try_number_failed/plus_try_number*100.0
        else:
            plus_error_ratio = 0

        # если были попытки вылить то считаем процент фейлов, если их не было то ставим 0
        if minus_try_number:
            minus_error_ratio = minus_try_number_failed/minus_try_number*100.0
        else:
            minus_error_ratio = 0

        # сколько литров удалось налить (фильтруем датфрейм чтобы был успех и наливание и суммируем по значениям)
        plus_value = df_filtered[(df_filtered['success'] == '(успех)') & (df_filtered['direction'] == '+')]['value'].sum()
        # сколько литров НЕ удалось налить
        plus_failed_value = df_filtered[(df_filtered['success'] == '(фейл)') & (df_filtered['direction'] == '+')]['value'].sum()
        # сколько литров удалось вылить
        minus_value = df_filtered[(df_filtered['success'] == '(успех)') & (df_filtered['direction'] == '-')]['value'].sum()
        # сколько литров НЕ удалось вылить
        minus_failed_value = df_filtered[(df_filtered['success'] == '(фейл)') & (df_filtered['direction'] == '-')][
            'value'].sum()

        # для подсчета обьема бочки на начальный момент - фильтруем датафрейм по датам меньшим стартового периода
        df_filtered_before = df[df['time_stamp'] < date_start]

        # считаем, сколько было успешно налито за все время до начального периода
        plus_before_start = \
        df_filtered_before[(df_filtered_before['success'] == '(успех)') & (df_filtered_before['direction'] == '+')][
            'value'].sum()
        # считаем, сколько было успешно вылито за все время до начального периода
        minus_before_start = \
        df_filtered_before[(df_filtered_before['success'] == '(успех)') & (df_filtered_before['direction'] == '-')][
            'value'].sum()

        # считаем обьем на момент начального периода
        # = сколько было изначально + успешно налито за все время до начального периода - успешно вылито за все время до начального периода
        volume_start = barrel_start + plus_before_start - minus_before_start

        # считаем обьем на момент конечного периода
        # = сколько было на начальный период + успешно налито за изучаемый период - успешно вылито за изучаемый период
        volume_end = volume_start + plus_value - minus_value

        # заполняем словарь с рассчитанной статистикой
        output_stat = {'period_start': str(period_start),
                        'period_end': str(period_end),
                       'volume_start': round(volume_start, 2),
                       'volume_end': round(volume_end, 2),
                       'try_number': try_number,

                        'plus_try_number': plus_try_number,
                        'plus_error_ratio': plus_error_ratio,
                        'plus_value': plus_value,
                        'plus_failed_value': plus_failed_value,

                       'minus_try_number': minus_try_number,
                       'minus_error_ratio': minus_error_ratio,
                        'minus_value': minus_value,
                        'minus_failed_value': minus_failed_value,
                       }

        # выводим словарь со статистикой в файл *.csv
        with open('mycsvfile.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, output_stat.keys())
            w.writeheader()
            w.writerow(output_stat)

    else:
        print("ошибка входных параметров")


