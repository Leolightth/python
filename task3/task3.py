import pandas as pd
import sys
from datetime import datetime
import csv


from random import *
from datetime import timedelta


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
log_file = ''

def read_log_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        d = {'time_stamp': [], 'username': [], 'direction': [], 'value': [], 'success': []}

        data = f.read().splitlines()

        barrel_max = float(data[1].split()[0])
        barrel_start = float(data[2].split()[0])

        data = data[3:]

        for line in data:
            splitted_line = line.split('–')
            time_stamp = splitted_line[0].replace('Z', '').strip()
            time_stamp = datetime.fromisoformat(time_stamp)
            username = splitted_line[1].split('-')[0].strip()
            action = splitted_line[1].split('-')[1].strip()
            action_list = action.split()

            if 'top' in action_list:
                direction = '+'
            else:
                direction = '-'

            value = 0
            for item in action_list:
                if 'l' in item:
                    value = float(item.replace('l', ''))
                if '(' in item:
                    success = item

            d['time_stamp'].append(time_stamp)
            d['username'].append(username)
            d['direction'].append(direction)
            d['value'].append(value)
            d['success'].append(success)

        df = pd.DataFrame(data=d)

    return df, barrel_start


def write_log(filename=''):
    d1 = datetime.fromisoformat('2019-01-01Т12:51:33.124')
    d2 = datetime.fromisoformat('2022-01-02Т12:51:32.124')

    barrel_max = 200
    barrel_start = 32

    dates_list = []
    direction_list = []
    value_list = []
    username_list = []
    success_list = []

    max_iter = 12975

    for i in range(max_iter):
        dates_list.append(random_date(d1, d2))
        direction_list.append(choice(['+', '-']))
        #value_list.append(round(barrel_max*random(), 2))
        value_list.append(round(uniform(0, barrel_max), 2))
        username_list.append(choice(['username1', 'username2', 'username3','username4', 'username5']))

    dates_list = sorted(dates_list)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('META DATA:\n')
        f.write('{} (объем бочки)\n'.format(barrel_max))
        f.write('{} (текущий объем воды в бочке)\n'.format(barrel_start))

        current_value = barrel_start
        for i in range(max_iter):
            direction = direction_list[i]
            value = value_list[i]

            if direction == '+':
                direction_string = 'wanna top up'
                if current_value+value <= barrel_max:
                    current_value = current_value+value
                    success_list.append('(успех)')
                else:
                    success_list.append('(фейл)')

            else:
                direction_string = 'wanna scoop'
                if current_value-value >= 0:
                    current_value = current_value-value
                    success_list.append('(успех)')
                else:
                    success_list.append('(фейл)')
                pass

            row = "{}Z – [{}] - {} {}l {}\n".format(dates_list[i].isoformat(), username_list[i], direction_string,  value, success_list[i])
            f.write(row)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        #sys.argv[0] - имя программы

        filename = sys.argv[1]
        period_start = sys.argv[2]
        period_end = sys.argv[3]

        try:
            date_start = datetime.fromisoformat(period_start)
        except ValueError:
            print("Первый аргумент не является датой, повторите попытку!")
            sys.exit()
            pass

        try:
            date_end = datetime.fromisoformat(period_end)
            print('ok')
        except ValueError:
            print("Второй аргумент не является датой, повторите попытку!")
            sys.exit()
            pass

        if date_start > date_end:
            print("Даты перевернуты, повторите попытку!")
            sys.exit()

        df, barrel_start = read_log_file(filename=filename)

        df_filtered = df[df['time_stamp'].between(date_start, date_end)]

        print(df_filtered)

        try_number = df_filtered.shape[0]

        plus_try_number = df_filtered[df_filtered['direction'] == '+'].shape[0]
        plus_try_number_failed = df_filtered[(df_filtered['direction'] == '+') & (df_filtered['success'] == '(фейл)')].shape[0]

        minus_try_number = df_filtered[df_filtered['direction'] == '-'].shape[0]
        minus_try_number_failed = df_filtered[(df_filtered['direction'] == '-') & (df_filtered['success'] == '(фейл)')].shape[0]

        if plus_try_number:
            plus_error_ratio = plus_try_number_failed/plus_try_number*100.0
        else:
            plus_error_ratio = 0

        if minus_try_number:
            minus_error_ratio = minus_try_number_failed/minus_try_number*100.0
        else:
            minus_error_ratio = 0

        plus_value = df_filtered[(df_filtered['success'] == '(успех)') & (df_filtered['direction'] == '+')]['value'].sum()
        plus_failed_value = df_filtered[(df_filtered['success'] == '(фейл)') & (df_filtered['direction'] == '+')]['value'].sum()
        minus_value = df_filtered[(df_filtered['success'] == '(успех)') & (df_filtered['direction'] == '-')]['value'].sum()
        minus_failed_value = df_filtered[(df_filtered['success'] == '(фейл)') & (df_filtered['direction'] == '-')][
            'value'].sum()

        print()


        df_filtered_before = df[df['time_stamp'] < date_start]
        print()

        plus_before_start = \
        df_filtered_before[(df_filtered_before['success'] == '(успех)') & (df_filtered_before['direction'] == '+')][
            'value'].sum()
        minus_before_start = \
        df_filtered_before[(df_filtered_before['success'] == '(успех)') & (df_filtered_before['direction'] == '-')][
            'value'].sum()

        volume_start = barrel_start + plus_before_start - minus_before_start
        volume_end = volume_start + plus_value - minus_value

        print(df_filtered_before)

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

        print(output_stat)

        with open('mycsvfile.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, output_stat.keys())
            w.writeheader()
            w.writerow(output_stat)

    else:
        print("ошибка входных параметров")

    pass

