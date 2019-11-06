import pygame
from tkinter import colorchooser 
from tkinter import * 
import numpy as np

# def callback(): 
#     filename = colorchooser.askcolor() 
#     print(filename) 
# root = Tk() 
# Button(root, text='b', command=callback).pack() 
# mainloop()
leds = np.zeros((8, 32), dtype=np.int)
block = 25
width, height = 960, 480 
pygame.init()           
screen = pygame.display.set_mode((width, height)) 
pygame.display.set_caption("led parser")        

#建立畫布bg
bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill((255,255,255))          
#顯示
screen.blit(bg, (0,0))
pygame.display.update()

for i in range(0,block*9,block):
    pygame.draw.line(bg,(0,0,0),(0,i),(block*32,i))
for i in range(0,block*33,block):
    pygame.draw.line(bg,(0,0,0),(i,0),(i,block*8))
screen.blit(bg, (0,0)) 
pygame.display.update()

def get_pos(pos):
    for i in range(0,block*33,block):
        if pos <= i + block and pos >= i:
            # print("get",i/25)
            return i

#關閉程式的程式碼
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit() 
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if pos[0] <= block*32 and pos[1] <= block*8:
                y = get_pos(pos[0])
                x = get_pos(pos[1])
                pygame.draw.rect(bg,(255,0,0),[y,x,block,block],0)
                leds[int(x/25)][int(y/25)]= 1
                # print(int(x/25),int(y/25),leds[int(x/25)][int(y/25)])  
                screen.blit(bg, (0,0)) 
                pygame.display.update()
                # print(pos)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:  
            pos_list = []
            for i in range(32):
                for j in range(8):  
                    if leds[j][i] == 1:
                        pos = 0
                        if i%2==0:
                            pos = 8*i+j+1
                        else:
                            pos = 8*i+(8-j)
                        pos_list.append(pos)

            pos_list.sort()
            print(pos_list)
