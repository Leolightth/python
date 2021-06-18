import math
import json
import re
import sys

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def found_nearest_index(initial_index, symbol_list):
    '''
    Функция поиска ближайшей (справа) позиции из списка symbol_list к позиции initial_index
    Возвращет элемент и номер ближайшего справа элемента из списка symbol_list.
    '''
    found_index = -1
    found_index_position = -1
    for index_position, index in enumerate(symbol_list):
        if index <= initial_index:
            pass
        else:
            if found_index == -1:
                found_index = index
                found_index_position = index_position
    return found_index, found_index_position


def read_data(filename):
    '''
    Функция, читающая файл с геометрией (имя файла - входной параметр).
    Так как не указано, какого формата файл - он читается как текстовый файл.
    Десериализовать как json нет возможности из-за способа записи ключей (без кавычек)
    Возвращает словарь геометрии
    '''

    # открываем файл для чтения
    with open(filename, 'r') as f:
        # читаем содержимое и убираем пробелы
        data = f.read()
        data = data.replace(' ', '')

        # инициализируем словарь геометрии
        geo_dict = {'sphere': {'center': [], 'radius': 0},
                     'line': [[], []]}

        # получаем список позиций симоволов скобок "[" и "]"
        right_brackets = [m.start() for m in re.finditer('\[' , data)]
        left_brackets = [m.start() for m in re.finditer('\]' , data)]

        # получаем список позиций симоволов скобок "{" и "}"
        right_brace = [m.start() for m in re.finditer('\{' , data)]
        left_brace = [m.start() for m in re.finditer('\}' , data)]

        # получаем позиции начала слов 'radius', 'center' и 'line'
        radius_index = [m.start() for m in re.finditer('radius', data)][0]
        center_index = [m.start() for m in re.finditer('center', data)][0]
        line_index = [m.start() for m in re.finditer('line', data)][0]

        # ищем ближайшую "{" к слову 'radius'
        found_index, _ = found_nearest_index(radius_index, left_brace)
        # получаем значение радиуса сферы и меняем тип из строкового в действительное число
        R = float(data[radius_index+len('radius:'): found_index])

        # ищем ближайшую "[" к слову 'center' - для получения списка координат центра сферы
        _, found_index_position = found_nearest_index(center_index, right_brackets)
        # получаем содержимое между полученной скобкой "[" и парной для нее "]" - преобразуем в список действительных чисел
        center_value = [float(i) for i in data[right_brackets[found_index_position]+1:left_brackets[found_index_position]].split(',')]

        # ищем ближайшую "[" к слову 'line' - для получения списка координат прямой
        _, found_index_position = found_nearest_index(line_index, right_brackets)
        # первая точка: получаем содержимое между полученной скобкой "[" и парной для нее "]" - преобразуем в список действительных чисел
        point1 = [float(i) for i in data[right_brackets[found_index_position]+1:left_brackets[found_index_position]].split(',')]
        # вторая точка: получаем содержимое между следующей по порядка скобкой "[" и парной для нее "]" - преобразуем в список действительных чисел
        point2 = [float(i) for i in data[right_brackets[found_index_position+1]+1:left_brackets[found_index_position+1]].split(',')]

        # заполняем словарь геометрии
        geo_dict['sphere']['center'] = center_value
        geo_dict['sphere']['radius'] = R
        geo_dict['line'] = [point1, point2]

        return geo_dict


def render_geo(geo_dict: dict, points: list):
    # радиус сферы
    R = geo_dict['sphere']['radius']
    # координаты центра сферы
    x0 = geo_dict['sphere']['center'][0]
    y0 = geo_dict['sphere']['center'][1]
    z0 = geo_dict['sphere']['center'][2]
    # координаты точек прямой
    x1 = geo_dict['line'][0][0]
    y1 = geo_dict['line'][0][1]
    z1 = geo_dict['line'][0][2]
    x2 = geo_dict['line'][1][0]
    y2 = geo_dict['line'][1][1]
    z2 = geo_dict['line'][1][2]

    # Создаем заготовку рисунка
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Создаются сферические координаты сферы
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)

    # Создаются прямоугольные координаты сферы
    x = R * np.outer(np.cos(u), np.sin(v)) + x0
    y = R * np.outer(np.sin(u), np.sin(v)) + y0
    z = np.outer(np.ones(np.size(u)), R * np.cos(v)) + z0

    # Рисуем сферу
    ax.plot_surface(x, y, z, rstride=4, cstride=4, color='yellow', linewidth=1, alpha=0.5)

    # Считаем координаты прямой
    if x2 != x1:
        # Если координаты x прямой не одинаковы - используем уравнение прямой для z и y, проходящей через две заданные точки
        # задаем x  в области сферы
        x_line = np.array([x0 - R * 1.5, x0 + R * 1.5])
        # из x получаем y и z
        z_line = z1 + (z2 - z1) / (x2 - x1) * (x_line - x1)
        y_line = y1 + (y2 - y1) / (x2 - x1) * (x_line - x1)
    else:
        # Если координаты x прямой одинаковы, но координаты z различны
        if z2 != z1:
            if y2 != y1:
                # если координаты y прямой НЕ одинаковы
                # задаем y  в области сферы, x принимает фиксированные значения,
                # а для z используем уравнение прямой, проходящей через две заданные точки
                # (прямая лежит в плоскости параллельной плоскости  Oyz)
                x_line = np.array([x1, x2])
                y_line = np.array([y0 - R * 1.5, y0 + R * 1.5])
                z_line = z1 + (z2 - z1) / (y2 - y1) * (y_line - y1)
            else:
                # если координаты y прямой одинаковы
                # задаем z  в области сферы, x и y принимают фиксированные значения
                # (прямая параллельна оси Oz)
                x_line = np.array([x1, x2])
                y_line = np.array([y1, y2])
                z_line = np.array([z0 - R * 1.5, z0 + R * 1.5])
        # Если координаты x и z прямой одинаковы
        else:
            if y2 != y1:
                # задаем y  в области сферы, x и z принимают фиксированные значения
                # (прямая параллельна оси Oy)
                x_line = np.array([x1, x2])
                z_line = np.array([z1, z2])
                y_line = np.array([y0 - R * 1.5, y0 + R * 1.5])

    # Рисуем прямую
    ax.plot3D(x_line, y_line, z_line, 'black')

    # устанавливаем начальный вид
    elev = 10.0
    ax.view_init(elev=elev, azim=0)

    # устанавливаем масштаб рисунка в области сферы
    ax.auto_scale_xyz([x0 - R * 1.5, x0 + R * 1.5],
                      [y0 - R * 1.5, y0 + R * 1.5],
                      [z0 - R * 1.5, z0 + R * 1.5])


    # Рисуем точки
    for point in points:
        ax.scatter(point[0], point[1], point[2], color='green')

    # Подписываем оси
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()


if __name__ == '__main__':
    geo_dict = read_data('task2_input.txt')
    # радиус сферы
    R = geo_dict['sphere']['radius']
    # координаты центра сферы
    x0 = geo_dict['sphere']['center'][0]
    y0 = geo_dict['sphere']['center'][1]
    z0 = geo_dict['sphere']['center'][2]
    # координаты точек прямой
    x1 = geo_dict['line'][0][0]
    y1 = geo_dict['line'][0][1]
    z1 = geo_dict['line'][0][2]
    x2 = geo_dict['line'][1][0]
    y2 = geo_dict['line'][1][1]
    z2 = geo_dict['line'][1][2]

    # создаем пустой список координат пересечения прямой со сферой
    coord_list = []

    # проверка попарного равенства ВСЕХ точек - если все пары равны, это ошибка
    if all([x1 == x2, y1 == y2, z1 == z2]):
        print(" Все точки прямой попарно равны, повторите попытку!")
        sys.exit()

    # проверка неотрицательности радиуса сферы
    if R <= 0:
        print("Радиус сферы равен нулю или отрицательный, повторите попытку!")
        sys.exit()

    # Если координаты x прямой не одинаковы
    if x2 != x1:
        # формулы  выводятся вручную..
        Y = (y2-y1)/(x2-x1)
        Z = (z2-z1)/(x2-x1)

        A = y1-y0-Y*x1
        B = z1-z0-Z*x1

        # задача сводится к решению квадратного уравнения: ax**2+bx+c=0,
        # где:
        a = 1 + Y**2 + Z**2
        b = -2*x0 + 2*A*Y + 2*B*Z
        c = x0**2 + A**2 + B**2 - R**2

        # дискриминант задачи
        D = b**2 - 4*a*c

        # если дискриминант отрицательный - персечений нет
        if D < 0:
            print("Коллизий не найдено")
        else:
            # если дискриминант равен нулю - добавляем в список координат одно пересечение
            if D == 0:
                coord_list.append([-b/(2*a)])
            # если дискриминант равен положителен - добавляем в список координат два пересечения
            else:
                coord_list.append([(-b + math.sqrt(D))/(2*a)])
                coord_list.append([(-b - math.sqrt(D))/(2*a)])

        # для каждой точки из списка пересечений - определяем y и z по уравнению прямой
        for point in coord_list:
            x = point[0]
            y = y1 + Y * (x - x1)
            z = z1 + Z * (x - x1)
            point.append(y)
            point.append(z)

    # Если координаты x прямой одинаковы
    # (прямая лежит в плоскости параллельной Oyz)
    else:

        # Если точка x прямой (x=x1=x2) лежит далеко от центра сферы - пересечений нет
        if R**2 - (x1-x0)**2 < 0:
            print("Коллизий не найдено")
        else:
            # Если по x прямая и сферы могут пересекаться
            # Если координаты z прямой НЕ одинаковы
            if z2 != z1:
                # В случае если прямая лежит в плоскости параллельной Oyz -
                # задача также сводится к квадратному уравнению
                # (ищем пересечение прямой z(y) с окружностью радиуса R**2 - (x1-x0)**2)

                Y = (y2-y1) / (z2-z1)
                a = 1 + Y ** 2
                b = 2*Y*(y1 - Y*z1)
                c = (y1-Y*z1)**2 - R ** 2 + (x1-x0)**2
                D = b ** 2 - 4 * a * c

                # если дискриминант отрицательный - персечений нет
                if D < 0:
                    print("Коллизий не найдено")
                else:
                    # если дискриминант равен нулю - добавляем в список координат одно пересечение
                    if D == 0:
                        z = -b / (2 * a)
                        coord_list.append([x1, Y*(z-z1)+y1, z])
                    else:
                        # если дискриминант равен положителен - добавляем в список координат два пересечения
                        z = (-b + math.sqrt(D)) / (2 * a)
                        coord_list.append([x1, Y * (z - z1) + y1, z])
                        z = (-b - math.sqrt(D)) / (2 * a)
                        coord_list.append([x1, Y * (z - z1) + y1, z])

            # Если координаты z прямой одинаковы
            # (прямая параллельна оси Oy)
            else:
                # Если точки x и z прямой (x=x1=x2) (z=z1=z2) лежат далеко от центра сферы - пересечений нет
                if R ** 2 - (x1 - x0) ** 2 - (z1 - z0) ** 2 < 0:
                    print("Коллизий не найдено")
                else:
                    # В случае если прямая параллельна оси Oy -
                    # задача также сводится к квадратному уравнению
                    # (ищем пересечение прямой y(x) с окружностью радиуса R**2 - (z1-z0)**2 в плоскости параллельной плоскости Oxy)
                    a = 1
                    b = -2*y0
                    c = y0 - R**2 + (z1-z0)**2 + (x1-x0)**2
                    D = b ** 2 - 4 * a * c

                    # если дискриминант отрицательный - персечений нет
                    if D < 0:
                        print("Коллизий не найдено")
                    else:
                        # если дискриминант равен нулю - добавляем в список координат одно пересечение
                        if D == 0:
                            coord_list.append([x1, -b / (2 * a), z1])

                        # если дискриминант равен положителен - добавляем в список координат два пересечения
                        else:
                            y = (-b + math.sqrt(D)) / (2 * a)
                            coord_list.append([x1, y, z1])
                            coord_list.append([x1, -y, z1])

    # выводим список точек пересечений на экран
    for point in coord_list:
        print(point)

    # рендерим геометрию
    render_geo(geo_dict, points=coord_list)




