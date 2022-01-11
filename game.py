import time, random
import curses
from dataclasses import dataclass


class Game_board:
    def __init__(self, width: int = 10, height: int = 20) -> None:
        self.width = width
        self.height = height
        self.b = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.board = []
        for line in self.b:
            line.insert(0, 3)
            line.append(3)
            self.board.append(line)

        self.board.append([3 for _ in range(self.width)])

    def get(self) -> str:
        string = ""
        for line in self.board:
            string += str(line) + "\n"
        return string

    def add_block(self, x, y, z) -> None:
        if not self.board[x][y] == 3:
            self.board[x][y] = z

    def check_block(self, x, y) -> int:
        try:
            return self.board[x][y]
        except IndexError:
            return 3

    def check_line(self, line_index):
        for pixel in self.board[line_index]:
            if pixel == 3:
                pass
            elif pixel < 2:
                return False
        return True

    def check_lines(self):
        line_count = 0
        for x, line in enumerate(self.board[:-1]):
            if self.check_line(x):
                self.board.pop(x)
                self.board.insert(0, [0 for _ in range(self.width)])
                self.board[0].insert(0, 3)
                self.board[0].append(3)
                line_count += 1

        return line_count

    def clear(self) -> None:
        """Removes any active blocks from the board."""
        clear_board = []
        for line in self.board:
            newline = []
            for space in line:
                newline.append(0) if 11 > space >= 4 or space == 2 else newline.append(
                    space
                )

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
        self.leftmost = None
        self.rightmost = None
        self.downwardmost = None
        self.update_block_extremities()

    def get_block_pos(self, blocks: list[tuple] = None) -> None:
        """Returns a list of tuples containing the blocks exact co-ordinates."""
        blocks = blocks if blocks else self.blocks
        blocks_pos = [0 for _ in blocks]
        for x, block in enumerate(self.blocks):
            positions = [
                block[0] + self.position[0],
                block[1] + self.position[1],
                block[2],
            ]
            blocks_pos[x] = positions
        return blocks_pos

    def update_block_extremities(self) -> None:
        leftmost_val = self.blocks[0][1]
        leftmost_block = [0]
        rightmost_val = self.blocks[0][1]
        rightmost_block = [0]
        downwardmost_val = self.blocks[0][0]
        downwardmost_block = [0]
        for n, block in enumerate(self.blocks):
            if block[1] >= rightmost_val:
                rightmost_block[0] = n
            if block[1] <= leftmost_val:
                leftmost_block[0] = n
            if block[0] >= downwardmost_val:
                downwardmost_block[0] = n

        for n, block in enumerate(self.blocks):
            if block[1] == rightmost_val and n not in rightmost_block:
                rightmost_block.append(n)
            if block[1] == leftmost_val and n not in leftmost_block:
                leftmost_block.append(n)
            if (
                block[0] == downwardmost_val
                or (block[0] + 1, block[1]) not in [(b[0], b[1]) for b in self.blocks]
                and n not in downwardmost_block
            ):
                downwardmost_block.append(n)

        self.leftmost = leftmost_block
        self.rightmost = rightmost_block
        self.downwardmost = downwardmost_block

    def calc_rotate(self, dir: str = None) -> list[tuple]:
        """Rotate the piece by 90 degrees"""
        if self.blocks_pos[0][2] == 2:
            return self.blocks
        new_blocks = []
        for block in self.blocks:
            new_block = (
                (-block[1], block[0], block[2])
                if dir == "L"
                else (block[1], -block[0], block[2])
            )
            new_blocks.append(new_block)
        return new_blocks


def rotate(board: Game_board, piece: Piece, dir: str = None) -> None:
    """Roates piece on board if there is space."""
    can_rotate = True
    rotated = piece.calc_rotate(dir)
    for block in rotated:
        if (
            board.check_block(
                piece.position[0] + block[0], piece.position[1] + block[1]
            )
            >= 2
        ):
            can_rotate = False
    if can_rotate:
        piece.blocks = rotated
        piece.update_block_extremities()


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
    try:
        for block in piece.leftmost:
            left = piece.blocks_pos[block]
            d["left"] = (
                False
                if left[1] - 1 == 0
                or board.board[left[0]][left[1] - 1] >= 2
                or not d["left"]
                else True
            )
    except IndexError:
        d["left"] = False

    try:
        for block in piece.rightmost:
            right = piece.blocks_pos[block]
            d["right"] = (
                False
                if right[1] + 1 == 11
                or board.board[right[0]][right[1] + 1] >= 2
                or not d["right"]
                else True
            )
    except IndexError:
        d["right"] = False

    try:
        for block in piece.downwardmost:
            bottom = piece.blocks_pos[block]
            d["down"] = (
                False
                if bottom[0] + 1 == 20
                or board.board[bottom[0] + 1][bottom[1]] >= 2
                or not d["down"]
                else True
            )
    except IndexError:
        d["down"] = False

    return d


def play_game():
    def _play_game(stdscr):
        curses.start_color()
        if not curses.has_colors():
            raise Exception
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_GREEN)
        LEVEL = 0
        DEBUGGING = True
        stdscr.clear()
        score = 0
        board = Game_board()
        playing = True
        moved = False
        view_size = "medium"
        prev_time = "0"
        t = "0"
        check = False

        # Each piece is represented by 4 blocks, with positions
        # relative to the center of a 9x9 square  (apart from
        # the long bar and square) (x, -y, color)
        pieces = [
            [(-1, 0, 4), (0, -1, 4), (0, 0, 4), (0, 1, 4)],  # T Block
            [(0, 0, 8), (0, 1, 8), (1, 0, 8), (-1, 1, 8)],  # Z Block
            [(0, -1, 7), (0, 0, 7), (0, 1, 7), (-1, 1, 7)],  # L block
            [(0, 1, 6), (0, 0, 6), (0, -1, 6), (-1, -1, 6)],  # J block
            [(1, 0, 9), (0, 0, 9), (0, -1, 9), (-1, -1, 9)],  # S block
            [(0, -1, 5), (0, -2, 5), (0, 0, 5), (0, 1, 5)],  # | Block
            [(0, 0, 2), (-1, 0, 2), (0, -1, 2), (-1, -1, 2)],  # Square Block
        ]

        active_piece = Piece(blocks=random.choice(pieces))
        while playing:
            moves = can_move(board, active_piece)

            # If the block lands, create a new one
            if not moves["down"] and str(time.time())[11] == t:
                for block in active_piece.blocks_pos:
                    board.add_block(block[0], block[1], block[2] + 10)
                active_piece.position = [0, 5]
                active_piece.blocks = random.choice(pieces)

            # Move ONCE every second
            if str(time.time())[11] == "0":
                if moves["down"] and not moved:
                    moved = True
                    active_piece.position[0] += active_piece.speed
                    t = "0"

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
                        pixel = pixel - 10 if pixel > 9 else pixel
                        pixel += 1 if pixel <= 1 else 0
                        if pixel == 0:
                            stdscr.addstr(x, y, "_", curses.color_pair(0))
                        elif pixel != 3:
                            stdscr.addstr(x, y, chr(9633), curses.color_pair(pixel))
                    except curses.error:
                        pass

            # Show score
            stdscr.addstr(debug_py, debug_px, f"Score: {score}")

            # DEBUG AREA
            if DEBUGGING:
                # Show timer
                stdscr.addstr(debug_py + 1, debug_px, f"Timer: {str(time.time())}")
                # Show individual block position
                stdscr.addstr(
                    debug_py + 2, debug_px, f"Pos: {active_piece.blocks_pos[3]}"
                )
                # Extra debug space
                stdscr.addstr(
                    debug_py + 3,
                    debug_px,
                    f"leftmost: {active_piece.blocks_pos[active_piece.leftmost[0]]}",
                )
                stdscr.addstr(
                    debug_py + 4,
                    debug_px,
                    f"rightmost: {active_piece.blocks_pos[active_piece.rightmost[0]]}",
                )
                stdscr.addstr(
                    debug_py + 5,
                    debug_px,
                    f"downwardmost: {active_piece.blocks_pos[active_piece.downwardmost[0]]}",
                )
                stdscr.addstr(debug_py + 6, debug_px, f'd["left"]: {moves["left"]}')
                stdscr.addstr(debug_py + 7, debug_px, f'd["right"]: {moves["right"]}')
                stdscr.addstr(debug_py + 8, debug_px, f'd["down"]: {moves["down"]}')

            board.clear()
            stdscr.refresh()
            stdscr.timeout(1)
            match board.check_lines():
                case 1:
                    score += 40 * (LEVEL + 1)
                case 2:
                    score += 100 * (LEVEL + 1)
                case 3:
                    score += 300 * (LEVEL + 1)
                case 4:
                    score += 1200 * (LEVEL + 1)

            score += board.check_lines() * 1000

            # Handle user input
            code = stdscr.getch()
            active_piece.update_block_extremities()
            if code != -1:
                if not str(time.time())[12] == prev_time:
                    match chr(code).lower():
                        case "a":
                            if (
                                moves["left"]
                                and active_piece.blocks_pos[active_piece.leftmost[0]][1]
                                - 1
                                != 0
                            ):
                                active_piece.position[1] -= 1
                                prev_time = str(time.time())[12]
                                check = True
                        case "d":
                            if (
                                moves["right"]
                                and active_piece.blocks_pos[active_piece.rightmost[0]][
                                    1
                                ]
                                + 1
                                != 11
                            ):
                                active_piece.position[1] += 1
                                if active_piece.position[1] == 11:
                                    active_piece.position[1] -= 1
                                prev_time = str(time.time())[12]
                        case "s":
                            if (
                                moves["down"]
                                and active_piece.blocks_pos[
                                    active_piece.downwardmost[0]
                                ][0]
                                + 1
                                != 20
                            ):
                                active_piece.position[0] += 1
                                prev_time = str(time.time())[12]
                                t = str(time.time())[11]
                        case "e":
                            rotate(board, active_piece, "L")
                        case "q":
                            rotate(board, active_piece, "R")

                stdscr.refresh()

    return curses.wrapper(_play_game)


if __name__ == "__main__":
    print(play_game())
