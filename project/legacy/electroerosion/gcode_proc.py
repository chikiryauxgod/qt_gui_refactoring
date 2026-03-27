import re
import os
import sys
import json

'''
Выделить перемещение с экструдером, и каждое перемещение разбить на отрезки длиной в диаметр электрода.
Перемещаться вдоль отрезков эрозируя между всеми перемещениями.
'''

MIN_DISTANCE = 5
SCALE_MODEL_FACTOR = 3

def gcode_proc(in_file, active_layer=None, logger=print):
    f = [x for x in open(in_file, 'r').readlines() if x.startswith('G') or x.startswith(';LAY')]
    y = re.findall(r'YER:(\d+)(.*?);((LA)|(En))', ''.join(f), re.DOTALL | re.MULTILINE)

    layer_count = len(y)
    layers = (x[1] for x in y)

    logger(f'Всего слоев: {layer_count}.', file=sys.stderr)
    
    active_layer = active_layer if active_layer else layer_count-1
    # ^^ Whats вронг with this ребятишки?
    layer_number = 0
    style = ""
    max_x = 0
    max_y = 0
    try:
        last_n_rr = ()
        err_cnt = 0
        l = 0
        ex_group = []
        for layer in layers:
            n_rr = re.findall(r'^G.*?X(\d+\.\d+).*?Y(\d+\.\d+)(.*?E(\d+\.\d+))?', layer, re.MULTILINE)
            for src in n_rr:
                try:
                    x = float(src[0])
                    y = float(src[1])
                    original_line = layer.split('\n')[l]
                    e = 1 if src[3] else 0
                    ex_group += [(x,y,l,e,original_line)]

                except IndexError:
                    logger(f'Некоторая ошибка с индексами src в номере слоя {l}.', file=sys.stderr)
            l += 1
            c_id = 0

        exit_code = 0
    except IOError as ex:
        logger(f'Проблема с файлом {in_file}, {ex}', file=sys.stderr)
        exit_code = -1
    except FileNotFoundError as ex:
        logger(f'[ ERROR ]: Not written!')
        exit_code = -2
    
    return exit_code, ex_group

if __name__ == '__main__':
    in_file = 'test.gcode'
    gcode_proc(in_file, active_layer=None)

