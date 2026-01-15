"""
Parameter Input UI for Pendulum Simulation
Provides a user-friendly interface to input pendulum parameters before simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
import config


class ParameterInputUI:
    """
    GUI window for inputting pendulum simulation parameters
    """

    def __init__(self, parent=None):
        """Initialize the parameter input window"""
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self.window.title("Pendulum Simulation - Parameter Input")
        self.window.geometry("600x750")
        self.window.resizable(False, False)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Store parameter values
        self.parameters = {}
        self.confirmed = False

        # Create widgets
        self.create_widgets()

        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (
            self.window.winfo_width() // 2
        )
        y = (self.window.winfo_screenheight() // 2) - (
            self.window.winfo_height() // 2
        )
        self.window.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create all UI widgets"""
        # Title
        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        title_label = ttk.Label(
            self.window,
            text="Pendulum Simulation Configuration",
            font=title_font,
            foreground="#2c3e50",
        )
        title_label.pack(pady=15)

        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="About Damping", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        info_text = """Why does the pendulum keep moving?
• With damping = 0: No air resistance, pendulum oscillates forever
• With damping > 0: Air resistance slows the pendulum over time
• Higher damping = faster decay (oscillations lose energy faster)
• Real pendulums have damping and eventually stop"""

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()

        # Parameters section
        params_frame = ttk.LabelFrame(main_frame, text="Pendulum Parameters", padding="15")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Row 1: Pendulum Length
        ttk.Label(params_frame, text="Pendulum Length (units):", font=("Helvetica", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=8
        )
        self.length_var = tk.DoubleVar(value=config.PENDULUM_LENGTH)
        length_entry = ttk.Entry(params_frame, textvariable=self.length_var, width=20)
        length_entry.grid(row=0, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(typically 1-5)", font=("Helvetica", 9), foreground="gray").grid(
            row=0, column=2, sticky=tk.W
        )

        # Row 2: Bob Mass
        ttk.Label(params_frame, text="Bob Mass (kg):", font=("Helvetica", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=8
        )
        self.mass_var = tk.DoubleVar(value=config.BOB_MASS)
        mass_entry = ttk.Entry(params_frame, textvariable=self.mass_var, width=20)
        mass_entry.grid(row=1, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(typically 0.5-2)", font=("Helvetica", 9), foreground="gray").grid(
            row=1, column=2, sticky=tk.W
        )

        # Row 3: Damping Factor
        ttk.Label(params_frame, text="Damping Factor:", font=("Helvetica", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=8
        )
        self.damping_var = tk.DoubleVar(value=config.DAMPING_COEFFICIENT)
        damping_entry = ttk.Entry(params_frame, textvariable=self.damping_var, width=20)
        damping_entry.grid(row=2, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(0 = no decay, 0.1-0.5 = decay)", font=("Helvetica", 9), foreground="gray").grid(
            row=2, column=2, sticky=tk.W
        )

        # Row 4: Initial Angle
        ttk.Label(params_frame, text="Initial Angle (radians):", font=("Helvetica", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=8
        )
        self.angle_var = tk.DoubleVar(value=config.INITIAL_ANGLE)
        angle_entry = ttk.Entry(params_frame, textvariable=self.angle_var, width=20)
        angle_entry.grid(row=3, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(0.1-3.0, in radians)", font=("Helvetica", 9), foreground="gray").grid(
            row=3, column=2, sticky=tk.W
        )

        # Row 5: Gravity
        ttk.Label(params_frame, text="Gravity (m/s²):", font=("Helvetica", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=8
        )
        self.gravity_var = tk.DoubleVar(value=config.GRAVITY)
        gravity_entry = ttk.Entry(params_frame, textvariable=self.gravity_var, width=20)
        gravity_entry.grid(row=4, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(typically 9.81)", font=("Helvetica", 9), foreground="gray").grid(
            row=4, column=2, sticky=tk.W
        )

        # Row 6: Simulation Speed
        ttk.Label(params_frame, text="Simulation Speed (multiplier):", font=("Helvetica", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=8
        )
        self.speed_var = tk.DoubleVar(value=config.SIMULATION_SPEED)
        speed_entry = ttk.Entry(params_frame, textvariable=self.speed_var, width=20)
        speed_entry.grid(row=5, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(0.1-3.0, 1.0 = real-time)", font=("Helvetica", 9), foreground="gray").grid(
            row=5, column=2, sticky=tk.W
        )

        # Row 7: Window Width
        ttk.Label(params_frame, text="Window Width (pixels):", font=("Helvetica", 10)).grid(
            row=6, column=0, sticky=tk.W, pady=8
        )
        self.width_var = tk.IntVar(value=config.WINDOW_WIDTH)
        width_entry = ttk.Entry(params_frame, textvariable=self.width_var, width=20)
        width_entry.grid(row=6, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(800-1600)", font=("Helvetica", 9), foreground="gray").grid(
            row=6, column=2, sticky=tk.W
        )

        # Row 8: Window Height
        ttk.Label(params_frame, text="Window Height (pixels):", font=("Helvetica", 10)).grid(
            row=7, column=0, sticky=tk.W, pady=8
        )
        self.height_var = tk.IntVar(value=config.WINDOW_HEIGHT)
        height_entry = ttk.Entry(params_frame, textvariable=self.height_var, width=20)
        height_entry.grid(row=7, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(600-1000)", font=("Helvetica", 9), foreground="gray").grid(
            row=7, column=2, sticky=tk.W
        )

        # Row 9: Enable Trace
        ttk.Label(params_frame, text="Show Trace Path:", font=("Helvetica", 10)).grid(
            row=8, column=0, sticky=tk.W, pady=8
        )
        self.trace_var = tk.BooleanVar(value=config.SHOW_TRACE)
        trace_check = ttk.Checkbutton(params_frame, variable=self.trace_var)
        trace_check.grid(row=8, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(shows motion path)", font=("Helvetica", 9), foreground="gray").grid(
            row=8, column=2, sticky=tk.W
        )

        # Row 10: Enable Grid
        ttk.Label(params_frame, text="Show Grid:", font=("Helvetica", 10)).grid(
            row=9, column=0, sticky=tk.W, pady=8
        )
        self.grid_var = tk.BooleanVar(value=config.SHOW_GRID)
        grid_check = ttk.Checkbutton(params_frame, variable=self.grid_var)
        grid_check.grid(row=9, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(reference grid)", font=("Helvetica", 9), foreground="gray").grid(
            row=9, column=2, sticky=tk.W
        )

        # Row 11: Enable Real-time Graph
        ttk.Label(params_frame, text="Show Real-time Graph:", font=("Helvetica", 10)).grid(
            row=10, column=0, sticky=tk.W, pady=8
        )
        self.graph_var = tk.BooleanVar(value=config.SHOW_REALTIME_GRAPH)
        graph_check = ttk.Checkbutton(params_frame, variable=self.graph_var)
        graph_check.grid(row=10, column=1, sticky=tk.W, padx=10)
        ttk.Label(params_frame, text="(angle, velocity, energy plots)", font=("Helvetica", 9), foreground="gray").grid(
            row=10, column=2, sticky=tk.W
        )

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)

        # Simulate button (green)
        simulate_button = ttk.Button(
            button_frame, text="▶ Emulate Pendulum", command=self.on_simulate
        )
        simulate_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Reset button
        reset_button = ttk.Button(button_frame, text="↺ Reset to Defaults", command=self.on_reset)
        reset_button.pack(side=tk.LEFT, padx=5)

        # Quit button
        quit_button = ttk.Button(button_frame, text="✕ Quit", command=self.on_quit)
        quit_button.pack(side=tk.RIGHT, padx=5)

    def on_simulate(self):
        """Handle simulate button click"""
        try:
            # Validate inputs
            length = self.length_var.get()
            mass = self.mass_var.get()
            damping = self.damping_var.get()
            angle = self.angle_var.get()
            gravity = self.gravity_var.get()
            speed = self.speed_var.get()
            width = self.width_var.get()
            height = self.height_var.get()

            # Validation checks
            if length <= 0:
                messagebox.showerror("Invalid Input", "Pendulum length must be positive!")
                return

            if mass <= 0:
                messagebox.showerror("Invalid Input", "Mass must be positive!")
                return

            if damping < 0:
                messagebox.showerror("Invalid Input", "Damping cannot be negative!")
                return

            if gravity <= 0:
                messagebox.showerror("Invalid Input", "Gravity must be positive!")
                return

            if speed <= 0:
                messagebox.showerror("Invalid Input", "Simulation speed must be positive!")
                return

            if width < 400 or height < 300:
                messagebox.showerror("Invalid Input", "Window size too small!")
                return

            # Store parameters
            self.parameters = {
                "length": length,
                "mass": mass,
                "damping": damping,
                "initial_angle": angle,
                "gravity": gravity,
                "simulation_speed": speed,
                "window_width": width,
                "window_height": height,
                "show_trace": self.trace_var.get(),
                "show_grid": self.grid_var.get(),
                "show_graph": self.graph_var.get(),
            }

            self.confirmed = True
            self.window.destroy()

        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers!")

    def on_reset(self):
        """Reset all values to defaults"""
        self.length_var.set(config.PENDULUM_LENGTH)
        self.mass_var.set(config.BOB_MASS)
        self.damping_var.set(config.DAMPING_COEFFICIENT)
        self.angle_var.set(config.INITIAL_ANGLE)
        self.gravity_var.set(config.GRAVITY)
        self.speed_var.set(config.SIMULATION_SPEED)
        self.width_var.set(config.WINDOW_WIDTH)
        self.height_var.set(config.WINDOW_HEIGHT)
        self.trace_var.set(config.SHOW_TRACE)
        self.grid_var.set(config.SHOW_GRID)
        self.graph_var.set(config.SHOW_REALTIME_GRAPH)

    def on_quit(self):
        """Handle quit button click"""
        self.confirmed = False
        self.window.destroy()

    def run(self):
        """Run the parameter input window"""
        self.window.mainloop()
        return self.parameters if self.confirmed else None
