import math

TICKS_PER_SEC = 150

SECTOR_SIZE = 16

GTIME = 0 # 当前世界时间
GDAY = 0.0005
GNIGHT = 0.0015

WALKING_SPEED = 5 # 走路速度
RUNNING_SPEED = 8 # 跑步速度
FLYING_SPEED = 15 # 飞行速度
SWIMMING_SPEED = 3

GRAVITY = 30.0 # 重力
MAX_JUMP_HEIGHT = 1.25 # 最大跳跃速度
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 35 # 终端速度

PLAYER_HEIGHT = 2 # 玩家高度

WORLDLEN = 64 # 世界长度
BASELEN = 16
DEEP = 16 # 世界深度

TEXTURE_PATH = 'texture.png' # 纹理文件

NRC = []
#DNRC = []

def initNRC():

    def sort_key(p):
        return p[0] ** 2 + p[1] ** 2

    pad = 4
    for x in range(-pad, pad + 1):
        for z in range(-pad, pad + 1):
            if x ** 2 + z ** 2 <= pad ** 2:
                NRC.append((x * BASELEN, z * BASELEN))
    NRC.sort(key=sort_key)
    print('NRC size: ',len(NRC))
    #for x in range(-1,2):
    #    for y in range(-1,2):
    #        DNRC.append((x*64, y*64))

initNRC()
