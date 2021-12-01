import time, random
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
    
    def clear(self) -> None:
        """Removes any active blocks from the board."""
        clear_board = []
        for line in self.board:
            newline = []
            for space in line:
                newline.append(0) if space == 1 else newline.append(space)
                
            clear_board.append(newline)
        self.board = clear_board
    
class Piece:
    def __init__(self, blocks: tuple, position: list = [0, 5], speed=1):
        self.blocks = blocks
        self.position = position
        self.height = max([block[0] for block in self.blocks]) + 1
        self.speed = speed
    
def draw_to_board(board: Game_board, *pieces: Piece) -> None:
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
        moved = False
        pieces = [
                  ((0, 1, 1), (1, 0, 1), (1, 1, 1), (2, 1, 1)),
                  ((0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)),
                  ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 2, 1))
                 ]
        active_piece = Piece(blocks=random.choice(pieces))
        
        while playing:
            # Create new piece if current piece is at the bottom of the board
            if active_piece.position[0] + 1 == board.height - active_piece.height:
                active_piece = Piece(blocks=random.choice(pieces))
            
            # Move every second
            if str(time.time())[11] == "0":
                if not moved:
                    moved = True
                    active_piece.position[0] += active_piece.speed
                    
            else:
                moved = False
                
            draw_to_board(board, active_piece)
            
            # Display the board
            for x, line in enumerate(board.board):
                for y, pixel in enumerate(line):
                    match pixel:
                        case 1 | 2:
                            stdscr.addstr(x, y, chr(9633))
                        case 0:
                            stdscr.addstr(x, y, chr(9632))
            stdscr.addstr(0, 22, str(time.time())[11])
            board.clear()
            stdscr.refresh()
            stdscr.timeout(10)
            
            code = stdscr.getch()
            if code != -1:
                match chr(code).lower():
                    case "a":
                        active_piece.position[1] -= 1
                    case "d":
                        active_piece.position[1] += 1
                    case "s":
                        active_piece.position[0] += 1
                
                stdscr.refresh()
                    

    return curses.wrapper(_play_game)

print(play_game())