import os
from random import choice
from mcpi.minecraft import Minecraft
import time
import keyboard
from keyboard import mouse
from math import floor


def build_field(coors, color_1, color_2): # Построить игровое поле 9x9 
    x, y, z = coors
    for i in range(9):
        for j in range(9):
            if i not in [3, 4, 5]:
                c1 = color_1
                c2 = color_2
            else:
                c1 = color_2
                c2 = color_1
            if j not in [3, 4, 5]:
                mc.setBlock(x + j, y + i, z, c1)
            else:
                mc.setBlock(x + j, y + i, z, c2)             


def build_part(coors, color, num, flag, is_start): # построить деталь
    count = 0
    detail_coors = []
    x, y, z = coors 
    x, y, z = int(x), round(y), int(z)
    f = open(f'details/{num}').readlines()
    for i, line in enumerate(f):
        line = line.strip('\n')
        for j, symbol in enumerate(line):
            if is_start == True:
                x, y, z = int(x), int(y), int(z)
                detail_coors.append([x - j, y + 2 - i, z])
            if symbol == 'B':
                count += 1
                mc.setBlock(x - 4 + (4 - j), y + 4 - i, z, color)
                if flag == True and is_start == False:
                    blocks.append([x - 4 + (4 - j), y + 4 - i, z])

    if is_start == True:
        return detail_coors
    else:
        if flag == True and is_start == False:
             return count
        else:
            return False


def detail_control(detail_taken, block_id, detail_name): # поставить взятую деталь, счёт использованных деталей
    while detail_taken == True:
        for block in blocks:
            mc.setBlock(block, block_id)
        x, y, z = calc_block_pos()
        coors = [x+2, y-2, z]
        if mc.getBlock(x, y, z) == 0:
            build_part(coors, block_id, detail_name, False, False)
            time.sleep(0.1)
            build_part(coors, 0, detail_name, False, False)
        if mouse.is_pressed('right'):
            count = build_part(coors, block_id, detail_name, True, False)
            detail_taken = False
            block_id = 0
            global scores
            scores += count
            mc.postToChat('+' + str(count))
            mc.postToChat('Общий счёт:' + ' ' + str(scores))
            if counter == 3:
                is_empty = True
                global details_coors
                details_coors.clear()
                global details_names
                details_names.clear()
            elif counter != 3:
                is_empty = False
    time.sleep(1)
    return is_empty
            

def choose_detail(detail_taken, details_coors, details_names, block_id, details_start_blocks): # выбор детали
    ok = False
    if mouse.is_pressed('right'):
        if detail_taken == False:
            x, y, z = calc_block_pos()
            summ = 0
            for coors in details_coors: # Проверка: какая деталь там, где взгляд
                if ok:
                    break
                for t1 in [0, 1, -1]:
                    for t2 in [0, 1, -1]:
                        if [x+t2, y+t1, z] in coors:
                            summ += 1
                            founded_coors = [x+t2, y+t1, z]
                if summ > 0:
                    count = 0
                    for detail_coors in details_coors:
                        count += 1
                        if founded_coors in detail_coors: # Если взгляд в одной из 25 кординат из detail_coors
                            mc.postToChat('деталь выбрана')
                            detail_name = details_names[count-1] # Проверка окончена, detail_name - искомая деталь
                            detail_coors.clear()
                            build_part(details_start_blocks[count - 1], 0, detail_name, False, False)
                            global counter
                            counter += 1
                            time.sleep(1)
                            is_empty = detail_control(True, block_id, detail_name)
                            if is_empty == True:
                                counter = 0
                            ok = True
                            return is_empty
 
                   
def calc_block_pos(): # подсчёт координат проецируемой детали
    pos = mc.player.getPos()
    direction = mc.player.getDirection()
    # координаты блока напротив игрока
    x = int(pos.x + (direction.x * BLOCKDISTANCE))
    y = round(pos.y + (direction.y * BLOCKDISTANCE))
    z = round(pos.z + (direction.z * BLOCKDISTANCE))
    return x, y, z


def block_placed(coors): # проверка: есть ли блок на координатах coors
    x, y, z = coors

    global color_3
    c_1, c_2 = color_3
    
    out1, out2 = mc.getBlockWithData(x, y, z-1)
    if out1 == c_1 and out2 == c_2:
        return True
    else:
        return False


def check_v_h_rows(start_coors): # проверка заполнения верт. и гориз. рядов
    is_true = False
    v_row = ''
    v_row_coors = []
    h_row = ''
    h_row_coors = []
    row = 'BBBBBBBBB'
    coors = []
    x, y, z = start_coors
    for i in range(9):
        for j in range(9):
            if block_placed([x+j, y+i, z]):
                h_row += 'B'
                h_row_coors.append([x+j, y+i, z-1])
            else:
                h_row += '*'
            
            if block_placed([x+i, y+j, z]):
                v_row += 'B'
                v_row_coors.append([x+i, y+j, z-1])
            else:
                v_row += '*'

        if row in h_row:
            coors = coors + h_row_coors
        
        if row in v_row:
            coors = coors + v_row_coors

        if row in h_row or row in v_row:
            is_true = True
            for el in coors:
                mc.setBlock(el, 0)
                el[0] = int(el[0]) 
                el[1] = int(el[1]) 
                el[-1] = floor(el[-1])

                if el in blocks:
                    blocks.remove(el)

        h_row = ''
        v_row = ''
        coors = []
        h_row_coors = []
        v_row_coors = []
    if is_true:
        global scores
        scores += 15
        mc.postToChat('+15')
        mc.postToChat('Общий счёт:' + ' ' + str(scores))


def check_square(start_coors): # проверка заполнения квадрата 3x3
    is_true = False
    l = []
    rows_coors = []
    x, y, z = start_coors
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            row = ''
            row_coors = []
            for a in range(3):
                for b in range(3):
                    if block_placed([x + j + b, y + i + a, z]):
                        row += 'B'
                        row_coors.append([floor(x + j + b), int(y + i + a), floor(z-1)])
                    else:
                        row += '*'
                        row_coors.append([floor(x + j + b), int(y + i + a), floor(z-1)])
                l.append(row)
                rows_coors.append(row_coors)
                row = ''
                row_coors = []
            if l == ['BBB', 'BBB', 'BBB']:
                is_true = True
                for row_coors in rows_coors:
                    for el in row_coors:
                        mc.setBlock(el, 0)
                        if el in blocks:
                            blocks.remove(el)             
            l = []
            rows_coors = []
    if is_true:
        global scores
        scores += 17
        mc.postToChat('+17')
        mc.postToChat('Общий счёт:' + ' ' + str(scores))

def spawn_details(details_start_blocks, color): # спавн новых деталей
    details = os.listdir('details')
    for i in range(0, 3): 
        detail_name = choice(details)

        global details_names
        details_names.append(detail_name)

        # details.remove(detail_name)
        detail_coors = build_part(details_start_blocks[i], color, detail_name, True, True)
        if detail_coors != False:
            details_coors.append(detail_coors)                  
             
def check_theme(): #смена темы, если нажата 'q'
    if keyboard.is_pressed('q'):
        global theme_id
        theme_id += 1
        if theme_id > len(themes) - 1:
            theme_id = 0
        global color_1
        color_1 = themes[theme_id][0]
        global color_2
        color_2 = themes[theme_id][1]
        global color_3
        color_3 = themes[theme_id][-1]
        mc.postToChat('тема сменена')
        for block in blocks:
            mc.setBlock(block, color_3)
        
        
# /py blockdoku
mc = Minecraft.create()
x, y, z = mc.player.getPos() # получение координат игрока

themes = [[[155, 0], [251, 0], [251, 11]], [[159, 15], [159, 12], [5, 0]], [[251, 10], [251, 2], [251, 4]]]
theme_id = 0

color_1 = themes[theme_id][0] # id блока для первого квадрата 3x3
color_2 = themes[theme_id][1] # id блока для второго квадрата 3x3
color_3 = themes[theme_id][-1] # id блоков детали
tab = 1 # размер отступа между спавнами деталей (в блоках) 
scores = 0 # очки 
counter = 0 # количество использованных деталей (макс 3)
BLOCKDISTANCE = 5 # расстояние от игрока до проецируемой детали

blocks = [] # координаты блоков на поле
details_coors = [] # 75 координат всех блоков, где могут заспавниться детали, details_coors = [0, 1, 2] 0-2 = detail_coors = 25 координат
details_names = [] # Названия файлов 3х деталей
details_start_blocks = [ [x+7, y+1, z+3], [x+1, y+1, z+3], [x-5, y+1, z+3] ] # координаты спавна первого блока каждой детали
start_coors = [x - 4, y + 6, z + 7] #координаты спавна первого блока поля


details = os.listdir('details') # файлы внутри папки details
l = len(details)

spawn_details(details_start_blocks, color_3) # спавнятся 3 детали

while True: # обработка событий, обновления блоков

    check_theme() # проверка смены темы
    build_field(start_coors, color_1, color_2 ) # обновление поля
    is_empty = choose_detail(False, details_coors, details_names, color_3, details_start_blocks) # если True - все детали использованы
    check_square(start_coors) # проверка собранных квадратов 3x3 
    check_v_h_rows(start_coors) # проверка собранных рядов поля 1x9

    if is_empty: # спавнятся новые детали
        spawn_details(details_start_blocks, color_3)

    time.sleep(0.1)
    






