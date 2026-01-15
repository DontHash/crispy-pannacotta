"""
Real-time graph module for Pendulum Simulation
Displays angle, velocity, and energy plots during simulation
"""

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for compatibility
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List, Tuple
import numpy as np


class RealtimeGraph:
    """
    Creates and manages real-time plots for pendulum simulation data.
    Displays angle, angular velocity, and energy (kinetic, potential, total) over time.
    """

    def __init__(self, update_interval: int = 100):
        """
        Initialize the real-time graph window.

        Args:
            update_interval: Update interval in milliseconds (default 100ms)
        """
        self.update_interval = update_interval
        
        # Data storage
        self.times: List[float] = []
        self.angles: List[float] = []
        self.velocities: List[float] = []
        self.kinetic_energies: List[float] = []
        self.potential_energies: List[float] = []
        self.total_energies: List[float] = []
        
        # Create figure and subplots
        self.fig, self.axes = plt.subplots(3, 1, figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('Pendulum Data - Real-time Analysis')
        
        # Configure subplot 1: Angle
        self.ax_angle = self.axes[0]
        self.ax_angle.set_title('Angular Position Over Time', fontsize=12, fontweight='bold')
        self.ax_angle.set_ylabel('Angle (radians)', fontsize=10)
        self.ax_angle.grid(True, alpha=0.3)
        self.line_angle, = self.ax_angle.plot([], [], 'b-', linewidth=2, label='Angle')
        self.ax_angle.legend(loc='upper right')
        
        # Configure subplot 2: Angular Velocity
        self.ax_velocity = self.axes[1]
        self.ax_velocity.set_title('Angular Velocity Over Time', fontsize=12, fontweight='bold')
        self.ax_velocity.set_ylabel('Angular Velocity (rad/s)', fontsize=10)
        self.ax_velocity.grid(True, alpha=0.3)
        self.line_velocity, = self.ax_velocity.plot([], [], 'g-', linewidth=2, label='Velocity')
        self.ax_velocity.legend(loc='upper right')
        
        # Configure subplot 3: Energy
        self.ax_energy = self.axes[2]
        self.ax_energy.set_title('Energy Over Time', fontsize=12, fontweight='bold')
        self.ax_energy.set_xlabel('Time (seconds)', fontsize=10)
        self.ax_energy.set_ylabel('Energy (Joules)', fontsize=10)
        self.ax_energy.grid(True, alpha=0.3)
        self.line_ke, = self.ax_energy.plot([], [], 'r-', linewidth=2, label='Kinetic Energy')
        self.line_pe, = self.ax_energy.plot([], [], 'orange', linewidth=2, label='Potential Energy')
        self.line_total, = self.ax_energy.plot([], [], 'purple', linewidth=2, label='Total Energy')
        self.ax_energy.legend(loc='upper right')
        
        plt.tight_layout()
        
        # Show the window in non-blocking mode
        plt.ion()
        plt.show(block=False)
        
        self.last_update_time = 0.0

    def add_data_point(self, time: float, angle: float, velocity: float, 
                      ke: float, pe: float, total_energy: float) -> None:
        """
        Add a new data point to the graph.

        Args:
            time: Simulation time in seconds
            angle: Angular position in radians
            velocity: Angular velocity in rad/s
            ke: Kinetic energy in Joules
            pe: Potential energy in Joules
            total_energy: Total energy in Joules
        """
        self.times.append(time)
        self.angles.append(angle)
        self.velocities.append(velocity)
        self.kinetic_energies.append(ke)
        self.potential_energies.append(pe)
        self.total_energies.append(total_energy)

    def update(self, current_time: float, max_points: int = 500) -> None:
        """
        Update the graph display with latest data.

        Args:
            current_time: Current simulation time
            max_points: Maximum number of points to display (for performance)
        """
        if not self.times:
            return
            
        # Limit data points for performance
        if len(self.times) > max_points:
            start_idx = len(self.times) - max_points
            times = self.times[start_idx:]
            angles = self.angles[start_idx:]
            velocities = self.velocities[start_idx:]
            ke = self.kinetic_energies[start_idx:]
            pe = self.potential_energies[start_idx:]
            total = self.total_energies[start_idx:]
        else:
            times = self.times
            angles = self.angles
            velocities = self.velocities
            ke = self.kinetic_energies
            pe = self.potential_energies
            total = self.total_energies
        
        # Update angle plot
        self.line_angle.set_data(times, angles)
        self.ax_angle.relim()
        self.ax_angle.autoscale_view()
        
        # Update velocity plot
        self.line_velocity.set_data(times, velocities)
        self.ax_velocity.relim()
        self.ax_velocity.autoscale_view()
        
        # Update energy plots
        self.line_ke.set_data(times, ke)
        self.line_pe.set_data(times, pe)
        self.line_total.set_data(times, total)
        self.ax_energy.relim()
        self.ax_energy.autoscale_view()
        
        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
        self.last_update_time = current_time

    def should_update(self, current_time: float, interval: float = 0.1) -> bool:
        """
        Check if enough time has passed to update the graph.

        Args:
            current_time: Current simulation time
            interval: Minimum time between updates in seconds

        Returns:
            True if graph should be updated
        """
        return (current_time - self.last_update_time) >= interval

    def clear(self) -> None:
        """Clear all data from the graph"""
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
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def close(self) -> None:
        """Close the graph window"""
        plt.close(self.fig)

    def save_plot(self, filename: str = 'pendulum_analysis.png') -> None:
        """
        Save the current graph to a file.

        Args:
            filename: Output filename (default 'pendulum_analysis.png')
        """
        try:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Graph saved to {filename}")
        except Exception as e:
            print(f"Error saving graph: {e}")
