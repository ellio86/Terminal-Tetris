import time, random
import curses
from dataclasses import dataclass


class Game_board:
    def __init__(self, width: int = 10, height: int = 20) -> None:
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.board.append([3 for _ in range(self.width)])

    def get(self) -> str:
        string = ""
        for line in self.board:
            string += str(line) + "\n"
        return string

    def add_block(self, x, y, z) -> None:
        self.board[x][y] = z

    def check_block(self, x, y) -> int:
        return self.board[x][y]

    def check_line(self, line_index):
        for pixel in self.board[line_index]:
            if pixel != 2:
                return False
        return True

    def check_lines(self):
        line_count = 0
        for x, line in enumerate(self.board):
            if self.check_line(x):
                self.board.pop(x)
                self.board.insert(0, [0 for _ in range(self.width)])
                line_count += 1

        return line_count

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
    def __init__(
        self, blocks: list[tuple], position: list = [0, 5], speed: int = 1
    ) -> None:
        self.blocks = blocks
        self.position = position
        self.height = max([block[0] for block in self.blocks]) + 1
        self.speed = speed
        self.blocks_pos = self.get_block_pos()

    def get_block_pos(self, blocks: list[tuple] = None) -> None:
        """Returns a list of tuples containing the blocks exact co-ordinates."""
        blocks = blocks if blocks else self.blocks
        blocks_pos = [0 for _ in blocks]
        for x, block in enumerate(self.blocks):
            positions = [block[0] + self.position[0], block[1] + self.position[1]]
            blocks_pos[x] = positions
        return blocks_pos

    def calc_rotate(self, dir: str = None) -> list[tuple]:
        """Rotate the piece by 90 degrees"""
        new_blocks = []
        for block in self.blocks:
            new_block = (
                (-block[1], block[0], 1) if dir == "L" else (block[1], -block[0], 1)
            )
            new_blocks.append(new_block)
        return new_blocks


def rotate(board: Game_board, piece: Piece, dir: str = None) -> None:
    """Roates piece on board if there is space."""
    can_rotate = True
    rotated = piece.calc_rotate(dir)
    for block in rotated:
        print(board.check_block(block[0], block[1]))
        if board.check_block(block[0], block[1]) >= 2:
            can_rotate = True  # <------- Should be FALSE but for some reason it stops roations from working
    if can_rotate:
        piece.blocks = rotated


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
    for block in piece.blocks_pos:
        try:
            d["left"] = False if block[1] - 1 == -1 or not d["left"] else True
            d["right"] = (
                False if block[1] + 1 == board.width or not d["right"] else True
            )
            d["down"] = (
                False
                if board.board[block[0] + 1][block[1]] in (2, 3) or not d["down"]
                else True
            )
        except IndexError:
            return {"left": False, "right": False, "down": False}
    return d


def play_game():
    def _play_game(stdscr):
        DEBUGGING = True
        stdscr.clear()
        score = 0
        board = Game_board()
        playing = True
        moved = False
        view_size = "medium"

        # Each piece is represented by 4 blocks, with positions
        # relative to the center of a 9x9 square  (apart from
        # the long bar and square) (x, y, color)
        pieces = [
            [(-1, 0, 1), (0, -1, 1), (0, 0, 1), (0, 1, 1)],  # T Block
            [(0, 0, 1), (0, 1, 1), (1, 0, 1), (-1, 1, 1)],  # Z Block
            [(0, -1, 1), (0, 0, 1), (0, 1, 1), (1, 1, 1)],  # L block
            [(0, 1, 1), (0, 0, 1), (0, -1, 1), (-1, -1, 1)],  # r block
            [(1, 0, 1), (0, 0, 1), (0, -1, 1), (-1, -1, 1)],  # S block
        ]

        active_piece = Piece(blocks=random.choice(pieces))
        while playing:
            moves = can_move(board, active_piece)

            # If the block lands, create a new one
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
            active_piece.blocks_pos = active_piece.get_block_pos()
            draw_to_board(board, active_piece)

            # Location of the debug info
            debug_py = 22
            debug_px = 0

            # Set up display
            match view_size:
                case "medium":
                    debug_py = 0
                    debug_px = 26
                    display_board = [
                        [p for p in board.board[n] for _ in (0, 1)]
                        for n, line in enumerate(board.board[:-1])
                        for _ in (0, 1)
                    ]
                case "small" | _:
                    display_board = board.board[:-1]

            # Display the board from the board matrix
            for x, line in enumerate(display_board):
                for y, pixel in enumerate(line):
                    try:
                        match pixel:
                            # Falling block
                            case 1:
                                stdscr.addstr(x, y, chr(9633))

                            # Still block
                            case 2:
                                stdscr.addstr(x, y, chr(9633))

                            # Empty Space
                            case 0:
                                stdscr.addstr(x, y, chr(9632))
                    except curses.error:
                        pass

            # DEBUG AREA
            if DEBUGGING:
                stdscr.addstr(
                    debug_py, debug_px, f"Timer: {str(time.time())}"
                )  # Show timer
                stdscr.addstr(
                    debug_py + 1, debug_px, f"{active_piece.blocks_pos[3]}"
                )  # Show individual block position
                stdscr.addstr(debug_py + 2, debug_px, f"{moves['down']}")
                stdscr.addstr(debug_py + 3, debug_px, f"Score: {score}")  # Show score

            board.clear()
            stdscr.refresh()
            stdscr.timeout(1)

            score += board.check_lines() * 1000

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
                        rotate(board, active_piece, "L")
                    case "q":
                        rotate(board, active_piece, "R")

                stdscr.refresh()

        print(f"Score: {score}")

    return curses.wrapper(_play_game)


print(play_game())
