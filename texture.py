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

def tex_coord(x, y, n=8):
    # 返回纹理的边界顶点。
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


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

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SNOW = tex_coords((4, 0), (0, 1), (1, 3))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
DIRT = tex_coords((0, 1), (0, 1), (0, 1))
STONE = tex_coords((2, 0), (2, 0), (2, 0))
ENDSTONE = tex_coords((2, 1), (2, 1), (2, 1))
WATER = tex_coords((0, 4), (0, 4), (0, 4))
ICE = tex_coords((3, 1), (3, 1), (3, 1))
WOOD = tex_coords((0, 2), (0, 2), (3, 0))
LEAF = tex_coords((0, 3), (0, 3), (0, 3))
BRICK = tex_coords((1, 2), (1, 2), (1, 2))
PUMKEY = tex_coords((2, 2), (3, 3), (2, 3))
MELON = tex_coords((2, 4), (2, 4), (1, 4))
CLOUD = tex_coords((3, 2), (3, 2), (3, 2))
TNT = tex_coords((4, 2), (4, 3), (4, 1))
DIMO = tex_coords((3, 4), (3, 4), (3, 4))
IRNO = tex_coords((4, 4), (4, 4), (4, 4))
COAL = tex_coords((5, 0), (5, 0), (5, 0))
GOLDO = tex_coords((5, 1), (5, 1), (5, 1))

# 立方体的6个面
FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]
