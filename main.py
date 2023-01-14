"""
All files and images are stored in "resources" folder
You move with arrows and combine tiles with the same value
Goal of the game is to get a 2048 tile
"""

import ast
import copy
import pygame
import random
import time
from tkinter import *
from tkinter.ttk import *
from _thread import *

pygame.init()

class Board:
    def __init__(self, win, board, padding, mini_padding, square_size, rows, cols, colors, width, height):
        self.win = win
        self.board = board
        self.padding = padding
        self.mini_padding = mini_padding
        self.square_size = square_size
        self.rows = rows
        self.cols = cols
        self.colors = colors
        self.width = width
        self.height = height

    def draw_board(self):
        pygame.draw.rect(self.win, self.colors["bg"], pygame.Rect(0, self.padding, self.width, self.height - self.padding))

        for row in range(self.rows):
            for col in range(self.cols):
                color = self.colors[self.board[row][col]] if self.board[row][col] <= 2048 else self.colors["other"]
                square_x = col * self.square_size + (self.mini_padding * (col + 1))
                square_y = row * self.square_size + self.padding + (self.mini_padding * (row + 1))
                pygame.draw.rect(self.win, color, pygame.Rect(square_x, square_y, self.square_size, self.square_size))
                if self.board[row][col] != 0:
                    font = pygame.font.Font('freesansbold.ttf', 40)
                    text_obj = font.render(str(self.board[row][col]), True, BLACK if self.board[row][col] <= 2048 else WHITE)
                    win.blit(text_obj, (square_x + (self.square_size / 2) - (text_obj.get_width() / 2),
                                        square_y + (self.square_size / 2) - (text_obj.get_height() / 2)))

    def can_slide(self, numbers):
        if numbers == self.slide_numbers(numbers.copy()):
            return False

        return True

    def connect_numbers(self, numbers):
        global score_to_add

        # Numbers are connecting towards left (normal for "up" and "left")
        for i in range(len(numbers) - 1):
            if numbers[i] == numbers[i + 1] and numbers[i] != 0 and numbers[i + 1] != 0:
                numbers[i] *= 2
                score_to_add += numbers[i]
                numbers[i + 1] = 0

        return numbers

    def slide_numbers(self, numbers):
        # Numbers are connecting towards left (normal for "up" and "left")
        for i in range(1, len(numbers)):
            if numbers[i]:
                if not numbers[i - 1]:
                    numbers[i - 1] = numbers[i]
                    numbers[i] = 0

        return numbers

    def get_numbers_list(self, direction, row, col, board):
        numbers = []

        if direction in ["up", "down"]:
            for r in range(self.rows):
                numbers.append(board[r][col])

        elif direction in ["left", "right"]:
            for c in range(self.cols):
                numbers.append(board[row][c])

        if direction in ["down", "right"]:
            numbers.reverse()

        return numbers

    def replace_numbers(self, numbers, direction, row, col, board):
        if direction in ["down", "right"]:
            numbers.reverse()

        if direction in ["up", "down"]:
            for r in range(self.rows):
                board[r][col] = numbers[r]

        elif direction in ["left", "right"]:
            for c in range(self.cols):
                board[row][c] = numbers[c]

    def make_move(self, direction, board):
        for rc in range(self.rows):
            numbers = self.get_numbers_list(direction, rc, rc, board)

            while self.can_slide(numbers):
                numbers = self.slide_numbers(numbers)

            numbers = self.connect_numbers(numbers)

            while self.can_slide(numbers):
                numbers = self.slide_numbers(numbers)

            self.replace_numbers(numbers, direction, rc, rc, board)

        return board

    def spawn_number(self):
        global PLAYING, CURRENT, SCORE, score_to_add, HIGHSCORE, WON

        numbers = [2, 4]
        weights = [9, 1]
        x, y = self.get_random_empty_spot()

        time.sleep(.25)
        self.board[x][y] = random.choices(numbers, weights)[0] # There is 10% chance of getting a 4 spawned, else is 2

        remove_further("gamelog.txt") # Removing further logs in case there was "undo" clicked
        write_last("gamelog.txt", board.board)

        remove_further("scores.txt") # Removing further logs in case there was "undo" clicked
        SCORE += score_to_add
        write_last("scores.txt", SCORE)
        score_to_add = 0

        if SCORE > get_smth("highscore.txt", 0):
            HIGHSCORE = SCORE
            write_smth("highscore.txt", HIGHSCORE)

        CURRENT += 1
        write_smth("current.txt", CURRENT)

        if not WON: # if statement so win message won't be shown every move with 2048 tile on the board
            if board.check_if_won(board.board):
                start_new_thread(show_message, ("You won", "YOU WON!!!"))
                WON = True

        board_copy = copy.deepcopy(board.board) # deepcopy() for multidimensional lists (list in a list)
        if board.check_if_lost(board_copy):
            start_new_thread(show_message, ("Game over", "GAME OVER"))

        PLAYING = True

    def get_empty_spots(self):
        empty_spots = []

        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 0:
                    empty_spots.append((row, col))

        return empty_spots

    def get_random_empty_spot(self):
        empty_spots = self.get_empty_spots()

        return random.choice(empty_spots)

    def check_if_lost(self, board):
        if len(self.get_empty_spots()) == 0:
            for dir in ["up", "down", "right", "left"]:
                board_copy = copy.deepcopy(board)
                if board != self.make_move(dir, board_copy):
                    return False
        else:
            return False

        return True

    def check_if_won(self, board):
        for row in range(self.rows):
            for col in range(self.cols):
                if board[row][col] >= 2048:
                    return True

        return False

def get_smth(file_name, line):
    with open(f"resources/{file_name}", "r") as f:
        lines = f.readlines()
        return ast.literal_eval(lines[line])

def write_smth(file_name, text):
    with open(f"resources/{file_name}", "w") as f:
        f.write(str(text))

def write_last(file_name, newest):
    with open(f"resources/{file_name}", "r") as f:
        last = f.readlines()

    last.append(f"{str(newest)}\n")

    with open(f"resources/{file_name}", "w") as f:
        f.writelines(last)

def create_board(grid_size):
    board = []
    for row in range(grid_size):
        board.append([])
        for col in range(grid_size):
            board[row].append(0)

    return board

def show_message(title, message):
    root = Tk()
    root.title(title)
    root.geometry("225x75")
    root.resizable(False, False)
    root.iconbitmap("resources/icon.ico")

    info_label = Label(root, text=message, font=("freesansbold.ttf", 20))
    info_label.pack(ipady=15)

    root.mainloop()

def remove_further(filename):
    with open(f"resources/{filename}", "r") as f:
        lines = f.readlines()

    to_save = lines[:CURRENT + 1]

    with open(f"resources/{filename}", "w") as f:
        f.writelines(to_save)

def undo():
    global CURRENT, PLAYING, SCORE, WON

    if CURRENT > 0:
        PLAYING = False
        CURRENT -= 1
        write_smth("current.txt", CURRENT)
        board.board = get_smth("gamelog.txt", CURRENT)
        SCORE = get_smth("scores.txt", CURRENT)

        if board.check_if_won(board.board):
            WON = True
        else:
            WON = False

        PLAYING = True

def redo():
    global CURRENT, PLAYING, SCORE, WON

    with open("resources/gamelog.txt", "r") as f:
        lines = f.readlines()

    if len(lines) > CURRENT + 1:
        PLAYING = False
        CURRENT += 1
        write_smth("current.txt", CURRENT)
        board.board = get_smth("gamelog.txt", CURRENT)
        SCORE = get_smth("scores.txt", CURRENT)

        if board.check_if_won(board.board):
            WON = True
        else:
            WON = False

        PLAYING = True

def main_restart(load, grid_size):
    global BOARD, WIDTH, PADDING, HEIGHT, ROWS, COLS, MINI_PADDING, SQUARE_SIZE, COLORS, CURRENT, PLAYING, SCORE, score_to_add, WON, HIGHSCORE

    if load:
        CURRENT = get_smth("current.txt", 0)
        SCORE = get_smth("scores.txt", CURRENT)
        BOARD = get_smth("gamelog.txt", CURRENT)
    else:
        BOARD = create_board(grid_size)
        write_smth("gamelog.txt", "")
        CURRENT = 0
        write_smth("current.txt", CURRENT)
        SCORE = 0
        write_smth("scores.txt", "")
        write_last("scores.txt", SCORE)

    score_to_add = 0
    ROWS = COLS = len(BOARD)
    MINI_PADDING = WIDTH * 0.1 / ROWS
    SQUARE_SIZE = WIDTH / COLS - MINI_PADDING
    MINI_PADDING = WIDTH * 0.1 / (ROWS + 1)
    HIGHSCORE = get_smth("highscore.txt", 0)
    PLAYING = True
    COLORS = {
        0: (204, 192, 179),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
        "other": BLACK,
        "bg": (187, 173, 160)
    }
    board = Board(win, BOARD, PADDING, MINI_PADDING, SQUARE_SIZE, ROWS, COLS, COLORS, WIDTH, HEIGHT)
    if board.check_if_won(board.board):
        WON = True
    else:
        WON = False

    return board

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH = 500
PADDING = WIDTH * 0.2
HEIGHT = WIDTH + PADDING
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Game")
icon = pygame.image.load("resources/icon.png")
pygame.display.set_icon(icon)

board = main_restart(True, None)

def draw_padding(win):
    global restart_rect, undo_rect, redo_rect, HIGHSCORE

    restart = pygame.image.load("resources/restart.png")
    restart = pygame.transform.scale(restart, (64, 64))
    undo = pygame.image.load("resources/undo.png")
    undo = pygame.transform.scale(undo, (50, 50))
    redo = pygame.image.load("resources/redo.png")
    redo = pygame.transform.scale(redo, (50, 50))

    button_size = 75
    restart_rect = pygame.draw.rect(win, COLORS["bg"], pygame.Rect(10, (PADDING / 2) - (button_size / 2), button_size, button_size))
    undo_rect = pygame.draw.rect(win, COLORS["bg"], pygame.Rect(100, (PADDING / 2) - (button_size / 2), button_size, button_size))
    redo_rect = pygame.draw.rect(win, COLORS["bg"], pygame.Rect(190, (PADDING / 2) - (button_size / 2), button_size, button_size))

    win.blit(restart, (15, 17.5))
    win.blit(undo, (112.5, 25))
    win.blit(redo, (202.5, 25))

    font = pygame.font.Font('freesansbold.ttf', 24)
    score_text = font.render(f"Score: {SCORE}", True, BLACK)
    highscore_text = font.render(f"Highscore: {HIGHSCORE}", True, BLACK)
    win.blit(score_text, (275, 22.5))
    win.blit(highscore_text, (275, 52.5))

def restart(grid_size, root):
    global board, PLAYING

    PLAYING = False
    root.destroy()
    board = main_restart(False, grid_size)

    for i in range(2):
        numbers = [2, 4]
        weights = [9, 1]
        x, y = board.get_random_empty_spot()

        time.sleep(.25)
        board.board[x][y] = random.choices(numbers, weights)[0]

    write_last("gamelog.txt", board.board)

    PLAYING = True

def restart_box():
    root = Tk()
    root.title("Restart")
    root.geometry("204x75")
    root.resizable(False, False)
    root.iconbitmap("resources/icon.ico")

    restart_label = Label(root, text="Choose the grid size:")
    restart_label.place(x=10, y=10)

    choices = ["4", "6", "8", "10"]
    variable = StringVar(root)
    variable.set("4")

    grid_size = Combobox(root, values=choices, textvariable=variable, state="readonly", width=5)
    grid_size.place(x=130, y=10)

    restart_btn = Button(root, text="Restart", command=lambda: restart(int(variable.get()), root))
    restart_btn.place(x=15, y=40)

    cancel_btn = Button(root, text="Cancel", command=lambda: root.destroy())
    cancel_btn.place(x=110, y=40)

    root.mainloop()

timer = pygame.time.Clock()
running = True
while running:
    timer.tick(60)

    win.fill(WHITE)
    draw_padding(win)
    board.draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_rect.collidepoint(event.pos):
                start_new_thread(restart_box, ())

            elif undo_rect.collidepoint(event.pos):
                start_new_thread(undo, ())

            elif redo_rect.collidepoint(event.pos):
                start_new_thread(redo, ())

        if event.type == pygame.KEYDOWN:
            if PLAYING: # if statement so that spam clicking doesn't crash the game
                last_board = get_smth("gamelog.txt", CURRENT)

                if event.key == pygame.K_UP:
                    board.make_move("up", board.board)
                elif event.key == pygame.K_DOWN:
                    board.make_move("down", board.board)
                elif event.key == pygame.K_LEFT:
                    board.make_move("left", board.board)
                elif event.key == pygame.K_RIGHT:
                    board.make_move("right", board.board)

                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if last_board != board.board: # There is a move
                        PLAYING = False
                        start_new_thread(board.spawn_number, ())

    pygame.display.flip()