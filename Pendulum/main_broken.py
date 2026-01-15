"""
Pendulum Simulation Application - Unified Interface
Main entry point with side-by-side windows
"""

import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import config
from physics import Pendulum
from graphics import Renderer
from utils import Timer, FrameRateLimiter, DataRecorder, PhysicsValidator
from ui import ParameterInputUI, UnifiedWindow


class PendulumSimulationUnified:
    """
    Main simulation class using side-by-side unified interface
    """

    def __init__(self, parameters=None):
        """Initialize the pendulum simulation"""
        # Use provided parameters or defaults
        if parameters:
            length = parameters.get("length", config.PENDULUM_LENGTH)
            mass = parameters.get("mass", config.BOB_MASS)
            gravity = parameters.get("gravity", config.GRAVITY)
            initial_angle = parameters.get("initial_angle", config.INITIAL_ANGLE)
            damping = parameters.get("damping", config.DAMPING_COEFFICIENT)
            simulation_width = parameters.get("window_width", 800)
            simulation_height = parameters.get("window_height", 900)
            show_trace = parameters.get("show_trace", config.SHOW_TRACE)
            show_grid = parameters.get("show_grid", config.SHOW_GRID)
            simulation_speed = parameters.get("simulation_speed", config.SIMULATION_SPEED)
        else:
            length = config.PENDULUM_LENGTH
            mass = config.BOB_MASS
            gravity = config.GRAVITY
            initial_angle = config.INITIAL_ANGLE
            damping = config.DAMPING_COEFFICIENT
            simulation_width = 800
            simulation_height = 900
            show_trace = config.SHOW_TRACE
            show_grid = config.SHOW_GRID
            simulation_speed = config.SIMULATION_SPEED

        # Physics
        self.pendulum = Pendulum(
            length=length,
            mass=mass,
            gravity=gravity,
            initial_angle=initial_angle,
            damping=damping,
        )

        # Graphics
        self.renderer = Renderer(simulation_width, simulation_height)

        # Timing
        self.timer = Timer()
        self.frame_limiter = FrameRateLimiter(config.TARGET_FPS)

        # Data recording
        self.recorder = DataRecorder()
        self.initial_energy = 0.0

        # Simulation state
        self.simulation_running = True
        self.simulation_paused = False
        self.show_trace = show_trace
        self.show_grid = show_grid
        self.accumulated_time = 0.0
        self.graph_update_accumulator = 0.0
        
        # Store parameters
        self.params = {
            "length": length,
            "mass": mass,
            "gravity": gravity,
            "initial_angle": initial_angle,
            "damping": damping,
            "simulation_width": simulation_width,
            "simulation_height": simulation_height,
            "simulation_speed": simulation_speed,
        }
        
        # Create unified window for graphs and controls (positioned to the right)
        self.window = UnifiedWindow(
            width=800,
            height=simulation_height,
            x_position=simulation_width + 10
        )
        
        # Set callbacks
        self.window.set_export_callback(self.export_data)
        self.window.set_pause_callback(self.toggle_pause)
        self.window.set_reset_callback(self.reset_simulation)
        self.window.set_trace_callback(self.toggle_trace)

    def initialize_glut(self):
        """Initialize GLUT and OpenGL"""
        # Initialize GLUT
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(self.params["simulation_width"], self.params["simulation_height"])
        glutInitWindowPosition(0, 0)  # Position at left edge
        glutCreateWindow(b"Pendulum Simulation")

        # OpenGL settings
        glClearColor(*config.BACKGROUND_COLOR)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Setup projection
        self.renderer.setup_projection()
        self.renderer.setup_viewport()

        # Register callbacks
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutTimerFunc(int(1000.0 / config.TARGET_FPS), self.timer_callback, 0)

        # Calculate initial energy
        total_energy, ke, pe = self.pendulum.get_energy()
        self.initial_energy = total_energy

        self.print_startup_info()

    def print_startup_info(self):
        """Print simulation startup information"""
        print("=" * 60)
        print("PENDULUM SIMULATION - SIDE-BY-SIDE UNIFIED INTERFACE")
        print("=" * 60)
        print(f"Pendulum Length: {self.params['length']:.4f} units")
        print(f"Bob Mass: {self.params['mass']:.4f} kg")
        print(f"Gravity: {self.params['gravity']:.4f} m/s²")
        print(f"Initial Angle: {self.params['initial_angle']:.4f} radians")
        print(f"Damping Factor: {self.params['damping']:.4f}")
        if self.params['damping'] > 0:
            print("  ✓ Pendulum will DECAY over time")
        else:
            print("  ✗ Pendulum will NOT decay (damping = 0)")
        print(f"Simulation Speed: {self.params['simulation_speed']}x")
        print(f"Initial Energy: {self.initial_energy:.6f} J")
        print("\nUNIFIED INTERFACE:")
        print("  Left Window: Pendulum Simulation")
        print("  Right Window: Real-time Graphs & Controls")
        print("\nKEYBOARD SHORTCUTS (in simulation window):")
        print("  SPACE: Pause/Resume")
        print("  R: Reset")
        print("  T: Toggle trace")
        print("  E: Export data & graph")
        print("  Q: Quit")
        print("=" * 60)

    def display(self):
        """OpenGL display callback"""
        if not self.simulation_running:
            return

        # Update unified window
        try:
            self.window.update()
        except:
            pass

        # Update physics if not paused
        if not self.simulation_paused:
            self.update_physics()

        # Render scene
        self.render_scene()

        # Swap buffers
        glutSwapBuffers()

    def update_physics(self):
        """Update physics simulation"""
        # Get time delta
        dt = self.timer.update()
        scaled_dt = dt * self.params["simulation_speed"]

        # Update pendulum physics multiple times per frame for accuracy
        steps = max(1, int(scaled_dt / config.TIME_STEP))
        for _ in range(steps):
            self.pendulum.update(config.TIME_STEP)

        # Add trace point
        if self.show_trace:
            bob_x, bob_y = self.pendulum.get_bob_position(config.PIVOT_X, config.PIVOT_Y)
            self.renderer.add_trace_point(bob_x, bob_y)

        # Record data
        self.accumulated_time += scaled_dt
        total_energy, ke, pe = self.pendulum.get_energy()

        if config.LOG_PHYSICS_DATA:
            self.recorder.record(
                time=self.accumulated_time,
                angle=self.pendulum.angle,
                angular_velocity=self.pendulum.angular_velocity,
                angular_acceleration=self.pendulum.angular_acceleration,
                total_energy=total_energy,
                kinetic_energy=ke,
                potential_energy=pe,
            )

        # Update graph data
        self.window.add_graph_data(
            time=self.accumulated_time,
            angle=self.pendulum.angle,
            velocity=self.pendulum.angular_velocity,
            ke=ke,
            pe=pe,
            total=total_energy
        )
        
        # Update graph display periodically
        self.graph_update_accumulator += scaled_dt
        if self.graph_update_accumulator >= config.GRAPH_UPDATE_INTERVAL:
            self.window.update_graphs()
            self.graph_update_accumulator = 0.0

    def render_scene(self):
        """Render the OpenGL scene"""
        # Clear screen
        self.renderer.clear_screen()

        # Get pendulum positions
        bob_x, bob_y = self.pendulum.get_bob_position(config.PIVOT_X, config.PIVOT_Y)

        # Draw grid
        if self.show_grid:
            self.renderer.draw_grid(config.GRID_SIZE)

        # Draw trace
        if self.show_trace:
            self.renderer.draw_trace()

        # Draw pendulum
        self.renderer.draw_pivot_point(config.PIVOT_X, config.PIVOT_Y)
        self.renderer.draw_rod(config.PIVOT_X, config.PIVOT_Y, bob_x, bob_y)
        self.renderer.draw_bob(bob_x, bob_y)

    def reshape(self, width: int, height: int):
        """Handle window resize"""
        self.renderer.width = width
        self.renderer.height = height
        self.renderer.setup_projection()
        self.renderer.setup_viewport()

    def keyboard(self, key: bytes, x: int, y: int):
        """Handle keyboard input"""
        key_char = key.decode("utf-8") if isinstance(key, bytes) else key

        if key_char == " ":  # Space - Pause/Resume
            self.toggle_pause()
            # Update button state in unified window
            if hasattr(self.window, 'is_paused'):
                self.window.is_paused = self.simulation_paused
                if self.simulation_paused:
                    self.window.pause_btn.config(text="▶ RESUME")
                    self.window.status_label.config(text="● PAUSED", fg="#e74c3c")
                else:
                    self.window.pause_btn.config(text="⏸ PAUSE")
                    self.window.status_label.config(text="● RUNNING", fg="#27ae60")

        elif key_char.upper() == "R":  # Reset
            self.reset_simulation()

        elif key_char.upper() == "T":  # Toggle trace
            self.toggle_trace()
            # Update button state in unified window
            if hasattr(self.window, 'trace_enabled'):
                self.window.trace_enabled = self.show_trace
                if self.show_trace:
                    self.window.trace_btn.config(text="👁 TRACE: ON")
                else:
                    self.window.trace_btn.config(text="👁 TRACE: OFF")

        elif key_char.upper() == "E":  # Export data
            self.export_data()

        elif key_char == "\x1b" or key_char.upper() == "Q":  # ESC or Q - Quit
            print("Exiting simulation...")
            sys.exit(0)

    def toggle_pause(self):
        """Toggle pause state"""
        self.simulation_paused = not self.simulation_paused
        status = "PAUSED" if self.simulation_paused else "RUNNING"
        print(f"Simulation {status}")

    def reset_simulation(self):
        """Reset simulation"""
        self.pendulum.reset(self.params['initial_angle'])
        self.renderer.clear_trace()
        self.accumulated_time = 0.0
        self.graph_update_accumulator = 0.0
        total_energy, _, _ = self.pendulum.get_energy()
        self.initial_energy = total_energy
        self.window.clear_graphs()
        self.recorder.clear()
        print("Simulation RESET")

    def toggle_trace(self):
        """Toggle trace visibility"""
        self.show_trace = not self.show_trace
        if not self.show_trace:
            self.renderer.clear_trace()
        status = "ON" if self.show_trace else "OFF"
        print(f"Trace {status}")

    def export_data(self):
        """Export data and graph"""
        self.recorder.export_csv("pendulum_data.csv")
        self.window.save_graph("pendulum_graph.png")
        print("✓ Data exported to pendulum_data.csv")
        print("✓ Graph saved to pendulum_graph.png")

    def timer_callback(self, value):
        """Timer callback for continuous redrawing"""
        if self.simulation_running:
            glutPostRedisplay()
            glutTimerFunc(int(1000.0 / config.TARGET_FPS), self.timer_callback, 0)

    def run(self):
        """Start the simulation"""
        self.initialize_glut()
        glutMainLoop()


def main():
    """Main entry point"""
    # Show parameter input UI
    ui = ParameterInputUI()
    parameters = ui.run()

    if parameters is None:
        print("Simulation cancelled by user")
        sys.exit(0)

    # Create and run simulation
    simulation = PendulumSimulationUnified(parameters)
    simulation.run()


if __name__ == "__main__":
    main()
