"""
Unified Window for Pendulum Simulation
Combines real-time graphs and controls - positions alongside GLUT window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import Optional, Callable


class UnifiedWindow:
    """
    Unified control and graph window - positions alongside OpenGL window
    """

    def __init__(self, width: int = 800, height: int = 900, x_position: int = 800):
        """
        Initialize the unified window
        
        Args:
            width: Window width
            height: Window height  
            x_position: X position on screen (to place next to OpenGL window)
        """
        self.window = tk.Tk()
        self.window.title("Graphs & Controls")
        
        # Position window next to OpenGL window
        self.window.geometry(f"{width}x{height}+{x_position}+0")
        
        # Callbacks
        self.render_callback: Optional[Callable] = None
        self.export_callback: Optional[Callable] = None
        self.pause_callback: Optional[Callable] = None
        self.reset_callback: Optional[Callable] = None
        self.trace_callback: Optional[Callable] = None
        
        # State
        self.is_paused = False
        self.trace_enabled = True
        
        # Graph data storage
        self.times = []
        self.angles = []
        self.velocities = []
        self.kinetic_energies = []
        self.potential_energies = []
        self.total_energies = []
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the unified UI layout"""
        # Main container
        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Graphs
        graph_frame = tk.Frame(main_container, bg='white')
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 8), dpi=100, facecolor='white')
        
        # Create subplots
        self.ax_angle = self.fig.add_subplot(311)
        self.ax_angle.set_title('Angular Position', fontsize=10, fontweight='bold')
        self.ax_angle.set_ylabel('Angle (rad)', fontsize=9)
        self.ax_angle.grid(True, alpha=0.3)
        self.line_angle, = self.ax_angle.plot([], [], 'b-', linewidth=2)
        
        self.ax_velocity = self.fig.add_subplot(312)
        self.ax_velocity.set_title('Angular Velocity', fontsize=10, fontweight='bold')
        self.ax_velocity.set_ylabel('Velocity (rad/s)', fontsize=9)
        self.ax_velocity.grid(True, alpha=0.3)
        self.line_velocity, = self.ax_velocity.plot([], [], 'g-', linewidth=2)
        
        self.ax_energy = self.fig.add_subplot(313)
        self.ax_energy.set_title('Energy Analysis', fontsize=10, fontweight='bold')
        self.ax_energy.set_xlabel('Time (s)', fontsize=9)
        self.ax_energy.set_ylabel('Energy (J)', fontsize=9)
        self.ax_energy.grid(True, alpha=0.3)
        self.line_ke, = self.ax_energy.plot([], [], 'r-', linewidth=2, label='Kinetic')
        self.line_pe, = self.ax_energy.plot([], [], 'orange', linewidth=2, label='Potential')
        self.line_total, = self.ax_energy.plot([], [], 'purple', linewidth=2, label='Total')
        self.ax_energy.legend(loc='upper right', fontsize=8)
        
        self.fig.tight_layout(pad=2.0)
        
        # Embed matplotlib in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bottom section - Controls
        control_frame = tk.Frame(main_container, bg='#34495e', height=100)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        control_frame.pack_propagate(False)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#34495e')
        button_frame.pack(expand=True)
        
        # Export button (highlighted)
        self.export_btn = tk.Button(
            button_frame,
            text="📊 EXPORT DATA & GRAPH",
            command=self.handle_export,
            bg='#27ae60',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            width=22,
            height=2,
            cursor='hand2'
        )
        self.export_btn.pack(side=tk.LEFT, padx=10)
        
        # Pause/Resume button
        self.pause_btn = tk.Button(
            button_frame,
            text="⏸ PAUSE",
            command=self.handle_pause,
            bg='#3498db',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            width=12,
            height=2,
            cursor='hand2'
        )
        self.pause_btn.pack(side=tk.LEFT, padx=10)
        
        # Reset button
        self.reset_btn = tk.Button(
            button_frame,
            text="↺ RESET",
            command=self.handle_reset,
            bg='#e74c3c',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            width=12,
            height=2,
            cursor='hand2'
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Toggle Trace button
        self.trace_btn = tk.Button(
            button_frame,
            text="👁 TRACE: ON",
            command=self.handle_trace,
            bg='#9b59b6',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            width=12,
            height=2,
            cursor='hand2'
        )
        self.trace_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="● RUNNING",
            font=('Helvetica', 12, 'bold'),
            fg='#27ae60',
            bg='#34495e'
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Keyboard shortcuts info
        info_label = tk.Label(
            control_frame,
            text="Shortcuts: SPACE=Pause | R=Reset | T=Trace | E=Export | Q=Quit",
            font=('Courier', 9),
            fg='white',
            bg='#34495e'
        )
        info_label.pack(side=tk.BOTTOM, pady=5)
        
    def set_render_callback(self, callback: Callable):
        """Set the OpenGL render callback"""
        self.render_callback = callback
        
    def set_export_callback(self, callback: Callable):
        """Set the export callback"""
        self.export_callback = callback
        
    def set_pause_callback(self, callback: Callable):
        """Set the pause callback"""
        self.pause_callback = callback
        
    def set_reset_callback(self, callback: Callable):
        """Set the reset callback"""
        self.reset_callback = callback
        
    def set_trace_callback(self, callback: Callable):
        """Set the trace toggle callback"""
        self.trace_callback = callback
        
    def handle_export(self):
        """Handle export button click"""
        if self.export_callback:
            self.export_callback()
            messagebox.showinfo(
                "Export Complete",
                "✓ Data exported to: pendulum_data.csv\n✓ Graph saved to: pendulum_graph.png\n\nCheck the project directory.",
                parent=self.window
            )
    
    def handle_pause(self):
        """Handle pause button click"""
        self.is_paused = not self.is_paused
        if self.pause_callback:
            self.pause_callback()
        
        if self.is_paused:
            self.pause_btn.config(text="▶ RESUME")
            self.status_label.config(text="● PAUSED", fg="#e74c3c")
        else:
            self.pause_btn.config(text="⏸ PAUSE")
            self.status_label.config(text="● RUNNING", fg="#27ae60")
    
    def handle_reset(self):
        """Handle reset button click"""
        if self.reset_callback:
            self.reset_callback()
        self.is_paused = False
        self.pause_btn.config(text="⏸ PAUSE")
        self.status_label.config(text="● RUNNING", fg="#3498db")
    
    def handle_trace(self):
        """Handle trace toggle button click"""
        self.trace_enabled = not self.trace_enabled
        if self.trace_callback:
            self.trace_callback()
        
        if self.trace_enabled:
            self.trace_btn.config(text="👁 TRACE: ON")
        else:
            self.trace_btn.config(text="👁 TRACE: OFF")
    
    def add_graph_data(self, time: float, angle: float, velocity: float,
                      ke: float, pe: float, total: float):
        """Add data point to graphs"""
        self.times.append(time)
        self.angles.append(angle)
        self.velocities.append(velocity)
        self.kinetic_energies.append(ke)
        self.potential_energies.append(pe)
        self.total_energies.append(total)
        
        # Limit data points for performance
        max_points = 500
        if len(self.times) > max_points:
            self.times = self.times[-max_points:]
            self.angles = self.angles[-max_points:]
            self.velocities = self.velocities[-max_points:]
            self.kinetic_energies = self.kinetic_energies[-max_points:]
            self.potential_energies = self.potential_energies[-max_points:]
            self.total_energies = self.total_energies[-max_points:]
    
    def update_graphs(self):
        """Update the graph displays"""
        if not self.times:
            return
        
        # Update angle plot
        self.line_angle.set_data(self.times, self.angles)
        self.ax_angle.relim()
        self.ax_angle.autoscale_view()
        
        # Update velocity plot
        self.line_velocity.set_data(self.times, self.velocities)
        self.ax_velocity.relim()
        self.ax_velocity.autoscale_view()
        
        # Update energy plots
        self.line_ke.set_data(self.times, self.kinetic_energies)
        self.line_pe.set_data(self.times, self.potential_energies)
        self.line_total.set_data(self.times, self.total_energies)
        self.ax_energy.relim()
        self.ax_energy.autoscale_view()
        
        # Redraw
        self.canvas.draw_idle()
    
    def clear_graphs(self):
        """Clear all graph data"""
        self.times.clear()
        self.angles.clear()
        self.velocities.clear()
        self.kinetic_energies.clear()
        self.potential_energies.clear()
        self.total_energies.clear()
        
        # Clear plot lines
        self.line_angle.set_data([], [])
        self.line_velocity.set_data([], [])
        self.line_ke.set_data([], [])
        self.line_pe.set_data([], [])
        self.line_total.set_data([], [])
        
        self.canvas.draw_idle()
    
    def save_graph(self, filename: str = 'pendulum_graph.png'):
        """Save current graph to file"""
        try:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Graph saved to {filename}")
        except Exception as e:
            print(f"Error saving graph: {e}")
    
    def update(self):
        """Update the window (call in main loop)"""
        try:
            self.window.update()
        except tk.TclError:
            pass
    
    def mainloop(self):
        """Run the window main loop"""
        self.window.mainloop()
    
    def destroy(self):
        """Close the window"""
        try:
            self.window.destroy()
        except:
            pass
