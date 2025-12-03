import random
from chessboard_gui import ChessBoardGUI
import tkinter as tk

def diag1(x, y, N): 
    return x - y + (N - 1)

def diag2(x, y, N): 
    return x + y

def print_solutions_formatted(solutions):
    for idx, sol in enumerate(solutions, start=1):
        print(f"Soln {idx} :")
        for qi, (x, y) in enumerate(sol, start=1):
            print(f"    Q{qi} → ({x}, {y})")
        print() 

def solve_iterative_optimized(N, max_restarts=800):

    solutions = []
    total_cells = N * N

    for attempt in range(max_restarts):

        
        row_used = [False] * N
        col_used = [False] * N
        d1_used = [False] * (2 * N - 1)   
        d2_used = [False] * (2 * N - 1)   

        queens = []

        
        all_cells = [(i, j) for i in range(N) for j in range(N)]

        for q in range(N):

            
            candidates = [
                (x, y)
                for (x, y) in all_cells
                if not row_used[x]
                and not col_used[y]
                and not d1_used[diag1(x, y, N)]
                and not d2_used[diag2(x, y, N)]
            ]

            if not candidates:
                break   

            
            x, y = random.choice(candidates)
            queens.append((x, y))

            
            row_used[x] = True
            col_used[y] = True
            d1_used[diag1(x, y, N)] = True
            d2_used[diag2(x, y, N)] = True

        
        if len(queens) == N:
            solutions.append(queens)

    return solutions

N = 8
sols = solve_iterative_optimized(N, max_restarts=3000)

root = tk.Tk()
gui = ChessBoardGUI(
    master=root,
    solutions=sols,
    board_size=N,
    queen_img_path=r"./Queen_chess_piece.png"
)
root.mainloop()