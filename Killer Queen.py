import tkinter as tk
from chessboard_gui import ChessBoardGUI


def global_sweep_elimination(n):
    """Return positions of queens that survive the global sweep elimination."""
    board = [[1] * n for _ in range(n)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for r in range(n):
        for c in range(n):
            if board[r][c] != 1:
                continue
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while 0 <= nr < n and 0 <= nc < n:
                    board[nr][nc] = 0
                    nr += dr
                    nc += dc
    return [(r, c) for r in range(n) for c in range(n) if board[r][c] == 1]


def solve_all_nqueens_bitmask(N, limit=None):
    """Enumerate all N-Queens solutions using a compact bitmask DFS.

    Returns a list of solutions; each solution is a list of (row, col) pairs.
    Set `limit` to stop early (None => unlimited).
    """
    mask = (1 << N) - 1
    results = []
    pos = [0] * N

    def dfs(row, cols, ld, rd):
        if limit and len(results) >= limit:
            return True
        if row == N:
            results.append([(r, pos[r]) for r in range(N)])
            return False
        avail = mask & ~(cols | ld | rd)
        while avail:
            bit = avail & -avail
            avail -= bit
            col = bit.bit_length() - 1
            pos[row] = col
            if dfs(row + 1, cols | bit, (ld | bit) << 1, (rd | bit) >> 1):
                return True
        return False

    dfs(0, 0, 0, 0)
    return results


def print_solutions_formatted(solutions):
    for idx, sol in enumerate(solutions, 1):
        print(f"Soln {idx} :")
        for qi, (x, y) in enumerate(sol, 1):
            print(f"    Q{qi} → ({x}, {y})")
        print()


# Run and show all solutions for N=8 (there are 92)
N = 8
sols = solve_all_nqueens_bitmask(N, limit=None)
print(f"Found {len(sols)} solutions for N={N}")

root = tk.Tk()
gui = ChessBoardGUI(master=root, solutions=sols, board_size=N, queen_img_path=r"./Queen_chess_piece.png")
root.mainloop()

