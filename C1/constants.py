class Colors:
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    PURPLE = (255, 0, 255)
    BLACK = (0, 0, 0)


class Display:
    WIDTH, HEIGHT = 1024, 768


edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]

walls = [
    [0, 1, 5, 4],  # bottom wall
    [2, 3, 7, 6],  # top wall
    [1, 2, 6, 5],  # right wall
    [3, 0, 4, 7],  # left wall
    [4, 5, 6, 7],  # front wall
    [0, 1, 2, 3]  # back wall
]
