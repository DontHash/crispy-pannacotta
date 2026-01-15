"""
Control Panel UI for Pendulum Simulation
Provides runtime controls including export functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
from typing import Callable, Optional


class ControlPanel:
    """
    Control panel window for runtime simulation controls
    Provides buttons for export, pause/resume, reset, etc.
    """

    def __init__(self, on_export: Callable = None, on_pause: Callable = None, 
                 on_reset: Callable = None, on_toggle_trace: Callable = None):
        """
        Initialize the control panel window
        
        Args:
            on_export: Callback function for export button
            on_pause: Callback function for pause/resume button
            on_reset: Callback function for reset button
            on_toggle_trace: Callback function for toggle trace button
        """
        self.window = tk.Tk()
        self.window.title("Pendulum Controls")
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        
        # Store callbacks
        self.on_export = on_export
        self.on_pause = on_pause
        self.on_reset = on_reset
        self.on_toggle_trace = on_toggle_trace
        
        # State tracking
        self.is_paused = False
        self.trace_enabled = True
        
        # Create widgets
        self.create_widgets()
        
        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Make window stay on top
        self.window.attributes('-topmost', True)

    def create_widgets(self):
        """Create all UI widgets"""
        # Title
        title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        title_label = ttk.Label(
            self.window,
            text="Simulation Controls",
            font=title_font,
            foreground="#2c3e50",
        )
        title_label.pack(pady=15)
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="Keyboard Shortcuts", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        shortcuts_text = """SPACE: Pause/Resume
R: Reset simulation
T: Toggle trace
E: Export data & graph
Q: Quit simulation"""
        
        shortcuts_label = ttk.Label(info_frame, text=shortcuts_text, justify=tk.LEFT, font=("Courier", 9))
        shortcuts_label.pack()
        
        # Control buttons section
        controls_frame = ttk.LabelFrame(main_frame, text="Quick Controls", padding="15")
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Export button (highlighted)
        self.export_button = tk.Button(
            controls_frame,
            text="📊 Export Data & Graph",
            command=self.handle_export,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 11, "bold"),
            height=2,
            cursor="hand2"
        )
        self.export_button.pack(fill=tk.X, pady=8)
        
        # Pause/Resume button
        self.pause_button = ttk.Button(
            controls_frame,
            text="⏸ Pause",
            command=self.handle_pause
        )
        self.pause_button.pack(fill=tk.X, pady=5)
        
        # Reset button
        reset_button = ttk.Button(
            controls_frame,
            text="↺ Reset Simulation",
            command=self.handle_reset
        )
        reset_button.pack(fill=tk.X, pady=5)
        
        # Toggle Trace button
        self.trace_button = ttk.Button(
            controls_frame,
            text="👁 Hide Trace",
            command=self.handle_toggle_trace
        )
        self.trace_button.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Status: Running",
            font=("Helvetica", 10),
            foreground="#27ae60"
        )
        self.status_label.pack(pady=10)

    def handle_export(self):
        """Handle export button click"""
        if self.on_export:
            self.on_export()
            messagebox.showinfo(
                "Export Complete",
                "Data has been exported to:\n• pendulum_data.csv\n• pendulum_graph.png\n\nCheck the project directory."
            )

    def handle_pause(self):
        """Handle pause/resume button click"""
        if self.on_pause:
            self.is_paused = not self.is_paused
            self.on_pause()
            
            if self.is_paused:
                self.pause_button.config(text="▶ Resume")
                self.status_label.config(text="Status: Paused", foreground="#e74c3c")
            else:
                self.pause_button.config(text="⏸ Pause")
                self.status_label.config(text="Status: Running", foreground="#27ae60")

    def handle_reset(self):
        """Handle reset button click"""
        if self.on_reset:
            self.on_reset()
            self.is_paused = False
            self.pause_button.config(text="⏸ Pause")
            self.status_label.config(text="Status: Running (Reset)", foreground="#3498db")

    def handle_toggle_trace(self):
        """Handle toggle trace button click"""
        if self.on_toggle_trace:
            self.trace_enabled = not self.trace_enabled
            self.on_toggle_trace()
            
            if self.trace_enabled:
                self.trace_button.config(text="👁 Hide Trace")
            else:
                self.trace_button.config(text="👁 Show Trace")

    def update(self):
        """Update the control panel (call this in main loop)"""
        try:
            self.window.update()
        except tk.TclError:
            # Window was closed
            pass

    def is_alive(self) -> bool:
        """Check if the window is still open"""
        try:
            return self.window.winfo_exists()
        except tk.TclError:
            return False

    def destroy(self):
        """Close the control panel window"""
        try:
            self.window.destroy()
        except:
            pass
