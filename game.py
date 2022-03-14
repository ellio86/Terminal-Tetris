import time
import random
import curses

CURSES_COLORS = [
    curses.COLOR_WHITE,
    curses.COLOR_BLACK,
    curses.COLOR_MAGENTA,
    curses.COLOR_CYAN,
    curses.COLOR_YELLOW,
    curses.COLOR_BLUE,
    curses.COLOR_RED,
    curses.COLOR_GREEN,
    curses.COLOR_WHITE,
]


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

    def add_block(self, x, y, z) -> None:
        """add z to the board at coord x,y."""
        if not self.board[x][y] == 3:
            self.board[x][y] = z

    def check_block(self, x, y) -> int:
        """Return block at x, y."""
        try:
            return self.board[x][y]
        except IndexError:
            return 3

    def check_line(self, line_index):
        """Check to see if a specific line is full."""
        for pixel in self.board[line_index]:
            if pixel == 3:
                pass
            elif pixel < 2:
                return False
        return True

    def check_lines(self):
        """Checks whole board to see if a line is full."""
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
        self.blocks_pos = []
        self.get_block_pos()
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
        self.blocks_pos = blocks_pos

    def update_block_extremities(self) -> None:
        """Finds which block is closest to the left/right/bottom of the board."""
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
            if block[1] >= rightmost_val and n not in rightmost_block:
                rightmost_block.append(n)
            if block[1] <= leftmost_val and n not in leftmost_block:
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
        """Rotate the piece by 90 degrees."""
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


def read_score(file) -> int:
    """Read score from file."""
    try:
        with open(file, "r") as f:
            try:
                return int(f.readlines()[0])
            except IndexError:
                return 0
    except FileNotFoundError:
        return 0


def save_score(file, score) -> None:
    """Save highscore to file."""
    try:
        with open(file, "x") as f:
            f.write(str(score))
    except FileExistsError:
        with open(file, "w") as f:
            f.write(str(score))


def mixed_bag_randomizer(array: list[object], prev_picks: list[object]):
    """Picks item from provided list ensuring a new item is picked."""
    available_items = []
    if len(prev_picks) == len(array):
        prev_picks.pop(0)

    for n in range(len(array)):
        if n not in prev_picks:
            available_items.append(n)
    if available_items:
        item_index = random.choice(available_items)
        prev_picks.append(item_index)
        return array[item_index], prev_picks

    available_items = range(len(array))

    # Can't have three of the same item in a row
    if arr[-1] == arr[-2]:
        available_items.remove(arr[-1])

    item_index = random.choice(available_items)
    prev_picks.append(item_index)
    return array[item_index], prev_picks


def play_game():
    def _play_game(stdscr):
        stdscr.clear()
        stdscr.nodelay(True)
        curses.start_color()
        if not curses.has_colors():
            raise Exception

        f = False
        for n, color in enumerate(CURSES_COLORS, 0):
            if n == 2:
                f = True
            elif f:
                curses.init_pair(n + 1, CURSES_COLORS[0], CURSES_COLORS[n - 1])
            else:
                curses.init_pair(n + 1, CURSES_COLORS[0], CURSES_COLORS[n])

        # Game over screen
        game_over = """
        ################################
        #                              #
        #          Game over !         #
        #                              #
        ################################
        """

        ######### SETTINGS #########
        debugging = False
        view_size = "medium"
        highscore_f = "highscore.txt"
        level = 0

        # Location of the scores/debug info
        score_px = 26
        score_py = 0
        debug_px = 26
        debug_py = 8

        ###### GAME VARIABLES ######
        # check = False
        prev_time = "0"
        speed = 9
        next_move = 0
        total_lines = 0
        score = 0
        board = Game_board()
        playing = True
        moved = False
        highscore = 0
        falltime = "0"
        piece_list = []
        ############################

        # Read Highscores from file (0 if file not found)
        highscore = read_score(highscore_f)

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

        # Create first piece
        blocks, piece_list = mixed_bag_randomizer(pieces, piece_list)
        active_piece = Piece(blocks=blocks)

        # Main Loop
        while playing:
            moves = can_move(board, active_piece)
            speed = 9 - level if level < 7 else 2
            debug_messages = [
                f"Timer: {str(time.time())}",
                f"Pos: {active_piece.blocks_pos[3]}",
                f"leftmost: {active_piece.blocks_pos[active_piece.leftmost[0]]}",
                f"rightmost: {active_piece.blocks_pos[active_piece.rightmost[0]]}",
                f"downwardmost: {next_move}",
                f"d['left']: {moves['left']}",
                f"d['right']: {moves['right']}",
                f"d['down']: {moves['down']}",
                f"falltime: {falltime}",
                f"piece_list: {piece_list}",
                f"{active_piece.leftmost=}",
            ]

            # Handle user input
            code = stdscr.getch()
            active_piece.update_block_extremities()

            c = chr(code).lower() if code != -1 else ""
            if c == "a":
                if (
                    moves["left"]
                    and active_piece.blocks_pos[active_piece.leftmost[0]][1] - 1 != 0
                    and not str(time.time())[12] == prev_time
                ):
                    active_piece.position[1] -= 1
                    prev_time = str(time.time())[12]
            elif c == "d":
                if (
                    moves["right"]
                    and active_piece.blocks_pos[active_piece.rightmost[0]][1] + 1 != 11
                    and not str(time.time())[12] == prev_time
                ):
                    active_piece.position[1] += 1
                    if active_piece.position[1] == 11:
                        active_piece.position[1] -= 1
                    prev_time = str(time.time())[12]
            elif c == "s":
                if (
                    moves["down"]
                    and active_piece.blocks_pos[active_piece.downwardmost[0]][0] + 1
                    != 20
                    # and not str(time.time())[12] == prev_time
                ):
                    active_piece.position[0] += 1
                    prev_time = str(time.time())[12]
            elif c == "e":
                rotate(board, active_piece, "L")
            elif c == "q":
                rotate(board, active_piece, "R")

            # Game over condition
            if not moves["down"] and active_piece.position[0] == 0:
                playing = False

            # Piece falling naturally
            if str(time.time())[11] == str(next_move):
                if moves["down"] and not moved:
                    moved = True
                    active_piece.position[0] += active_piece.speed
                    next_move = str(int(str(time.time())[11]) + speed)[-1]
            else:
                moved = False

            # If the block lands, create a new one
            if not moves["down"] and str(time.time())[11] == falltime and c != "s":
                for block in active_piece.blocks_pos:
                    board.add_block(block[0], block[1], block[2] + 10)
                active_piece.position = [0, 5]
                active_piece.blocks, piece_list = mixed_bag_randomizer(
                    pieces, piece_list
                )

            elif not moves["down"] and c == "s":
                for block in active_piece.blocks_pos:
                    board.add_block(block[0], block[1], block[2] + 10)
                active_piece.position = [0, 5]
                active_piece.blocks, piece_list = mixed_bag_randomizer(
                    pieces, piece_list
                )
                falltime = str(time.time())[11]

            # Clear full lines and add to score
            cleared_line_num = board.check_lines()
            if cleared_line_num == 1:
                score += 40 * (level + 1)
            elif cleared_line_num == 2:
                score += 100 * (level + 1)
            elif cleared_line_num == 3:
                score += 300 * (level + 1)
            elif cleared_line_num == 4:
                score += 1200 * (level + 1)

            total_lines += cleared_line_num

            # Re-Draw the piece to the board
            active_piece.get_block_pos()
            draw_to_board(board, active_piece)

            # Update and save the highscore
            highscore = score if score > highscore else highscore
            save_score(highscore_f, highscore) if highscore_f else None

            # Go to the next level every time 10 lines are cleared
            if str(total_lines)[-1] < str(total_lines - cleared_line_num)[-1]:
                level += 1

            # Set up display
            if view_size == "medium":
                display_board = [
                    [p for p in board.board[n] for _ in (0, 1)]
                    for n, line in enumerate(board.board[:-1])
                    for _ in (0, 1)
                ]
            else:
                score_px = 0
                score_py = 22
                debug_px = 0
                debug_py = 28
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
            stdscr.addstr(score_py, score_px, f"Score: {score}")
            stdscr.addstr(score_py + 2, score_px, f"Highscore: {highscore}")
            stdscr.addstr(score_py + 4, score_px, f"Level: {level}")

            # Show debug messages
            if debugging:
                for n, message in enumerate(debug_messages):
                    stdscr.addstr(debug_py + n, debug_px, message)
            board.clear()
            stdscr.refresh()

        stdscr.addstr(5, 10, game_over)
        stdscr.refresh()
        time.sleep(5)
        quit()

    return curses.wrapper(_play_game)


if __name__ == "__main__":
    print(play_game())
