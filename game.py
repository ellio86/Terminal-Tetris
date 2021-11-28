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
    
    def add_block(self, x, y, z):
        self.board[x][y] = z
        
    def check_block(self, x, y) -> int:
        return self.board(x, y)
    
class Piece:
    def __init__(self, position: list = [0, 5], blocks: list = None):
        self.position = position
        self.blocks = blocks if blocks else [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (2, 1, 1), (0, 2, 0)]
        self.height = max([block[0] for block in self.blocks]) + 1
    
def draw_to_board(board: Game_board, *pieces: list[Piece]) -> None:
    """Takes in a list of pieces and displays them on the board."""
    for piece in pieces:
        for block in piece.blocks:
            x = piece.position[0] + block[0]
            y = piece.position[1] + block[1]
            board.add_block(x, y, block[2])  
               
def play_game():
    def _play_game(stdscr):
        stdscr.clear()
        board = Game_board(11, 21)
        playing = True
        active_piece = Piece(position=[-1, 5])
        piece_speed = 1
        while playing:
            time.sleep(0.5)
            if active_piece.position[0] + 1 == board.height - active_piece.height:
                piece_speed = 0 
            
            active_piece.position[0] += piece_speed
            board.board[active_piece.position[0] - 1] = [n if n != 1 else 0 for n in board.board[active_piece.position[0] - 1]]
            draw_to_board(board, active_piece)
            
            # Display the board
            for x, line in enumerate(board.board):
                for y, pixel in enumerate(line):
                    match pixel:
                        case 1 | 2:
                            stdscr.addstr(x, y, chr(9633))
                        case 0:
                            stdscr.addstr(x, y, chr(9632))
                        
            stdscr.refresh()
            stdscr.timeout(100)
            
            code = stdscr.getch()
            if code != -1:
                match chr(code).lower():
                    case "a":
                        active_piece.position[1] -= 1
                    case "d":
                        active_piece.position[1] += 1
                        
                stdscr.refresh()
                    

    return curses.wrapper(_play_game)

pieces = [Piece(([0, 1, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 0]))]
print(play_game())