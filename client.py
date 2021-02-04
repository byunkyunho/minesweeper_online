import pygame as pg
import random as rd
import time
import threading
import socket
import json

pg.init()
pg.key.set_repeat(1, 1)

HOST =  '192.168.1.50'
PORT = 5000

width = 680
height = 430
row, column, all_bomb = 10,10,10

pg.display.set_caption("minesweeper (client)")

try:
    load_image = pg.image.load("mine.png")
    icon_image = pg.transform.scale(load_image, (32, 32))
    mine_image = pg.transform.scale(load_image, (22, 22))
    pg.display.set_icon(icon_image)
    load_mine = True
except :
    load_mine = False

num_font = pg.font.SysFont("Viga",35 ,bold=100)
start_font  = pg.font.SysFont("Viga",200)

win_game = pg.font.SysFont("Viga", 150).render("WIN!", True, (0,255,0))
lose_game = pg.font.SysFont("Viga", 150).render("LOSE!", True, (255,0,0))
question_mark = pg.font.SysFont("Viga", 500).render("?", True, (255,255,0))

num_color_list = [(0,0,255), (0,128,0), (255,0,0),(1, 0, 24),(1, 0, 124),(1, 0, 124),(1, 0, 124),(1, 0, 124)]

start_text_list = []

index_list = [(0, - 1), (0,  1), (1, 0), ( -1, 0), (-1, 1), (- 1, - 1), (1,1), (1, -1)]

num_light_list =[
    (True, True, True, True, True, True, False),
    (False, False, False, True, True, False, False),
    (True, False, True, True, False, True, True),
    (True, False, False, True, True, True ,True),
    (False, True, False, True, True,False, True),
    (True, True, False, False, True, True, True),
    (True, True, True, False, True, True, True),
    (True, False, False, True, True, False, False),
    (True, True, True, True, True, True, True),
    (True, True, False, True, True, True, True)
]

text_list = []

for a in range(5):
    start_text_list.append(start_font.render(str(a+1), True,(0,0,0)))

for a in range(8):
    text_list.append(num_font.render(str(a+1), True,num_color_list[a]))

def for_loop(x,y):
    check_list = [ x != 0, x !=row-1, y != column-1, y != 0, y != 0 and x != row-1, y != 0 and x != 0, y != column-1 and x != row-1, y != column-1 and x != 0]
    return zip(index_list, check_list)

def d_block(x1,y1, width, height, center_color, side_gap,ud_gap, flip):
    block_color = [ (128,128,128), (255,255,255)]
    if flip:
        block_color.reverse()
    pg.draw.polygon(screen, block_color[0], [(x1, y1), (x1 + width, y1), (x1, y1 + height)])
    pg.draw.polygon(screen, block_color[1], [(x1 + width, y1), (x1, y1 + height),(x1 + width, y1 + height )])
    pg.draw.rect(screen,  center_color, [ x1 + side_gap,y1 + ud_gap,  width - side_gap*2, height - ud_gap*2])

def d_exit():
    screen.blit(question_mark, (400 ,108))

def set_array():
    global main_array, state_array
    state_array = [[1 for a in range(row)] for b in range(column)]
    main_array =  [[0 for a in range(row)] for b in range(column)] 
    random = 0
    while not random == all_bomb:
        random_raw = rd.randint(0,column-1)
        random_column = rd.randint(0,row-1)
        if not main_array[random_raw][random_column] == 10:
            main_array[random_raw][random_column] = 10
            random += 1

    for y in range(column):
        for x in range(row):
            around_bomb = 0
            if not main_array[y][x] == 10:
                for  index,check in for_loop(x,y):
                    if check:
                        if main_array[y + index[0]][x + index[1]] == 10:
                            around_bomb += 1

                main_array[y][x] = around_bomb

def change_color(index):
    global light_color
    light_color = (96,0,0)
    if light[index]:
        light_color = (255,0,0)

def draw_num(x,y,num):
    global light_color, light
    
    light = num_light_list[num]

    num_xy_list =[
        (0,0,10,6,0,0,  -5, 0, 0, 5, 10, 0, 15,0, 10, 5),
        ( -6,8,6,9,-6,8,-1,8,-6,3,-6,17,-1,17,-6,22), 
        (-6,31,6,9,-6,30,-1,30,-6,24,-6,40,-1,40,-6,45),
        (12,8,6,9,17,8,12,8,17,3,17,17,12,17,17,22),
        (12,31,6,9,17,30,12,30,17,24,17,40,12,40,17,45),
        (1,42,9,6,1,42,-4,47,0,47,10,42,15,47,10,47),
        (0,20,11,7,0,20,-5,23,0,26,10,20,15,23,10,26),
    ]
    for num in range(7):
        change_color(num)
        xy_list = num_xy_list[num]
        pg.draw.rect(screen, light_color, [x + xy_list[0] , y + xy_list[1], xy_list[2],xy_list[3]])
        pg.draw.polygon(screen, light_color, [(x + xy_list[4], y + xy_list[5]), (x + xy_list[6], y + xy_list[7] ), (x + xy_list[8], y + xy_list[9])])
        pg.draw.polygon(screen, light_color, [(x + xy_list[10],y + xy_list[11]), (x  + xy_list[12], y+ xy_list[13] ), (x + xy_list[14], y + xy_list[15])])

def game_set():
    global main_array, state_array, gameover, bomb, start_time, start, win, red_block, button_up
    bomb = all_bomb
    set_array()
    gameover = False
    red_block = []
    win = False
    button_up = True

def d_time():
    global now
    if  win or other_win:
        for a,num in enumerate(now):
            draw_num(300+a*34,28, int(num))
    else:
        if start == 0:
            for a in range(3):
                draw_num(300+a*34,28, 0)

        else:
            now = round(time.time() - start)
            now = int_2_string(now)
            for a,num in enumerate(now):
                draw_num(300+a*34,28, int(num))

def d_background():
    d_block(0,0,width,height,(192,192,192),4,4,True)
    d_block(20 , 13 , width-40 , 80,(198,198,198),3,3, False) 

    d_block(20, 100, 310,310,(0,0,0),5,5 ,False) 
    d_block(350, 100, 310,310,(0,0,0),5,5 ,False) 

    d_block(30 , 23 , 110 , 60, (0,0,0),3,3, False)
    d_block(535 , 23 , 110 , 60, (0,0,0),3,3, False)
    d_block(285 , 23 , 110 , 60, (0,0,0),3,3, False) 
   
def d_line():
    for a in range(2):
        for x in range(row):
            pg.draw.line(screen, (128,128,128),(55+30*x+330*a, 105),(55+30*x+330*a, 104+30*column),  1)
        for y in range(column):
            pg.draw.line(screen, (128,128,128),(25+330*a, 104+30*y),(25+30*row+330*a, 104+30*y),  1)

def check_win():
    find = 0
    for y in range(column):
        for x in range(row):
            if state_array[y][x] == 0:
                find += 1
    if (row*column - all_bomb) == find:
        return True

def d_board(i,j,x, state, main):
    if state[i][j] == 0:
        pg.draw.rect(screen, (196,196,196), [x+j*30, 105+i*30, 30,30])
        if not  main[i][j] == 0:
            if not main[i][j] == 10:
                screen.blit(text_list[main[i][j] - 1], ((x+9)+j*30, 109+i*30))

    if state[i][j] > 0:
        d_block(x+j*30,105+i*30,30,30,(198,198,198), 5,5,True)

    if state[i][j] == 2:
        pg.draw.polygon(screen, (255,0,0), [((x+10)+j*30, 122+i*30), ((x+10)+j*30, 108 +i*30),((x+23)+j*30, 115+i*30)])
        pg.draw.line(screen, (0,0,0), ((x+9)+j*30, 108 +i*30), ((x+9)+j*30, 128 +i*30), 3)

def d_bomb(i,j,x, main, red):
    if main[i][j] == 10:
        if [i,j] in red or (i,j) in red:
            pg.draw.rect(screen, (255,0,0), [x+j*30, 105+i*30, 30,30])
        else:
            pg.draw.rect(screen, (196,196,196), [x+j*30, 105+i*30, 30,30])
        if load_mine:
            screen.blit(mine_image, ((x+4)+j*30, 107+i*30))
        else:
            pg.draw.line(screen, (255,0,0),((x+10)+j*30, 120+i*30),((x+20)+j*30, 108+i*30),  2)
            pg.draw.circle(screen, (0,0,0), (x+15+j*30, 120+i*30), 10)

def die(red_block_list):
    global red_block, count ,count_time, gameover
    red_block = red_block_list
    count = True
    gameover = True
    count_time = time.time()

def open_block(open):
    global bomb
    for y,x in open:
        if state_array[y][x] == 2:
            bomb += 1 
        state_array[y][x] = 0

        for  index,check in for_loop(x,y):
            if check:
                if not main_array[y + index[0]][x + index[1]] == 0:
                    if state_array[y + index[0]][x + index[1]] == 2:
                        bomb += 1
                    state_array[y + index[0]][x + index[1]] = 0

def update_main_array():
    global gameover, main_array, open_list, state_array, red_block, start, now, bomb, count, count_time
    if main_array[mouse_y][mouse_x] == 10:
        die([(mouse_y ,mouse_x)])
    elif state == 0:
        if main_array[mouse_y][mouse_x] != 0:
            around_flag = 0
            for (index_y, index_x), check in for_loop(mouse_x, mouse_y):
                if check:
                    if state_array[mouse_y + index_y][mouse_x + index_x] == 2:
                        around_flag+=1

            if around_flag == main_array[mouse_y][mouse_x]:
                red_block_list = []
            
                for (index_y, index_x), check in for_loop(mouse_x, mouse_y):
                    if check:
                        if main_array[mouse_y + index_y][mouse_x + index_x] == 10:
                            if state_array[mouse_y + index_y][mouse_x + index_x] != 2:
                                red_block_list.append((mouse_y + index_y, mouse_x + index_x))
                        elif main_array[mouse_y + index_y][mouse_x + index_x] == 0:
                            open_list = [(mouse_y+ index_y, mouse_x+ index_x)]         
                            copy_list  = []   
                            
                            for a in range(15):
                                copy_list = [xy for xy in open_list if xy not in copy_list]
                                for y,x in copy_list: 
                                    for index, check in for_loop(x,y):
                                        if check:
                                            if main_array[y + index[0]][x + index[1]] == 0:
                                                open_list.append((y + index[0], x + index[1]))
                                open_list = list(set(open_list))

                            open_block(open_list)

                        else:
                            if state_array[mouse_y + index_y][mouse_x + index_x] != 2:
                                state_array[mouse_y +index_y][mouse_x + index_x] = 0

                if red_block_list != []:
                    die(red_block_list)
    

    elif state == 1:

        if main_array[mouse_y][mouse_x] == 0:
            
            open_list = [(mouse_y, mouse_x)]         
            
            copy_list  = []   

            for a in range(15):
                copy_list = [xy for xy in open_list if xy not in copy_list]
                for y,x in copy_list: 
                    for index, check in for_loop(x,y):
                        if check:
                            if main_array[y + index[0]][x + index[1]] == 0:
                                open_list.append((y + index[0], x + index[1]))
                open_list = list(set(open_list))
                        
            open_block(open_list)
                         
        else:
            state_array[mouse_y][mouse_x] = 0        

def d_num_bomb():
    for a,num in enumerate(int_2_string(bomb)):
        draw_num(45 + a*34,28, int(num))
    for a,num in enumerate(int_2_string(other_bomb)):
        draw_num(550 + a*34,28, int(num))

def int_2_string(num):
    if num < 10:
        return f"00{num}"
    elif num < 100:
        return f"0{num}"
    elif num > 999:
        return "999"
    else:
        return str(num)

def update_data():
    global other_main, other_state, connecting, gameover, other_bomb, other_die, other_win, other_red_block
    connecting = True
    while connecting:
        try:
            send_data = json.dumps({"state":state_array,"main":main_array,"bomb":bomb,"die":gameover,"win":win,"red_block":red_block})
            client_socket.sendall(send_data.encode())
            data = json.loads(client_socket.recv(1024).decode())
            other_main = data['main']
            other_state = data['state']
            other_bomb = data['bomb']
            other_die = data['die']
            other_win = data['win']
            other_red_block = data['red_block']
        except:
            connecting = False
def connect():
    global client_socket
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            break
        except :
            pass


connect()


screen = pg.display.set_mode((width, height))

count = True
count_time = time.time()
game_set()
start_time = True
start = 0
other_main = [[1 for a in range(10)] for b in range(10)]
other_state = [[1 for a in range(10)] for b in range(10)]
other_bomb = 0
other_die = False
other_win = False
other_red_block = []
down_button = 0
running = True

connect_thread = threading.Thread(target=update_data)
connect_thread.daemon = True
connect_thread.start()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if not count:
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                if mouse_x > row*15 and mouse_x < 60+row*15 and mouse_y > 23 and mouse_y < 83:
                    game_set()
                    button_up = False
                    down_time = time.time()

                if not win and not gameover and not other_win:
                    if mouse_x > 32 and mouse_x < 25+30*row and mouse_y > 107 and mouse_y < 104+30*column:

                        mouse_x, mouse_y = (mouse_x - 25) // 30 ,(mouse_y - 105) // 30

                        state = state_array[mouse_y][mouse_x]

                        if event.button == 1 and state != 2:
                            update_main_array()

                        elif event.button == 3:
                            if state == 2:
                                state_array[mouse_y][mouse_x] = 1
                                bomb += 1
                            else:
                                if bomb > 0:
                                    if state == 1:
                                        state_array[mouse_y][mouse_x] = 2
                                        bomb -= 1

                    if check_win():
                        win = True
                        gameover = True
                        now = round((time.time() - start))
                        bomb = 0
                        now = int_2_string(now)


    d_background()

    for i in range(column):
        for j in range(row):

            d_board(i,j,25, state_array, main_array)
            d_board(i,j,355, other_state, other_main)

            if other_die:
                d_bomb(i,j,355, other_main, other_red_block)
            if gameover:
                d_bomb(i,j,25, main_array, red_block)
    d_line()
    d_time()
    d_num_bomb()


    if not connecting:
        d_exit()


    if win:
        screen.blit(win_game, (210, 170))
    elif other_win:
        screen.blit(lose_game, (200, 170))
     
    if not button_up:
        if time.time() - down_time > 0.1:
            button_up = True

    if count:
        if round(time.time() - count_time) < 5:
            screen.blit(start_text_list[4-round(time.time()-count_time)], (300, 140))
        else:
            count = False
            game_set()
            if start_time:
                start = time.time()
                start_time = False
    
    pg.display.update()
