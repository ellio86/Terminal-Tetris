import time, random
import curses
from dataclasses import dataclass

class Game_board:
    def __init__(self, width: int=10, height: int=20) -> None:
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.board.append([2 for _ in range(self.width)])
        
    def get(self) -> str:
        string = ""
        for line in self.board:
            string += str(line) + "\n"
        return string
    
    def add_block(self, x, y, z) -> None:
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
    def __init__(self, blocks: tuple, position: list = [0, 5], speed: int=1) -> None:
        self.blocks = blocks
        self.blocks_pos = [0,0,0,0]
        self.position = position
        self.height = max([block[0] for block in self.blocks]) + 1
        self.speed = speed
        self.update_block_pos()

    def update_block_pos(self) -> None:
        for x, block in enumerate(self.blocks):
            positions = [block[0] + self.position[0], block[1] + self.position[1]]
            self.blocks_pos[x] = positions
    
def draw_to_board(board: Game_board, *pieces: Piece) -> None:
    """Takes in a list of pieces and displays them on the board."""
    for piece in pieces:
        for block in piece.blocks:
            x = piece.position[0] + block[0]
            y = piece.position[1] + block[1]
            board.add_block(x, y, block[2])  

def can_move(board: Game_board, piece: Piece) -> dict:
    """Checks whether a piece can move left, right or down."""
    d = {"left": True, "right": True, "down": True}
    for x, block in enumerate(piece.blocks_pos):
        d["left"] = False if block[1] - 1 == -1 or not d["left"] else True
        d["right"] = False if block[1] + 1 == board.width or not d["right"] else True
        d["down"] = False if board.board[block[0] + 1][block[1]] == 2 or not d["down"] else True
    return d

               
def play_game():
    def _play_game(stdscr):
        stdscr.clear()
        board = Game_board()
        playing = True
        moved = False
        pieces = [
                  ((0, 1, 1), (1, 0, 1), (1, 1, 1), (2, 1, 1)),
                  ((0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)),
                  ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 2, 1))
                 ]
        active_piece = Piece(blocks=random.choice(pieces))
        
        while playing:
            # 
            moves = can_move(board, active_piece)
            if not moves["down"]:
                for block in active_piece.blocks_pos:
                    board.add_block(block[0], block[1], 2)
                active_piece.position = [0, 5]
                active_piece.blocks = random.choice(pieces)

            # Move ONCE every second
            if str(time.time())[11] == "0":
                if moves["down"] and not moved:
                    moved = True
                    active_piece.position[0] += active_piece.speed
            else:
                moved = False
                
            # Re-Draw the piece to the board
            active_piece.update_block_pos()
            draw_to_board(board, active_piece)

            # Display the board from the board matrix
            for x, line in enumerate(board.board[:-1]):
                for y, pixel in enumerate(line):
                    match pixel:
                        case 1 | 2:
                            stdscr.addstr(x, y, chr(9633))
                        case 0:
                            stdscr.addstr(x, y, chr(9632))

            # DEBUG AREA
            stdscr.addstr(22, 0, f"Timer: {str(time.time())[11]}") # Show timer
            stdscr.addstr(23, 0, f"{active_piece.blocks_pos[3]}") # Show individual block position
            stdscr.addstr(24, 0, f"{moves['down']}") 


            board.clear()
            stdscr.refresh()
            stdscr.timeout(1)
            
            # Handle user input
            code = stdscr.getch()
            if code != -1:
                match chr(code).lower():
                    case "a":
                        if moves["left"]:
                            active_piece.position[1] -= 1
                    case "d":
                        if moves["right"]:
                            active_piece.position[1] += 1
                    case "s":
                        if moves["down"]:
                            active_piece.position[0] += 1
                    case "e":
                        pass
                    case "q":
                        pass
                
                stdscr.refresh()
                    

    return curses.wrapper(_play_game)

print(play_game())