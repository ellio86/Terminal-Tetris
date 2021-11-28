import time
import curses
from dataclasses import dataclass

class Game_board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(self.width - 1)] for _ in range(self.height - 1)]
        
    def get(self) -> str:
        string = ""
        for line in self.board:
            string += str(line) + "\n"
        return string

class Piece:
    def __init__(self, shape: tuple) -> None:
        self.is_new = True
        self.shape = shape
        self.starting = True
        self.next_line_to_display = len(shape) - 1
         
def update_board(board, current_piece, player_x) -> list:
    old_board = new_board = board
    if current_piece.starting:
        player_x = 5
        current_piece.starting = False
        
    for i, board_line in enumerate(old_board[::-1]):
        new_line = board_line
        if i == len(old_board) - 1 and current_piece.is_new:
            for n, pixel in enumerate(current_piece.shape[current_piece.next_line_to_display], start=player_x):
                if not new_line[n] and pixel:
                    new_line[n] = pixel
                else:
                    return None
        
            current_piece.next_line_to_display -= 1
            if current_piece.next_line_to_display == - 1:
                current_piece.is_new = False

        for j, pixel in enumerate(board_line):
            if pixel == 1:
                if i < 0:
                    below_line = old_board[i-1]
                if below_line:
                    if not below_line[j]:
                        new_line[j] = 1
                        
        new_board.append(new_line)
    return new_board[::-1], player_x

                    
def play_game():
    def _play_game(stdscr):
        stdscr.clear()
        board = Game_board(11, 21)
        playing = True
        player_x = 5
        while playing:
            for x, line in enumerate(board.board):
                stdscr.addstr(x, 0, str(line))
                stdscr.refresh()
            
            #code = stdscr.getch()
            #stdscr.refresh()
            #stdscr.timeout(100)
            board.board, player_x = update_board(board.board, pieces[0], player_x)
            #match chr(code).lower():
                #case ch:
                  #  board.board[0][0] = ch
                  #  continue
                    

    return curses.wrapper(_play_game)

pieces = [Piece(([0, 0, 0, 0],
                 [0, 1, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0]))]
print(play_game())