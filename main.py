"""
Name: Minecraft Python Edition
Version: v1.1.0-beta
Python-version: 3.9
Home-page: zifan.site
Author: Zifan
Author-email:
License: GPL3.0
"""
import sys
import time
import threading
import noise

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
from settings import *
from texture import *


def normalize(position):
    # 将三维坐标'position'的x、y、z取近似值
    x, y, z = position
    x, y, z = (round(x), round(y), round(z))
    return (x, y, z)

threads = deque() # 多线程队列


class mbatch:
    def __init__(self):
        self.batch = {}

    def add(self, x, z, *args):
        x = int(x / BASELEN) * BASELEN
        z = int(z / BASELEN) * BASELEN
        if (x, z) not in self.batch:
            self.batch[(x, z)] = pyglet.graphics.Batch()
        return self.batch[(x, z)].add(*args)

    def draw(self, dx, dz):
        dx = int(dx / BASELEN) * BASELEN
        dz = int(dz / BASELEN) * BASELEN
        for ax, az in NRC:
            x = dx + ax
            z = dz + az
            if (x, z) in self.batch:
                self.batch[(x, z)].draw()


class Model(object):

    def __init__(self):

        self.batch = mbatch()
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture()) # 纹理列表
        self.world = {} # 地图
        self.shown = {} # 显示的方块
        self._shown = {} # 显示的纹理
        self.pool = {} # 水池
        self.areat = {}
        self.mine = {}
        self.queue = deque() # 指令队列
        print("Loading...")
        self.dfy = self._initialize()
        print("OK")

    def tree(self, y, x, z, flag=True):
        # 生成树
        th = random.randint(3, 5)
        if th == 5:
            ts = 3
        else:
            ts = 3 if random.randint(1, 4) == 1 else 2
        mode = ts == 2 and random.random() > 0.3

        if flag:
            for i in range(y, y + th):
                self.add_block((x, i, z), WOOD)
            for dx in range(x - ts, x + ts + 1):
                for dz in range(z - ts, z + ts + 1):
                    if (dx == x - ts or dx == x + ts) and (dz == z - ts or dz == z + ts) and random.randint(1, 6) == 1:
                         continue
                    self.add_block((dx, y + th, dz), LEAF)
                    if (dx == x - ts or dx == x + ts) and (dz == z - ts or dz == z + ts) and random.randint(1, 4) == 1:
                         continue
                    self.add_block((dx, y + th + 1, dz), LEAF)
            if mode:
                for i in range(2):
                    self.add_block((x, y + th + 2 + i, z), LEAF)
                    self.add_block((x - 1, y + th + 2 + i, z), LEAF)
                    self.add_block((x + 1, y + th + 2 + i, z), LEAF)
                    self.add_block((x, y + th + 2 + i, z - 1), LEAF)
                    self.add_block((x, y + th + 2 + i, z + 1), LEAF)
            else:
                for dy in range(y + th + 2, y + th + ts + 2):
                    ts -= 1
                    for dx in range(x - ts, x + ts + 1):
                        for dz in range(z - ts, z + ts + 1):
                            self.add_block((dx, dy, dz), LEAF)
        else:
            for i in range(y, y + th):
                self._enqueue(self.add_block, (x, i, z), WOOD)
            for dx in range(x - ts, x + ts + 1):
                for dz in range(z - ts, z + ts + 1):
                    if (dx == x - ts or dx == x + ts) and (dz == z - ts or dz == z + ts) and random.randint(1, 6) == 1:
                        continue
                    self._enqueue(self.add_block, (dx, y + th, dz), LEAF)
                    if (dx == x - ts or dx == x + ts) and (dz == z - ts or dz == z + ts) and random.randint(1, 4) == 1:
                         continue
                    self._enqueue(self.add_block, (dx, y + th + 1, dz), LEAF)
            if mode:
                for i in range(2):
                    self._enqueue(self.add_block, (x, y + th + 2 + i, z), LEAF)
                    self._enqueue(self.add_block, (x - 1, y + th + 2 + i, z), LEAF)
                    self._enqueue(self.add_block, (x + 1, y + th + 2 + i, z), LEAF)
                    self._enqueue(self.add_block, (x, y + th + 2 + i, z - 1), LEAF)
                    self._enqueue(self.add_block, (x, y + th + 2 + i, z + 1), LEAF)
            else:
                for dy in range(y + th + 2, y + th + ts + 2):
                    ts -= 1
                    for dx in range(x - ts, x + ts + 1):
                        for dz in range(z - ts, z + ts + 1):
                            self._enqueue(self.add_block, (dx, dy, dz), LEAF)

    def get_mine(self, x, y, z):
        if (x, y, z) in self.mine:
            return MINE[self.mine[(x, y, z)]]
        d = (1 - y) / DEEP
        ds = random.random()
        s = 0
        if d < 0.5 or d > 0.8:
            if ds < 0.9930:
                s = 0
            elif ds < 0.9982:
                s = 4
            elif ds < 0.9995:
                s = 3
            elif ds < 0.9999:
                s = 2
            else:
                s = 1

        else:
            if ds < 0.99:
                s = 0
            elif ds < 0.996:
                s = 4
            elif ds < 0.999:
                s = 3
            elif ds < 0.9998:
                s = 2
            else:
                s = 1

        self.mine[(x, y, z)] = s
        if s != 0:
            for i in range(0, 2):
                for j in range(0, 2):
                    for k in range(0, 2):
                        if (x+i, y+j, z+k) not in self.mine:
                            self.mine[(x+i, y+j, z+k)] = s

        return MINE[s]

    def _initialize(self):
        # 初始化世界
        hl = WORLDLEN >> 1
        mn = 0
        gmap = [[0 for x in range(0, WORLDLEN)]for z in range(0, WORLDLEN)]
        quality = 16
        mul = 8
        print('Generating terrain...')
        for x in range(-hl, hl):
            for z in range(-hl, hl):
                gmap[x][z] = round(noise.pnoise2(
                                        x / quality, z / quality,
                                        octaves = Number_Of_Octaves,
                                        persistence = persistence,
                                        base = noise_seed
                                    ) * mul)
                mn = min(mn, gmap[x][z])
        mn = abs(mn)
        self.mn = mn
        print('Generating world...')
        for x in range(-hl, hl):
            for z in range(-hl, hl):
                self.areat[(int(x / BASELEN) * BASELEN, int(z / BASELEN) * BASELEN)] = 1
                gmap[x][z] += mn
                if gmap[x][z] < 2:
                    self.add_block((x, -1, z), random.choice([SAND, STONE]))
                    self.pool[(x, 0, z)] = 1
                    self._show_block((x, 0, z), WATER)
                    self.pool[(x, 1, z)] = 1
                    self._show_block((x, 1, z), WATER)
                    for y in range(-DEEP + 1, -1):
                        n = noise.pnoise3(x / quality, (y + DEEP) / quality, z / quality,
                                         octaves = Number_Of_Octaves,
                                         persistence = persistence,
                                         base = noise_seed)
                        if n > -0.4 or y > -3 or y < -DEEP + 3:
                            mine = self.get_mine(x, y, z)
                            if mine == STONE:
                                if y < -DEEP * 0.3 and ((n > -0.1 and n < 0) or n < -0.41):mine = ANDESITE
                                elif y < -DEEP * 0.4 and n > 0.1 and n < 0.2:mine = GRANITE
                                elif y < -DEEP * 0.5 and n > 0.25 and n < 0.3:mine = DIORITE
                            self.add_block((x, y, z), mine)
                else:
                    for y in range(-DEEP + 1, gmap[x][z]):
                        if y < 2:
                            n = noise.pnoise3(x / quality, (y + DEEP) / quality, z / quality,
                                             octaves = Number_Of_Octaves,
                                             persistence = persistence,
                                             base = noise_seed)
                            if n > -0.4 or y > -2 or y < -DEEP + 3:
                                mine = self.get_mine(x, y, z)
                                if mine == STONE:
                                    if y < -DEEP * 0.3 and ((n > -0.1 and n < 0) or n < -0.41):mine = ANDESITE
                                    elif y < -DEEP * 0.4 and n > 0.1 and n < 0.2:mine = GRANITE
                                    elif y < -DEEP * 0.5 and n > 0.25 and n < 0.3:mine = DIORITE
                                self.add_block((x, y, z), mine)
                        elif y >= gmap[x][z] - 1:
                            self.add_block((x, y, z), DIRT)
                        else:
                            self.add_block((x, y, z), STONE)
                    self.add_block((x, gmap[x][z], z), GRASS)
                self.add_block((x, -DEEP, z), ENDSTONE)
        print('Generating trees...')
        for x in range(-hl, hl, 4):
            for z in range(-hl, hl, 4):
                if x == 0 and z == 0:
                    continue
                if random.randint(1, 8) == 1 and gmap[x][z] > 1:
                    self.tree(gmap[x][z] + 1, x, z)
                    for i in range(x, x + 4):
                        for j in range(z, z + 4):
                            self._show_block((i, 30, j), CLOUD)
                elif random.randint(1, 8) == 1 and gmap[x][z] > 2:
                    if random.randint(1, 2) == 1:
                        self.add_block((x, gmap[x][z] + 1, z), random.choice([PUMKIN, PUMKIN, PUMKIN_FACE1, PUMKIN_FACE2, PUMKIN_FACE3, PUMKIN_FACE4]))
                    else:
                        self.add_block((x, gmap[x][z] + 1, z), MELON)
        return gmap[0][0] + 2

    def getsand(self):
        result = []
        func = [tex_coord, tex_coord1, tex_coord2, tex_coord3]
        result.extend(random.choice(func)(1, 1) * 6)
        return result

    def initdesert(self, dx, dz):
        gmap = [[0 for x in range(0, BASELEN)]for z in range(0, BASELEN)]
        hole = [[0 for x in range(0, BASELEN)]for z in range(0, BASELEN)]
        quality = 16
        mul = 8
        for x in range(0, BASELEN):
            for z in range(0, BASELEN):
                gmap[x][z] = round(noise.pnoise2(
                                        (dx + x) / quality, (dz + z) / quality,
                                        octaves = Number_Of_Octaves,
                                        persistence = persistence,
                                        base = noise_seed
                                    ) * mul)
        for x in range(0, BASELEN):
            for z in range(0, BASELEN):
                gmap[x][z] = max(gmap[x][z] + self.mn, 2)
                xx = x + dx
                zz = z + dz
                for y in range(-DEEP + 1, gmap[x][z] + 1):
                    if y < 2:
                        n = noise.pnoise3(xx / quality, (y + DEEP) / quality, zz / quality,
                                          octaves = Number_Of_Octaves,
                                          persistence = persistence,
                                          base = noise_seed)
                        if n > -0.4 or y > -2 or y < -DEEP + 3:
                            mine = self.get_mine(xx, y, zz)
                            if mine == STONE:
                                if y < -DEEP * 0.3 and ((n > -0.1 and n < 0) or n < -0.41):mine = ANDESITE
                                elif y < -DEEP * 0.4 and n > 0.1 and n < 0.2:mine = GRANITE
                                elif y < -DEEP * 0.5 and n > 0.25 and n < 0.3:mine = DIORITE
                            self._enqueue(self.add_block, (xx, y, zz), mine)
                    else:
                        self._enqueue(self.add_block, (xx, y, zz), self.getsand())
                self._enqueue(self.add_block, (xx, -DEEP, zz), ENDSTONE)
        for x in range(0, BASELEN, 4):
            for z in range(0, BASELEN, 4):
                xx = x + dx
                zz = z + dz
                if random.randint(1, 16) == 1:
                    tall = random.randint(2, 4)
                    for i in range(tall):
                        self._enqueue(self.add_block, (xx, gmap[x][z] + i + 1, zz), CACTUS)

    def initpart(self, dx, dz):
        random.seed(SEED)
        mode = self.areat[(dx, dz)]
        if mode == 0:
            self.initdesert(dx, dz)
            return
        gmap = [[0 for x in range(0, BASELEN)]for z in range(0, BASELEN)]
        hole = [[0 for x in range(0, BASELEN)]for z in range(0, BASELEN)]
        quality = 16
        mul = 8 if mode <= 2 else 16 * (mode - 2)
        for x in range(0, BASELEN):
            for z in range(0, BASELEN):
                gmap[x][z] = round(noise.pnoise2(
                                        (dx + x) / quality, (dz + z) / quality,
                                        octaves = Number_Of_Octaves,
                                        persistence = persistence,
                                        base = noise_seed
                                    ) * mul)

        for x in range(0, BASELEN):
            for z in range(0, BASELEN):
                gmap[x][z] += self.mn if mode <= 2 else self.mn + 2
                xx = x + dx
                zz = z + dz
                if gmap[x][z] < 2:
                    self._enqueue(self.add_block, (xx, -1, zz), random.choice([SAND, STONE]))
                    if mode != 1:
                        self._enqueue(self.add_block, (xx, 0, zz), ICE)
                        self._enqueue(self.add_block, (xx, 1, zz), ICE)
                    else:
                        self.pool[(xx, 0, zz)] = 1
                        self._enqueue(self._show_block, (xx, 0, zz), WATER)
                        self.pool[(xx, 1, zz)] = 1
                        self._enqueue(self._show_block, (xx, 1, zz), WATER)
                    for y in range(-DEEP + 1, -1):
                        n = noise.pnoise3(xx / quality, (y + DEEP) / quality, zz / quality,
                                         octaves = Number_Of_Octaves,
                                         persistence = persistence,
                                         base = noise_seed)
                        if n > -0.4 or y > -3 or y < -DEEP + 3:
                            mine = self.get_mine(xx, y, zz)
                            if mine == STONE:
                                if y < -DEEP * 0.3 and ((n > -0.1 and n < 0) or n < -0.41):mine = ANDESITE
                                elif y < -DEEP * 0.4 and n > 0.1 and n < 0.2:mine = GRANITE
                                elif y < -DEEP * 0.5 and n > 0.25 and n < 0.3:mine = DIORITE
                            self._enqueue(self.add_block, (xx, y, zz), mine)
                else:
                    for y in range(-DEEP + 1, gmap[x][z]):
                        n = noise.pnoise3(xx / quality, (y + DEEP) / quality, zz / quality,
                                          octaves = Number_Of_Octaves,
                                          persistence = persistence,
                                          base = noise_seed)
                        if n < -0.5 and (hole[x][z] == 1 or y < 2) and hole[x][z] != 2:
                            hole[x][z] = 1
                            continue
                        elif y >= 2:
                            hole[x][z] = 2
                        if y < 2:
                            if n > -0.4 or y > -2 or y < -DEEP + 3:
                                mine = self.get_mine(xx, y, zz)
                                if mine == STONE:
                                    if y < -DEEP * 0.3 and ((n > -0.1 and n < 0) or n < -0.41):mine = ANDESITE
                                    elif y < -DEEP * 0.4 and n > 0.1 and n < 0.2:mine = GRANITE
                                    elif y < -DEEP * 0.5 and n > 0.25 and n < 0.3:mine = DIORITE
                                self._enqueue(self.add_block, (xx, y, zz), mine)
                        elif y >= gmap[x][z] - 1:
                            self._enqueue(self.add_block, (xx, y, zz), DIRT)
                        else:
                            self._enqueue(self.add_block, (xx, y, zz), STONE)
                    if noise.pnoise3(xx / quality, (gmap[x][z] + DEEP) / quality, zz / quality,
                                     octaves = Number_Of_Octaves,
                                     persistence = persistence,
                                     base = noise_seed) >= -0.5 or hole[x][z] != 1:
                        self._enqueue(self.add_block, (xx, gmap[x][z], zz), GRASS if mode == 1 else SNOW)
                self._enqueue(self.add_block, (xx, -DEEP, zz), ENDSTONE)
        for x in range(0, BASELEN, 4):
            for z in range(0, BASELEN, 4):
                if hole[x][z]:
                    continue
                xx = x + dx
                zz = z + dz
                if mode == 1:
                    if random.randint(1, 8) == 1 and gmap[x][z] > 1:
                        self.tree(gmap[x][z] + 1, xx, zz, False)
                        for i in range(xx, xx + 4):
                            for j in range(zz, zz + 4):
                                self._enqueue(self._show_block, (i, 30, j), CLOUD)
                    elif random.randint(1, 8) == 1 and gmap[x][z] > 2:
                        if random.randint(1, 2) == 1:
                            self._enqueue(self.add_block, (xx, gmap[x][z] + 1, zz), random.choice([PUMKIN, PUMKIN, PUMKIN_FACE1, PUMKIN_FACE2, PUMKIN_FACE3, PUMKIN_FACE4]))
                        else:
                            self._enqueue(self.add_block, (xx, gmap[x][z] + 1, zz), MELON)
                else:
                    if random.randint(1, 16) == 1 and gmap[x][z] > 1:
                        self.tree(gmap[x][z] + 1, xx, zz, False)
                        for i in range(xx, xx + 4):
                            for j in range(zz, zz + 4):
                                self._enqueue(self._show_block, (i, 30, j), CLOUD)
                    elif random.randint(1, 15) == 1 and gmap[x][z] > 2:
                        self._enqueue(self.add_block, (xx, gmap[x][z] + 1, zz), random.choice([PUMKIN, PUMKIN, PUMKIN_FACE1, PUMKIN_FACE2, PUMKIN_FACE3, PUMKIN_FACE4]))

    def hit_test(self, position, vector, max_distance=8):
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        if immediate:
            if self.exposed(position):# 如果看不见就不显示
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        del self.world[position]
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):# 方块周围看到的显示看不到的隐藏
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        self._shown[position] = self.batch.add(x, z, 24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        self._shown.pop(position).delete()

    def _enqueue(self, func, *args):
        self.queue.append((func, args))

    def _dequeue(self):
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        start = time.perf_counter()
        while threads and time.perf_counter() - start < 0.9 / TICKS_PER_SEC:
            threading.Thread(target=self.initpart, args=threads.popleft()).start()
        while self.queue and time.perf_counter() - start < 0.9 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        while self.queue:
            self._dequeue()


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.exclusive = False
        self.flying = False # 是否在飞行
        self.swimming = False # 是否在游泳
        self.walking = True # 是否在走路
        self.jumping = False # 是否在跳
        self.model = Model()
        self.strafe = [0, 0]
        self.position = (0, self.model.dfy, 0)
        self.rotation = (0, 0)
        self.reticle = None
        self.dy = 0
        self.pw = False
        self.pa = False
        self.ps = False
        self.pd = False
        self.inventory = [GRASS, DIRT, STONE, SAND, WOOD, BRICK, PUMKIN, MELON, TNT]
        self.block = self.inventory[0]
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        x, y = self.rotation
        m = math.cos(math.radians(y))
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying or self.swimming:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    dy *= -1
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        # 刷新
        global GTIME
        global GNIGHT
        global GDAY
        glClearColor(0.5 - GTIME * 0.01, 0.69 - GTIME * 0.01, 1.0 - GTIME * 0.01, 1)
        setup_fog()
        GTIME += GDAY if GTIME < 23 else GNIGHT
        if GTIME > 50:
            GTIME = 50
            GNIGHT = -GNIGHT
            GDAY = -GDAY
        elif GTIME < 0:
            GTIME = 0
            GNIGHT = -GNIGHT
            GDAY = -GDAY
        self.model.process_queue()
        x, y, z = self.position
        self.swimming = False
        for i in range(0, PLAYER_HEIGHT):
            if normalize((x, y - i, z)) in self.model.pool:
                self.swimming = True
                break
        dx = int(self.position[0] / BASELEN) * BASELEN
        dz = int(self.position[2] / BASELEN) * BASELEN
        quality = 256
        for ax, az in NRC:
            x = dx + ax
            z = dz + az
            if (x, z) not in self.model.areat:
                self.model.areat[(x, z)] = 1
                n = noise.pnoise2(x / quality, z / quality,
                                 octaves = 1,
                                 persistence = 0.3,
                                 base = noise_seed)
                if n < -0.08:
                    self.model.areat[(x, z)] = 1
                elif n < 0.08:
                    self.model.areat[(x, z)] = 0
                elif n < 0.3:
                    self.model.areat[(x, z)] = 2
                else:
                    self.model.areat[(x, z)] = 3 + n
                threads.append((x, z))
        m = 8
        dt = min(dt, 0.2)
        if self.jumping:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        for _ in range(m):
            self._update(dt / m)

    def _update(self, dt):
        speed = FLYING_SPEED if self.flying else WALKING_SPEED if self.walking else RUNNING_SPEED
        if self.swimming:
            speed = SWIMMING_SPEED
        d = dt * speed
        dx, dy, dz = self.get_motion_vector()
        dx, dy, dz = dx * d, dy * d, dz * d
        if not self.flying and not self.swimming:
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

    def collide(self, position, height):
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:
            for i in range(3):
                if not face[i]:
                    continue
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(height):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        self.dy = 0
                    break
        return tuple(p)

    def TNTboom(self, dx, dy, dz):
        # TNT爆炸
        r = 3
        self.model.remove_block((dx, dy, dz))
        for x in range(dx - r, dx + r + 1):
            for y in range(dy - r, dy + r + 1):
                for z in range(dz - r, dz + r + 1):
                    if (x, y, z) not in self.model.world or self.model.world[(x, y, z)] == ENDSTONE:
                        continue
                    if self.model.world[(x, y, z)] == TNT:
                        self.TNTboom(x, y, z)
                        continue
                    d = math.sqrt((x-dx)*(x-dx)+(y-dy)*(y-dy)+(z-dz)*(z-dz))
                    if d < r - 0.3:
                        self.model.remove_block((x, y, z))
                    elif d < r + 0.3 and random.randint(0, 1):
                        self.model.remove_block((x, y, z))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                if previous:
                    # 鼠标右击
                    x, y, z = self.position
                    flag = True
                    for i in range(0, PLAYER_HEIGHT):
                        if previous == normalize((x, y - i, z)):
                            flag = False
                            break
                    if flag:
                        self.model.add_block(previous, self.block)
            elif button == pyglet.window.mouse.LEFT and block:
                # 鼠标左击
                texture = self.model.world[block]
                if texture == TNT:
                    self.TNTboom(block[0], block[1], block[2])
                elif texture != ENDSTONE:
                    self.model.remove_block(block)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        # 键盘按键
        if symbol == key.W:
            self.strafe[0] -= 1
            self.pw = True
        elif symbol == key.S:
            self.strafe[0] += 1
            self.ps = True
        elif symbol == key.A:
            self.strafe[1] -= 1
            self.pa = True
        elif symbol == key.D:
            self.strafe[1] += 1
            self.pd = True
        elif symbol == key.SPACE:
            self.jumping = True
        elif symbol == key.R:
            self.walking = not self.walking
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.E:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]

    def on_key_release(self, symbol, modifiers):
        # 键盘松键
        if symbol == key.W:
            if self.pw:
                self.strafe[0] += 1
                self.pw = False
        elif symbol == key.S:
            if self.ps:
                self.strafe[0] -= 1
                self.ps = False
        elif symbol == key.A:
            if self.pa:
                self.strafe[1] += 1
                self.pa = False
        elif symbol == key.D:
            if self.pd:
                self.strafe[1] -= 1
                self.pd = False
        elif symbol == key.SPACE:
            self.jumping = False

    def on_resize(self, width, height):
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        # 3d模式
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        # 3d模式
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        # 绘制
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw(self.position[0], self.position[2])
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

    def draw_focused_block(self):
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        x, y, z = self.position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label.draw()

    def draw_reticle(self):
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)


def setup_fog():
    # 初始化迷雾和光照
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5 - GTIME * 0.01, 0.69 - GTIME * 0.01, 1.0 - GTIME * 0.01, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 30.0)
    glFogf(GL_FOG_END, 60.0)
    #setup_light()

def setup_light():
    # 初始化光照
    gamelight = 5.0 - GTIME / 10
    glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(gamelight, gamelight, gamelight, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(gamelight, gamelight, gamelight, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (GLfloat * 4)(1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(0.0, 0.0, 0.0, 0.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

def setup():
    # 初始化
    glClearColor(0.5 - GTIME * 0.01, 0.69 - GTIME * 0.01, 1.0 - GTIME * 0.01, 1)
    glEnable(GL_CULL_FACE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()

def main():
    window = Window(width=800, height=600, caption='Minecraft Python Edition', resizable=True)
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()

if __name__ == '__main__':
    main()
