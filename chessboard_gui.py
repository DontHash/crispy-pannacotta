# chessboard_gui.py

import tkinter as tk
from PIL import Image, ImageTk

class ChessBoardGUI:
    def __init__(self, master, solutions, board_size, queen_img_path):
        self.master = master
        self.master.title("N-Queens Viewer")

        self.solutions = solutions
        self.N = board_size
        self.index = 0  

        
        self.board_px = 600
        self.square = self.board_px // self.N

        # load queen image 
        img = Image.open(queen_img_path)
        img = img.resize((self.square - 10, self.square - 10), Image.LANCZOS)
        self.queen_image = ImageTk.PhotoImage(img)

        # canvas for drawing board
        self.canvas = tk.Canvas(
            master,
            width=self.board_px + 40,
            height=self.board_px + 40
        )
        self.canvas.pack(pady=10)

        
        btn_frame = tk.Frame(master)
        btn_frame.pack()

        tk.Button(btn_frame, text="<< Prev", command=self.prev_solution).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Next >>", command=self.next_solution).pack(side=tk.LEFT, padx=10)

        
        master.bind("<Left>", lambda e: self.prev_solution())
        master.bind("<Right>", lambda e: self.next_solution())

        self.draw_solution()


    # Draw chessboard + queens
   
    def draw_solution(self):
        self.canvas.delete("all")

        # Draw board
        for r in range(self.N):
            for c in range(self.N):
                x1 = c * self.square + 20
                y1 = r * self.square + 20
                x2 = x1 + self.square
                y2 = y1 + self.square

                
                color = "#EEEED2" if (r + c) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        # Board labels (a,b,c...) & (1,2...)
        for i in range(self.N):
            # columns
            col_label = chr(ord('A') + i)
            self.canvas.create_text(20 + i*self.square + self.square/2,
                                    10, text=col_label, font=("Arial", 12, "bold"))
            # rows
            self.canvas.create_text(10,
                                    20 + i*self.square + self.square/2,
                                    text=str(self.N-i), font=("Arial", 12, "bold"))

        # Draw queens
        queens = self.solutions[self.index]
        for (x, y) in queens:
            cx = y * self.square + 20 + self.square/2
            cy = x * self.square + 20 + self.square/2
            self.canvas.create_image(cx, cy, image=self.queen_image)

        
        self.master.title(f"N-Queens Viewer — Solution {self.index+1}/{len(self.solutions)}")


    def next_solution(self):
        self.index = (self.index + 1) % len(self.solutions)
        self.draw_solution()

    def prev_solution(self):
        self.index = (self.index - 1) % len(self.solutions)
        self.draw_solution()
