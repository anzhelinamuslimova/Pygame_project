import sys
import random
import pygame
from pygame.locals import *

# цвета
gray = (100, 100, 100)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
orange = (255, 128, 0)
purple = (255, 0, 255)
blue_lilac = (108, 70, 117)
moderate_purple = (84, 57, 100)

colors = (red, green, blue, yellow, orange, purple)

background_color = blue_lilac  # цвет фона
background_color2 = moderate_purple  # цвет фона в конце игры

internal_color = white  # внутренний цвет квадрата
outline_square = purple  # контур квадрата

speed = 25  # скорость работы программы
width_window = 580  # ширина окна в px
height_window = 400  # высота окна в px
speed_reveal = 10  # скорость раскрытия боксов
reveal_size = 40  # размер(высота и ширина) боксов в px
distance_box = 15  # расстояние между боксами
height = 4  # количество боксов в длину
width = 5  # количество боксов в ширину

assert (width * height) % 2 == 0

n = int((width_window - (width * (reveal_size + distance_box))) / 2)
m = int((height_window - (height * (reveal_size + distance_box))) / 2)

# фигуры
circle = 'круг'
oval = 'овал'
square = 'квадрат'
rhombus = 'ромб'
lines = 'линии'

shapes = (circle, oval, square, rhombus, lines)

assert len(colors) * len(shapes) * 2 >= width * height


def main():
    global clock_
    global display_

    pygame.init()
    clock_ = pygame.time.Clock()
    display_ = pygame.display.set_mode((width_window, height_window))
    pygame.display.set_caption('Memory Puzzle Game')

    x = 0
    y = 0
    main_board = get_random()
    revealed_boxes = generating_box_data(False)
    first_selection = None

    display_.fill(background_color)
    start_game(main_board)

    # основной игровой цикл
    while True:
        mouse_click = False

        display_.fill(background_color)  # рисует окно
        draw_board(main_board, revealed_boxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                x, y = event.pos
            elif event.type == MOUSEBUTTONUP:
                x, y = event.pos
                mouse_click = True

        box_x, box_y = box_pixel(x, y)
        if box_x != None and box_y != None:
            if not revealed_boxes[box_x][box_y]:
                draw_highlight(box_x, box_y)
            if not revealed_boxes[box_x][box_y] and mouse_click:
                reveal_box(main_board, [(box_x, box_y)])
                revealed_boxes[box_x][box_y] = True

                if first_selection == None:
                    first_selection = (box_x, box_y)
                else:
                    icon_shape, icon_color = shape_color(main_board, first_selection[0], first_selection[1])
                    icon_shape2, icon_color2 = shape_color(main_board, box_x, box_y)

                    # если 2 иконы не совпадают, то обе скрываются
                    if icon_shape != icon_shape2 or icon_color != icon_color2:
                        pygame.time.wait(1000)
                        cover_box(main_board, [(first_selection[0], first_selection[1]), (box_x, box_y)])
                        revealed_boxes[first_selection[0]][first_selection[1]] = False
                        revealed_boxes[box_x][box_y] = False
                    elif has_won(revealed_boxes):
                        game_won(main_board)
                        pygame.time.wait(2000)

                        main_board = get_random()
                        revealed_boxes = generating_box_data(False)

                        draw_board(main_board, revealed_boxes)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        start_game(main_board)
                    first_selection = None
        pygame.display.update()
        clock_.tick(speed)


def draw_board(board, revealed):
    # рисует все боксы в раскрытом или закрытом состоянии
    for box_x in range(width):
        for box_y in range(height):
            left, top = left_top(box_x, box_y)
            if not revealed[box_x][box_y]:
                pygame.draw.rect(display_, internal_color, (left, top, reveal_size, reveal_size))  # закрытый бокс
            else:
                shape, color = shape_color(board, box_x, box_y)  # раскрытый бокс
                draw_icon(shape, color, box_x, box_y)


def left_top(box_x, box_y):
    # координаты доски
    left = box_x * (reveal_size + distance_box) + n
    top = box_y * (reveal_size + distance_box) + m
    return left, top


def draw_icon(shape, color, box_x, box_y):
    quarter = int(reveal_size * 0.25)
    half = int(reveal_size * 0.5)
    left, top = left_top(box_x, box_y)

    if shape == circle:  # круг
        pygame.draw.circle(display_, color, (left + half, top + half), half - 5)
        pygame.draw.circle(display_, background_color, (left + half, top + half), quarter - 5)
    elif shape == oval:  # овал
        pygame.draw.ellipse(display_, color, (left, top + quarter, reveal_size, half))
    elif shape == square:  # квадрат
        pygame.draw.rect(display_, color, (left + quarter, top + quarter, reveal_size - half, reveal_size - half))
    elif shape == rhombus:  # ромб
        pygame.draw.polygon(display_, color, (
            (left + half, top), (left + reveal_size - 1, top + half), (left + half, top + reveal_size - 1),
            (left, top + half)))
    elif shape == lines:  # линии
        for i in range(0, reveal_size, 4):
            pygame.draw.line(display_, color, (left, top + i), (left + i, top))
            pygame.draw.line(display_, color, (left + i, top + reveal_size - 1), (left + reveal_size - 1, top + i))


def draw_highlight(box_x, box_y):
    left, top = left_top(box_x, box_y)
    pygame.draw.rect(display_, outline_square, (left - 5, top - 5, reveal_size + 10, reveal_size + 10), 4)


def get_random():
    # список имеющихся форм в любом имеющимся цвете
    icon = []

    for color in colors:
        for shape in shapes:
            icon.append((shape, color))

    random.shuffle(icon)
    icons_used = int(width * height / 2)  # сколько нужно иконок
    icon = icon[:icons_used] * 2  # из 1 в 2
    random.shuffle(icon)

    # создание структуры данных доски со случайно расположенными иконами
    board = []
    for x in range(width):
        column = []
        for y in range(height):
            column.append(icon[0])
            del icon[0]
        board.append(column)
    return board


def generating_box_data(val):
    revealed_boxes = []
    for i in range(width):
        revealed_boxes.append([val] * height)
    return revealed_boxes


def split_groups(size, list_):
    result = []
    for i in range(0, len(list_), size):
        result.append(list_[i:i + size])
    return result


def shape_color(board, box_x, box_y):
    # значение формы x, y хранится на доске[x][y][0]
    # значение цвета x, y хранится на доске[x][y][1]
    return board[box_x][box_y][0], board[box_x][box_y][1]


def box_pixel(x, y):
    for box_x in range(width):
        for box_y in range(height):
            left, top = left_top(box_x, box_y)
            box_ = pygame.Rect(left, top, reveal_size, reveal_size)
            if box_.collidepoint(x, y):
                return box_x, box_y
    return None, None


def draw_boxes(board, boxes, cover):
    # рисует боксы, которые закрыты или раскрыты
    for box in boxes:
        left, top = left_top(box[0], box[1])
        pygame.draw.rect(display_, background_color, (left, top, reveal_size, reveal_size))
        shape, color = shape_color(board, box[0], box[1])
        draw_icon(shape, color, box[0], box[1])
        if cover > 0:
            pygame.draw.rect(display_, internal_color, (left, top, cover, reveal_size))
    pygame.display.update()
    clock_.tick(speed)


def cover_box(board, boxes_to_cover):
    for cover in range(0, reveal_size + speed_reveal, speed_reveal):
        draw_boxes(board, boxes_to_cover, cover)


def reveal_box(board, boxes_to_reveal):
    for cover in range(reveal_size, (-speed_reveal) - 1, - speed_reveal):
        draw_boxes(board, boxes_to_reveal, cover)


def start_game(board):
    covered_boxes = generating_box_data(False)
    boxes = []

    for x in range(width):
        for y in range(height):
            boxes.append((x, y))
    random.shuffle(boxes)
    box_groups = split_groups(8, boxes)
    draw_board(board, covered_boxes)

    for box_group in box_groups:
        reveal_box(board, box_group)
        cover_box(board, box_group)


def game_won(board):
    # когда игрок выигрывает, фон меняется
    covered_boxes = generating_box_data(True)
    color_1 = background_color2
    color_2 = background_color

    for i in range(13):
        color_1, color_2 = color_2, color_1
        display_.fill(color_1)
        draw_board(board, covered_boxes)
        pygame.display.update()
        pygame.time.wait(300)


def has_won(revealed_boxes):
    # елси все боксы раскрыты - True, иначе - False
    for i in revealed_boxes:
        if False in i:
            return False
    return True


if __name__ == '__main__':
    main()
