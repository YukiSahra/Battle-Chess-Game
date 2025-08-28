

from typing import List, Optional, Tuple

FILES = "abcdefgh"
RANKS = "12345678"

Piece = str 

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8

def algebraic_to_rc(move_sq: str) -> Tuple[int, int]:
    """Convert 'e2' -> (row, col) with row 0 at top (rank 8)."""
    file = FILES.index(move_sq[0])
    rank = RANKS.index(move_sq[1]) 
    row = 7 - rank                 
    col = file
    return row, col

def rc_to_algebraic(r: int, c: int) -> str:
    return f"{FILES[c]}{RANKS[7-r]}"

def starting_position() -> List[List[Optional[Piece]]]:
    board = [[None for _ in range(8)] for _ in range(8)]
    back = ["R","N","B","Q","K","B","N","R"]

   
    for c,k in enumerate(back):
        board[0][c] = "b"+k
    for c in range(8):
        board[1][c] = "bP"

  
    for c,k in enumerate(back):
        board[7][c] = "w"+k
    for c in range(8):
        board[6][c] = "wP"

    return board

def print_board_ascii(board: List[List[Optional[Piece]]]) -> str:
    """Return an ASCII board for displaying in terminal."""
    rows = []
    for r in range(8):
        line = [str(8-r)]
        for c in range(8):
            p = board[r][c]
            if p is None:
                line.append(".")
            else:
                color, kind = p[0], p[1]
                ch = kind
                ch = ch.upper() if color == "w" else ch.lower()
                line.append(ch)
        rows.append(" ".join(line))
    rows.append("  a b c d e f g h")
    return "\n".join(rows)

def path_clear(board, r0, c0, r1, c1) -> bool:
    """Check sliding path (rook/bishop/queen)."""
    dr = (r1 - r0)
    dc = (c1 - c0)
    step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
    step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
    r, c = r0 + step_r, c0 + step_c
    while (r, c) != (r1, c1):
        if board[r][c] is not None:
            return False
        r += step_r
        c += step_c
    return True

def piece_legal(board, turn: str, r0, c0, r1, c1) -> bool:
    """Basic per-piece movement legality (no self-check detection)."""
    p = board[r0][c0]
    if not p or p[0] != turn:
        return False
    target = board[r1][c1]
    if target and target[0] == turn:
        return False

    color, kind = p[0], p[1]
    dr, dc = r1 - r0, c1 - c0

    if kind == "P":
        dir_ = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1


        if dc == 0:
            if dr == dir_ and target is None:
                return True
            if r0 == start_row and dr == 2*dir_ and target is None and board[r0+dir_][c0] is None:
                return True
            return False


        if abs(dc) == 1 and dr == dir_ and target is not None and target[0] != color:
            return True

        return False

    if kind == "N":
        return (abs(dr), abs(dc)) in [(2,1),(1,2)]

    if kind == "B":
        if abs(dr) == abs(dc) and path_clear(board, r0, c0, r1, c1):
            return True
        return False

    if kind == "R":
        if (dr == 0 or dc == 0) and path_clear(board, r0, c0, r1, c1):
            return True
        return False

    if kind == "Q":
        if ((dr == 0 or dc == 0) or (abs(dr) == abs(dc))) and path_clear(board, r0, c0, r1, c1):
            return True
        return False

    if kind == "K":
        return max(abs(dr), abs(dc)) == 1 

    return False

def apply_move(board, move: str, turn: str) -> Tuple[bool, str]:
    """
    move: 'e2e4'
    return: (ok, message)
    """
    if len(move) != 4:
        return False, "Sai định dạng (ví dụ: e2e4)."

    try:
        r0, c0 = algebraic_to_rc(move[:2])
        r1, c1 = algebraic_to_rc(move[2:])
    except Exception:
        return False, "Ô cờ không hợp lệ."

    if not in_bounds(r0,c0) or not in_bounds(r1,c1):
        return False, "Tọa độ ngoài bàn cờ."

    if not piece_legal(board, turn, r0, c0, r1, c1):
        return False, "Nước đi không hợp lệ theo luật cơ bản."

    piece = board[r0][c0]
    board[r0][c0] = None
    board[r1][c1] = piece

    if piece and piece[1] == "P" and (r1 == 0 or r1 == 7):
        board[r1][c1] = piece[0] + "Q"

    next_turn = "b" if turn == "w" else "w"
    return True, next_turn
