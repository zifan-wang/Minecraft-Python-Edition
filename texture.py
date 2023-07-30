def cube_vertices(x, y, z, n):
    # 返回立方体的顶点，大小为2n。
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

n = 8

def tex_coord(x, y):
    # 返回纹理的边界顶点。
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def tex_coord1(x, y):
    # 返回纹理的边界顶点。
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx, dy + m, dx + m, dy + m, dx + m, dy

def tex_coord2(x, y):
    # 返回纹理的边界顶点。
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx + m, dy + m, dx + m, dy, dx, dy, dx, dy + m

def tex_coord3(x, y):
    # 返回纹理的边界顶点。
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx + m, dy + m, dx, dy + m, dx, dy, dx + m, dy

def tex_coords(top, bottom, side):
    # 返回顶部、底部和侧面的纹理列表。
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result

def tex_coords6(top, bottom, left, right, front, back):
    # 返回顶部、底部和侧面的纹理列表。
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    left = tex_coord(*left)
    right = tex_coord(*right)
    front = tex_coord(*front)
    back = tex_coord(*back)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(left)
    result.extend(right)
    result.extend(front)
    result.extend(back)
    return result

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SNOW = tex_coords((4, 0), (0, 1), (1, 3))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
DIRT = tex_coords((0, 1), (0, 1), (0, 1))
ICE = tex_coords((3, 1), (3, 1), (3, 1))
WOOD = tex_coords((0, 2), (0, 2), (3, 0))
LEAF = tex_coords((0, 3), (0, 3), (0, 3))

WATER = tex_coords((0, 4), (0, 4), (0, 4))
BRICK = tex_coords((1, 2), (1, 2), (1, 2))
PUMKIN = tex_coords((2, 2), (3, 3), (3, 3))
PUMKIN_FACE1 = tex_coords6((2, 2), (3, 3), (2, 3), (3, 3), (3, 3), (3, 3))
PUMKIN_FACE2 = tex_coords6((2, 2), (3, 3), (3, 3), (2, 3), (3, 3), (3, 3))
PUMKIN_FACE3 = tex_coords6((2, 2), (3, 3), (3, 3), (3, 3), (2, 3), (3, 3))
PUMKIN_FACE4 = tex_coords6((2, 2), (3, 3), (3, 3), (3, 3), (3, 3), (2, 3))
MELON = tex_coords((2, 4), (2, 4), (1, 4))
CLOUD = tex_coords((3, 2), (3, 2), (3, 2))
TNT = tex_coords((4, 2), (4, 3), (4, 1))
CACTUS = tex_coords((6, 3), (7, 0), (6, 4))

STONE = tex_coords((2, 0), (2, 0), (2, 0))
ENDSTONE = tex_coords((2, 1), (2, 1), (2, 1))
ANDESITE = tex_coords((6, 2), (6, 2), (6, 2))
DIORITE = tex_coords((6, 1), (6, 1), (6, 1))
GRANITE = tex_coords((6, 0), (6, 0), (6, 0))

COAL = tex_coords((5, 0), (5, 0), (5, 0))
IRNO = tex_coords((4, 4), (4, 4), (4, 4))
GOLDO = tex_coords((5, 1), (5, 1), (5, 1))
DIMO = tex_coords((3, 4), (3, 4), (3, 4))

MINE = [STONE, DIMO, GOLDO, IRNO, COAL, TNT]

# 立方体的6个面
FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]
